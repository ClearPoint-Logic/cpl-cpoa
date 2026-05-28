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

// Layered architecture: top → bottom is the request path. Every node is a Google
// Cloud product or open protocol, so the diagram doubles as the platform mapping.
interface Node {
  name: string;
  note: string;
  icon: string;
}
interface Layer {
  label: string;
  caption: string;
  products: string[];
  nodes: Node[];
}

const LAYERS: Layer[] = [
  {
    label: "Presentation",
    caption: "Judge-facing console and the in-platform advisor",
    products: ["Cloud Run", "Google Stitch"],
    nodes: [
      { name: "Next.js Web UI", note: "lifecycle console", icon: "web" },
      { name: "Compass advisor", note: "natural-language slide-over", icon: "explore" },
    ],
  },
  {
    label: "Gateway & protocol",
    caption: "Authenticated entry point and agent interoperability surface",
    products: ["Cloud Run", "A2A"],
    nodes: [
      { name: "FastAPI gateway", note: "auth · rate limit · audit log", icon: "api" },
      { name: "A2A Agent Card", note: "/.well-known/agent.json", icon: "hub" },
    ],
  },
  {
    label: "Agent orchestration",
    caption: "ADK root orchestrator coordinating six specialist subagents, reasoning on Gemini",
    products: ["Agent Development Kit", "Gemini 3.5 Flash · Vertex AI"],
    nodes: [
      { name: "Discovery", note: "intake review", icon: "radar" },
      { name: "Policy", note: "scope envelope", icon: "gavel" },
      { name: "Artifact", note: "passport · BOM", icon: "inventory_2" },
      { name: "Validation", note: "screening suite", icon: "fact_check" },
      { name: "Evidence", note: "hash-chained file", icon: "verified_user" },
      { name: "Explanation", note: "grounded narrative", icon: "menu_book" },
    ],
  },
  {
    label: "Tools & grounding",
    caption: "Secured tool surface and retrieval over the regulatory corpus",
    products: ["Model Context Protocol", "Vertex AI Search"],
    nodes: [
      { name: "MCP server", note: "5 tools · NSA baseline", icon: "build" },
      { name: "Vertex AI Search", note: "grounding + local fallback", icon: "search" },
    ],
  },
  {
    label: "State, trust & observability",
    caption: "Durable runs, cryptographic provenance, and end-to-end tracing",
    products: ["Firestore", "Cloud KMS", "Cloud Trace"],
    nodes: [
      { name: "Firestore", note: "runs + lifecycle state", icon: "database" },
      { name: "Evidence chain", note: "SHA-256 + KMS signing", icon: "lock" },
      { name: "Cloud Trace", note: "span-level observability", icon: "timeline" },
    ],
  },
];

export default function Architecture() {
  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-heading text-2xl font-semibold">Architecture</h1>
        <p className="text-on-surface-variant">
          How the AI Workforce Management onboarding gate is composed on Google&apos;s agent platform.
          Top-to-bottom is the request path — and every box is a Google Cloud product or open protocol.
        </p>
      </div>

      {/* Visual platform diagram */}
      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Platform diagram
        </h2>
        <div className="rounded-2xl border border-outline-variant/40 bg-surface-container-lowest p-4 sm:p-6">
          <div className="flex flex-col gap-0">
            {LAYERS.map((layer, i) => (
              <div key={layer.label}>
                <LayerCard layer={layer} />
                {i < LAYERS.length - 1 && (
                  <div className="flex justify-center py-1.5" aria-hidden>
                    <span className="material-symbols-outlined text-[20px] text-primary/50">arrow_downward</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Cross-cutting platform agents */}
          <div className="mt-5 rounded-xl border border-dashed border-primary/40 bg-primary/[0.04] p-4">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-primary">visibility</span>
              <h3 className="font-heading text-sm font-semibold text-on-surface">Platform agents — cross-cutting</h3>
            </div>
            <p className="mt-1 text-xs text-on-surface-variant">
              <strong className="text-on-surface">Compass</strong> reads across every layer to advise in natural
              language and act on confirmation. <strong className="text-on-surface">Sentinel</strong> watches the
              active roster in the background and surfaces anomalies up to Compass and the operator.
            </p>
          </div>
        </div>
        <p className="text-sm text-on-surface-variant">
          The onboarding decision (score, caps, blockers, final disposition) is computed
          deterministically from §11 schemas. Gemini contributes summaries, rationale, and
          explanations only — so the gate is reliable, reproducible, and audit-defensible.
        </p>
      </section>

      {/* Google platform mapping table */}
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
      </section>
    </div>
  );
}

function LayerCard({ layer }: { layer: Layer }) {
  return (
    <div className="rounded-xl border border-outline-variant/50 border-l-4 border-l-primary bg-surface p-4 shadow-sm">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-on-surface">
            {layer.label}
          </h3>
          <p className="text-xs text-on-surface-variant">{layer.caption}</p>
        </div>
        <div className="flex flex-wrap gap-1">
          {layer.products.map((p) => (
            <span
              key={p}
              className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-primary"
            >
              {p}
            </span>
          ))}
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {layer.nodes.map((n) => (
          <div
            key={n.name}
            className="flex min-w-[8.5rem] flex-1 items-center gap-2 rounded-lg border border-outline-variant/40 bg-surface-container-lowest px-3 py-2"
          >
            <span className="material-symbols-outlined text-[18px] text-primary">{n.icon}</span>
            <div className="min-w-0">
              <div className="truncate text-xs font-semibold text-on-surface">{n.name}</div>
              <div className="truncate text-[11px] text-on-surface-variant">{n.note}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
