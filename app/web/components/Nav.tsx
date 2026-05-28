import Link from "next/link";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/agents", label: "Agent Zoo" },
  { href: "/grounding", label: "Grounding" },
  { href: "/architecture", label: "Architecture" },
  { href: "/judge", label: "Judge Access" },
];

export function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-outline-variant/40 bg-surface/95 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-8">
        <Link href="/" className="flex items-center gap-2 text-primary">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
            security
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">
            ClearPoint Onboarding Agent
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
