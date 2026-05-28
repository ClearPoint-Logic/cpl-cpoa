import Link from "next/link";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/agents", label: "Agent Zoo" },
  { href: "/architecture", label: "Architecture" },
  { href: "/judge", label: "Judge Access" },
];

export function Nav() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-cpl-blue text-sm font-bold text-white">
            CP
          </span>
          <span className="font-heading text-lg font-semibold text-cpl-charcoal">
            ClearPoint Onboarding Agent
          </span>
        </Link>
        <ul className="flex items-center gap-1 text-sm">
          {LINKS.map((l) => (
            <li key={l.href}>
              <Link
                href={l.href}
                className="rounded-md px-3 py-2 text-slate-600 hover:bg-slate-100 hover:text-cpl-charcoal"
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
