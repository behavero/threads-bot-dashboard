/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#a78bfa', // purple-400
        accent: '#7dd3fc',  // sky-300
        glass: {
          50: 'rgba(255, 255, 255, 0.02)',
          100: 'rgba(255, 255, 255, 0.05)',
          200: 'rgba(255, 255, 255, 0.08)',
          300: 'rgba(255, 255, 255, 0.10)',
          400: 'rgba(255, 255, 255, 0.15)',
          500: 'rgba(255, 255, 255, 0.20)',
          border: 'rgba(255, 255, 255, 0.10)',
          highlight: 'rgba(255, 255, 255, 0.06)',
        },
        indigo: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'neon': '0 0 20px rgba(167, 139, 250, 0.3), 0 0 40px rgba(167, 139, 250, 0.1)',
        'neon-accent': '0 0 20px rgba(125, 211, 252, 0.3), 0 0 40px rgba(125, 211, 252, 0.1)',
        'inner-glass': 'inset 0 1px 1px rgba(255, 255, 255, 0.06)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1), 0 1px 1px rgba(255, 255, 255, 0.06)',
      },
      animation: {
        'float': 'float 8s ease-in-out infinite',
        'float-slow': 'float-slow 12s ease-in-out infinite',
        'fade-in': 'fade-in 400ms ease-out',
        'slide-up': 'slide-up 300ms ease-out',
        'slide-down': 'slide-down 300ms ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '33%': { transform: 'translateY(-10px) rotate(1deg)' },
          '66%': { transform: 'translateY(8px) rotate(-1deg)' },
        },
        'float-slow': {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '33%': { transform: 'translateY(-14px) rotate(2deg)' },
          '66%': { transform: 'translateY(12px) rotate(-2deg)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-down': {
          '0%': { opacity: '0', transform: 'translateY(-12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'ui-monospace', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
} 