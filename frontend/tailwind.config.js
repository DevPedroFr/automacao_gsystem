const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './app/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#080d16',
        card: 'rgba(12, 21, 34, 0.82)',
        cardBorder: 'rgba(148, 163, 184, 0.14)',
        accent: {
          cyan: '#06B6D4',
          emerald: '#10B981',
          indigo: '#6366F1',
          purple: '#8B5CF6'
        },
        navy: {
          700: '#1E3A5F',
          800: '#172E4A',
          900: '#0F2744',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', ...defaultTheme.fontFamily.sans],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'pulse-soft': 'pulseSoft 2s infinite',
        'glow': 'glow 3s infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        glow: {
          '0%': { boxShadow: '0 0 10px rgba(6, 182, 212, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(6, 182, 212, 0.6)' },
        }
      }
    },
  },
  plugins: [],
};
