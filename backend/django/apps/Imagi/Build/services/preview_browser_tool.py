"""
The preview browser as a tool for the agent.

Claude's browser use toolset (browser_toolset_20260801) is a client toolset:
the model asks for actions — navigate, screenshot, click, type, read the page
— and the harness carries them out in a browser of its own. Here that browser
is the workspace preview: the headless Chromium BrowserPreviewService already
runs next to the project's dev servers. The coordinator and threads drive the
same page the user watches in the preview pane, so every action shows up
there as it happens.

Coordinates are viewport pixels of the screenshots this returns. A viewport
larger than SCREENSHOT_MAX_EDGE is shot scaled down, and the model's
coordinates are scaled back up before they reach the page.

Element references (ref_1, ref_2, ...) come from read_page and find. They are
kept inside the page (window.__imagiAgent), like the console-error buffer —
any worker can serve any call, and a navigation clears them for free.

Only the app's own pages open: navigate takes a path or a URL on the app's
origin, and an action that lands the page anywhere else is undone.
"""

import json
import logging
import time
from urllib.parse import urlsplit

from .agent_runtime import ClientToolset

logger = logging.getLogger(__name__)

# The longest edge, in pixels, of a screenshot sent to the model. Small enough
# that a long session's screenshots stay inside the API's per-image limits,
# large enough to read body text.
SCREENSHOT_MAX_EDGE = 1280
SCREENSHOT_JPEG_QUALITY = 80

# read_page / get_page_text output ceiling (the toolset's own limit).
PAGE_TEXT_MAX_CHARS = 50_000
FIND_MAX_RESULTS = 20
MAX_WAIT_S = 30
NAVIGATION_SETTLE_S = 3.0

TAB_ID = 'preview'

# Members this harness implements. Tab management is off (the preview has one
# page), as are the members that need more trust than an agent editing a
# business's site should have: arbitrary JavaScript, file uploads, and a raw
# network log.
DISABLED_MEMBERS = (
    'new_tab', 'list_tabs', 'switch_tab', 'close_tab',
    'javascript_exec', 'file_upload', 'read_network', 'hold_key',
)
ENABLED_OPTIONAL_MEMBERS = ('read_console',)

# CDP modifier bitmask.
_MODIFIER_BITS = {
    'alt': 1, 'option': 1,
    'ctrl': 2, 'control': 2,
    'meta': 4, 'cmd': 4, 'command': 4, 'super': 4, 'win': 4,
    'shift': 8,
}

# Named keys: key value, code, Windows virtual key code, and the text the
# key types (if any).
_NAMED_KEYS = {
    'enter': ('Enter', 'Enter', 13, '\r'),
    'return': ('Enter', 'Enter', 13, '\r'),
    'tab': ('Tab', 'Tab', 9, ''),
    'escape': ('Escape', 'Escape', 27, ''),
    'esc': ('Escape', 'Escape', 27, ''),
    'backspace': ('Backspace', 'Backspace', 8, ''),
    'delete': ('Delete', 'Delete', 46, ''),
    'space': (' ', 'Space', 32, ' '),
    'arrowup': ('ArrowUp', 'ArrowUp', 38, ''),
    'up': ('ArrowUp', 'ArrowUp', 38, ''),
    'arrowdown': ('ArrowDown', 'ArrowDown', 40, ''),
    'down': ('ArrowDown', 'ArrowDown', 40, ''),
    'arrowleft': ('ArrowLeft', 'ArrowLeft', 37, ''),
    'left': ('ArrowLeft', 'ArrowLeft', 37, ''),
    'arrowright': ('ArrowRight', 'ArrowRight', 39, ''),
    'right': ('ArrowRight', 'ArrowRight', 39, ''),
    'home': ('Home', 'Home', 36, ''),
    'end': ('End', 'End', 35, ''),
    'pageup': ('PageUp', 'PageUp', 33, ''),
    'page_up': ('PageUp', 'PageUp', 33, ''),
    'pagedown': ('PageDown', 'PageDown', 34, ''),
    'page_down': ('PageDown', 'PageDown', 34, ''),
}
_NAMED_KEYS.update({f'f{n}': (f'F{n}', f'F{n}', 111 + n, '') for n in range(1, 13)})

