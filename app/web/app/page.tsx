import Link from "next/link";

const PAIRS = [
  { human: "ID badge", ai: "Agent Passport", desc: "identity, owner, trust tier" },
  { human: "Job description", ai: "Policy Envelope", desc: "authorized scope of action" },
  { human: "Résumé", ai: "AI Bill of Materials", desc: "declared models, tools, dependencies" },
  { human: "Personnel file", ai: "Evidence Bundle", desc: "the record that follows it forward" },
];

const STACK = [
  "ADK", "Gemini (Vertex AI)", "Google Stitch", "MCP", "Agent Engine", "Cloud Run", "Vertex AI Search",
];

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="space-y-4">
        <span className="inline-block rounded-full bg-cpl-blue/10 px-3 py-1 text-xs font-semibold text-cpl-blue">
          Google for Startups AI Agents Challenge · Track 1 — Build
        </span>
        <h1 className="max-w-3xl text-4xl font-bold leading-tight text-cpl-charcoal">
          Hire AI agents into the workforce — with a passport, a job description, a résumé, and a
          personnel file at the gate.
        </h1>
        <p className="max-w-2xl text-lg text-slate-600">
          Every enterprise has a hiring process for humans. AI agents are joining the workforce —
          and most organizations have no equivalent process for them. ClearPoint Onboarding Agent
          gives every new agent the same structured intake before it does any work.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            href="/agents"
            className="rounded-lg bg-cpl-blue px-5 py-2.5 font-semibold text-white shadow-sm hover:bg-cpl-blue/90"
          >
            Start Onboarding →
          </Link>
          <Link
            href="/architecture"
            className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 font-semibold text-cpl-charcoal hover:bg-slate-50"
          >
            See the architecture
          </Link>
        </div>
      </section>

      <section aria-labelledby="grid-title" className="space-y-4">
        <h2 id="grid-title" className="text-xl font-semibold text-cpl-charcoal">
          The workforce frame
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {PAIRS.map((p) => (
            <div key={p.ai} className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="w-28 shrink-0 text-sm font-medium text-slate-500">{p.human}</div>
              <div className="text-cpl-aqua" aria-hidden>→</div>
              <div>
                <div className="font-heading font-semibold text-cpl-charcoal">{p.ai}</div>
                <div className="text-sm text-slate-500">{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-cpl-charcoal">Built on the Google stack</h2>
        <div className="flex flex-wrap gap-2">
          {STACK.map((s) => (
            <span key={s} className="rounded-md bg-white px-3 py-1.5 text-sm text-slate-700 ring-1 ring-slate-200">
              {s}
            </span>
          ))}
        </div>
        <p className="max-w-2xl text-sm text-slate-500">
          The onboarding decision is computed deterministically; Gemini contributes summaries,
          rationale, and explanations. The onboarding gate is the start — continuous attestation is
          the roadmap.
        </p>
      </section>
    </div>
  );
}
