"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Run } from "@/lib/types";
import { DecisionBadge } from "@/components/DecisionBadge";

// Tab labels use HR/workforce vocabulary; the canonical technical name appears in
// the section title inside the tab so both judges and reviewers see them.
const TABS = ["Passport", "Résumé", "Job Description", "Background Check", "Personnel File"] as const;
type Tab = (typeof TABS)[number];

const SEV_CLS: Record<string, string> = {
  critical: "text-decision-blocked",
  high: "text-decision-blocked",
  medium: "text-decision-conditional",
  low: "text-slate-500",
  info: "text-slate-400",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h4 className="mb-2 text-sm font-semibold text-slate-500">{title}</h4>
      {children}
    </div>
  );
}

function Raw({ obj }: { obj: unknown }) {
  return (
    <details className="mt-3">
      <summary className="cursor-pointer text-xs text-slate-400">Raw JSON</summary>
      <pre className="mt-2 max-h-80 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100">
        {JSON.stringify(obj, null, 2)}
      </pre>
    </details>
  );
}

export default function RunPage({ params }: { params: { id: string } }) {
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Passport");
  const [live, setLive] = useState<string | null>(null);
  const [narrating, setNarrating] = useState(false);

  async function narrate() {
    setNarrating(true);
    try {
      const r = await api.narrate(params.id);
      setLive(r.narrative);
    } catch (e) {
      setLive(`(live narration unavailable on this deployment: ${String(e)})`);
    } finally {
      setNarrating(false);
    }
  }

  useEffect(() => {
    api.getRun(params.id).then(setRun).catch((e) => setError(String(e)));
  }, [params.id]);

  if (error) return <p role="alert" className="text-decision-blocked">Could not load run: {error}</p>;
  if (!run) return <p className="text-slate-500">Loading run…</p>;

  const p = run.passport;
  const pol = run.policy;
  const bom = run.ai_bom;

  return (
    <div className="space-y-6">
      {/* 1. Candidate card */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="font-heading text-2xl font-bold text-cpl-charcoal">{run.agent_name}</h1>
            <p className="text-sm text-slate-500">
              {run.candidate_agent_id} · {run.candidate_manifest.origin}
            </p>
          </div>
          <DecisionBadge decision={run.decision} size="lg" />
        </div>
        <dl className="mt-4 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div><dt className="text-slate-400">Owner</dt><dd>{p.owner.name ?? "—"} ({p.owner.status})</dd></div>
          <div><dt className="text-slate-400">Purpose</dt><dd>{p.purpose.status}</dd></div>
          <div><dt className="text-slate-400">Autonomy</dt><dd>{run.candidate_manifest.autonomy.level}</dd></div>
          <div><dt className="text-slate-400">Trust tier</dt><dd>{p.trust_tier}</dd></div>
        </dl>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-6">
          {/* 2. Workflow rail */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-3 font-heading text-lg font-semibold">Multi-agent onboarding workflow</h2>
            <ol className="space-y-2">
              {run.events.map((e, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-cpl-blue/10 text-[10px] font-bold text-cpl-blue">
                    {i + 1}
                  </span>
                  <div>
                    <span className="font-medium text-cpl-charcoal">{e.event_type}</span>
                    <span className="ml-2 text-[11px] text-on-surface-variant">· {e.actor.id}</span>
                    <p className="text-slate-500">{e.summary}</p>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          {/* 3. Artifact workspace */}
          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div role="tablist" className="flex flex-wrap gap-1 border-b border-slate-200 p-2">
              {TABS.map((t) => (
                <button
                  key={t}
                  role="tab"
                  aria-selected={tab === t}
                  onClick={() => setTab(t)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                    tab === t ? "bg-cpl-blue text-white" : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
            <div className="space-y-3 p-5 text-sm">
              {tab === "Passport" && (
                <>
                  <Section title="ID badge">
                    <ul className="space-y-1">
                      <li>Owner: {p.owner.name ?? "—"} &lt;{p.owner.email ?? "—"}&gt; [{p.owner.status}]</li>
                      <li>Purpose: {p.purpose.declared ?? "—"} ({p.purpose.status})</li>
                      <li>Runtime: {p.runtime.framework} / {p.runtime.deployment_target}</li>
                      <li>Kill-switch: {p.kill_switch_state}</li>
                      <li>Approvals: {p.approval_requirements.join("; ") || "none"}</li>
                    </ul>
                  </Section>
                  <Raw obj={p} />
                </>
              )}
              {tab === "Résumé" && (
                <>
                  <Section title="AI Bill of Materials — declared models, tools, dependencies">
                    <p>{bom.models.length} model(s), {bom.tools.length} tool(s), {bom.data_sources.length} data source(s)</p>
                    <ul className="mt-2 space-y-1">
                      {bom.models.map((m: any, i: number) => (
                        <li key={i}>model: {m.model} ({m.provider}) — source: {m.source}, confidence: {m.confidence}</li>
                      ))}
                      {bom.tools.map((t: any, i: number) => (
                        <li key={i}>tool: {t.name} ({t.risk_tier}) — source: {t.source}, confidence: {t.confidence}</li>
                      ))}
                    </ul>
                    {bom.known_unknowns?.length ? (
                      <p className="mt-2 text-slate-500">Known unknowns: {bom.known_unknowns.join("; ")}</p>
                    ) : null}
                  </Section>
                  <Raw obj={bom} />
                </>
              )}
              {tab === "Job Description" && (
                <>
                  <Section title="Policy Envelope — boundaries & approvals">
                    <ul className="space-y-1">
                      <li>Allowed tools: {pol.tool_boundary.allowed_tools.join(", ") || "—"}</li>
                      <li>Requires approval: {pol.tool_boundary.requires_approval.join(", ") || "—"}</li>
                      <li>Denied tools: {pol.tool_boundary.denied_tools.join(", ") || "—"}</li>
                      <li>Budget: ${pol.budget_boundary.monthly_usd}/mo, on breach: {pol.budget_boundary.on_breach}</li>
                    </ul>
                    {pol.approval_rules?.length ? (
                      <ul className="mt-2 list-disc pl-5 text-slate-600">
                        {pol.approval_rules.map((r: any, i: number) => (
                          <li key={i}>{r.condition} → {r.required_approver_role} ({r.approval_mode})</li>
                        ))}
                      </ul>
                    ) : null}
                  </Section>
                  {pol.grounding_refs?.length ? (
                    <Section title="Grounded sources">
                      <ul className="space-y-1 text-xs text-on-surface-variant">
                        {pol.grounding_refs.map((g: any, i: number) => (
                          <li key={i} title={g.snippet}>
                            <span className="font-semibold text-on-surface">{g.source_id}</span>
                            {g.source_title ? ` — ${g.source_title}` : ""}
                          </li>
                        ))}
                      </ul>
                    </Section>
                  ) : null}
                  <Raw obj={pol} />
                </>
              )}
              {tab === "Background Check" && (
                <>
                  <Section title="Onboarding Validation Suite — pre-employment screening">
                    {run.validation_run.findings.length ? (
                      <ul className="space-y-3">
                        {run.validation_run.findings.map((f, i) => (
                          <li key={i} className="rounded-lg border border-slate-200 p-3">
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-bold uppercase ${SEV_CLS[f.severity] ?? ""}`}>{f.severity}</span>
                              <span className="text-xs font-semibold text-on-surface-variant">{f.test_id}</span>
                              <span className="font-medium">{f.title}</span>
                              {f.blocks_ready_decision && <span className="text-xs text-decision-blocked">blocks Ready</span>}
                            </div>
                            <p className="mt-1 text-slate-600">↳ {f.recommended_remediation}</p>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-decision-ready">No findings — all pre-employment screening checks passed.</p>
                    )}
                  </Section>
                </>
              )}
              {tab === "Personnel File" && (
                <>
                  <Section title="Evidence Bundle — hash-chained personnel record">
                    <p>Bundle: {run.evidence_bundle.bundle_id}</p>
                    <p className="break-all text-xs text-slate-500">{run.evidence_bundle.bundle_hash}</p>
                    <table className="mt-3 w-full text-left text-xs">
                      <thead className="text-slate-400"><tr><th className="pr-2">#</th><th className="pr-2">Event</th><th>Hash</th></tr></thead>
                      <tbody>
                        {run.events.map((e, i) => (
                          <tr key={i} className="border-t border-slate-100">
                            <td className="pr-2">{i}</td>
                            <td className="pr-2">{e.event_type}</td>
                            <td className="font-mono text-slate-500">{e.event_hash.slice(7, 21)}…</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <ul className="mt-3 list-disc pl-5 text-xs text-slate-500">
                      {run.evidence_bundle.limitations.map((l: string, i: number) => <li key={i}>{l}</li>)}
                    </ul>
                  </Section>
                  <div className="flex flex-wrap gap-2">
                    <a href={api.downloadUrl(run.run_id, "json")} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">Download JSON</a>
                    <a href={api.downloadUrl(run.run_id, "md")} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">Download Markdown</a>
                    <a href={api.downloadUrl(run.run_id, "pdf")} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50">Download PDF</a>
                  </div>
                </>
              )}
            </div>
          </section>
        </div>

        {/* 4. Decision panel */}
        <aside className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <DecisionBadge decision={run.decision} size="lg" />
            <div className="mt-3 text-3xl font-bold text-cpl-charcoal">
              {run.score.score}<span className="text-base font-normal text-slate-400">/100</span>
            </div>
            <div className="text-sm text-slate-500">Day-1 readiness · {run.score.band}</div>
            <div className="mt-3 space-y-1">
              {Object.entries(run.score.components).map(([k, v]) => (
                <div key={k} className="text-xs">
                  <div className="flex justify-between text-slate-500"><span>{k.replaceAll("_", " ")}</span><span>{v}</span></div>
                  <div className="h-1.5 rounded bg-slate-100"><div className="h-1.5 rounded bg-cpl-blue" style={{ width: `${Math.min(100, (v as number) * 4)}%` }} /></div>
                </div>
              ))}
            </div>
          </div>

          {(run.blockers.length > 0 || run.conditions.length > 0) && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm shadow-sm">
              {run.blockers.map((b, i) => <p key={i} className="text-decision-blocked">⛔ {b}</p>)}
              {run.conditions.map((c, i) => <p key={i} className="text-decision-conditional">• {c}</p>)}
            </div>
          )}

          <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm shadow-sm">
            <h3 className="mb-1 font-semibold">Onboarding summary</h3>
            <p className="text-slate-600">{run.narrative.headline}</p>
            {run.narrative.grounded_sources?.length ? (
              <p className="mt-2 text-xs text-slate-500">Grounded: {run.narrative.grounded_sources.join("; ")}</p>
            ) : null}
            <button
              onClick={narrate}
              disabled={narrating}
              className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-semibold text-primary hover:bg-primary/5 disabled:opacity-60"
            >
              <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
              {narrating ? "Asking Gemini…" : "Explain with Gemini (live)"}
            </button>
            {live && (
              <div className="mt-3 rounded-lg bg-primary/5 p-3">
                <div className="mb-1 inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
                  <span className="material-symbols-outlined text-[12px]">spark</span> Gemini · live (Vertex AI)
                </div>
                <p className="text-slate-700">{live}</p>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