# The in-page half of the toolset: accessibility-style page reading, element
# refs, and form filling. Installed lazily on every call that needs it (a
# navigation starts a fresh document without it).
_AGENT_JS = r"""
(function () {
  if (window.__imagiAgent) return window.__imagiAgent;
  var refs = new Map(), ids = new WeakMap(), next = 1;
  var INTERACTIVE = {link: 1, button: 1, textbox: 1, searchbox: 1, checkbox: 1, radio: 1,
    combobox: 1, slider: 1, option: 1, tab: 1, menuitem: 1, 'switch': 1, spinbutton: 1};
  var NAMED_BY_TEXT = {link: 1, button: 1, heading: 1, option: 1, tab: 1, menuitem: 1,
    paragraph: 1, listitem: 1, cell: 1, columnheader: 1, label: 1, text: 1};
  function refOf(el) {
    var id = ids.get(el);
    if (!id) { id = 'ref_' + (next++); ids.set(el, id); refs.set(id, new WeakRef(el)); }
    return id;
  }
  function clean(text, max) {
    text = String(text == null ? '' : text).replace(/\s+/g, ' ').trim();
    return text.length > max ? text.slice(0, max - 1) + '…' : text;
  }
  function roleOf(el) {
    var explicit = el.getAttribute('role');
    if (explicit) return explicit.split(' ')[0];
    var tag = el.tagName.toLowerCase();
    switch (tag) {
      case 'a': return el.hasAttribute('href') ? 'link' : null;
      case 'button': case 'summary': return 'button';
      case 'select': return 'combobox';
      case 'textarea': return 'textbox';
      case 'option': return 'option';
      case 'input':
        var type = (el.getAttribute('type') || 'text').toLowerCase();
        if (type === 'hidden') return null;
        if (['button', 'submit', 'reset', 'image'].indexOf(type) >= 0) return 'button';
        if (type === 'checkbox') return 'checkbox';
        if (type === 'radio') return 'radio';
        if (type === 'range') return 'slider';
        if (type === 'number') return 'spinbutton';
        return type === 'search' ? 'searchbox' : 'textbox';
      case 'h1': case 'h2': case 'h3': case 'h4': case 'h5': case 'h6': return 'heading';
      case 'img': return 'img';
      case 'nav': return 'navigation';
      case 'main': return 'main';
      case 'header': return 'banner';
      case 'footer': return 'contentinfo';
      case 'aside': return 'complementary';
      case 'form': return 'form';
      case 'dialog': return 'dialog';
      case 'ul': case 'ol': return 'list';
      case 'li': return 'listitem';
      case 'table': return 'table';
      case 'tr': return 'row';
      case 'td': return 'cell';
      case 'th': return 'columnheader';
      case 'p': return 'paragraph';
      case 'label': return 'label';
    }
    if (el.isContentEditable && el.getAttribute('contenteditable') !== null) return 'textbox';
    // A leaf with its own text and no role still reads as text.
    if (!el.children.length && clean(el.textContent, 2)) return 'text';
    return null;
  }
  function nameOf(el, role) {
    var label = el.getAttribute('aria-label');
    if (label) return clean(label, 100);
    var by = el.getAttribute('aria-labelledby');
    if (by) {
      var parts = by.split(/\s+/).map(function (id) {
        var node = document.getElementById(id); return node ? node.textContent : '';
      });
      if (clean(parts.join(' '), 2)) return clean(parts.join(' '), 100);
    }
    var tag = el.tagName.toLowerCase();
    if (tag === 'img') return clean(el.getAttribute('alt') || '', 100);
    if (tag === 'input' || tag === 'textarea' || tag === 'select') {
      if (el.labels && el.labels.length) return clean(el.labels[0].textContent, 100);
      if (el.getAttribute('placeholder')) return clean(el.getAttribute('placeholder'), 100);
      if (tag === 'input' && /^(button|submit|reset)$/i.test(el.type)) return clean(el.value, 100);
    }
    if (NAMED_BY_TEXT[role]) return clean(el.innerText || el.textContent, 100);
    return clean(el.getAttribute('title') || '', 100);
  }
  function visible(el, all) {
    var rect = el.getBoundingClientRect();
    if (!(rect.width > 0 && rect.height > 0)) return false;
    var style = getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none') return false;
    if (all) return true;
    return rect.bottom > 0 && rect.right > 0 && rect.top < innerHeight && rect.left < innerWidth;
  }
  function isInteractive(el, role) {
    if (INTERACTIVE[role]) return true;
    var tabindex = el.getAttribute('tabindex');
    return el.hasAttribute('onclick') || (tabindex !== null && Number(tabindex) >= 0);
  }
  function describe(el, role) {
    var line = role;
    var name = nameOf(el, role);
    if (name) line += ' "' + name.replace(/"/g, '\\"') + '"';
    var tag = el.tagName.toLowerCase();
    if (role === 'heading') line += ' level=' + tag.slice(1);
    if (role === 'link') {
      var href = el.getAttribute('href') || '';
      if (href && href.charAt(0) !== '#') line += ' href="' + clean(href, 80) + '"';
    }
    if (role === 'checkbox' || role === 'radio' || role === 'switch') line += el.checked ? ' (checked)' : ' (unchecked)';
    if ((role === 'textbox' || role === 'searchbox' || role === 'spinbutton') && el.value) {
      line += ' value="' + clean(el.type === 'password' ? '••••' : el.value, 60) + '"';
    }
    if (role === 'combobox' && el.options && el.selectedIndex >= 0) {
      line += ' value="' + clean(el.options[el.selectedIndex].text, 60) + '"';
    }
    if (el.disabled) line += ' (disabled)';
    return line + ' [' + refOf(el) + ']';
  }
  var SKIP = {SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEMPLATE: 1, HEAD: 1};
  var api = {
    read: function (filter, depth, ref) {
      var root = document.body;
      if (ref) {
        var target = api.element(ref);
        if (typeof target === 'string') return {error: target};
        root = target;
      }
      var all = filter === 'all', interactiveOnly = filter === 'interactive';
      var lines = [], size = 0, truncated = false;
      function walk(el, level, indent) {
        if (truncated || SKIP[el.tagName]) return;
        var role = roleOf(el), shown = false;
        if (role && visible(el, all) && (!interactiveOnly || isInteractive(el, role))) {
          var line = (interactiveOnly ? '' : Array(indent + 1).join('  ')) + describe(el, role);
          size += line.length + 1;
          if (size > %(max_chars)d) { truncated = true; return; }
          lines.push(line);
          shown = true;
        }
        if (el.tagName === 'svg' || role === 'img' || role === 'text') return;
        var nextLevel = shown ? level + 1 : level;
        if (nextLevel > depth) return;
        for (var i = 0; i < el.children.length; i++) {
          walk(el.children[i], nextLevel, shown ? indent + 1 : indent);
        }
      }
      walk(root, 1, 0);
      return {text: lines.join('\n'), truncated: truncated};
    },
    find: function (query) {
      var words = clean(query, 200).toLowerCase().split(' ').filter(Boolean);
      var scored = [];
      var nodes = document.body.querySelectorAll('*');
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        if (SKIP[el.tagName]) continue;
        var role = roleOf(el);
        if (!role || !visible(el, true)) continue;
        var hay = (role + ' ' + nameOf(el, role) + ' ' + (el.getAttribute('placeholder') || '') +
          ' ' + (el.getAttribute('type') || '')).toLowerCase();
        var score = 0;
        for (var w = 0; w < words.length; w++) if (hay.indexOf(words[w]) >= 0) score += 1;
        if (!score) continue;
        if (isInteractive(el, role)) score += 0.5;
        scored.push({el: el, role: role, score: score, order: i});
      }
      scored.sort(function (a, b) { return b.score - a.score || a.order - b.order; });
      return scored.slice(0, %(find_max)d).map(function (s) { return describe(s.el, s.role); }).join('\n');
    },
    text: function () {
      var root = document.querySelector('main, [role=main], article') || document.body;
      return String(root.innerText || '').replace(/\n{3,}/g, '\n\n').trim();
    },
    element: function (ref) {
      var holder = refs.get(ref);
      var el = holder && holder.deref();
      if (!el || !el.isConnected) {
        return 'Error: ' + ref + ' is stale or not found on the current page. Re-read the page to get fresh references.';
      }
      return el;
    },
    point: function (ref) {
      var el = api.element(ref);
      if (typeof el === 'string') return {error: el};
      el.scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'});
      var rect = el.getBoundingClientRect();
      return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2};
    },
    fill: function (ref, value) {
      var el = api.element(ref);
      if (typeof el === 'string') return {error: el};
      var tag = el.tagName.toLowerCase();
      el.scrollIntoView({block: 'center', behavior: 'instant'});
      if (tag === 'input' && /^(checkbox|radio)$/i.test(el.type)) {
        var want = value === true || value === 'true' || value === 1 || value === 'on';
        if (el.checked !== want) el.click();
        return {ok: el.type + ' ' + (el.checked ? 'checked' : 'unchecked')};
      }
      if (tag === 'select') {
        var text = String(value);
        for (var i = 0; i < el.options.length; i++) {
          var option = el.options[i];
          if (option.value === text || clean(option.text, 200) === clean(text, 200)) {
            el.selectedIndex = i;
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            return {ok: 'selected "' + clean(option.text, 60) + '"'};
          }
        }
        return {error: 'Error: no option "' + clean(text, 60) + '" in ' + ref + '.'};
      }
      if (tag === 'input' || tag === 'textarea') {
        var proto = tag === 'input' ? HTMLInputElement.prototype : HTMLTextAreaElement.prototype;
        Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, String(value));
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        return {ok: 'value set'};
      }
      if (el.isContentEditable) {
        el.textContent = String(value);
        el.dispatchEvent(new Event('input', {bubbles: true}));
        return {ok: 'text set'};
      }
      return {error: 'Error: ' + ref + ' is not a form field.'};
    },
    scroll: function () { return [window.scrollX, window.scrollY]; }
  };
  window.__imagiAgent = api;
  return api;
})()
""" % {'max_chars': PAGE_TEXT_MAX_CHARS, 'find_max': FIND_MAX_RESULTS}


