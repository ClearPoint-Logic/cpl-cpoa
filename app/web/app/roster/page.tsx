"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { DiscoveredAgent, DiscoveryScanResult, LifecycleAction, LifecycleState } from "@/lib/types";

// Roster = the Manage phase of the AI Workforce lifecycle. Governed agents on
// the active roster — each carries a current Passport, Policy Envelope, AI Bill
// of Materials, and a hash-chained Personnel File. The HR Console appends a real
// evidence event for every action (leave, return, manager handoff, role change).

export default function Roster() {
  const [scan, setScan] = useState<DiscoveryScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const r = await api.discoveryScan();
      setScan(r);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onboarded = useMemo(
    () => scan?.results.filter((r) => r.status === "known") ?? [],
    [scan],
  );

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-heading text-2xl font-semibold">Roster</h1>
        <p className="max-w-3xl text-on-surface-variant">
          The <strong className="text-on-surface">Manage</strong> phase. Governed agents on the
          active roster, each carrying a current Passport, Policy Envelope, AI Bill of Materials,
          and a hash-chained Personnel File. Use the HR Console to place an agent on leave, hand
          off to a new manager, or update its role. Every action appends a real evidence event to
          the agent&apos;s personnel file. New hires arrive from{" "}
          <Link href="/agents" className="text-primary underline">Pre-Boarding</Link>.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-on-surface-variant">
            {onboarded.length} governed {onboarded.length === 1 ? "agent" : "agents"} on the active roster.
          </p>
          <button
            onClick={load}
            disabled={loading}
            className="rounded-lg border border-outline px-3 py-1.5 text-sm font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
          >
            {loading ? "Refreshing…" : "Refresh roster"}
          </button>
        </div>
        {onboarded.length === 0 && !loading ? (
          <p className="text-on-surface-variant">No governed agents detected on the roster.</p>
        ) : (
          <ul className="grid gap-4">
            {onboarded.map((a) => (
              <OnboardedAgentCard key={a.endpoint} agent={a} />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function OnboardedAgentCard({ agent }: { agent: DiscoveredAgent }) {
  const candidateId = agent.candidate_agent_id ?? "";
  const [state, setState] = useState<LifecycleState | null>(null);
  const [busy, setBusy] = useState<LifecycleAction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showLog, setShowLog] = useState(false);

  useEffect(() => {
    if (!candidateId) return;
    api.getLifecycleState(candidateId).then(setState).catch((e) => setError(String(e)));
  }, [candidateId]);

  async function act(action: LifecycleAction, payload: Record<string, unknown>) {
    setBusy(action);
    setError(null);
    try {
      const r = await api.applyLifecycleAction(candidateId, action, payload);
      setState(r.state);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  function promptAndHandoff() {
    const v = window.prompt("New owner email:");
    if (v && v.includes("@")) act("manager_handoff", { new_owner_email: v });
  }

  function promptAndPlaceOnLeave() {
    const v = window.prompt("Reason for placing on leave (will be recorded):", "");
    act("place_on_leave", { reason: v ?? "" });
  }

  function promptAndReturn() {
    const v = window.prompt("Return note (will be recorded):", "");
    act("return_from_leave", { reason: v ?? "" });
  }

  const status = state?.status ?? "active";
  const onLeave = status === "on_leave";
  const owner = state?.owner_email ?? agent.matched_registry_entry?.owner_email ?? "—";

  return (
    <li
      className={`rounded-xl border-2 p-5 text-sm ${
        onLeave
          ? "border-decision-conditional/40 bg-decision-conditional/5"
          : "border-decision-ready/30 bg-decision-ready/5"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="font-heading text-base font-semibold text-on-surface">
            {agent.agent_card?.name ?? candidateId}
          </h3>
          <p className="text-xs text-on-surface-variant">
            {candidateId} · {agent.matched_registry_entry?.origin}
          </p>
        </div>
        <span
          className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
            onLeave
              ? "bg-decision-conditional/15 text-decision-conditional"
              : "bg-decision-ready/15 text-decision-ready"
          }`}
        >
          {onLeave ? "On leave" : "On staff"}
        </span>
      </div>

      <p className="mt-2 text-xs text-on-surface-variant">{agent.agent_card?.description}</p>

      <dl className="mt-3 grid gap-x-6 gap-y-1 text-xs text-on-surface-variant sm:grid-cols-2">
        <div>
          <dt className="inline font-semibold text-on-surface">Manager: </dt>
          <dd className="inline">{owner}</dd>
        </div>
        {state?.updated_at && (
          <div>
            <dt className="inline font-semibold text-on-surface">Updated: </dt>
            <dd className="inline">{state.updated_at}</dd>
          </div>
        )}
      </dl>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        {onLeave ? (
          <button
            onClick={promptAndReturn}
            disabled={busy !== null}
            className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-on-primary hover:bg-primary-hover disabled:opacity-60"
          >
            {busy === "return_from_leave" ? "Returning…" : "Return from leave"}
          </button>
        ) : (
          <button
            onClick={promptAndPlaceOnLeave}
            disabled={busy !== null}
            className="rounded-lg border border-outline px-3 py-1.5 text-xs font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
          >
            {busy === "place_on_leave" ? "Placing on leave…" : "Place on leave"}
          </button>
        )}
        <button
          onClick={promptAndHandoff}
          disabled={busy !== null}
          className="rounded-lg border border-outline px-3 py-1.5 text-xs font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
        >
          {busy === "manager_handoff" ? "Handing off…" : "Manager handoff"}
        </button>
        <button
          onClick={() => act("role_change", { scope_changes: { reviewed_at: new Date().toISOString() } })}
          disabled={busy !== null}
          className="rounded-lg border border-outline px-3 py-1.5 text-xs font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
        >
          {busy === "role_change" ? "Updating…" : "Role change (review)"}
        </button>
        {state && state.event_log.length > 0 && (
          <button
            onClick={() => setShowLog((v) => !v)}
            className="rounded-lg px-2 py-1.5 text-xs font-semibold text-primary hover:underline"
          >
            {showLog ? "Hide" : "Show"} personnel-file events ({state.event_log.length})
          </button>
        )}
      </div>

      {showLog && state?.event_log.length ? (
        <ol className="mt-3 space-y-1 border-t border-outline-variant/40 pt-3 text-xs">
          {state.event_log.map((evt) => (
            <li key={evt.event_id} className="flex items-start gap-2">
              <span className="font-mono text-[10px] text-on-surface-variant">
                {evt.timestamp.slice(0, 19).replace("T", " ")}
              </span>
              <span className="font-semibold text-on-surface">{evt.event_type}</span>
              <span className="text-on-surface-variant">{evt.summary}</span>
            </li>
          ))}
        </ol>
      ) : null}

      {error && (
        <p role="alert" className="mt-2 text-xs text-decision-blocked">
          {error}
        </p>
      )}
    </li>
  );
}
