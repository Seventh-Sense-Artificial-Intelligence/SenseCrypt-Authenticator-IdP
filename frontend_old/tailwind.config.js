/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: {
          red: '#B3231D',
          'red-dark': '#A91E22',
          'red-light': '#E04040',
          gold: '#F5A324',
        },
        surface: {
          DEFAULT: '#F5F5F5',
          elevated: '#FFFFFF',
          dark: '#1A1A2E',
          'dark-elevated': '#242440',
        },
        muted: '#999999',
        body: '#3F4246',
        'dark-bg': '#0F0F1A',
      },
      fontFamily: {
        display: ['"Wix Madefor Display"', 'Inter', 'sans-serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-cta': 'linear-gradient(90deg, #B3231D 0%, #F5A324 100%)',
        'gradient-cta-dark': 'linear-gradient(90deg, #E04040 0%, #F5A324 100%)',
        'network': "url('/images/network.png')",
      },
      borderRadius: {
        'pill': '9999px',
      },
      animation: {
        'pulse-ring': 'pulse-ring 3s ease-in-out infinite',
        'fade-in': 'fade-in 0.2s ease',
        'slide-up': 'slide-up 0.3s ease',
      },
      keyframes: {
        'pulse-ring': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.3' },
          '50%': { transform: 'scale(1.05)', opacity: '0.6' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
