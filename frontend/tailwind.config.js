/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#FBFAF7",
        ink: "#1C2127",
        "ink-soft": "#4A5260",
        rule: "#D9D4C8",
        "rule-soft": "#E8E4D9",
        forest: "#2F5233",
        "forest-soft": "#E4EBE2",
        brick: "#B23A48",
        "brick-soft": "#F6E4E2",
        amber: "#A9752B",
        "amber-soft": "#F3E8D4",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
