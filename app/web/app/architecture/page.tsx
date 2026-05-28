const MAPPING: [string, string][] = [
  ["Intelligence", "Gemini via Vertex AI (deterministic decision; Gemini narrates)"],
  ["Orchestration", "Agent Development Kit (ADK) — root LlmAgent + 6 subagents"],
  ["Tools", "Model Context Protocol — secure HTTP MCP server (NSA baseline)"],
  ["Grounding / RAG", "Vertex AI Search with a local corpus fallback"],
  ["Orchestrator runtime", "Agent Engine / Agent Runtime (Cloud Run fallback)"],
  ["UI / API / MCP runtime", "Cloud Run"],
  ["UI design pipeline", "Google Stitch → Next.js + Tailwind (CPL brand tokens)"],
  ["Observability", "Cloud Logging / Trace + hash-chained evidence"],
];

const FLOW = [
  "Judge / Web UI (Stitch-sourced Next.js on Cloud Run)",
  "API gateway / web backend (Cloud Run)",
  "ADK orchestrator (Agent Engine) → Discovery · Policy · Artifact · Validation · Evidence · Explanation",
  "Secure MCP server (Cloud Run): inspect · policy · artifacts · validation · evidence",
  "Grounding (Vertex AI Search / local corpus) + Artifact store & hash-chained evidence log",
];

export default function Architecture() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-cpl-charcoal">Architecture</h1>
        <p className="text-slate-600">How the Google stack fits together for the onboarding gate.</p>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Request flow</h2>
        <ol className="space-y-2">
          {FLOW.map((f, i) => (
            <li key={i} className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-3 text-sm">
              <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-cpl-blue/10 text-xs font-bold text-cpl-blue">{i + 1}</span>
              <span>{f}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Google platform mapping</h2>
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr><th className="px-4 py-2">Need</th><th className="px-4 py-2">Google surface</th></tr>
            </thead>
            <tbody>
              {MAPPING.map(([need, surface]) => (
                <tr key={need} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium text-cpl-charcoal">{need}</td>
                  <td className="px-4 py-2 text-slate-600">{surface}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-slate-500">
          The decision (score, caps, blockers) is computed deterministically; Gemini contributes
          summaries, rationale, and explanations. If Agent Engine is unavailable, the orchestrator
          runs on Cloud Run with the same API contract.
        </p>
      </section>
    </div>
  );
}
