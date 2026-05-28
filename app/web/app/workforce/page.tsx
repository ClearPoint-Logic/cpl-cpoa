"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { DiscoveredAgent, DiscoveryScanResult, FixtureCard } from "@/lib/types";

// Discover phase of the AI Workforce Management lifecycle.
//
// Three tabs: Discovered (unmanaged / shadow IT — real A2A crawl results),
// Pre-Boarding (candidates awaiting the onboarding gate), Onboarded (governed
// agents from the registry). Each section uses workforce/HR vocabulary; the
// crawl itself is a real HTTP scan of A2A Agent Cards.

type Tab = "Discovered" | "Pre-Boarding" | "Onboarded";

export default function Workforce() {
  const [scan, setScan] = useState<DiscoveryScanResult | null>(null);
  const [fixtures, setFixtures] = useState<FixtureCard[]>([]);
  const [tab, setTab] = useState<Tab>("Discovered");
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);

  async function runScan() {
    setScanning(true);
    setError(null);
    try {
      const r = await api.discoveryScan();
      setScan(r);
    } catch (e) {
      setError(String(e));
    } finally {
      setScanning(false);
    }
  }

  useEffect(() => {
    runScan();
    api.listFixtures().then(setFixtures).catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const unmanaged = useMemo(
    () => scan?.results.filter((r) => r.status === "unknown") ?? [],
    [scan],
  );
  const onboarded = useMemo(
    () => scan?.results.filter((r) => r.status === "known") ?? [],
    [scan],
  );
  const unreachable = useMemo(
    () => scan?.results.filter((r) => r.status === "unreachable" || r.status === "invalid") ?? [],
    [scan],
  );

  const counts = {
    Discovered: unmanaged.length,
    "Pre-Boarding": fixtures.length,
    Onboarded: onboarded.length,
  };

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-heading text-2xl font-semibold">Workforce</h1>
        <p className="text-on-surface-variant">
          The AI workforce census. <strong className="text-on-surface">Discovered</strong> agents
          are operating in the environment without a Passport — shadow IT, found via a real
          Agent-to-Agent (A2A) directory crawl. <strong className="text-on-surface">Pre-Boarding</strong>{" "}
          holds candidates awaiting the gate. <strong className="text-on-surface">Onboarded</strong>{" "}
          are governed agents on the active roster.
        </p>
      </header>

      {/* Top-line metrics */}
      <section className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Discovered (unmanaged)" value={counts.Discovered} tone="warn" />
        <MetricCard label="Pre-Boarding" value={counts["Pre-Boarding"]} tone="info" />
        <MetricCard label="Onboarded" value={counts.Onboarded} tone="ok" />
      </section>

      {/* Tabs */}
      <div role="tablist" className="flex flex-wrap gap-1 border-b border-outline-variant/40">
        {(["Discovered", "Pre-Boarding", "Onboarded"] as Tab[]).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`rounded-t-md px-4 py-2 text-sm font-medium ${
              tab === t
                ? "border-b-2 border-primary text-primary"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {t}{" "}
            <span className="ml-1 text-xs text-on-surface-variant">({counts[t]})</span>
          </button>
        ))}
      </div>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}

      {/* Tab contents */}
      {tab === "Discovered" && (
        <DiscoveredSection
          agents={unmanaged}
          unreachable={unreachable}
          scope={scan?.scope}
          scanning={scanning}
          onRescan={runScan}
        />
      )}
      {tab === "Pre-Boarding" && <PreBoardingSection fixtures={fixtures} />}
      {tab === "Onboarded" && <OnboardedSection agents={onboarded} />}
    </div>
  );
}

function MetricCard({ label, value, tone }: { label: string; value: number; tone: "ok" | "warn" | "info" }) {
  const cls = tone === "warn"
    ? "border-decision-blocked/30 bg-decision-blocked/5"
    : tone === "ok"
    ? "border-decision-ready/30 bg-decision-ready/5"
    : "border-outline-variant/40 bg-surface-container-lowest";
  return (
    <div className={`rounded-xl border p-4 ${cls}`}>
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-on-surface-variant">{label}</div>
      <div className="mt-1 font-heading text-3xl font-semibold text-on-surface">{value}</div>
    </div>
  );
}

function DiscoveredSection({
  agents,
  unreachable,
  scope,
  scanning,
  onRescan,
}: {
  agents: DiscoveredAgent[];
  unreachable: DiscoveredAgent[];
  scope: string | undefined;
  scanning: boolean;
  onRescan: () => void;
}) {
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="max-w-3xl text-sm text-on-surface-variant">
          Agents found via real HTTP crawl of <code className="rounded bg-surface-container px-1 text-on-surface">/.well-known/agent.json</code>{" "}
          endpoints across the A2A directory. Any agent not in the governed registry surfaces
          here as <strong className="text-on-surface">shadow IT</strong> — no Passport, no Policy
          Envelope, no Evidence Bundle, operating outside the gate.
        </p>
        <button
          onClick={onRescan}
          disabled={scanning}
          className="rounded-lg border border-outline px-3 py-1.5 text-sm font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
        >
          {scanning ? "Scanning…" : "Re-scan directory"}
        </button>
      </div>

      {agents.length === 0 && !scanning ? (
        <p className="text-decision-ready">No unmanaged agents detected.</p>
      ) : (
        <ul className="space-y-3">
          {agents.map((a) => (
            <li
              key={a.endpoint}
              className="rounded-xl border-2 border-decision-blocked/30 bg-surface-container-lowest p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-heading text-lg font-semibold text-on-surface">
                    {a.agent_card?.name ?? a.candidate_agent_id}
                  </h3>
                  <p className="text-xs text-on-surface-variant">
                    {a.candidate_agent_id} ·{" "}
                    <code className="text-[11px]">{a.endpoint}</code>
                  </p>
                </div>
                <span className="rounded bg-decision-blocked/10 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider text-decision-blocked">
                  Shadow IT
                </span>
              </div>

              <p className="mt-2 text-sm text-on-surface-variant">
                {a.agent_card?.description ?? "No description provided."}
              </p>

              <dl className="mt-3 grid gap-x-6 gap-y-1 text-xs text-on-surface-variant sm:grid-cols-2">
                {a.agent_card?.metadata?.owner && (
                  <div>
                    <dt className="inline font-semibold text-on-surface">Owner: </dt>
                    <dd className="inline">{a.agent_card.metadata.owner}</dd>
                  </div>
                )}
                {a.agent_card?.metadata?.team && (
                  <div>
                    <dt className="inline font-semibold text-on-surface">Team: </dt>
                    <dd className="inline">{a.agent_card.metadata.team}</dd>
                  </div>
                )}
                {a.agent_card?.metadata?.deployment && (
                  <div>
                    <dt className="inline font-semibold text-on-surface">Deployment: </dt>
                    <dd className="inline">{a.agent_card.metadata.deployment}</dd>
                  </div>
                )}
                {a.agent_card?.metadata?.first_seen && (
                  <div>
                    <dt className="inline font-semibold text-on-surface">First seen: </dt>
                    <dd className="inline">{a.agent_card.metadata.first_seen}</dd>
                  </div>
                )}
              </dl>

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <Link
                  href="/agents"
                  className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-on-primary hover:bg-primary-hover"
                >
                  Send to Pre-Boarding →
                </Link>
                <span className="text-[11px] text-on-surface-variant">
                  Routes this agent into the onboarding gate (Passport + Policy + Evidence)
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {unreachable.length > 0 && (
        <details className="rounded-lg border border-outline-variant/40 bg-surface-container-lowest p-3 text-xs text-on-surface-variant">
          <summary className="cursor-pointer font-semibold">
            Unreachable / invalid endpoints ({unreachable.length})
          </summary>
          <ul className="mt-2 space-y-1">
            {unreachable.map((u) => (
              <li key={u.endpoint}>
                <code>{u.endpoint}</code> — {u.error}
              </li>
            ))}
          </ul>
        </details>
      )}

      {scope && (
        <p className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-3 text-xs italic text-on-surface-variant">
          <span className="font-semibold not-italic">Honest scope:</span> {scope}
        </p>
      )}
    </section>
  );
}

function PreBoardingSection({ fixtures }: { fixtures: FixtureCard[] }) {
  return (
    <section className="space-y-3">
      <p className="text-sm text-on-surface-variant">
        Candidates awaiting their first day. Each is exercised end-to-end through the
        Onboarding gate from the <Link href="/agents" className="text-primary underline">Pre-Boarding</Link>{" "}
        roster.
      </p>
      <ul className="grid gap-3 md:grid-cols-2">
        {fixtures.map((f) => (
          <li
            key={f.name}
            className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4 text-sm"
          >
            <div className="font-heading text-base font-semibold text-on-surface">{f.agent_name}</div>
            <p className="mt-1 line-clamp-3 text-xs text-on-surface-variant">{f.business_story}</p>
            <p className="mt-2 text-[11px] text-on-surface-variant">
              Expected: <span className="font-semibold text-on-surface">{f.expected_decision}</span>{" "}
              · Tier: {f.tier}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

function OnboardedSection({ agents }: { agents: DiscoveredAgent[] }) {
  return (
    <section className="space-y-3">
      <p className="text-sm text-on-surface-variant">
        Governed agents on the active roster — each carries a current Passport, Policy Envelope,
        AI Bill of Materials, and a hash-chained Personnel File. Day-to-day actions (place on
        leave, manager handoff, role change) live in the HR Console.
      </p>
      {agents.length === 0 ? (
        <p className="text-on-surface-variant">No governed agents detected in this scan.</p>
      ) : (
        <ul className="grid gap-3 md:grid-cols-2">
          {agents.map((a) => (
            <li
              key={a.endpoint}
              className="rounded-xl border border-decision-ready/30 bg-decision-ready/5 p-4 text-sm"
            >
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-heading text-base font-semibold text-on-surface">
                  {a.agent_card?.name ?? a.candidate_agent_id}
                </h3>
                <span className="rounded bg-decision-ready/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-decision-ready">
                  On staff
                </span>
              </div>
              <p className="mt-1 text-xs text-on-surface-variant">
                {a.candidate_agent_id} · {a.matched_registry_entry?.origin}
              </p>
              <p className="mt-2 text-xs text-on-surface-variant">
                {a.agent_card?.description}
              </p>
              {a.matched_registry_entry?.owner_email && (
                <p className="mt-2 text-[11px] text-on-surface-variant">
                  <span className="font-semibold text-on-surface">Owner: </span>
                  {a.matched_registry_entry.owner_email}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
