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

  const groups: [string, FixtureCard[]][] = [
    ["Must-ship", fixtures.filter((f) => f.tier === "must_ship")],
    ["Stretch", fixtures.filter((f) => f.tier !== "must_ship")],
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-semibold text-cpl-charcoal">Pre-Boarding</h1>
        <p className="text-on-surface-variant">
          The roster of candidate AI agents awaiting their first day. Pick one and run it through
          the onboarding gate end-to-end. Each candidate exercises a distinct production scenario —
          clean intake, governance gaps, regulated data, budget exposure, prompt injection, and
          supply-chain risk.
        </p>
      </div>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}
      {!fixtures.length && !error && <p className="text-slate-500">Loading fixtures…</p>}

      {groups.map(([label, items]) =>
        items.length ? (
          <section key={label} className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{label}</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {items.map((f) => (
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
                    {busy === f.name ? "Onboarding…" : "Run onboarding →"}
                  </button>
                </article>
              ))}
            </div>
          </section>
        ) : null,
      )}
    </div>
  );
}
