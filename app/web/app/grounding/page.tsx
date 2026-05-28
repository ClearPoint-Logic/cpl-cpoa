"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Side {
  method: string;
  explanation: string;
  grounding_refs: { source_id: string; source_title: string; snippet?: string }[];
}

export default function Grounding() {
  const [data, setData] = useState<{ ungrounded: Side; grounded: Side } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.grounding("grounding_required_policy_agent").then(setData).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-semibold">Grounded vs. ungrounded</h1>
        <p className="text-on-surface-variant">
          The same candidate, explained two ways. A single ungrounded model call gives a generic
          answer; the grounded multi-agent path cites specific public sources (NSA MCP CSI, NIST AI
          RMF, EU AI Act) — the multi-agent value made visible (FR-084).
        </p>
      </div>

      {error && <p role="alert" className="text-status-blocked">Could not load comparison: {error}</p>}
      {!data && !error && <p className="text-on-surface-variant">Loading comparison…</p>}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-surface-container px-3 py-1 text-xs font-semibold uppercase tracking-wider text-on-surface-variant">
              <span className="material-symbols-outlined text-[16px]">blur_on</span> Ungrounded — single call
            </div>
            <p className="text-sm text-on-surface-variant">{data.ungrounded.explanation}</p>
            <p className="mt-4 text-xs italic text-on-surface-variant">No sources cited.</p>
          </section>

          <section className="rounded-xl border-2 border-primary/30 bg-surface-container-lowest p-5">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-primary-container/40 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-primary-hover">
              <span className="material-symbols-outlined text-[16px]">hub</span> Grounded — multi-agent
            </div>
            <p className="text-sm text-on-surface">{data.grounded.explanation}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {data.grounded.grounding_refs.map((g) => (
                <span
                  key={g.source_id}
                  title={g.snippet}
                  className="inline-flex items-center gap-1 rounded-full bg-cpl-aqua/15 px-2.5 py-1 text-xs font-semibold text-on-surface ring-1 ring-cpl-aqua/40"
                >
                  <span className="material-symbols-outlined text-[14px]">link</span> {g.source_id}
                </span>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
