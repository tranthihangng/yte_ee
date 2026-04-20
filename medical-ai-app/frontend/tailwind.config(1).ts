import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
          900: "#0f172a"
        },
        appbg: "#f4f6fb",
        card: "#ffffff",
        mutedtext: "#64748b"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(15, 23, 42, 0.05)"
      },
      borderRadius: {
        xl2: "1.25rem"
      }
    },
  },
  plugins: [],
} satisfies Config;
