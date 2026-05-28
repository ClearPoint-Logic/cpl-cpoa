const MAP: Record<string, { label: string; cls: string }> = {
  Ready: { label: "Ready", cls: "bg-decision-ready/10 text-decision-ready ring-decision-ready/30" },
  "Ready with Conditions": {
    label: "Conditional",
    cls: "bg-decision-conditional/10 text-decision-conditional ring-decision-conditional/30",
  },
  "Blocked Pending Remediation": {
    label: "Blocked",
    cls: "bg-decision-blocked/10 text-decision-blocked ring-decision-blocked/30",
  },
};

export function DecisionBadge({ decision, size = "md" }: { decision: string; size?: "sm" | "md" | "lg" }) {
  const m = MAP[decision] ?? { label: decision, cls: "bg-slate-100 text-slate-700 ring-slate-300" };
  const sz = size === "lg" ? "text-base px-4 py-1.5" : size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1";
  return (
    <span className={`inline-flex items-center rounded-full font-semibold ring-1 ${m.cls} ${sz}`}>
      {m.label}
    </span>
  );
}
