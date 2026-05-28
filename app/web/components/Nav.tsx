"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { useCompass } from "@/components/Compass";
import { api } from "@/lib/api";

type NavItem = { href: string; label: string; hint?: string };

// Every stage of the workforce process lives under one "Workforce" menu — the
// six-phase lifecycle, in order, mapping one-to-one to a surface: Hire
// (Discover), Pre-Boarding (Onboard), Roster (Manage), Compliance (Govern),
// Operate, and Talent Development (Optimize). Sentinel is the monitoring engine
// behind Operate, not a page of its own.
const WORKFORCE: NavItem[] = [
  { href: "/workforce", label: "Hire", hint: "Discover" },
  { href: "/agents", label: "Pre-Boarding", hint: "Onboard" },
  { href: "/roster", label: "Roster", hint: "Manage" },
  { href: "/compliance", label: "Compliance", hint: "Govern" },
  { href: "/operate", label: "Operate", hint: "Operate" },
  { href: "/optimize", label: "Talent Development", hint: "Optimize" },
];

// Demo collateral — the non-lifecycle "how it's built" evidence surfaces.
const DEMO: NavItem[] = [
  { href: "/architecture", label: "Architecture" },
  { href: "/grounding", label: "Grounding" },
];

function linkCls(active: boolean): string {
  return `whitespace-nowrap rounded-lg px-2.5 py-2 text-xs font-semibold uppercase tracking-wider transition-colors ${
    active ? "bg-surface-container text-primary" : "text-on-surface-variant hover:bg-surface-container hover:text-primary"
  }`;
}

export function Nav() {
  const pathname = usePathname();
  const { openCompass } = useCompass();

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

        {/* No overflow-x clipping here: an absolutely-positioned dropdown panel must
            be allowed to escape the bar, so the menus actually render. */}
        <ul className="ml-auto flex min-w-0 items-center gap-0.5">
          <li>
            <Link href="/" className={linkCls(pathname === "/")}>
              Home
            </Link>
          </li>
          <li>
            <NavMenu label="Workforce" items={WORKFORCE} align="left" />
          </li>
          <li>
            <NavMenu label="Demo" items={DEMO} align="right" footer={<ResetDemoItem />} />
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

function NavMenu({
  label,
  items,
  align,
  footer,
}: {
  label: string;
  items: NavItem[];
  align: "left" | "right";
  footer?: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const isActive = (href: string) => pathname === href || pathname.startsWith(href);
  const active = items.some((it) => isActive(it.href));

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
        {label}
        <span className="material-symbols-outlined text-[16px]">{open ? "arrow_drop_up" : "arrow_drop_down"}</span>
      </button>
      {open && (
        <div
          role="menu"
          className={`absolute ${align === "right" ? "right-0" : "left-0"} top-full z-50 mt-1 min-w-[12rem] overflow-hidden rounded-lg border border-outline-variant/40 bg-surface shadow-lg`}
        >
          {items.map((it) => (
            <Link
              key={it.href}
              href={it.href}
              role="menuitem"
              className={`block px-3 py-2 transition-colors ${
                isActive(it.href)
                  ? "bg-surface-container text-primary"
                  : "text-on-surface-variant hover:bg-surface-container hover:text-primary"
              }`}
            >
              <span className="block text-xs font-semibold uppercase tracking-wider">{it.label}</span>
              {it.hint && (
                <span className="mt-0.5 block text-[10px] font-medium normal-case tracking-normal text-on-surface-variant/80">
                  {it.hint}
                </span>
              )}
            </Link>
          ))}
          {footer && (
            <>
              <div className="border-t border-outline-variant/40" />
              {footer}
            </>
          )}
        </div>
      )}
    </div>
  );
}

// Reset the lifecycle demo to its pristine state. Two-click confirm (so an
// errant click never wipes mid-demo state), then a reload so every surface —
// the roster and the per-phase lifecycle cards — re-derives from the clean
// store. Onboarding runs are untouched server-side.
type ResetPhase = "idle" | "confirm" | "working" | "done" | "error";

function resetLabel(phase: ResetPhase): { icon: string; text: string; tone: string } {
  switch (phase) {
    case "confirm":
      return {
        icon: "restart_alt",
        text: "Click again to confirm",
        tone: "bg-surface-container text-status-blocked",
      };
    case "working":
      return { icon: "progress_activity", text: "Resetting…", tone: "text-on-surface-variant" };
    case "done":
      return { icon: "check_circle", text: "Demo reset", tone: "text-status-ready" };
    case "error":
      return { icon: "error", text: "Reset failed — try again", tone: "text-status-blocked" };
    default:
      return {
        icon: "restart_alt",
        text: "Reset demo",
        tone: "text-on-surface-variant hover:bg-surface-container hover:text-status-blocked",
      };
  }
}

function ResetDemoItem() {
  const [phase, setPhase] = useState<ResetPhase>("idle");

  // Auto-disarm the confirm prompt if the user hesitates.
  useEffect(() => {
    if (phase !== "confirm") return;
    const t = setTimeout(() => setPhase("idle"), 4000);
    return () => clearTimeout(t);
  }, [phase]);

  async function handle() {
    if (phase === "idle" || phase === "error") {
      setPhase("confirm");
      return;
    }
    if (phase === "confirm") {
      setPhase("working");
      try {
        await api.resetDemo();
        setPhase("done");
        setTimeout(() => window.location.reload(), 700);
      } catch {
        setPhase("error");
      }
    }
  }

  const { icon, text, tone } = resetLabel(phase);

  return (
    <button
      type="button"
      role="menuitem"
      onClick={handle}
      disabled={phase === "working" || phase === "done"}
      className={`flex w-full items-center gap-2 px-3 py-2 text-left transition-colors ${tone}`}
    >
      <span className={`material-symbols-outlined text-[16px] ${phase === "working" ? "animate-spin" : ""}`}>
        {icon}
      </span>
      <span className="block text-xs font-semibold uppercase tracking-wider">{text}</span>
    </button>
  );
}
