"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { FixtureCard } from "@/lib/types";

export default function NewRun() {
  const router = useRouter();
  const [fixtures, setFixtures] = useState<FixtureCard[]>([]);
  const [selected, setSelected] = useState("");
  const [manifest, setManifest] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listFixtures().then((f) => {
      setFixtures(f);
      if (f[0]) setSelected(f[0].name);
    }).catch((e) => setError(String(e)));
  }, []);

  async function runFixture() {
    setBusy(true); setError(null);
    try {
      const r = await api.createRun(selected);
      router.push(`/runs/${r.run_id}`);
    } catch (e) { setError(String(e)); setBusy(false); }
  }

  async function runManifest() {
    setBusy(true); setError(null);
    try {
      const body = JSON.parse(manifest);
      const res = await fetch("/api/runs", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_manifest: body }),
      });
      if (!res.ok) throw new Error(await res.text());
      const r = await res.json();
      router.push(`/runs/${r.run_id}`);
    } catch (e) { setError(String(e)); setBusy(false); }
  }

  return (
    <div className="max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold text-cpl-charcoal">Start an onboarding run</h1>
      {error && <p role="alert" className="rounded border border-decision-blocked/30 bg-decision-blocked/5 p-3 text-sm text-decision-blocked">{error}</p>}

      <section className="space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Pick a fixture</h2>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2"
        >
          {fixtures.map((f) => (
            <option key={f.name} value={f.name}>{f.agent_name} ({f.expected_decision})</option>
          ))}
        </select>
        <button onClick={runFixture} disabled={busy || !selected} className="rounded-lg bg-cpl-blue px-4 py-2 text-sm font-semibold text-white hover:bg-cpl-blue/90 disabled:opacity-60">
          {busy ? "Onboarding…" : "Run onboarding →"}
        </button>
      </section>

      <section className="space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">…or paste a candidate manifest (JSON)</h2>
        <textarea
          value={manifest}
          onChange={(e) => setManifest(e.target.value)}
          rows={10}
          placeholder='{ "candidate_agent_id": "...", "name": "...", ... }'
          className="w-full rounded-lg border border-slate-300 p-3 font-mono text-xs"
        />
        <button onClick={runManifest} disabled={busy || !manifest.trim()} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold hover:bg-slate-50 disabled:opacity-60">
          Onboard pasted manifest →
        </button>
      </section>
    </div>
  );
}
