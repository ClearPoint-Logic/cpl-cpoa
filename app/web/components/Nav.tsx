"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useCompass } from "@/components/Compass";

// Primary lifecycle surfaces. Compass is no longer a page (it's the global
// slide-over advisor); the Govern control matrix now lives under Demo > Compliance.
const PRIMARY = [
  { href: "/workforce", label: "Workforce" },
  { href: "/agents", label: "Pre-Boarding" },
  { href: "/operate", label: "Sentinel" },
  { href: "/optimize", label: "Talent Dev" },
  { href: "/architecture", label: "Architecture" },
];

// Demo collateral — the judge-facing evidence surfaces.
const DEMO = [
  { href: "/grounding", label: "Grounding" },
  { href: "/compliance", label: "Compliance" },
];

function linkCls(active: boolean): string {
  return `whitespace-nowrap rounded-lg px-2.5 py-2 text-xs font-semibold uppercase tracking-wider transition-colors ${
    active ? "bg-surface-container text-primary" : "text-on-surface-variant hover:bg-surface-container hover:text-primary"
  }`;
}

export function Nav() {
  const pathname = usePathname();
  const { openCompass } = useCompass();
  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <header className="sticky top-0 z-50 border-b border-outline-variant/40 bg-surface/95 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-8">
        <Link href="/" className="flex shrink-0 items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/clearpoint-logo.png" alt="ClearPoint Logic" className="h-7 w-auto" />
          <span className="hidden border-l border-outline-variant/50 pl-3 text-sm font-medium text-on-surface-variant lg:inline">
            Workforce Agent
          </span>
        </Link>

        <ul className="ml-auto flex min-w-0 items-center gap-0.5 overflow-x-auto">
          <li>
            <Link href="/" className={linkCls(pathname === "/")}>
              Home
            </Link>
          </li>
          {PRIMARY.map((l) => (
            <li key={l.href}>
              <Link href={l.href} className={linkCls(isActive(l.href))}>
                {l.label}
              </Link>
            </li>
          ))}
          <li>
            <DemoMenu active={DEMO.some((d) => isActive(d.href))} />
          </li>
        </ul>

        <button
          onClick={() => openCompass({ page: pathname })}
          className="flex shrink-0 items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-xs font-semibold uppercase tracking-wider text-on-primary transition-colors hover:bg-primary-hover"
        >
          <span className="material-symbols-outlined text-[16px]">explore</span>
          <span className="hidden sm:inline">Ask Compass</span>
        </button>
      </nav>
    </header>
  );
}

function DemoMenu({ active }: { active: boolean }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  // Close on outside click or route change.
  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        className={`flex items-center gap-0.5 ${linkCls(active)}`}
      >
        Demo
        <span className="material-symbols-outlined text-[16px]">{open ? "arrow_drop_up" : "arrow_drop_down"}</span>
      </button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 top-full z-50 mt-1 min-w-[10rem] overflow-hidden rounded-lg border border-outline-variant/40 bg-surface shadow-lg"
        >
          {DEMO.map((d) => (
            <Link
              key={d.href}
              href={d.href}
              role="menuitem"
              className={`block px-3 py-2 text-xs font-semibold uppercase tracking-wider transition-colors ${
                pathname.startsWith(d.href)
                  ? "bg-surface-container text-primary"
                  : "text-on-surface-variant hover:bg-surface-container hover:text-primary"
              }`}
            >
              {d.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
