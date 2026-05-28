"use client";

import { useEffect, useState } from "react";

// Govern (Compass) — live control matrix mapping every enforced control to
// NSA MCP CSI / NIST AI RMF / EU AI Act passages from the grounding corpus.

interface Citation {
  id: string;
  title: string;
  snippet: string;
  source_id: string;
  source_title: string;
}

interface Control {
  control_id: string;
  name: string;
  category: string;
  summary: string;
  enforces: string[];
  citations: {
    nsa_mcp_csi: Citation[];
    nist_ai_rmf: Citation[];
    eu_ai_act: Citation[];
  };
}

interface Framework {
  key: string;
  source_id: string;
  source_title: string;
  source_url: string | null;
  passage_count: number;
  controls_citing: number;
}

interface ControlMatrix {
  controls: Control[];
  frameworks: Framework[];
  summary: {
    controls_total: number;
    frameworks_total: number;
    citations_total: number;
  };
}

export default function Govern() {
  const [matrix, setMatrix] = useState<ControlMatrix | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/govern/controls", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${r.status}`))))
      .then(setMatrix)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-heading text-2xl font-semibold">Compass</h1>
        <p className="text-on-surface-variant">
          The Govern layer of the AI Workforce Management lifecycle. Every control
          CPOA enforces — Onboarding Validation Suite checks, Policy Envelope primitives,
          the secure-MCP baseline, the hash-chained personnel file — is mapped here to
          the public regulatory and security frameworks the deployment is grounded in.
          Citations resolve live against the corpus that ships with this repo.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">
          Could not load control matrix: {error}
        </div>
      )}
      {!matrix && !error && <p className="text-on-surface-variant">Loading control matrix…</p>}

      {matrix && (
        <>
          {/* Summary strip */}
          <section className="grid gap-4 sm:grid-cols-3">
            <Metric label="Controls enforced" value={matrix.summary.controls_total} />
            <Metric label="Frameworks mapped" value={matrix.summary.frameworks_total} />
            <Metric label="Citations resolved" value={matrix.summary.citations_total} />
          </section>

          {/* Frameworks */}
          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
              Frameworks in scope
            </h2>
            <ul className="grid gap-3 md:grid-cols-3">
              {matrix.frameworks.map((f) => (
                <li
                  key={f.key}
                  className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4 text-sm"
                >
                  <h3 className="font-heading text-base font-semibold text-on-surface">
                    {f.source_id}
                  </h3>
                  <p className="mt-1 text-xs text-on-surface-variant">{f.source_title}</p>
                  <p className="mt-2 text-[11px] text-on-surface-variant">
                    {f.passage_count} passages · {f.controls_citing} controls citing
                  </p>
                </li>
              ))}
            </ul>
          </section>

          {/* Matrix */}
          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
              Control matrix
            </h2>
            <div className="space-y-3">
              {matrix.controls.map((c) => (
                <article
                  key={c.control_id}
                  className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5"
                >
                  <header className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="font-heading text-base font-semibold text-on-surface">
                      <span className="font-mono text-xs text-on-surface-variant">
                        {c.control_id}
                      </span>{" "}
                      · {c.name}
                    </h3>
                    <span className="rounded bg-primary/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary">
                      {c.category}
                    </span>
                  </header>
                  <p className="mt-2 text-sm text-on-surface-variant">{c.summary}</p>
                  <p className="mt-1 text-xs text-on-surface-variant">
                    <span className="font-semibold text-on-surface">Enforces: </span>
                    {c.enforces.join("; ")}
                  </p>

                  <div className="mt-4 grid gap-3 md:grid-cols-3">
                    <CitationColumn label="NSA MCP CSI" citations={c.citations.nsa_mcp_csi} />
                    <CitationColumn label="NIST AI RMF" citations={c.citations.nist_ai_rmf} />
                    <CitationColumn label="EU AI Act" citations={c.citations.eu_ai_act} />
                  </div>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4">
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-on-surface-variant">
        {label}
      </div>
      <div className="mt-1 font-heading text-3xl font-semibold text-on-surface">{value}</div>
    </div>
  );
}

function CitationColumn({ label, citations }: { label: string; citations: Citation[] }) {
  return (
    <div className="rounded-lg border border-outline-variant/30 bg-surface p-3 text-xs">
      <h4 className="mb-1 text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">
        {label}
      </h4>
      {citations.length === 0 ? (
        <p className="text-on-surface-variant">—</p>
      ) : (
        <ul className="space-y-2">
          {citations.map((cite) => (
            <li key={cite.id}>
              <p className="font-semibold text-on-surface">{cite.title}</p>
              <p className="text-on-surface-variant">{cite.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
