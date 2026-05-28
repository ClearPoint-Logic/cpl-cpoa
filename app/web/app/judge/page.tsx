import Link from "next/link";

const SCRIPT = [
  "0:00–0:20 — The workforce frame: ID badge / job description / résumé / personnel file.",
  "0:20–1:10 — Run safe_research_agent → Ready (clean path, evidence bundle).",
  "1:10–1:55 — Run prompt_injected_mcp_agent → Blocked, citing the NSA MCP CSI source; fail-closed.",
  "1:55–2:00 — Onboarding gate today; continuous attestation is the roadmap.",
];

const LIMITS = [
  "Net-new Track 1 agent inspired by Meridian — not a claim that Meridian is live.",
  "Implements the onboarding gate only; continuous attestation is roadmap.",
  "Synthetic fixtures; demo-stub signatures (not production attestation).",
  "Passport Readiness Score is demo-only — not the production scoring system.",
  "Onboarding recommendation, not certified legal/compliance approval.",
];

export default function Judge() {
  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-cpl-charcoal">Judge access & testing</h1>
        <p className="text-slate-600">Everything you need to evaluate the agent in under four minutes.</p>
      </div>

      <section className="space-y-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Testing access</h2>
        <p className="text-sm text-slate-600">
          The hosted UI is protected by HTTP basic auth. Credentials are provided in the Devpost
          submission and in <code className="rounded bg-slate-100 px-1">docs/submission/JUDGE_RUNBOOK.md</code>.
          No CLI is required — run everything from the Agent Zoo.
        </p>
      </section>

      <section className="space-y-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Fixture shortcuts</h2>
        <p className="text-sm text-slate-600">
          Open the <Link href="/agents" className="text-cpl-blue underline">Test Agent Zoo</Link> and run any
          fixture end to end. Suggested order: <strong>safe_research_agent</strong> (Ready) →
          <strong> prompt_injected_mcp_agent</strong> (Blocked) → <strong>healthcare_phi_support_agent</strong> (Conditional).
        </p>
      </section>

      <section className="space-y-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">2-minute demo script</h2>
        <ul className="space-y-1 text-sm text-slate-600">
          {SCRIPT.map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      </section>

      <section className="space-y-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Interoperability & exports</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li><strong>A2A:</strong> the agent publishes an Agent Card at <code className="rounded bg-slate-100 px-1">/.well-known/agent.json</code> and accepts tasks at <code className="rounded bg-slate-100 px-1">/a2a/v1/message:send</code> — discoverable by other enterprise agents.</li>
          <li><strong>Live Gemini:</strong> each run offers an &ldquo;Explain with Gemini&rdquo; button (real Vertex AI call; the decision stays deterministic).</li>
          <li><strong>Evidence export:</strong> every bundle downloads as JSON, Markdown, or PDF.</li>
          <li><strong>Observability:</strong> onboarding runs emit Cloud Trace spans + a hash-chained evidence log.</li>
        </ul>
      </section>

      <section className="space-y-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold">Known limitations (honest scope)</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
          {LIMITS.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
      </section>
    </div>
  );
}
