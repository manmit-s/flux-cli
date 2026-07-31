import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './content/**/*.{md,mdx}',
    './node_modules/fumadocs-ui/dist/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        flux: {
          purple: '#e7aafb',
          slate: '#a191f8',
          blue: '#8bcefc',
          cyan: '#7fe4eb',
          rose: '#f43f5e',
          green: '#4ade80',
        },
        brand: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e7aafb',
          300: '#d48cf8',
          400: '#bf7cf5',
          500: '#a191f8',
          600: '#8b7cf0',
          700: '#7c6de8',
          800: '#6b5dd6',
          900: '#5a4ec4',
        },
        surface: {
          DEFAULT: '#0a0a0f',
          50: '#111118',
          100: '#16161e',
          200: '#1c1c26',
          300: '#24242f',
          400: '#2e2e3a',
          500: '#3a3a47',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: '#e2e8f0',
            a: {
              color: '#8bcefc',
              '&:hover': {
                color: '#a191f8',
              },
            },
            'h1, h2, h3, h4': {
              color: '#f1f5f9',
              fontWeight: '600',
            },
            code: {
              color: '#e7aafb',
              backgroundColor: '#1c1c26',
              borderRadius: '0.375rem',
              padding: '0.125rem 0.375rem',
              fontWeight: '400',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            pre: {
              backgroundColor: '#0d0d14',
              border: '1px solid #1e1e2e',
              borderRadius: '0.75rem',
            },
          },
        },
      },
      animation: {
        'gradient-x': 'gradient-x 15s ease infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.5s ease-out',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center',
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center',
          },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [require('@tailwindcss/typography'), require('tailwindcss-animate')],
}

export default config