class BrowserActionError(Exception):
    """An action the model asked for could not be carried out; its message is
    what the model reads."""


def _text(value):
    return [{'type': 'text', 'text': value}]


class PreviewBrowserToolset(ClientToolset):
    """browser_toolset_20260801, executed against the workspace preview."""

    toolset_name = 'browser'
    name = 'browser'

    def to_param(self):
        configs = {member: {'enabled': False} for member in DISABLED_MEMBERS}
        configs.update({member: {'enabled': True} for member in ENABLED_OPTIONAL_MEMBERS})
        return {'type': 'browser_toolset_20260801', 'configs': configs}

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def run_member(self, wrapper, name, tool_input):
        """Carry out one member call; returns (content, is_error)."""
        if name in DISABLED_MEMBERS:
            return f"Error: {name} is not enabled in this environment.", True
        handler = getattr(self, f'_do_{name}', None)
        if handler is None:
            return f"Error: {name} is not supported in the preview.", True
        if not isinstance(tool_input, dict):
            return "Error: the action's input must be an object.", True
        try:
            session = _PreviewSession.open(getattr(wrapper, 'context', None))
            return handler(session, tool_input), False
        except BrowserActionError as e:
            return str(e), True
        except Exception as e:
            from .browser_preview_service import BrowserPreviewError
            if isinstance(e, BrowserPreviewError):
                return f"Error: {e}", True
            logger.exception("Preview browser action %s failed", name)
            return f"Error: the preview browser could not do that ({e}).", True

    # ------------------------------------------------------------------
    # Navigation and capture
    # ------------------------------------------------------------------

    def _do_navigate(self, session, tool_input):
        url = str(tool_input.get('url') or '').strip()
        if not url:
            raise BrowserActionError('Error: navigate needs a url.')
        return session.navigate(url)

    def _do_screenshot(self, session, tool_input):
        return [session.screenshot()]

    def _do_zoom(self, session, tool_input):
        region = tool_input.get('region')
        if not (isinstance(region, list) and len(region) == 4):
            raise BrowserActionError('Error: zoom needs region as [x0, y0, x1, y1].')
        return [session.zoom(region)]

    # ------------------------------------------------------------------
    # Pointer
    # ------------------------------------------------------------------

    def _click(self, session, tool_input, button='left', count=1):
        x, y = session.target_point(tool_input.get('target'))
        modifiers = _modifier_mask(tool_input.get('modifiers'))
        return session.act(lambda conn: _click(conn, x, y, button, count, modifiers),
                           f"Clicked {_describe_target(tool_input.get('target'))}.")

    def _do_left_click(self, session, tool_input):
        return self._click(session, tool_input)

    def _do_right_click(self, session, tool_input):
        return self._click(session, tool_input, button='right')

    def _do_middle_click(self, session, tool_input):
        return self._click(session, tool_input, button='middle')

    def _do_double_click(self, session, tool_input):
        return self._click(session, tool_input, count=2)

    def _do_triple_click(self, session, tool_input):
        return self._click(session, tool_input, count=3)

    def _do_hover(self, session, tool_input):
        x, y = session.target_point(tool_input.get('target'))
        return session.act(lambda conn: _mouse(conn, 'mouseMoved', x, y),
                           f"Hovering over {_describe_target(tool_input.get('target'))}.")

    def _do_mouse_move(self, session, tool_input):
        return self._do_hover(session, tool_input)

    def _do_left_mouse_down(self, session, tool_input):
        x, y = session.target_point(tool_input.get('target'))

        def body(conn):
            _mouse(conn, 'mouseMoved', x, y)
            _mouse(conn, 'mousePressed', x, y, button='left', buttons=1, count=1)
        return session.act(body, 'Pressed the left button.')

    def _do_left_mouse_up(self, session, tool_input):
        x, y = session.target_point(tool_input.get('target'))

        def body(conn):
            _mouse(conn, 'mouseMoved', x, y, buttons=1)
            _mouse(conn, 'mouseReleased', x, y, button='left', count=1)
        return session.act(body, 'Released the left button.')

    def _do_left_click_drag(self, session, tool_input):
        x0, y0 = session.target_point(tool_input.get('from'))
        x1, y1 = session.target_point(tool_input.get('target'))

        def body(conn):
            _mouse(conn, 'mouseMoved', x0, y0)
            _mouse(conn, 'mousePressed', x0, y0, button='left', buttons=1, count=1)
            for step in range(1, 6):
                t = step / 5
                _mouse(conn, 'mouseMoved', x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, buttons=1)
            _mouse(conn, 'mouseReleased', x1, y1, button='left', count=1)
        return session.act(body, 'Dragged.')

    def _do_scroll(self, session, tool_input):
        direction = tool_input.get('scroll_direction')
        if direction not in ('up', 'down', 'left', 'right'):
            raise BrowserActionError('Error: scroll_direction must be up, down, left or right.')
        try:
            amount = max(1, min(int(tool_input.get('scroll_amount') or 3), 10))
        except (TypeError, ValueError):
            amount = 3
        target = tool_input.get('target')
        x, y = session.target_point(target) if target else session.center()
        delta = amount * 100
        dx = delta if direction == 'right' else -delta if direction == 'left' else 0
        dy = delta if direction == 'down' else -delta if direction == 'up' else 0

        def body(conn):
            conn.call('Input.dispatchMouseEvent', {
                'type': 'mouseWheel', 'x': x, 'y': y, 'deltaX': dx, 'deltaY': dy,
            })
            time.sleep(0.25)  # Chromium applies the wheel on its next frame
        return session.act(body, f'Scrolled {direction}.')

    def _do_scroll_to(self, session, tool_input):
        session.ref_point(tool_input.get('target'))  # scrolls it into view
        return _text(f"Scrolled {_describe_target(tool_input.get('target'))} into view.")

    # ------------------------------------------------------------------
    # Keyboard and timing
    # ------------------------------------------------------------------

    def _do_type(self, session, tool_input):
        text = str(tool_input.get('text') or '')
        if not text:
            raise BrowserActionError('Error: type needs text.')
        return session.act(lambda conn: conn.call('Input.insertText', {'text': text}),
                           f'Typed {len(text)} characters.')

    def _do_key(self, session, tool_input):
        text = str(tool_input.get('text') or '').strip()
        if not text:
            raise BrowserActionError('Error: key needs text, such as "Enter" or "ctrl+a".')
        try:
            repeat = max(1, min(int(tool_input.get('repeat') or 1), 100))
        except (TypeError, ValueError):
            repeat = 1
        chords = [_parse_chord(chord) for chord in text.split()]

        def body(conn):
            for _ in range(repeat):
                for chord in chords:
                    _press(conn, *chord)
        return session.act(body, f'Pressed {text}' + (f' {repeat} times.' if repeat > 1 else '.'))

    def _do_wait(self, session, tool_input):
        try:
            duration = max(0.0, min(float(tool_input.get('duration') or 0), MAX_WAIT_S))
        except (TypeError, ValueError):
            duration = 1.0
        time.sleep(duration)
        return _text(f'Waited {duration:g} seconds.')

    # ------------------------------------------------------------------
    # Page reading and forms
    # ------------------------------------------------------------------

    def _do_read_page(self, session, tool_input):
        filter_ = tool_input.get('filter')
        if filter_ not in (None, 'interactive', 'all'):
            filter_ = None
        try:
            depth = max(1, int(tool_input.get('depth') or 15))
        except (TypeError, ValueError):
            depth = 15
        ref = tool_input.get('ref')
        result = session.page_call('read', filter_, depth, ref if isinstance(ref, str) else None)
        if not isinstance(result, dict):
            raise BrowserActionError('Error: the page could not be read.')
        if result.get('error'):
            raise BrowserActionError(result['error'])
        text = result.get('text') or '(nothing visible on the page)'
        if result.get('truncated'):
            text += (
                f"\n[Output cut off at {PAGE_TEXT_MAX_CHARS:,} characters. Narrow it "
                "with filter, depth or ref.]"
            )
        return _text(text)

    def _do_find(self, session, tool_input):
        query = str(tool_input.get('query') or '').strip()
        if not query:
            raise BrowserActionError('Error: find needs a query.')
        found = session.page_call('find', query)
        return _text(found or f'No elements match "{query}". Try read_page.')

    def _do_get_page_text(self, session, tool_input):
        text = session.page_call('text') or ''
        if len(text) > PAGE_TEXT_MAX_CHARS:
            text = text[:PAGE_TEXT_MAX_CHARS] + (
                f"\n[Text cut off at {PAGE_TEXT_MAX_CHARS:,} characters.]"
            )
        return _text(text or '(the page has no visible text)')

    def _do_form_input(self, session, tool_input):
        target = tool_input.get('target') or {}
        ref = target.get('ref') if isinstance(target, dict) else None
        if not ref:
            raise BrowserActionError('Error: form_input needs a ref target from read_page or find.')
        value = tool_input.get('value')
        result = session.page_call('fill', ref, value)
        if not isinstance(result, dict) or result.get('error'):
            raise BrowserActionError((result or {}).get('error') or f'Error: could not fill {ref}.')
        return _text(f"Set {ref}: {result.get('ok')}.")

    def _do_read_console(self, session, tool_input):
        errors = session.console_errors()
        if not errors:
            return _text('No console errors on this page.')
        lines = [f"[error] {error['text']}" for error in errors]
        return _text('Recent console errors, oldest first:\n' + '\n'.join(lines))


