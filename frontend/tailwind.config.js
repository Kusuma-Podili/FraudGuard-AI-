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
        background: "#FFFFFF",
        workspace: "#FFFFFF",
        sidebar: "#FFFFFF",
        "sidebar-selected": "#FFF7ED",
        "sidebar-text": "#374151",
        "sidebar-selected-text": "#9A3412",
        surface: "#FFFFFF",
        "surface-raised": "#F9FAFB",
        "surface-border": "#E5E7EB",
        card: "#FFFFFF",
        "card-border": "#E5E7EB",
        primary: {
          DEFAULT: "#FB923C",
          hover: "#F97316",
          light: "#FDBA74",
        },
        textPrimary: "#111827",
        textSecondary: "#4B5563",
        textMuted: "#9CA3AF",
        risk: {
          low: "#F3F4F6",
          lowText: "#374151",
          medium: "#F3F4F6",
          mediumText: "#374151",
          high: "#FFEDD5",
          highText: "#9A3412",
          critical: "#FFEDD5",
          criticalText: "#EA580C",
        },
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "10px",
        xl: "12px",
      },
    },
  },
  plugins: [],
};
