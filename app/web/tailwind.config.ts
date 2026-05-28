import type { Config } from "tailwindcss";

// CPL brand tokens (§15.5) applied as Tailwind theme overrides.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cpl: {
          blue: "#0B65FC",
          charcoal: "#1F262B",
          aqua: "#43CFDF",
          orange: "#F59E0B",
          gray: "#CFD2D3",
        },
        decision: {
          ready: "#15803d",
          conditional: "#b45309",
          blocked: "#b91c1c",
        },
      },
      fontFamily: {
        heading: ["Lexend", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
