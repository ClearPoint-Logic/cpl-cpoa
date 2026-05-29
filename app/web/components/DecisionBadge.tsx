// Decision indicator: bold colored uppercase label, no pill background.
// AI Workforce Management design language: authoritative, sober, enterprise-grade.
const MAP: Record<string, { label: string; cls: string }> = {
  Ready: { label: "Ready", cls: "text-status-ready" },
  "Ready with Conditions": { label: "Conditional", cls: "text-status-conditional" },
  "Blocked Pending Remediation": { label: "Blocked", cls: "text-status-blocked" },
};

export function DecisionBadge({ decision, size = "md" }: { decision: string; size?: "sm" | "md" | "lg" }) {
  const m = MAP[decision] ?? { label: decision, cls: "text-on-surface-variant" };
  const sz = size === "lg" ? "text-base" : size === "sm" ? "text-[11px]" : "text-xs";
  return (
    <span
      className={`inline-flex items-center font-heading font-bold uppercase tracking-[0.18em] ${m.cls} ${sz}`}
    >
      {m.label}
    </span>
  );
}
