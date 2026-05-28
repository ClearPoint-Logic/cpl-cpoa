import { Fragment } from "react";
import Link from "next/link";

const PAIRS = [
  { human: "ID badge", hIcon: "badge", ai: "Agent Passport", aIcon: "smart_toy", note: "identity, owner, trust tier" },
  { human: "Job description", hIcon: "assignment", ai: "Policy Envelope", aIcon: "gavel", note: "authorized scope of action" },
  { human: "Résumé", hIcon: "description", ai: "AI Bill of Materials", aIcon: "inventory_2", note: "declared models, tools, deps" },
  { human: "Personnel file", hIcon: "folder_shared", ai: "Evidence Bundle", aIcon: "verified_user", note: "the record that follows it forward" },
];

const STACK = ["ADK", "Gemini · Vertex AI", "Google Stitch", "MCP", "Agent Engine", "Cloud Run", "Vertex AI Search"];

export default function Home() {
  return (
    <div className="space-y-14">
      <section className="relative overflow-hidden rounded-2xl border border-outline-variant/30 bg-surface-container-low px-6 py-12 sm:px-10 sm:py-16">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.035]"
          style={{ backgroundImage: "radial-gradient(circle at 2px 2px, black 1px, transparent 0)", backgroundSize: "32px 32px" }}
        />
        <div className="relative grid items-center gap-gutter lg:grid-cols-2">
          <div className="flex max-w-2xl flex-col gap-6">
            <h1 className="font-heading text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
              Hire AI agents. <br />
              <span className="text-primary">Don&apos;t just deploy code.</span>
            </h1>
            <p className="text-lg text-on-surface-variant">
              Every enterprise hires humans with an ID badge, a job description, a résumé, and a
              personnel file. AI agents are joining the workforce — and most organizations have no
              equivalent process. ClearPoint Onboarding Agent gives every new agent the same
              structured intake, with an audit-ready decision at the gate.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/agents" className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-on-primary shadow-sm transition-colors hover:bg-primary-hover">
                <span className="material-symbols-outlined text-[18px]">how_to_reg</span> Start Onboarding
              </Link>
              <Link href="/architecture" className="inline-flex items-center gap-2 rounded-lg border border-outline px-6 py-3 text-sm font-semibold text-on-surface transition-colors hover:bg-surface-container">
                <span className="material-symbols-outlined text-[18px]">account_tree</span> See the architecture
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="text-center text-xs font-semibold uppercase tracking-widest text-on-surface-variant">Human onboarding</div>
            <div className="text-center text-xs font-semibold uppercase tracking-widest text-primary">Agent equivalent</div>
            {PAIRS.map((p) => (
              <Fragment key={p.ai}>
                <div className="flex items-center gap-3 rounded-lg border border-outline-variant/30 bg-surface p-3 opacity-70 grayscale transition-all hover:opacity-100 hover:grayscale-0">
                  <span className="material-symbols-outlined text-on-surface-variant">{p.hIcon}</span>
                  <span className="text-xs font-semibold">{p.human}</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg border border-l-4 border-outline-variant/30 border-l-primary bg-surface p-3 shadow-sm transition-all hover:shadow-md">
                  <span className="material-symbols-outlined text-primary">{p.aIcon}</span>
                  <div>
                    <div className="text-xs font-semibold">{p.ai}</div>
                    <div className="text-[11px] text-on-surface-variant">{p.note}</div>
                  </div>
                </div>
              </Fragment>
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="font-heading text-xl font-semibold">Built on the Google stack</h2>
        <div className="flex flex-wrap gap-2">
          {STACK.map((s) => (
            <span key={s} className="rounded-lg bg-surface-container-lowest px-3 py-1.5 text-sm text-on-surface-variant ring-1 ring-outline-variant/40">
              {s}
            </span>
          ))}
        </div>
        <p className="max-w-2xl text-sm text-on-surface-variant">
          The onboarding decision is computed deterministically (score, caps, blockers); Gemini
          contributes summaries, rationale, and explanations. The onboarding gate is the start —
          continuous attestation is the roadmap.
        </p>
      </section>
    </div>
  );
}
