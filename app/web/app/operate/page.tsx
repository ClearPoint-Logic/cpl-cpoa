"use client";

import { useEffect, useState } from "react";

// Operate — fleet health + anomaly detection across the active roster, powered
// by the Sentinel monitoring engine (which runs behind the scenes). Signals are
// real: derived from each agent's onboarding outcome (Onboarding Validation Suite
// findings, readiness score, decision) and the live lifecycle state from the HR
// Console.

interface FleetMember {
  candidate_agent_id: string;
  name: string;
  status: string;
  risk_tier: string;
  autonomy_level: string;
  readiness_score: number;
  onboarding_decision: string;
  open_findings: number;
  blocking_findings: number;
  lifecycle_events_30d: number;
  last_event_at: string | null;
  anomalies: Array<{ rule_id: string; severity: string; summary: string }>;
}

interface FleetSnapshot {
  summary: {
    agents: number;
    active: number;
    on_leave: number;
    agents_with_anomalies: number;
    total_anomalies: number;
    by_risk_tier: Record<string, number>;
  };
  members: FleetMember[];
}

export default function Operate() {
  const [snap, setSnap] = useState<FleetSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  async function refresh() {
    setRefreshing(true);
    setError(null);
    try {
      const r = await fetch("/api/operate/fleet", { cache: "no-store" });
      if (!r.ok) throw new Error(`${r.status}`);
      setSnap(await r.json());
    } catch (e) {
      setError(String(e));
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="space-y-8">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Operate</h1>
          <p className="text-on-surface-variant">
            The Operate phase of the AI Workforce Management lifecycle — continuous
            performance management across the active roster, powered by the{" "}
            <strong className="text-on-surface">Sentinel</strong> monitoring engine
            running behind the scenes. Real signals from each agent&apos;s onboarding
            outcome and lifecycle history, with deterministic anomaly detection that
            lands findings on the hash-chained personnel file.
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="rounded-lg border border-outline px-3 py-1.5 text-sm font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
        >
          {refreshing ? "Refreshing…" : "Refresh assessment"}
        </button>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}
      {!snap && !error && <p className="text-on-surface-variant">Loading fleet health…</p>}

      {snap && (
        <>
          <section className="grid gap-4 sm:grid-cols-4">
            <Metric label="Agents on roster" value={snap.summary.agents} />
            <Metric label="Active" value={snap.summary.active} tone="ok" />
            <Metric label="On leave" value={snap.summary.on_leave} tone="warn" />
            <Metric
              label="With anomalies"
              value={snap.summary.agents_with_anomalies}
              tone={snap.summary.agents_with_anomalies > 0 ? "warn" : "ok"}
            />
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
              Risk-tier distribution
            </h2>
            <ul className="flex flex-wrap gap-2 text-xs">
              {Object.entries(snap.summary.by_risk_tier).map(([tier, count]) => (
                <li
                  key={tier}
                  className="rounded border border-outline-variant/40 bg-surface-container-lowest px-3 py-1 text-on-surface-variant"
                >
                  <span className="font-semibold text-on-surface">{tier}</span>: {count}
                </li>
              ))}
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
              Fleet
            </h2>
            <ul className="grid gap-3 md:grid-cols-2">
              {snap.members.map((m) => (
                <li
                  key={m.candidate_agent_id}
                  className={`rounded-xl border p-4 text-sm ${
                    m.anomalies.length > 0
                      ? "border-decision-conditional/40 bg-decision-conditional/5"
                      : "border-outline-variant/40 bg-surface-container-lowest"
                  }`}
                >
                  <header className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="font-heading text-base font-semibold text-on-surface">
                      {m.name}
                    </h3>
                    <span className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                      m.status === "active"
                        ? "bg-decision-ready/15 text-decision-ready"
                        : m.status === "on_leave"
                        ? "bg-decision-conditional/15 text-decision-conditional"
                        : "bg-surface-container text-on-surface-variant"
                    }`}>
                      {m.status}
                    </span>
                  </header>
                  <p className="mt-1 text-xs text-on-surface-variant">{m.candidate_agent_id}</p>
                  <dl className="mt-2 grid gap-x-4 gap-y-1 text-xs text-on-surface-variant sm:grid-cols-2">
                    <div>
                      <dt className="inline font-semibold text-on-surface">Risk tier: </dt>
                      <dd className="inline">{m.risk_tier}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Autonomy: </dt>
                      <dd className="inline">{m.autonomy_level}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Readiness: </dt>
                      <dd className="inline">{m.readiness_score}/100</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Decision: </dt>
                      <dd className="inline">{m.onboarding_decision}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Open conditions: </dt>
                      <dd className="inline">{m.open_findings}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-on-surface">Events (30d): </dt>
                      <dd className="inline">{m.lifecycle_events_30d}</dd>
                    </div>
                  </dl>
                  {m.anomalies.length > 0 && (
                    <div className="mt-3 border-t border-outline-variant/40 pt-2">
                      <p className="mb-1 text-[11px] font-bold uppercase tracking-wider text-decision-conditional">
                        Anomalies detected
                      </p>
                      <ul className="space-y-1 text-xs">
                        {m.anomalies.map((a) => (
                          <li key={a.rule_id} className="flex items-start gap-2">
                            <span
                              className={`shrink-0 rounded px-1.5 text-[10px] font-bold uppercase ${
                                a.severity === "high"
                                  ? "bg-decision-blocked/15 text-decision-blocked"
                                  : "bg-decision-conditional/15 text-decision-conditional"
                              }`}
                            >
                              {a.severity}
                            </span>
                            <div>
                              <p className="font-semibold text-on-surface">{a.rule_id}</p>
                              <p className="text-on-surface-variant">{a.summary}</p>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </section>

          <p className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-3 text-xs italic text-on-surface-variant">
            <span className="font-semibold not-italic">How this works:</span> Sentinel
            runs the gate code against each fixture (deterministically, no LLM) to
            recover findings + readiness; combines that with the live lifecycle state
            from the HR Console; then applies anomaly rules. Any anomaly the operator
            records via the API appends a real <code>operate.anomaly_detected</code>{" "}
            event to the agent&apos;s personnel-file hash chain.
          </p>
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
      ? "border-decision-conditional/30 bg-decision-conditional/5"
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
