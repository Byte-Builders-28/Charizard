/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Chakra Petch"', 'sans-serif'],
      },
      colors: {
        space: {
          950: '#050810',
          900: '#0a0f1e',
          800: '#111827',
          700: '#1f2937',
          600: '#374151',
        },
        flame: {
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
        },
        ember: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
        charizard: {
          wing: '#1b7a82',
          orange: '#ff6b1a',
          belly: '#ffe082',
          flame: '#ff3d00',
        },
      },
    },
  },
  plugins: [],
}
