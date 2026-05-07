/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0B0B0C",
        surface: "#111214",
        "text-primary": "#E8EAF0",
        "text-secondary": "#9AA0A6",
        border: "#1A1C1F",
        accent: "#C6A85B",
      },
      boxShadow: {
        card: "0 8px 24px rgba(0, 0, 0, 0.18)",
      },
      fontFamily: {
        sans: ['"Aptos"', '"Segoe UI"', "sans-serif"],
      },
    },
  },
  plugins: [],
};
