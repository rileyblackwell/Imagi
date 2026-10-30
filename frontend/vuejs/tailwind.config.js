import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // The product's surfaces, defined once in shared/styles/tokens.css and
        // read from there. Each is theme-aware on its own — the custom property
        // changes under `.dark` — so `bg-paper` is correct in both themes and
        // needs no `dark:` twin. The `<alpha-value>` placeholder keeps opacity
        // modifiers working, so `bg-canvas/80` still composes.
        paper: 'rgb(var(--app-paper) / <alpha-value>)',
        'paper-raised': 'rgb(var(--app-paper-raised) / <alpha-value>)',
        'paper-inverted': 'rgb(var(--app-paper-inverted) / <alpha-value>)',
        canvas: 'rgb(var(--app-canvas) / <alpha-value>)',

        // The two inks, shared with the editorial surface (editorial.css
        // --ink). `ink` is the light theme's text and the primary button fill;
        // `bone` is the dark theme's text — a warm off-white rather than a blue
        // tint, so the signed-in tools read in the same voice as the home page.
        ink: '#131a2c',
        bone: '#f6f4f0',

        // The Spotlight tokens (shared/styles/spotlight.css, plus the
        // workspace's additions in build/styles/workspace.css). Each class is
        // named after its custom property — `text-sl-muted` reads
        // var(--sl-muted) — and each is theme-aware on its own, so none needs
        // a `dark:` twin. They resolve only inside a `.spotlight` root.
        sl: Object.fromEntries(
          [
            'bg', 'bg-deep', 'surface', 'surface-2', 'line', 'line-strong',
            'text', 'muted', 'faint', 'coral', 'amber', 'focus', 'selection',
            'glow', 'glow-soft', 'text-glow', 'cool', 'cool-line', 'warm-line',
            'on-accent', 'ok', 'bad', 'wait', 'work', 'spot-core', 'spot-mid',
            'spot-wide', 'beam-edge', 'beam-core', 'section-glow', 'dot',
            'chip-bg', 'chip-bg-hover', 'placeholder', 'chrome-dot',
            'chrome-dot-edge', 'rule',
          ].map((name) => [name, `var(--sl-${name})`]),
        ),

        // The editorial tokens (shared/styles/editorial.css), which resolve
        // inside an `.editorial` root: `text-ed-ink-55` reads var(--ink-55).
        ed: Object.fromEntries(
          [
            'paper', 'paper-raised', 'ink', 'ink-70', 'ink-55', 'ink-40',
            'rule', 'rule-strong', 'accent', 'accent-soft',
          ].map((name) => [name, `var(--${name})`]),
        ),

        // The workspace's material tokens (build/styles/workspace.css).
        iw: {
          hairline: 'var(--iw-hairline)',
          'material-bg': 'var(--iw-material-bg)',
          'material-border': 'var(--iw-material-border)',
        },

        // Clean neutral palette
        dark: {
          950: '#0a0a0a',
          900: '#0f0f0f',
          800: '#171717',
          700: '#262626',
          600: '#404040',
        },
        light: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
        },
        // Minimal accent color
        primary: {
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
        },
      },
      fontFamily: {
        // Instrument Sans is the site's text face (it is what index.html
        // loads). This used to lead with Inter, which nothing loads, so every
        // element not explicitly set in `font-body` fell through to Arial.
        sans: [
          'Instrument Sans',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        display: [
          'Fraunces',
          'Georgia',
          'Cambria',
          'Times New Roman',
          'serif',
        ],
        // The Spotlight faces, read from spotlight.css.
        'sl-display': 'var(--sl-font-display)',
        'sl-body': 'var(--sl-font-body)',
        body: [
          'Instrument Sans',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      spacing: {
        // The fixed top bar's true height: BaseNavbar's h-14 row plus its 1px
        // bottom hairline. Anything that sits under the bar (the shell's
        // sidebar, main content and mobile scrim) offsets by this, so the
        // panels sit flush against it instead of leaving a dead strip.
        // Keep in sync with the row height in BaseNavbar.vue.
        'nav': 'calc(3.5rem + 1px)',
      },
      // Gradients and layered backgrounds from spotlight.css: `bg-sl-grad`.
      backgroundImage: Object.fromEntries(
        [
          'grad', 'card-bg', 'prompt-bg', 'prompt-edge', 'half-build-bg',
          'half-run-bg', 'chrome-bg', 'win-edge',
        ].map((name) => [`sl-${name}`, `var(--sl-${name})`]),
      ),
      boxShadow: {
        'sl-card': 'var(--sl-card-shadow)',
        'sl-prompt': 'var(--sl-prompt-shadow)',
        'sl-prompt-focus': 'var(--sl-prompt-shadow-focus)',
        'sl-btn': 'var(--sl-btn-shadow)',
        'sl-btn-hover': 'var(--sl-btn-shadow-hover)',
        'sl-win': 'var(--sl-win-shadow)',
        'iw-1': 'var(--iw-shadow-1)',
        'iw-2': 'var(--iw-shadow-2)',
        'iw-3': 'var(--iw-shadow-3)',
        'iw-focus': 'var(--iw-focus-ring)',
        'app-card': 'var(--app-shadow-card)',
        'app-card-hover': 'var(--app-shadow-card-hover)',
      },
      borderRadius: {
        'iw-xs': 'var(--iw-r-xs)',
        'iw-sm': 'var(--iw-r-sm)',
        'iw-md': 'var(--iw-r-md)',
        'iw-lg': 'var(--iw-r-lg)',
      },
      // The workspace's motion vocabulary (build/styles/workspace.css) and the
      // site-wide ease (tokens.css): `duration-iw-2 ease-iw-out`.
      transitionDuration: {
        'iw-1': 'var(--iw-dur-1)',
        'iw-2': 'var(--iw-dur-2)',
        'iw-3': 'var(--iw-dur-3)',
        'iw-4': 'var(--iw-dur-4)',
        'app-fast': 'var(--app-dur-fast)',
        'app-slow': 'var(--app-dur-slow)',
      },
      transitionTimingFunction: {
        'iw-out': 'var(--iw-ease-out)',
        'iw-spring': 'var(--iw-ease-spring)',
        'iw-inout': 'var(--iw-ease-inout)',
        'iw-ambient': 'var(--iw-ease-ambient)',
        app: 'var(--app-ease)',
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out forwards',
        'fade-in-up': 'fade-in-up 0.5s ease-out forwards',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    typography,
  ],
}
