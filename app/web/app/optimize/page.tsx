"use client";

import { useEffect, useState } from "react";

interface Item {
  finding_id: string;
  title: string;
  severity: string;
  remediation: string;
  blocks_promotion?: boolean;
}

interface Plan {
  candidate_agent_id: string;
  name: string;
  current_autonomy: string;
  next_autonomy: string | null;
  tools: string[];
  monthly_budget_usd: number | null;
  development_items: Item[];
  promotion_blockers: Item[];
  ready_for_promotion: boolean;
}

interface PlansEnvelope {
  summary: {
    agents: number;
    ready_for_promotion: number;
    with_development_items: number;
    with_blockers: number;
  };
  plans: Plan[];
}

export default function Optimize() {
  const [data, setData] = useState<PlansEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/optimize/plans", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${r.status}`))))
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-heading text-2xl font-semibold">Talent Development</h1>
        <p className="text-on-surface-variant">
          This is the Optimize phase, where agents grow. Everyone gets a real development plan: the
          open conditions from the Onboarding Validation Suite become things to work on, and each
          rung of the autonomy ladder becomes a promotion to earn. Clear the items, earn the next
          rung. Just like the rest of your team.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}
      {!data && !error && <p className="text-on-surface-variant">Drawing up development plans…</p>}

      {data && (
        <>
          <section className="grid gap-4 sm:grid-cols-4">
            <Metric label="Agents" value={data.summary.agents} />
            <Metric label="Ready for promotion" value={data.summary.ready_for_promotion} tone="ok" />
            <Metric label="With development items" value={data.summary.with_development_items} tone="info" />
            <Metric label="With blockers" value={data.summary.with_blockers} tone="warn" />
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
              Development plans
            </h2>
            <ul className="space-y-3">
              {data.plans.map((p) => (
                <article
                  key={p.candidate_agent_id}
                  className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5"
                >
                  <header className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="font-heading text-base font-semibold text-on-surface">{p.name}</h3>
                    {p.ready_for_promotion ? (
                      <span className="rounded bg-decision-ready/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-ready">
                        Ready for promotion
                      </span>
                    ) : p.promotion_blockers.length > 0 ? (
                      <span className="rounded bg-decision-blocked/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-blocked">
                        Promotion blocked
                      </span>
                    ) : (
                      <span className="rounded bg-decision-conditional/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-conditional">
                        Development in progress
                      </span>
                    )}
                  </header>
                  <p className="mt-1 text-xs text-on-surface-variant">{p.candidate_agent_id}</p>

                  <dl className="mt-3 grid gap-x-6 gap-y-1 text-xs text-on-surface-variant sm:grid-cols-3">
                    <div>
                      <dt className="inline font-semibold text-on-surface">Current rung: </dt>
                      <dd className="inline">{p.current_autonomy}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Next rung: </dt>
                      <dd className="inline">{p.next_autonomy ?? "(top of ladder)"}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Monthly budget: </dt>
                      <dd className="inline">
                        {p.monthly_budget_usd != null ? `$${p.monthly_budget_usd}` : "—"}
                      </dd>
                    </div>
                  </dl>

                  {p.development_items.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant">
                        Development items
                      </h4>
                      <ul className="mt-1 space-y-1 text-sm">
                        {p.development_items.map((item) => (
                          <li key={item.finding_id} className="rounded border border-outline-variant/30 p-2">
                            <p className="font-semibold text-on-surface">{item.title}</p>
                            <p className="text-xs text-on-surface-variant">{item.remediation}</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {p.promotion_blockers.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-[11px] font-bold uppercase tracking-wider text-decision-blocked">
                        Promotion blockers
                      </h4>
                      <ul className="mt-1 space-y-1 text-sm">
                        {p.promotion_blockers.map((item) => (
                          <li key={item.finding_id} className="rounded border border-decision-blocked/30 bg-decision-blocked/5 p-2">
                            <p className="font-semibold text-on-surface">{item.title}</p>
                            <p className="text-xs text-on-surface-variant">{item.remediation}</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {p.development_items.length === 0 && p.promotion_blockers.length === 0 && (
                    <p className="mt-3 text-xs italic text-on-surface-variant">
                      Nothing outstanding. {p.next_autonomy
                        ? `Ready to move up to ${p.next_autonomy}.`
                        : "Already at the top of the ladder."}
                    </p>
                  )}
                </article>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  tone = "info",
}: {
  label: string;
  value: number;
  tone?: "ok" | "warn" | "info";
}) {
  const cls =
    tone === "warn"
      ? "border-decision-blocked/30 bg-decision-blocked/5"
      : tone === "ok"
      ? "border-decision-ready/30 bg-decision-ready/5"
      : "border-outline-variant/40 bg-surface-container-lowest";
  return (
    <div className={`rounded-xl border p-4 ${cls}`}>
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-on-surface-variant">
        {label}
      </div>
      <div className="mt-1 font-heading text-3xl font-semibold text-on-surface">{value}</div>
    </div>
  );
}
