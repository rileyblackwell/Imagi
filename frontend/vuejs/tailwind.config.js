/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#0a0b0f',
          900: '#111318',
          800: '#1a1d24',
          700: '#282c35',
        },
        primary: {
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      spacing: {
        'header': '64px',
      },
      keyframes: {
        float: {
          '0%, 100%': { 
            transform: 'translateY(0)',
            filter: 'drop-shadow(0 0 20px rgba(34,211,238,0.35))'
          },
          '50%': { 
            transform: 'translateY(-10px)',
            filter: 'drop-shadow(0 0 30px rgba(34,211,238,0.45))'
          },
        }
      },
      animation: {
        float: 'float 3s ease-in-out infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} 