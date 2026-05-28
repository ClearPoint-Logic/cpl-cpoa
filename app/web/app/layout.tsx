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
      <body className="flex min-h-screen flex-col">
        <Nav />
        <main className="mx-auto w-full max-w-7xl flex-grow px-4 py-8 sm:px-8">{children}</main>
        <footer className="mt-auto border-t border-outline-variant/40 bg-surface-dim">
          <div className="mx-auto max-w-7xl px-4 py-6 text-xs text-on-surface-variant sm:px-8">
            © 2026 Mabry Ventures
          </div>
        </footer>
      </body>
    </html>
  );
}
