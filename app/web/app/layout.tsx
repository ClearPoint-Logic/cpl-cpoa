import type { Metadata } from "next";
import { Nav } from "@/components/Nav";
import { CompassProvider } from "@/components/Compass";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClearPoint Workforce Agent: AI Workforce Management",
  description:
    "The AI Workforce Management onboarding gate. Built on Google's agent platform (ADK, Gemini on Vertex AI, MCP, Vertex AI Search, Cloud Run, A2A) to hire AI agents the way enterprises hire humans.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <CompassProvider>
          <Nav />
          <main className="mx-auto w-full max-w-7xl flex-grow px-4 py-8 sm:px-8">{children}</main>
          <footer className="mt-auto border-t border-outline-variant/40 bg-surface-dim">
            <div className="mx-auto max-w-7xl px-4 py-6 text-xs text-on-surface-variant sm:px-8">
              © 2026 ClearPoint Logic
            </div>
          </footer>
        </CompassProvider>
      </body>
    </html>
  );
}