# ---------------------------------------------------------------------------
# The preview page, as one action sees it
# ---------------------------------------------------------------------------

class _PreviewSession:
    """The project's preview browser, for the length of one action."""

    def __init__(self, service, state):
        self.service = service
        self.state = state
        width, height = state.get('viewport') or (1280, 800)
        self.width, self.height = int(width), int(height)
        self.dsf = float(state.get('device_scale_factor') or 1)
        # Screenshot pixels per CSS pixel.
        self.scale = min(1.0, SCREENSHOT_MAX_EDGE / max(self.width, self.height))
        self.app_url = (state.get('app_url') or '').rstrip('/')

    @classmethod
    def open(cls, context):
        """The preview for the run's project, started if it is not running.

        Always the canonical project: a thread's worktree has no preview of
        its own, so the preview shows the app as it is now.
        """
        from apps.Imagi.ProjectManager.models import Project
        from .browser_preview_service import BrowserPreviewService

        project_id = getattr(context, 'project_id', None)
        user_id = getattr(context, 'user_id', None)
        if not project_id:
            raise BrowserActionError('Error: no project is open, so there is no preview.')
        try:
            project = Project.objects.get(id=project_id, user_id=user_id, is_active=True)
        except Project.DoesNotExist:
            raise BrowserActionError('Error: the project could not be found.')
        service = BrowserPreviewService(project)
        state = service._load_state()
        if not state or not service._browser_alive(state):
            service.start()
            state = service._load_state()
            if not state:
                raise BrowserActionError('Error: the preview could not be started.')
        return cls(service, state)

    # -- plumbing -------------------------------------------------------

    def run(self, body):
        """body(conn) on the page, under the preview's page lock."""
        def wrapped(conn, _page):
            self.service._apply_viewport(conn, self.state)
            return body(conn)
        return self.service._with_page(self.state, wrapped, idempotent=False)

    def _evaluate(self, conn, expression):
        result = conn.call('Runtime.evaluate', {
            'expression': expression, 'returnByValue': True, 'awaitPromise': True,
        })
        if result.get('exceptionDetails'):
            details = result['exceptionDetails']
            message = (details.get('exception') or {}).get('description') or details.get('text')
            raise BrowserActionError(f'Error: the page raised {message}')
        return (result.get('result') or {}).get('value')

    def page_call(self, method, *args):
        """Call the in-page helper (installing it first if needed)."""
        expression = f"({_AGENT_JS}).{method}.apply(null, {json.dumps(list(args))})"
        return self.run(lambda conn: self._evaluate(conn, expression))

    def _location(self, conn):
        history = conn.call('Page.getNavigationHistory')
        entries = history.get('entries', [])
        index = history.get('currentIndex', 0)
        current = entries[index] if 0 <= index < len(entries) else {}
        return current.get('url', ''), current.get('title', '')

    def _on_app(self, url):
        return not url or url == 'about:blank' or url == self.app_url or url.startswith(self.app_url + '/')

    def _browser_state(self, url, title):
        return {
            'type': 'browser_state',
            'tabs': [{
                'tab_id': TAB_ID,
                'title': (title or url or 'Preview')[:4096],
                'url': (url or 'about:blank')[:4096],
                'active': True,
            }],
        }

    def _wait_for_load(self, conn):
        deadline = time.monotonic() + NAVIGATION_SETTLE_S
        time.sleep(0.15)
        while time.monotonic() < deadline:
            try:
                if self._evaluate(conn, 'document.readyState') == 'complete':
                    break
            except BrowserActionError:
                pass
            time.sleep(0.1)
        time.sleep(0.2)  # a Vue app renders just after load

    def act(self, body, acknowledgement):
        """Run an input action; report where the page ended up.

        An action that takes the page off the app (an outside link) is undone:
        the preview only shows the app's own pages.
        """
        def wrapped(conn):
            before = self._location(conn)
            body(conn)
            time.sleep(0.1)
            after = self._location(conn)
            if after != before:
                self._wait_for_load(conn)
                after = self._location(conn)
            if not self._on_app(after[0]):
                conn.call('Page.navigate', {'url': before[0] if self._on_app(before[0]) else self.app_url + '/'})
                self._wait_for_load(conn)
                raise BrowserActionError(
                    'Error: that led outside the app, so the preview went back. '
                    "Only this app's own pages open in the preview."
                )
            return before, after

        before, after = self.run(wrapped)
        content = _text(acknowledgement)
        if after != before:
            content.append(self._browser_state(*after))
        return content

    # -- coordinates ----------------------------------------------------

    def to_css(self, x, y):
        """A screenshot coordinate as a viewport (CSS pixel) coordinate."""
        try:
            x, y = float(x), float(y)
        except (TypeError, ValueError):
            raise BrowserActionError('Error: coordinates must be numbers.')
        x, y = x / self.scale, y / self.scale
        if not (0 <= x <= self.width and 0 <= y <= self.height):
            raise BrowserActionError(
                f'Error: ({x:.0f}, {y:.0f}) is outside the {self.width}x{self.height} viewport.'
            )
        return x, y

    def center(self):
        return self.width / 2, self.height / 2

    def ref_point(self, target):
        ref = target.get('ref') if isinstance(target, dict) else None
        if not ref:
            raise BrowserActionError('Error: this action needs a ref target from read_page or find.')
        point = self.page_call('point', ref)
        if not isinstance(point, dict) or point.get('error'):
            raise BrowserActionError((point or {}).get('error') or f'Error: {ref} could not be found.')
        x = max(0.0, min(float(point['x']), self.width - 1))
        y = max(0.0, min(float(point['y']), self.height - 1))
        return x, y

    def target_point(self, target):
        if not isinstance(target, dict):
            raise BrowserActionError('Error: the action needs a target.')
        if target.get('type') == 'ref' or (target.get('ref') and 'x' not in target):
            return self.ref_point(target)
        return self.to_css(target.get('x'), target.get('y'))

    # -- actions --------------------------------------------------------

    def navigate(self, url):
        from .browser_preview_service import BrowserPreviewService

        lowered = url.lower()

        def body(conn):
            if lowered in ('back', 'forward'):
                history = conn.call('Page.getNavigationHistory')
                index = history.get('currentIndex', 0) + (1 if lowered == 'forward' else -1)
                entries = history.get('entries', [])
                if not (0 <= index < len(entries)):
                    raise BrowserActionError(f'Error: there is no page to go {lowered} to.')
                target = entries[index].get('url', '')
                if not self._on_app(target):
                    raise BrowserActionError("Error: that page is outside the app.")
                conn.call('Page.navigateToHistoryEntry', {'entryId': entries[index]['id']})
            elif lowered == 'reload':
                conn.call('Page.reload', {'ignoreCache': False})
            else:
                conn.call('Page.navigate', {'url': self.app_url + self._app_path(url, BrowserPreviewService)})
            self._wait_for_load(conn)
            return self._location(conn)

        location = self.run(body)
        verb = {'back': 'Went back', 'forward': 'Went forward', 'reload': 'Reloaded'}.get(lowered, 'Opened')
        return [*_text(f'{verb} {location[0] or url}.'), self._browser_state(*location)]

    def _app_path(self, url, service_cls):
        """The app path a navigate url names, or an error for anything else."""
        if url.startswith('/') and not url.startswith('//'):
            try:
                return service_cls._normalize_path(url)
            except Exception as e:
                raise BrowserActionError(f'Error: {e}')
        candidate = url if '://' in url else 'https://' + url
        parts = urlsplit(candidate)
        if parts.scheme not in ('http', 'https'):
            raise BrowserActionError('Error: Navigation refused. Only http and https URLs are allowed.')
        app = urlsplit(self.app_url)
        local_hosts = {app.hostname, 'localhost', '127.0.0.1'}
        if parts.hostname not in local_hosts or (parts.port and parts.port != app.port):
            raise BrowserActionError(
                "Error: Navigation refused. The preview only opens this app's own pages — "
                'pass a path such as /about.'
            )
        path = parts.path or '/'
        if parts.query:
            path += '?' + parts.query
        if parts.fragment:
            path += '#' + parts.fragment
        return path

    def screenshot(self):
        def body(conn):
            x, y = self._evaluate(conn, '[window.scrollX, window.scrollY]') or (0, 0)
            return self.service._capture_screenshot(conn, SCREENSHOT_JPEG_QUALITY, {
                'x': float(x), 'y': float(y),
                'width': self.width, 'height': self.height,
                'scale': self.scale / self.dsf,
            })
        shot = self.run(body)
        return _image(shot.get('data', ''))

    def zoom(self, region):
        try:
            x0, y0, x1, y1 = (float(v) for v in region)
        except (TypeError, ValueError):
            raise BrowserActionError('Error: region values must be numbers.')
        if x1 <= x0 or y1 <= y0:
            raise BrowserActionError('Error: region must be [x0, y0, x1, y1] with x1 > x0 and y1 > y0.')
        cx0, cy0 = self.to_css(x0, y0)
        cx1, cy1 = self.to_css(min(x1, self.width * self.scale), min(y1, self.height * self.scale))
        width, height = max(cx1 - cx0, 1), max(cy1 - cy0, 1)
        # Fill the usual screenshot size, at most 4x magnified.
        fit = min(self.width * self.scale / width, self.height * self.scale / height, 4.0)

        def body(conn):
            sx, sy = self._evaluate(conn, '[window.scrollX, window.scrollY]') or (0, 0)
            return self.service._capture_screenshot(conn, SCREENSHOT_JPEG_QUALITY, {
                'x': float(sx) + cx0, 'y': float(sy) + cy0,
                'width': width, 'height': height,
                'scale': fit / self.dsf,
            })
        shot = self.run(body)
        return _image(shot.get('data', ''))

    def console_errors(self):
        return self.run(self.service._collect_console_errors)


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def _image(data):
    if not data:
        raise BrowserActionError('Error: the screenshot came back empty.')
    return {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': data}}


def _describe_target(target):
    if isinstance(target, dict):
        if target.get('ref'):
            return target['ref']
        if 'x' in target:
            return f"({target.get('x')}, {target.get('y')})"
    return 'the target'


def _modifier_mask(modifiers):
    mask = 0
    for part in str(modifiers or '').lower().split('+'):
        mask |= _MODIFIER_BITS.get(part.strip(), 0)
    return mask


def _mouse(conn, event_type, x, y, button='none', buttons=0, count=0, modifiers=0):
    conn.call('Input.dispatchMouseEvent', {
        'type': event_type, 'x': x, 'y': y, 'button': button,
        'buttons': buttons, 'clickCount': count, 'modifiers': modifiers,
    })


def _click(conn, x, y, button, count, modifiers):
    pressed = {'left': 1, 'right': 2, 'middle': 4}[button]
    _mouse(conn, 'mouseMoved', x, y, modifiers=modifiers)
    for n in range(1, count + 1):
        _mouse(conn, 'mousePressed', x, y, button, pressed, n, modifiers)
        _mouse(conn, 'mouseReleased', x, y, button, 0, n, modifiers)


def _parse_chord(chord):
    """'ctrl+shift+a' -> (modifier mask, key, code, key code, text)."""
    parts = [p for p in chord.split('+') if p]
    if not parts:
        raise BrowserActionError(f'Error: "{chord}" is not a key.')
    *mods, key = parts
    mask = 0
    for mod in mods:
        bit = _MODIFIER_BITS.get(mod.lower())
        if bit is None:
            raise BrowserActionError(f'Error: "{mod}" is not a modifier key.')
        mask |= bit
    named = _NAMED_KEYS.get(key.lower())
    if named:
        value, code, key_code, text = named
    elif len(key) == 1:
        value = key
        upper = key.upper()
        if upper.isalpha():
            code, key_code = f'Key{upper}', ord(upper)
        elif key.isdigit():
            code, key_code = f'Digit{key}', ord(key)
        else:
            code, key_code = '', ord(key) if ord(key) < 128 else 0
        text = key
    else:
        raise BrowserActionError(f'Error: "{key}" is not a key name this preview knows.')
    # A chord with ctrl/alt/meta is a shortcut, not typing.
    if mask & (1 | 2 | 4):
        text = ''
    return mask, value, code, key_code, text


def _press(conn, mask, key, code, key_code, text):
    down = {
        'type': 'keyDown' if text else 'rawKeyDown',
        'key': key, 'code': code, 'modifiers': mask,
        'windowsVirtualKeyCode': key_code, 'nativeVirtualKeyCode': key_code,
    }
    if text:
        down['text'] = text
    conn.call('Input.dispatchKeyEvent', down)
    conn.call('Input.dispatchKeyEvent', {
        'type': 'keyUp', 'key': key, 'code': code, 'modifiers': mask,
        'windowsVirtualKeyCode': key_code, 'nativeVirtualKeyCode': key_code,
    })
