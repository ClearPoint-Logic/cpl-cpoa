// Solid pill status badges per the Stitch design system (DESIGN.md "Decision Suite").
const MAP: Record<string, { label: string; cls: string }> = {
  Ready: { label: "Ready", cls: "bg-status-ready text-white" },
  "Ready with Conditions": { label: "Conditional", cls: "bg-status-conditional text-white" },
  "Blocked Pending Remediation": { label: "Blocked", cls: "bg-status-blocked text-white" },
};

export function DecisionBadge({ decision, size = "md" }: { decision: string; size?: "sm" | "md" | "lg" }) {
  const m = MAP[decision] ?? { label: decision, cls: "bg-on-surface-variant text-white" };
  const sz =
    size === "lg" ? "text-sm px-4 py-1.5" : size === "sm" ? "text-[11px] px-2.5 py-0.5" : "text-xs px-3 py-1";
  return (
    <span
      className={`inline-flex items-center rounded-full font-heading font-semibold uppercase tracking-wider ${m.cls} ${sz}`}
    >
      {m.label}
    </span>
  );
}
