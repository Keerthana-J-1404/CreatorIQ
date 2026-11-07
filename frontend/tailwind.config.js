/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoal: {
          950: '#0a0a0c',
          900: '#121217',
          850: '#181820',
          800: '#1f1f29',
          700: '#2d2d3b',
        },
        violet: {
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          accent: '#9333ea',
        },
        indigo: {
          500: '#6366f1',
          600: '#4f46e5',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
