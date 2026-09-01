/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F7F4EF",
        workspace: "#F7F4EF",
        sidebar: "#DCE7E1",
        "sidebar-selected": "#C7D9D0",
        "sidebar-text": "#26332F",
        "sidebar-selected-text": "#17231F",
        surface: "#FFFDFC",
        "surface-raised": "#F7F4EF",
        "surface-border": "#E5DED5",
        card: "#FFFDFC",
        "card-border": "#E5DED5",
        primary: {
          DEFAULT: "#5F8F83",
          hover: "#4F7D72",
          light: "#7BA89D",
        },
        lavender: "#A99BBE",
        "dusty-blue": "#9DB7C5",
        textPrimary: "#29332F",
        textSecondary: "#69736E",
        textMuted: "#929A95",
        risk: {
          low: "#A8C5B5",
          lowText: "#35604B",
          medium: "#E8C98A",
          mediumText: "#795B20",
          high: "#E8A98A",
          highText: "#8A472E",
          critical: "#D99A9A",
          criticalText: "#7B3030",
        },
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "10px",
        xl: "12px",
        "2xl": "14px",
      },
    },
  },
  plugins: [],
};
