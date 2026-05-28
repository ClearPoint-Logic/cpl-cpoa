import type { Config } from "tailwindcss";

// Stitch design system (Material 3 tonal tokens) with CPL brand overrides (§15.4/§15.5):
// CPL primary blue (#0B65FC) replaces Stitch's default primary where they conflict.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Tonal surfaces
        surface: "#f7fafb",
        "surface-dim": "#d7dadb",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f1f4f5",
        "surface-container": "#ebeeef",
        "surface-container-high": "#e6e9ea",
        "surface-container-highest": "#e0e3e4",
        "on-surface": "#181c1d",
        "on-surface-variant": "#424655",
        outline: "#737687",
        "outline-variant": "#c2c6d8",
        // Primary = CPL brand blue (override)
        primary: "#0B65FC",
        "primary-hover": "#004ecb",
        "on-primary": "#ffffff",
        "primary-container": "#dbe1ff",
        "on-primary-container": "#00184a",
        tertiary: "#00626b",
        // Decision triage (solid)
        "status-ready": "#10B981",
        "status-conditional": "#F59E0B",
        "status-blocked": "#EF4444",
        // CPL brand anchors (retained)
        cpl: { blue: "#0B65FC", charcoal: "#1F262B", aqua: "#43CFDF", orange: "#F59E0B", gray: "#CFD2D3" },
        decision: { ready: "#10B981", conditional: "#F59E0B", blocked: "#EF4444" },
      },
      fontFamily: {
        heading: ["Lexend", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Courier Prime", "ui-monospace", "monospace"],
      },
      spacing: { gutter: "24px", "rail-h": "80px", sidebar: "320px" },
      borderRadius: { lg: "0.5rem", xl: "0.75rem", "2xl": "1rem" },
    },
  },
  plugins: [],
};

export default config;
