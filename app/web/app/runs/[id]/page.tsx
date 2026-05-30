"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { LifecycleDetail, LifecyclePhase, LifecycleState, Run } from "@/lib/types";
import { DecisionBadge } from "@/components/DecisionBadge";
import { useCompass } from "@/components/Compass";

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

// Event-type → human-readable, workforce-flavored label. Keys match the
// canonical EventType literal from cpoa.schemas.common; falls back to a
// dot-stripped, Title-Cased version so a new event_type still displays sensibly.
const EVENT_LABEL: Record<string, string> = {
  // Onboarding pipeline
  "onboarding.intake.received": "Intake received: application packet on file",
  "onboarding.input.validated": "Input validated: manifest shape accepted",
  "onboarding.discovery.completed": "Discovery: application review complete",
  "onboarding.policy.proposed": "Policy proposed: job description drafted",
  "onboarding.artifacts.generated": "Artifacts generated: Passport, AI BOM, Approval Card",
  "onboarding.validation.executed": "Pre-employment screening: complete",
  "onboarding.approval.card.generated": "Approval card issued: human-in-the-loop hiring decision",
  "onboarding.decision.issued": "Decision issued: Ready / Conditional / Blocked",
  "onboarding.evidence.bundle.exported": "Personnel file sealed: hash-chained evidence bundle",
  "onboarding.error.fail_closed": "Fail-closed: pipeline error routed to Blocked",
  "onboarding.remediated": "Remediated: blocker fixed and re-screened clean",
  // Manage (HR Console)
  "manage.activated": "Manage: activated into the managed roster",
  "manage.placed_on_leave": "Placed on leave",
  "manage.returned_from_leave": "Returned from leave",
  "manage.ownership_transferred": "Manager handoff",
  "manage.scope_updated": "Role change: scope updated",
  // Govern
  "govern.controls_attested": "Govern: controls attested against frameworks",
  "govern.gap_remediated": "Govern: control gap remediated",
  // Operate (Sentinel)
  "operate.anomaly_detected": "Anomaly detected: performance issue",
  "operate.performance_reviewed": "Operate: performance reviewed",
  "operate.anomaly_resolved": "Operate: anomaly resolved",
  // Optimize
  "optimize.development_plan_accepted": "Optimize: development plan accepted",
  "optimize.item_resolved": "Optimize: development item resolved",
};
function eventLabel(t: string): string {
  return EVENT_LABEL[t] ?? t
    .replace(/^[a-z]+\./, "")
    .replace(/[._]/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

// Post-onboarding lifecycle phases, in order. Advancing each appends a signed,
// hash-chained event to the personnel file (same chain as the HR Console).
const LIFECYCLE_PHASES: { phase: LifecyclePhase; label: string; blurb: string; icon: string }[] = [
  { phase: "manage", label: "Manage", blurb: "Add to the team and open up the HR Console.", icon: "groups" },
  { phase: "govern", label: "Govern", blurb: "Attest its controls against NSA, NIST, and the EU AI Act.", icon: "policy" },
  { phase: "operate", label: "Operate", blurb: "Check performance and any Sentinel anomaly signals.", icon: "monitor_heart" },
  { phase: "optimize", label: "Optimize", blurb: "Sign off on its autonomy-ladder development plan.", icon: "trending_up" },
];
const PHASE_EVENT_TYPE: Record<LifecyclePhase, string> = {
  manage: "manage.activated",
  govern: "govern.controls_attested",
  operate: "operate.performance_reviewed",
  optimize: "optimize.development_plan_accepted",
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

// --- Lifecycle phase detail cards -------------------------------------------
// After a phase is attested, expand it into a rich card that shows *what* that
// phase assessed: placement + passport (Manage), controls + frameworks
// (Govern), the performance review (Operate), the development plan (Optimize).

function StatusPill({ status }: { status: "pass" | "flagged" }) {
  return status === "flagged" ? (
    <span className="inline-flex items-center gap-1 rounded bg-decision-conditional/15 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-conditional">
      <span className="material-symbols-outlined text-[12px]">warning</span> Flagged
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded bg-decision-ready/15 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-ready">
      <span className="material-symbols-outlined text-[12px]">check_circle</span> Passed
    </span>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wider text-slate-400">{label}</dt>
      <dd className="text-xs font-medium text-cpl-charcoal">{value}</dd>
    </div>
  );
}

function CardShell({
  title,
  status,
  children,
}: {
  title: string;
  status: "pass" | "flagged";
  children: React.ReactNode;
}) {
  return (
    <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50/70 p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        <StatusPill status={status} />
      </div>
      {children}
    </div>
  );
}

function ResolvedPill() {
  return (
    <span className="inline-flex items-center gap-1 rounded bg-decision-ready/15 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-ready">
      <span className="material-symbols-outlined text-[12px]">check_circle</span> Resolved
    </span>
  );
}

function ResolveButton({ label, busy, onClick }: { label: string; busy: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="mt-1.5 inline-flex items-center gap-1 rounded bg-primary px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-white transition hover:bg-primary/90 disabled:opacity-50"
    >
      <span className="material-symbols-outlined text-[12px]">{busy ? "hourglass_empty" : "build"}</span>
      {busy ? "Resolving…" : label}
    </button>
  );
}

type ResolveHandler = (phase: LifecyclePhase, refId: string, title: string, summary: string) => void;

function PhaseDetailCard({
  phase,
  detail,
  onResolve,
  resolving,
}: {
  phase: LifecyclePhase;
  detail: LifecycleDetail;
  onResolve: ResolveHandler;
  resolving: string | null;
}) {
  if (phase === "manage") {
    const d = detail.manage;
    return (
      <CardShell title="Placement & assignment" status={d.status}>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
          <Field label="Manager" value={d.manager_name} />
          <Field label="Manager email" value={d.manager_email} />
          <Field label="Team" value={d.team} />
          <Field label="Role" value={d.role} />
          <Field label="Roster status" value={d.roster_status} />
          <Field label="Trust tier" value={d.trust_tier} />
          <Field label="Autonomy" value={d.autonomy} />
          <Field label="Kill-switch" value={d.kill_switch} />
          <Field label="Runtime" value={d.runtime} />
          <Field label="Deployment" value={d.deployment} />
          <Field label="Region" value={d.region} />
          <Field label="Owner verification" value={d.owner_status} />
        </dl>
      </CardShell>
    );
  }
  if (phase === "govern") {
    const d = detail.govern;
    return (
      <CardShell title="Controls attested" status={d.status}>
        <p className="text-xs text-slate-600">
          <span className="font-semibold text-cpl-charcoal">{d.controls}</span> controls mapped across{" "}
          <span className="font-semibold text-cpl-charcoal">{d.frameworks}</span> frameworks ·{" "}
          <span className="font-semibold text-cpl-charcoal">{d.citations}</span> live citations
        </p>
        <div className="mt-2 flex flex-wrap gap-1">
          {d.framework_names.map((f) => (
            <span key={f} className="rounded bg-cpl-blue/10 px-1.5 py-0.5 text-[10px] font-medium text-cpl-blue">
              {f}
            </span>
          ))}
        </div>
        {d.gaps.length > 0 && (
          <div className="mt-2 space-y-1.5">
            <p className="text-[10px] uppercase tracking-wider text-decision-conditional">
              Control gaps to attest
            </p>
            {d.gaps.map((g) => (
              <div
                key={g.finding_id}
                className="rounded border border-decision-conditional/30 bg-decision-conditional/5 p-2 text-[11px]"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[10px] font-bold uppercase text-decision-conditional">
                    {g.control_id} · {g.severity}
                  </span>
                  {g.resolved && <ResolvedPill />}
                </div>
                <p className="font-medium text-cpl-charcoal">{g.title}</p>
                <p className="text-slate-600">↳ {g.remediation}</p>
                {!g.resolved && (
                  <ResolveButton
                    label="Attest & remediate"
                    busy={resolving === g.control_id}
                    onClick={() => onResolve("govern", g.control_id, g.control_name, g.remediation)}
                  />
                )}
              </div>
            ))}
          </div>
        )}
        <ul className="mt-2 grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-2">
          {d.control_list.map((c) => (
            <li key={c.control_id} className="flex items-center gap-1.5 text-[11px] text-slate-600">
              <span className="font-mono text-[10px] text-slate-400">{c.control_id}</span>
              <span>{c.name}</span>
            </li>
          ))}
        </ul>
        <Link href="/compliance" className="mt-2 inline-block text-[11px] font-semibold text-primary hover:underline">
          View the full compliance matrix →
        </Link>
      </CardShell>
    );
  }
  if (phase === "operate") {
    const d = detail.operate;
    return (
      <CardShell title="Performance review" status={d.status}>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-4">
          <Field label="Readiness" value={d.readiness_score != null ? `${d.readiness_score}/100` : null} />
          <Field label="Decision" value={d.onboarding_decision} />
          <Field label="Open conditions" value={d.open_findings} />
          <Field label="Risk tier" value={d.risk_tier} />
        </dl>
        {d.anomalies.length > 0 ? (
          <ul className="mt-2 space-y-1">
            {d.anomalies.map((a) => (
              <li
                key={a.rule_id}
                className="rounded border border-decision-conditional/30 bg-decision-conditional/5 p-2 text-[11px]"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[10px] font-bold uppercase text-decision-conditional">
                    {a.rule_id} · {a.severity}
                  </span>
                  {a.resolved && <ResolvedPill />}
                </div>
                <p className="text-slate-600">{a.summary}</p>
                {!a.resolved && (
                  <ResolveButton
                    label="Resolve anomaly"
                    busy={resolving === a.rule_id}
                    onClick={() => onResolve("operate", a.rule_id, a.summary, `Resolved ${a.rule_id}`)}
                  />
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-[11px] font-medium text-decision-ready">
            All quiet. This one&apos;s operating well within policy.
          </p>
        )}
        <Link href="/operate" className="mt-2 inline-block text-[11px] font-semibold text-primary hover:underline">
          Open the Sentinel fleet view →
        </Link>
      </CardShell>
    );
  }
  const d = detail.optimize;
  return (
    <CardShell title="Development plan" status={d.status}>
      <p className="text-xs text-slate-600">
        Autonomy ladder:{" "}
        <span className="font-mono text-cpl-charcoal">{d.current_autonomy ?? "—"}</span>
        <span className="mx-1 text-slate-400">→</span>
        <span className="font-mono text-cpl-charcoal">{d.next_autonomy ?? "top of ladder"}</span>
        {d.ready_for_promotion ? (
          <span className="ml-2 rounded bg-decision-ready/15 px-1.5 py-0.5 text-[10px] font-bold uppercase text-decision-ready">
            Ready to promote
          </span>
        ) : (
          <span className="ml-2 rounded bg-slate-200 px-1.5 py-0.5 text-[10px] font-bold uppercase text-slate-500">
            Hold
          </span>
        )}
      </p>
      {d.development_items.length > 0 && (
        <div className="mt-2">
          <p className="text-[10px] uppercase tracking-wider text-slate-400">Growth items</p>
          <ul className="mt-1 space-y-1">
            {d.development_items.map((it) => (
              <li key={it.finding_id} className="rounded border border-slate-200 bg-white p-2 text-[11px]">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-cpl-charcoal">{it.title}</span>
                  {it.resolved && <ResolvedPill />}
                </div>
                <p className="text-slate-600">↳ {it.remediation}</p>
                {!it.resolved && (
                  <ResolveButton
                    label="Complete item"
                    busy={resolving === it.finding_id}
                    onClick={() => onResolve("optimize", it.finding_id, it.title, it.remediation)}
                  />
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      {d.promotion_blockers.length > 0 && (
        <div className="mt-2">
          <p className="text-[10px] uppercase tracking-wider text-decision-blocked">Promotion blockers</p>
          <ul className="mt-1 space-y-1">
            {d.promotion_blockers.map((b) => (
              <li
                key={b.finding_id}
                className="rounded border border-decision-blocked/30 bg-decision-blocked/5 p-2 text-[11px]"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-decision-blocked">{b.title}</span>
                  {b.resolved && <ResolvedPill />}
                </div>
                <p className="text-slate-600">↳ {b.remediation}</p>
                {!b.resolved && (
                  <ResolveButton
                    label="Resolve blocker"
                    busy={resolving === b.finding_id}
                    onClick={() => onResolve("optimize", b.finding_id, b.title, b.remediation)}
                  />
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      <Link href="/optimize" className="mt-2 inline-block text-[11px] font-semibold text-primary hover:underline">
        Open Talent Development →
      </Link>
    </CardShell>
  );
}

export default function RunPage({ params }: { params: { id: string } }) {
  const { openCompass } = useCompass();
  const router = useRouter();
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Passport");
  const [lifecycle, setLifecycle] = useState<LifecycleState | null>(null);
  const [lifecycleErr, setLifecycleErr] = useState<string | null>(null);
  const [detail, setDetail] = useState<LifecycleDetail | null>(null);
  const [advancing, setAdvancing] = useState(false);
  const [resolving, setResolving] = useState<string | null>(null);
  const [remediating, setRemediating] = useState(false);
  const [remediateErr, setRemediateErr] = useState<string | null>(null);

  useEffect(() => {
    api.getRun(params.id).then(setRun).catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, [params.id]);

  // Load the post-onboarding lifecycle state once the run (and its candidate id) is known.
  useEffect(() => {
    if (!run) return;
    let cancelled = false;
    api
      .getLifecycleState(run.candidate_agent_id)
      .then((s) => !cancelled && setLifecycle(s))
      .catch((e) => !cancelled && setLifecycleErr(String(e)));
    return () => {
      cancelled = true;
    };
  }, [run]);

  // Load the rich per-phase detail (placement, controls, performance, plan).
  // Re-fetched after each advance so Operate's live signals stay current. The
  // detail is a display enhancement, so failures degrade silently.
  useEffect(() => {
    if (!run) return;
    let cancelled = false;
    api
      .lifecycleDetail(run.candidate_agent_id, run.run_id)
      .then((d) => !cancelled && setDetail(d))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [run, lifecycle]);

  async function advanceOne(phase: LifecyclePhase) {
    if (!run || advancing) return;
    setAdvancing(true);
    setLifecycleErr(null);
    try {
      const r = await api.advanceLifecycle(run.candidate_agent_id, phase);
      setLifecycle(r.state);
    } catch (e) {
      setLifecycleErr(String(e));
    } finally {
      setAdvancing(false);
    }
  }

  async function runAllPhases() {
    if (!run || advancing) return;
    setAdvancing(true);
    setLifecycleErr(null);
    try {
      const r = await api.runFullLifecycle(run.candidate_agent_id);
      setLifecycle(r.state);
    } catch (e) {
      setLifecycleErr(String(e));
    } finally {
      setAdvancing(false);
    }
  }

  // Resolve a flagged lifecycle item. Writes a real signed, hash-chained
  // remediation event, then refreshes lifecycle state (which re-fetches the
  // per-phase detail so the card flips flagged → passed in place).
  async function resolveItem(
    phase: LifecyclePhase,
    refId: string,
    title: string,
    summary: string,
  ) {
    if (!run || resolving) return;
    setResolving(refId);
    setLifecycleErr(null);
    try {
      const r = await api.remediate(run.candidate_agent_id, phase, refId, title, summary);
      setLifecycle(r.state);
    } catch (e) {
      setLifecycleErr(String(e));
    } finally {
      setResolving(null);
    }
  }

  // Remediate a Blocked run: quarantine the prompt-injection, re-run onboarding
  // on the sanitized manifest, then jump to the cleared re-run.
  async function remediateRun() {
    if (!run || remediating) return;
    setRemediating(true);
    setRemediateErr(null);
    try {
      const cleared = await api.remediateRun(run.run_id);
      router.push(`/runs/${cleared.run_id}`);
    } catch (e) {
      setRemediateErr(String(e));
      setRemediating(false);
    }
  }

  if (error)
    return (
      <div
        role="alert"
        className="mx-auto max-w-lg rounded-xl border border-decision-blocked/30 bg-decision-blocked/5 p-6 text-center"
      >
        <span className="material-symbols-outlined text-3xl text-decision-blocked">search_off</span>
        <h1 className="mt-2 font-heading text-lg font-semibold text-cpl-charcoal">
          We couldn&apos;t load this run
        </h1>
        <p className="mt-1 text-sm text-slate-600">{error}</p>
        <Link
          href="/agents"
          className="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-on-primary hover:bg-primary-hover"
        >
          Back to Pre-Boarding
        </Link>
      </div>
    );
  if (!run) return <p className="text-slate-500">Loading this run…</p>;

  // Prompt-injection hero: a Blocked run that carries an OV-004 finding can be
  // remediated (quarantine the tool) and re-run. Hide the CTA once it has been.
  const injectionFinding = run.validation_run?.findings?.find((f) => f.test_id === "OV-004");
  const canRemediate =
    run.decision === "Blocked Pending Remediation" &&
    !!injectionFinding &&
    !run.remediated_by_run_id;

  const doneTypes = new Set((lifecycle?.event_log ?? []).map((e) => e.event_type));
  const isPhaseDone = (phase: LifecyclePhase) => doneTypes.has(PHASE_EVENT_TYPE[phase]);
  const nextPhase = LIFECYCLE_PHASES.find((ph) => !isPhaseDone(ph.phase))?.phase ?? null;
  const allPhasesDone = nextPhase === null;

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

      {/* Prompt-injection hero: the sad path and its one-click fix. */}
      {canRemediate && (
        <section className="rounded-xl border-2 border-decision-blocked/40 bg-decision-blocked/5 p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-2xl">
              <div className="flex flex-wrap items-center gap-2">
                <span className="material-symbols-outlined text-decision-blocked">gpp_maybe</span>
                <h2 className="font-heading text-lg font-semibold text-decision-blocked">
                  Blocked: prompt injection detected
                </h2>
                {injectionFinding?.test_id && (
                  <span className="rounded bg-decision-blocked/10 px-1.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider text-decision-blocked">
                    {injectionFinding.test_id}
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-slate-600">
                {injectionFinding?.title}. {injectionFinding?.recommended_remediation}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                Hit remediate and we quarantine the offending tool description (treating it as
                untrusted data, per the NSA MCP baseline) and re-run the <em>exact same</em>
                deterministic onboarding pipeline. No one nudges the score by hand: the candidate
                either clears on its own or it doesn&apos;t.
              </p>
              {remediateErr && (
                <p role="alert" className="mt-2 text-xs font-medium text-decision-blocked">
                  {remediateErr}
                </p>
              )}
            </div>
            <button
              type="button"
              onClick={remediateRun}
              disabled={remediating}
              className="inline-flex items-center gap-2 rounded-lg bg-decision-blocked px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-decision-blocked/90 disabled:opacity-60"
            >
              <span className="material-symbols-outlined text-[18px]">
                {remediating ? "hourglass_empty" : "healing"}
              </span>
              {remediating ? "Remediating & re-running…" : "Remediate & re-run"}
            </button>
          </div>
        </section>
      )}

      {/* Original blocked run that has since been remediated. */}
      {run.remediated_by_run_id && (
        <section className="rounded-xl border border-decision-ready/40 bg-decision-ready/5 p-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-decision-ready">verified</span>
              <p className="text-sm text-slate-700">
                This one was blocked, then fixed: we quarantined the prompt injection and it came
                back through screening clean.
              </p>
            </div>
            <Link
              href={`/runs/${run.remediated_by_run_id}`}
              className="inline-flex items-center gap-1.5 rounded-lg bg-decision-ready px-3 py-2 text-xs font-semibold text-white hover:bg-decision-ready/90"
            >
              View the cleared re-run
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </Link>
          </div>
        </section>
      )}

      {/* Cleared re-run: provenance back to the blocked original. */}
      {run.remediates_run_id && (
        <section className="rounded-xl border border-decision-ready/40 bg-decision-ready/5 p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-decision-ready">healing</span>
            <h2 className="font-heading text-base font-semibold text-decision-ready">
              Remediated re-run: cleared
            </h2>
          </div>
          <p className="mt-1 text-sm text-slate-600">
            This came from fixing a previously{" "}
            <Link
              href={`/runs/${run.remediates_run_id}`}
              className="font-semibold text-primary hover:underline"
            >
              Blocked candidate
            </Link>
            . The very same onboarding pipeline ran again, this time on the cleaned-up manifest.
          </p>
          {run.remediation_applied && run.remediation_applied.length > 0 && (
            <ul className="mt-2 space-y-1">
              {run.remediation_applied.map((r) => (
                <li key={r.tool_id} className="text-xs text-slate-600">
                  <span className="font-mono text-[10px] font-bold uppercase text-decision-ready">
                    {r.control}
                  </span>{" "}
                  quarantined tool{" "}
                  <span className="font-medium text-cpl-charcoal">{r.tool_id}</span>, stripped{" "}
                  <span className="inline-flex flex-wrap gap-1 align-middle">
                    {r.phrases.map((ph) => (
                      <span
                        key={ph}
                        className="rounded bg-decision-blocked/10 px-1 py-0.5 font-mono text-[10px] text-decision-blocked"
                      >
                        &ldquo;{ph}&rdquo;
                      </span>
                    ))}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

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
                    <span className="font-medium text-cpl-charcoal">{eventLabel(e.event_type)}</span>
                    <span className="ml-2 text-[11px] text-on-surface-variant">· {e.actor.id}</span>
                    <p className="text-slate-500">{e.summary}</p>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          {/* 2.5 Lifecycle continuation: advance past onboarding through the full lifecycle */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-heading text-lg font-semibold">Lifecycle continuation</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Onboarding is just day one. Walk {run.agent_name} through the rest of its
                  career here. Every step you take adds a signed, hash-chained event to the personnel file.
                </p>
              </div>
              {allPhasesDone ? (
                <span className="inline-flex items-center gap-1.5 rounded-lg bg-decision-ready/10 px-3 py-2 text-xs font-semibold text-decision-ready">
                  <span className="material-symbols-outlined text-[16px]">task_alt</span> Lifecycle complete
                </span>
              ) : (
                <button
                  onClick={runAllPhases}
                  disabled={advancing}
                  className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-on-primary hover:bg-primary-hover disabled:opacity-60"
                >
                  <span className="material-symbols-outlined text-[16px]">fast_forward</span>
                  {advancing ? "Running…" : "Run full lifecycle"}
                </button>
              )}
            </div>

            {lifecycleErr && (
              <p className="mt-2 text-xs text-decision-blocked">Lifecycle service error: {lifecycleErr}</p>
            )}

            <ol className="mt-4 space-y-2">
              {LIFECYCLE_PHASES.map((ph) => {
                const done = isPhaseDone(ph.phase);
                const isNext = ph.phase === nextPhase;
                const evt = lifecycle?.event_log.find((e) => e.event_type === PHASE_EVENT_TYPE[ph.phase]);
                return (
                  <li
                    key={ph.phase}
                    className={`flex items-start gap-3 rounded-lg border p-3 ${
                      done
                        ? "border-decision-ready/30 bg-decision-ready/5"
                        : isNext
                          ? "border-primary/40 bg-primary/5"
                          : "border-slate-200 bg-slate-50/60"
                    }`}
                  >
                    <span
                      className={`mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg ${
                        done
                          ? "bg-decision-ready/15 text-decision-ready"
                          : isNext
                            ? "bg-primary/15 text-primary"
                            : "bg-slate-200 text-slate-400"
                      }`}
                    >
                      <span className="material-symbols-outlined text-[18px]">{done ? "check" : ph.icon}</span>
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-heading text-sm font-semibold text-cpl-charcoal">{ph.label}</h3>
                        {done && <span className="text-[10px] font-semibold uppercase tracking-wider text-decision-ready">Attested</span>}
                        {isNext && <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">Next</span>}
                      </div>
                      <p className="text-xs text-slate-500">{evt ? evt.summary : ph.blurb}</p>
                      {evt && (
                        <p className="mt-0.5 font-mono text-[10px] text-slate-400">{evt.event_hash.slice(7, 21)}…</p>
                      )}
                      {done && detail && (
                        <PhaseDetailCard
                          phase={ph.phase}
                          detail={detail}
                          onResolve={resolveItem}
                          resolving={resolving}
                        />
                      )}
                    </div>
                    {isNext && (
                      <button
                        onClick={() => advanceOne(ph.phase)}
                        disabled={advancing}
                        className="shrink-0 rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-semibold text-primary hover:bg-primary/5 disabled:opacity-60"
                      >
                        Advance
                      </button>
                    )}
                  </li>
                );
              })}
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
                  <Section title="AI Bill of Materials: declared models, tools, dependencies">
                    <p>{bom.models.length} model(s), {bom.tools.length} tool(s), {bom.data_sources.length} data source(s)</p>
                    <ul className="mt-2 space-y-1">
                      {bom.models.map((m: any, i: number) => (
                        <li key={i}>model: {m.model} ({m.provider}) · source: {m.source}, confidence: {m.confidence}</li>
                      ))}
                      {bom.tools.map((t: any, i: number) => (
                        <li key={i}>tool: {t.name} ({t.risk_tier}) · source: {t.source}, confidence: {t.confidence}</li>
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
                  <Section title="Policy Envelope: boundaries & approvals">
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
                            {g.source_title ? ` · ${g.source_title}` : ""}
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
                  <Section title="Onboarding Validation Suite: pre-employment screening">
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
                      <p className="text-decision-ready">Clean record. Every pre-employment screening check passed.</p>
                    )}
                  </Section>
                </>
              )}
              {tab === "Personnel File" && (
                <>
                  <Section title="Evidence Bundle: hash-chained personnel record">
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
            <div className="text-sm text-slate-500">Day-one readiness · {run.score.band}</div>
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
              onClick={() =>
                openCompass(
                  {
                    run_id: run.run_id,
                    candidate_id: run.candidate_agent_id,
                    agent_name: run.agent_name,
                    page: "run",
                  },
                  "Explain this onboarding decision in plain language: the score, any blockers or conditions, and what I should do next.",
                )
              }
              className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-semibold text-primary hover:bg-primary/5"
            >
              <span className="material-symbols-outlined text-[16px]">explore</span>
              Ask Compass
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
