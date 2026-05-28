const MAPPING: [string, string][] = [
  ["Multi-agent orchestration", "Agent Development Kit (ADK) — root LlmAgent + six subagents"],
  ["Reasoning", "Gemini 3.5 Flash on Vertex AI (region: global)"],
  ["Tool surface", "Model Context Protocol — secure HTTP MCP server, NSA MCP security baseline"],
  ["Grounding / RAG", "Vertex AI Search (Discovery Engine) with local-corpus fallback"],
  ["Interoperability", "Agent-to-Agent (A2A) protocol — Agent Card at /.well-known/agent.json"],
  ["Persistence", "Firestore — durable runs across scale-to-zero"],
  ["Runtime", "Cloud Run (web, API, MCP) deployed via Cloud Build"],
  ["Observability", "Cloud Trace spans + SHA-256 hash-chained evidence log"],
  ["Design system", "Google Stitch → Next.js + Tailwind with Material 3 tokens"],
];

const FLOW = [
  "Judge / Web UI — Next.js on Cloud Run, designed via Google Stitch",
  "API gateway — FastAPI on Cloud Run; basic auth; A2A surface at /.well-known/agent.json",
  "ADK orchestrator — Discovery → Policy → Artifact → Validation → Evidence → Explanation",
  "MCP server (Cloud Run) — inspect · policy · artifacts · validation · evidence, NSA-baselined",
  "Grounding (Vertex AI Search / local corpus) · Firestore run store · Cloud Trace · evidence chain",
];

export default function Architecture() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-semibold">Architecture</h1>
        <p className="text-on-surface-variant">
          How the AI Workforce Management onboarding gate is composed on Google&apos;s agent platform.
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Request flow
        </h2>
        <ol className="space-y-2">
          {FLOW.map((f, i) => (
            <li
              key={i}
              className="flex items-start gap-3 rounded-lg border border-outline-variant/40 bg-surface-container-lowest p-3 text-sm"
            >
              <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-primary/10 text-[11px] font-bold text-primary">
                {i + 1}
              </span>
              <span className="text-on-surface">{f}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Google platform mapping
        </h2>
        <div className="overflow-hidden rounded-xl border border-outline-variant/40 bg-surface-container-lowest">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-container text-on-surface-variant">
              <tr>
                <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wider">Capability</th>
                <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wider">Google product</th>
              </tr>
            </thead>
            <tbody>
              {MAPPING.map(([need, surface]) => (
                <tr key={need} className="border-t border-outline-variant/30">
                  <td className="px-4 py-2 font-medium text-on-surface">{need}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{surface}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-on-surface-variant">
          The onboarding decision (score, caps, blockers, final disposition) is computed
          deterministically from §11 schemas. Gemini contributes summaries, rationale, and
          explanations only — so the gate is reliable, reproducible, and audit-defensible.
        </p>
      </section>
    </div>
  );
}
