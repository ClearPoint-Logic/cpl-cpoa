"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { DiscoveredAgent, DiscoveryScanResult } from "@/lib/types";

// Hire = the Discover phase of the AI Workforce lifecycle. A real HTTP crawl of
// A2A Agent Cards surfaces agents operating without a Passport (shadow IT) so
// they can be routed into the onboarding gate. Onboarding candidates live on
// Pre-Boarding; the governed roster + HR Console live on the Roster (Manage) page.

export default function Hire() {
  const [scan, setScan] = useState<DiscoveryScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [lastScanned, setLastScanned] = useState<string | null>(null);

  async function runScan() {
    setScanning(true);
    setError(null);
    try {
      const r = await api.discoveryScan();
      setScan(r);
      setLastScanned(new Date().toLocaleTimeString());
    } catch (e) {
      setError(String(e));
    } finally {
      setScanning(false);
    }
  }

  useEffect(() => {
    runScan();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const unmanaged = useMemo(
    () => scan?.results.filter((r) => r.status === "unknown") ?? [],
    [scan],
  );
  const governed = useMemo(
    () => scan?.results.filter((r) => r.status === "known") ?? [],
    [scan],
  );
  const unreachable = useMemo(
    () => scan?.results.filter((r) => r.status === "unreachable" || r.status === "invalid") ?? [],
    [scan],
  );

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-heading text-2xl font-semibold">Hire</h1>
        <p className="max-w-3xl text-on-surface-variant">
          This is the <strong className="text-on-surface">Discover</strong> phase. We crawl your
          Agent-to-Agent (A2A) directory for real and turn up agents that are already working
          without a Passport: your{" "}
          <strong className="text-on-surface">shadow IT</strong>. Found one you want? Send it
          straight to the hiring gate. Put it through onboarding on{" "}
          <Link href="/agents" className="text-primary underline">Pre-Boarding</Link>, then manage
          your governed team on the{" "}
          <Link href="/roster" className="text-primary underline">Roster</Link>.
        </p>
      </header>

      {/* Top-line metrics */}
      <section className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Found, unmanaged" value={unmanaged.length} tone="warn" />
        <MetricCard label="Already on the books" value={governed.length} tone="ok" />
        <MetricCard label="Endpoints scanned" value={scan?.summary.scanned ?? 0} tone="info" />
      </section>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          {error}
        </div>
      )}

      <DiscoveredSection
        agents={unmanaged}
        unreachable={unreachable}
        scope={scan?.scope}
        scanning={scanning}
        lastScanned={lastScanned}
        onRescan={runScan}
      />
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
  lastScanned,
  onRescan,
}: {
  agents: DiscoveredAgent[];
  unreachable: DiscoveredAgent[];
  scope: string | undefined;
  scanning: boolean;
  lastScanned: string | null;
  onRescan: () => void;
}) {
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="max-w-3xl text-sm text-on-surface-variant">
          These are real agents, picked up by crawling the{" "}
          <code className="rounded bg-surface-container px-1 text-on-surface">/.well-known/agent.json</code>{" "}
          endpoints across your A2A directory. Anything that isn&apos;t already in the governed
          registry shows up here as <strong className="text-on-surface">shadow IT</strong>: no
          Passport, no Policy Envelope, no Evidence Bundle, working outside the gate.
        </p>
        <div className="flex flex-col items-end gap-1">
          <button
            onClick={onRescan}
            disabled={scanning}
            className="rounded-lg border border-outline px-3 py-1.5 text-sm font-semibold text-on-surface hover:bg-surface-container disabled:opacity-60"
          >
            {scanning ? "Scanning…" : "Re-scan directory"}
          </button>
          <span className="text-[11px] text-on-surface-variant" aria-live="polite">
            {scanning
              ? "Crawling /.well-known/agent.json endpoints…"
              : lastScanned
              ? `Last crawl ${lastScanned}`
              : ""}
          </span>
        </div>
      </div>

      {agents.length === 0 && !scanning ? (
        <p className="text-decision-ready">All clear. Every agent out there is already accounted for.</p>
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
                {a.agent_card?.description ?? "No description on file."}
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
                  href={`/agents?from=discovery&agent=${encodeURIComponent(a.candidate_agent_id)}&name=${encodeURIComponent(a.agent_card?.name ?? a.candidate_agent_id)}`}
                  className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-on-primary hover:bg-primary-hover"
                >
                  Send to Pre-Boarding →
                </Link>
                <span className="text-[11px] text-on-surface-variant">
                  Routes it to the onboarding gate — Passport, Policy, and Evidence
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
                <code>{u.endpoint}</code>: {u.error}
              </li>
            ))}
          </ul>
        </details>
      )}

      {scope && (
        <p className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-3 text-xs italic text-on-surface-variant">
          <span className="font-semibold not-italic">Straight talk on scope:</span> {scope}
        </p>
      )}
    </section>
  );
}
