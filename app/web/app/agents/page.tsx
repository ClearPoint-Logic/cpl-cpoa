"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { FixtureCard } from "@/lib/types";
import { DecisionBadge } from "@/components/DecisionBadge";

export default function AgentZoo() {
  const router = useRouter();
  const [fixtures, setFixtures] = useState<FixtureCard[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listFixtures().then(setFixtures).catch((e) => setError(String(e)));
  }, []);

  async function run(name: string) {
    setBusy(name);
    setError(null);
    try {
      const r = await api.createRun(name);
      router.push(`/runs/${r.run_id}`);
    } catch (e) {
      setError(String(e));
      setBusy(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-semibold text-cpl-charcoal">Pre-Boarding</h1>
        <p className="text-on-surface-variant">
          The roster of candidate AI agents awaiting their first day. Pick one and run it through
          the onboarding gate end-to-end. Each candidate exercises a distinct production scenario:
          clean intake, governance gaps, regulated data, budget exposure, prompt injection, and
          supply-chain risk.
        </p>
      </div>

      {/* Decision legend — what the badge on each candidate means */}
      <section className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4">
        <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-on-surface-variant">
          What the decision on each candidate means
        </h2>
        <dl className="mt-3 grid gap-3 sm:grid-cols-3">
          <LegendItem
            label="Ready"
            cls="text-status-ready"
            text="Clears the onboarding gate on day one: no blocking findings. Safe to deploy within its declared scope."
          />
          <LegendItem
            label="Conditional"
            cls="text-status-conditional"
            text="Hireable with conditions: scope caps, human approvals, or remediations attached before activation."
          />
          <LegendItem
            label="Blocked"
            cls="text-status-blocked"
            text="Cannot be onboarded as submitted: one or more fail-closed findings must be remediated first."
          />
        </dl>
      </section>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}
      {!fixtures.length && !error && <p className="text-slate-500">Loading fixtures…</p>}

      {fixtures.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {fixtures.map((f) => (
            <article key={f.name} className="flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-heading text-lg font-semibold text-cpl-charcoal">{f.agent_name}</h3>
                <DecisionBadge decision={f.expected_decision} size="sm" />
              </div>
              <p className="mt-2 flex-1 text-sm text-on-surface-variant">{f.business_story}</p>
              <dl className="mt-3 space-y-1 text-xs text-on-surface-variant">
                <div><span className="font-semibold text-on-surface">Autonomy</span> · {f.autonomy}</div>
                <div>
                  <span className="font-semibold text-on-surface">Tools</span> ·{" "}
                  {f.tools.length ? f.tools.map((t) => `${t.name} (${t.risk_tier})`).join(" · ") : "none"}
                </div>
                <div>
                  <span className="font-semibold text-on-surface">Data</span> ·{" "}
                  {f.data_classes.length ? f.data_classes.join(", ") : "public"}
                </div>
              </dl>
              <button
                onClick={() => run(f.name)}
                disabled={busy === f.name}
                className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-on-primary hover:bg-primary-hover disabled:opacity-60"
              >
                {busy === f.name ? "Onboarding…" : "Begin onboarding →"}
              </button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function LegendItem({ label, cls, text }: { label: string; cls: string; text: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className={`font-heading text-sm font-bold uppercase tracking-[0.18em] ${cls}`}>{label}</span>
      <span className="text-xs text-on-surface-variant">{text}</span>
    </div>
  );
}
