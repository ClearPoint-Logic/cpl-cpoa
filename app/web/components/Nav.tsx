import Link from "next/link";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/workforce", label: "Workforce" },
  { href: "/agents", label: "Pre-Boarding" },
  { href: "/govern", label: "Compass" },
  { href: "/operate", label: "Sentinel" },
  { href: "/optimize", label: "Talent Dev" },
  { href: "/grounding", label: "Grounding" },
  { href: "/architecture", label: "Architecture" },
  { href: "/judge", label: "Judge Access" },
];

export function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-outline-variant/40 bg-surface/95 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-8">
        <Link href="/" className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/clearpoint-logo.png" alt="ClearPoint Logic" className="h-7 w-auto" />
          <span className="hidden border-l border-outline-variant/50 pl-3 text-sm font-medium text-on-surface-variant sm:inline">
            Onboarding Agent
          </span>
        </Link>
        <ul className="flex items-center gap-1">
          {LINKS.map((l) => (
            <li key={l.href}>
              <Link
                href={l.href}
                className="rounded-lg px-3 py-2 text-xs font-semibold uppercase tracking-wider text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
