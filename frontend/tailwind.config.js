/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "surface-container-lowest": "#0A0C10",
        "surface-container-highest": "#333539",
        "surface-container": "#1A1D23",
        "surface-container-high": "#282a2e",
        "on-surface": "#e2e2e8",
        "on-surface-variant": "#b9cbbc",
        "primary": "#0AFF9D",
        "primary-container": "#0aff9d",
        "on-primary-container": "#007143",
        "outline-variant": "#3b4a3f",
      },
      fontFamily: {
        "inter": ["Inter", "sans-serif"],
      }
    },
  },
  plugins: [],
}