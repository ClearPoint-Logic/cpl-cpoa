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
          RMF, EU AI Act), the multi-agent value made visible (FR-084).
        </p>
      </div>

      {error && <p role="alert" className="text-status-blocked">Could not load comparison: {error}</p>}
      {!data && !error && <p className="text-on-surface-variant">Loading comparison…</p>}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
            <h2 className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-on-surface-variant">
              Ungrounded: single model call
            </h2>
            <p className="text-sm text-on-surface-variant">{data.ungrounded.explanation}</p>
            <p className="mt-4 text-xs italic text-on-surface-variant">No sources cited.</p>
          </section>

          <section className="rounded-xl border-2 border-primary/30 bg-surface-container-lowest p-5">
            <h2 className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-primary-hover">
              Grounded: multi-agent
            </h2>
            <p className="text-sm text-on-surface">{data.grounded.explanation}</p>
            <ul className="mt-4 space-y-1 border-t border-outline-variant/30 pt-3 text-xs text-on-surface-variant">
              {data.grounded.grounding_refs.map((g) => (
                <li key={g.source_id} title={g.snippet}>
                  <span className="font-semibold text-on-surface">{g.source_id}</span>
                  {g.source_title ? <> · {g.source_title}</> : null}
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
}
