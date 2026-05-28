import type { Metadata } from "next";
import { Nav } from "@/components/Nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClearPoint Onboarding Agent",
  description:
    "A net-new ADK + Gemini multi-agent system that helps enterprises hire AI agents into the workforce.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="border-t border-slate-200 bg-white">
          <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-slate-500">
            Net-new Track 1 challenge agent inspired by ClearPoint Meridian — not a claim that
            Meridian is live. Implements the onboarding gate only; continuous attestation is the
            roadmap. Artifacts are demo-safe (synthetic fixtures, demo-stub signatures, demo-only
            readiness score). Onboarding recommendation, not certified compliance.
          </div>
        </footer>
      </body>
    </html>
  );
}
