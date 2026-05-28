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
        <h1 className="text-2xl font-bold text-cpl-charcoal">Test Agent Zoo</h1>
        <p className="text-slate-600">
          Pick a candidate agent and run the onboarding workflow end to end.
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
                  <p className="mt-2 flex-1 text-sm text-slate-600">{f.business_story}</p>
                  <div className="mt-3 flex flex-wrap gap-1.5 text-xs text-slate-500">
                    <span className="rounded bg-slate-100 px-2 py-0.5">{f.autonomy}</span>
                    {f.tools.map((t) => (
                      <span key={t.name} className="rounded bg-slate-100 px-2 py-0.5">
                        {t.name} · {t.risk_tier}
                      </span>
                    ))}
                    {f.data_classes.map((d) => (
                      <span key={d} className="rounded bg-cpl-aqua/10 px-2 py-0.5 text-cpl-charcoal">{d}</span>
                    ))}
                  </div>
                  <button
                    onClick={() => run(f.name)}
                    disabled={busy === f.name}
                    className="mt-4 rounded-lg bg-cpl-blue px-4 py-2 text-sm font-semibold text-white hover:bg-cpl-blue/90 disabled:opacity-60"
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
