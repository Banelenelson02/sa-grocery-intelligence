/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Grounded in the subject: fresh produce green, marigold accent
        // (not the generic terracotta/cream AI-default), charcoal text.
        forest: {
          50: '#EAF1EC',
          100: '#CBDCD1',
          400: '#3A7359',
          600: '#245239',
          900: '#1B4332',
        },
        marigold: {
          400: '#F0B44D',
          500: '#E8A33D',
          600: '#C6822A',
        },
        sand: '#FAF9F4',
        ink: '#20241F',
        sage: '#D8E3D3',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
