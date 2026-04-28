import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        aqua: {
          50: "#f1f7ff",
          100: "#e5f1ff",
          200: "#d6eaff",
          400: "#5aa9f4",
          500: "#388bdd",
          700: "#125ea8"
        }
      },
      boxShadow: {
        panel: "0 2px 8px rgba(24, 86, 148, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
