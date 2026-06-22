/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#0A0A0B",
          surface: "#141416",
          raised: "#1B1B1E",
          border: "#262629",
          "border-strong": "#34343A",
        },
        ink: {
          DEFAULT: "#F4F4F5",
          muted: "#A1A1AA",
          subtle: "#71717A",
        },
        accent: {
          DEFAULT: "#6366F1",
          hover: "#7C7FF2",
          muted: "#312E81",
        },
        success: { DEFAULT: "#22C55E", muted: "#14532D" },
        warning: { DEFAULT: "#F59E0B", muted: "#78350F" },
        danger: { DEFAULT: "#EF4444", muted: "#7F1D1D" },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        card: "12px",
      },
      boxShadow: {
        card: "0 1px 2px 0 rgba(0,0,0,0.4)",
        "card-hover": "0 4px 16px 0 rgba(0,0,0,0.5)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
