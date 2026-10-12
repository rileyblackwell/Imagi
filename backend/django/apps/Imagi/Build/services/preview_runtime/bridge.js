// Imagi preview bridge. Injected into the app's pages by the preview's Vite
// wrapper config (dev server only; it never reaches the app's own build).
// It tells the Imagi workspace around the iframe where the app is and what
// it logs, and takes a few commands back. Both directions are origin-checked:
// it answers only a parent whose origin matches __IMAGI_PARENT_RE__, and only
// after that parent has said hello.
;(function () {
  if (window.__imagiBridge || window.parent === window) return
  var PARENT_RE = new RegExp(__IMAGI_PARENT_RE__)
  var BASE = __IMAGI_BASE__ // "/s/<token>" with no trailing slash
  var parentOrigin = null
  var queue = []
  var MAX_QUEUE = 200
  var MAX_TEXT = 2000

  function post(msg) {
    msg.source = 'imagi-preview'
    if (!parentOrigin) {
      if (queue.length < MAX_QUEUE) queue.push(msg)
      return
    }
    try {
      window.parent.postMessage(msg, parentOrigin)
    } catch (e) {}
  }

  function clip(text) {
    text = String(text)
    return text.length > MAX_TEXT ? text.slice(0, MAX_TEXT) + '…' : text
  }

  function fmt(arg) {
    if (arg instanceof Error) return arg.stack || arg.message
    if (typeof arg === 'string') return arg
    try {
      return JSON.stringify(arg)
    } catch (e) {
      return String(arg)
    }
  }

  // The app's own path, without the preview's /s/<token> prefix.
  function appPath() {
    var p = location.pathname
    if (p.indexOf(BASE) === 0) p = p.slice(BASE.length) || '/'
    return p + location.search + location.hash
  }

  function nav() {
    var st = history.state || {}
    post({
      type: 'nav',
      path: appPath(),
      title: document.title,
      canGoBack: st.back != null,
      canGoForward: st.forward != null,
    })
  }

  // -- navigation ---------------------------------------------------------
  ;['pushState', 'replaceState'].forEach(function (name) {
    var orig = history[name]
    history[name] = function () {
      var out = orig.apply(this, arguments)
      setTimeout(nav, 0)
      return out
    }
  })
  window.addEventListener('popstate', function () { setTimeout(nav, 0) })
  window.addEventListener('hashchange', nav)
  new MutationObserver(function () { nav() }).observe(document.querySelector('title') || document.head, {
    childList: true, subtree: true, characterData: true,
  })

  // -- console and errors ---------------------------------------------------
  ;['log', 'info', 'warn', 'error', 'debug'].forEach(function (level) {
    var orig = console[level]
    console[level] = function () {
      try {
        var text = Array.prototype.map.call(arguments, fmt).join(' ')
        post({ type: 'console', level: level === 'debug' ? 'log' : level, text: clip(text), ts: Date.now() })
      } catch (e) {}
      return orig.apply(this, arguments)
    }
  })
  window.addEventListener('error', function (e) {
    var text = e.error ? fmt(e.error) : e.message
    if (!text && e.target && e.target !== window) {
      text = 'Failed to load ' + (e.target.src || e.target.href || e.target.tagName)
    }
    post({ type: 'console', level: 'error', text: clip(text || 'Unknown error'), ts: Date.now() })
  }, true)
  window.addEventListener('unhandledrejection', function (e) {
    post({ type: 'console', level: 'error', text: clip('Unhandled promise rejection: ' + fmt(e.reason)), ts: Date.now() })
  })

  // -- network --------------------------------------------------------------
  function shortUrl(u) {
    try {
      var url = new URL(u, location.href)
      if (url.origin !== location.origin) return url.href
      var p = url.pathname
      if (p.indexOf(BASE) === 0) p = p.slice(BASE.length) || '/'
      return p + url.search
    } catch (e) {
      return String(u)
    }
  }
  function isNoise(u) {
    // Vite's own module and HMR traffic is not the app's network activity.
    return /\/(@vite|@id|@fs|node_modules|src)\//.test(u) || /\.(vue|ts|js|css)(\?|$)/.test(u)
  }
  var nextId = 1
  if (window.fetch) {
    var origFetch = window.fetch
    window.fetch = function (input, init) {
      var url = typeof input === 'string' ? input : (input && input.url) || String(input)
      var method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase()
      var id = nextId++
      var started = performance.now()
      var promise = origFetch.apply(this, arguments)
      if (!isNoise(url)) {
        promise.then(function (r) {
          post({ type: 'net', id: id, method: method, url: shortUrl(url), status: r.status, ms: Math.round(performance.now() - started) })
        }, function () {
          post({ type: 'net', id: id, method: method, url: shortUrl(url), status: 0, ms: Math.round(performance.now() - started) })
        })
      }
      return promise
    }
  }
  var XHR = window.XMLHttpRequest
  if (XHR) {
    var open = XHR.prototype.open
    var send = XHR.prototype.send
    XHR.prototype.open = function (method, url) {
      this.__imagi = { method: String(method || 'GET').toUpperCase(), url: String(url) }
      return open.apply(this, arguments)
    }
    XHR.prototype.send = function () {
      var info = this.__imagi
      if (info && !isNoise(info.url)) {
        var id = nextId++
        var started = performance.now()
        var xhr = this
        xhr.addEventListener('loadend', function () {
          post({ type: 'net', id: id, method: info.method, url: shortUrl(info.url), status: xhr.status, ms: Math.round(performance.now() - started) })
        })
      }
      return send.apply(this, arguments)
    }
  }

  // -- element picker -----------------------------------------------------
  var picking = false
  var box = null
  function componentInfo(el) {
    var node = el
    while (node && !node.__vueParentComponent) node = node.parentElement
    var inst = node && node.__vueParentComponent
    var chain = []
    var file = ''
    while (inst && chain.length < 6) {
      var type = inst.type || {}
      var name = type.name || type.__name || (type.__file ? type.__file.split('/').pop().replace(/\.vue$/, '') : '')
      if (name) chain.push(name)
      if (!file && type.__file) file = type.__file
      inst = inst.parent
    }
    return { component: chain[0] || '', chain: chain, file: file }
  }
  function describe(el) {
    var text = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ')
    var info = componentInfo(el)
    var cls = typeof el.className === 'string' ? el.className.trim().split(/\s+/).slice(0, 4).join('.') : ''
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      classes: cls,
      text: clip(text).slice(0, 160),
      component: info.component,
      chain: info.chain,
      file: info.file.replace(/^.*?\/(src\/)/, '$1'),
    }
  }
  function onMove(e) {
    if (!box) {
      box = document.createElement('div')
      box.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;border:2px solid #4f8cff;background:rgba(79,140,255,.12);border-radius:3px;transition:all .05s'
      document.documentElement.appendChild(box)
    }
    var r = e.target.getBoundingClientRect()
    box.style.left = r.left + 'px'
    box.style.top = r.top + 'px'
    box.style.width = r.width + 'px'
    box.style.height = r.height + 'px'
  }
  function stopPicking() {
    picking = false
    document.removeEventListener('mousemove', onMove, true)
    document.removeEventListener('click', onPick, true)
    document.removeEventListener('keydown', onKey, true)
    if (box) { box.remove(); box = null }
    document.documentElement.style.cursor = ''
  }
  function onPick(e) {
    e.preventDefault()
    e.stopPropagation()
    var el = e.target
    stopPicking()
    post({ type: 'picked', element: describe(el), path: appPath() })
  }
  function onKey(e) {
    if (e.key === 'Escape') {
      stopPicking()
      post({ type: 'picked', element: null })
    }
  }
  function startPicking() {
    if (picking) return
    picking = true
    document.documentElement.style.cursor = 'crosshair'
    document.addEventListener('mousemove', onMove, true)
    document.addEventListener('click', onPick, true)
    document.addEventListener('keydown', onKey, true)
  }

  // -- commands from the workspace -------------------------------------------
  function router() {
    var el = document.querySelector('[data-v-app]') || document.getElementById('app')
    var app = el && el.__vue_app__
    return app && app.config && app.config.globalProperties && app.config.globalProperties.$router
  }
  function goto(p) {
    if (typeof p !== 'string' || p.charAt(0) !== '/' || p.charAt(1) === '/' || p.indexOf('\\') !== -1) return
    var r = router()
    if (r) r.push(p).catch(function () {})
    else location.assign(BASE + p)
  }

  window.addEventListener('message', function (e) {
    if (e.source !== window.parent || typeof e.origin !== 'string' || !PARENT_RE.test(e.origin)) return
    var d = e.data
    if (!d || typeof d !== 'object' || d.target !== 'imagi-preview' || typeof d.cmd !== 'string') return
    if (d.cmd === 'hello') {
      parentOrigin = e.origin
      var pending = queue
      queue = []
      post({ type: 'ready', path: appPath(), title: document.title })
      for (var i = 0; i < pending.length; i++) post(pending[i])
      nav()
      return
    }
    if (e.origin !== parentOrigin) return
    if (d.cmd === 'back') history.back()
    else if (d.cmd === 'forward') history.forward()
    else if (d.cmd === 'reload') location.reload()
    else if (d.cmd === 'navigate') goto(d.path)
    else if (d.cmd === 'pick') startPicking()
    else if (d.cmd === 'cancel-pick') stopPicking()
  })

  // The workspace's shortcuts keep working while focus is inside the app.
  window.addEventListener('keydown', function (e) {
    if (!(e.metaKey || e.ctrlKey) || e.altKey) return
    var k = String(e.key || '').toLowerCase()
    if (k === 'l' || k === 'j' || k === 'r' || (k === 'c' && e.shiftKey)) {
      e.preventDefault()
      post({ type: 'shortcut', key: k, shift: e.shiftKey })
    }
  }, true)

  window.__imagiBridge = { post: post }
  post({ type: 'loading', path: appPath() })
})()
