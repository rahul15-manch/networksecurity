/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#090909",
          secondary: "#111111",
          card: "#171717",
          elevated: "#202020",
        },
        crimson: {
          DEFAULT: "#DC2626",
          hover: "#EF4444",
          dark: "#991B1B",
          glow: "rgba(220, 38, 38, 0.25)",
        },
        txt: {
          primary: "#F5F5F5",
          secondary: "#A3A3A3",
          muted: "#737373",
        },
        border: {
          subtle: "#303030",
          hover: "#404040",
          accent: "#DC2626",
        },
        status: {
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#DC2626",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
      boxShadow: {
        'glow-red': '0 0 25px -5px rgba(220, 38, 38, 0.3)',
        'glow-red-lg': '0 0 40px -10px rgba(220, 38, 38, 0.4)',
        'card-dark': '0 8px 30px rgba(0, 0, 0, 0.8)',
      }
    },
  },
  plugins: [],
}
