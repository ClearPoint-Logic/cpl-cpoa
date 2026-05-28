import { Fragment } from "react";
import Link from "next/link";

const PAIRS = [
  { human: "ID badge", hIcon: "badge", ai: "Agent Passport", aIcon: "smart_toy", note: "identity, owner, trust tier" },
  { human: "Job description", hIcon: "assignment", ai: "Policy Envelope", aIcon: "gavel", note: "authorized scope of action" },
  { human: "Résumé", hIcon: "description", ai: "AI Bill of Materials", aIcon: "inventory_2", note: "declared models, tools, deps" },
  { human: "Personnel file", hIcon: "folder_shared", ai: "Evidence Bundle", aIcon: "verified_user", note: "the record that follows it forward" },
];

const LIFECYCLE = [
  { phase: "Discover", icon: "radar", href: "/workforce", note: "Real HTTPS crawl of A2A Agent Cards; surface unmanaged shadow IT" },
  { phase: "Onboard", icon: "how_to_reg", href: "/agents", note: "Six-stage gate; deterministic Ready / Conditional / Blocked" },
  { phase: "Manage", icon: "groups", href: "/workforce", note: "HR Console: place on leave, manager handoff, role change" },
  { phase: "Govern", icon: "policy", href: "/compliance", note: "Compliance: live control mapping to NSA / NIST / EU AI Act" },
  { phase: "Operate", icon: "monitor_heart", href: "/operate", note: "Sentinel: fleet health + deterministic anomaly rules" },
  { phase: "Optimize", icon: "trending_up", href: "/optimize", note: "Talent Development: per-agent autonomy-ladder plans" },
];

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
              Enterprises hire humans with an ID badge, a job description, a résumé, and a
              personnel file. AI agents are joining the workforce with no equivalent process.
              <strong className="font-semibold text-on-surface"> ClearPoint Workforce Agent</strong>{" "}
              ships the first <strong className="font-semibold text-on-surface">six phases of AI
              Workforce Management</strong> end-to-end — discover the unmanaged agents already
              running, onboard new ones through a deterministic gate, then manage, govern,
              operate, and grow them along an explicit autonomy ladder.
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

      <section className="space-y-4">
        <div>
          <h2 className="font-heading text-xl font-semibold">The AI Workforce Management lifecycle</h2>
          <p className="mt-1 text-sm text-on-surface-variant">
            Six phases shipped end-to-end. Every phase writes into one continuous,
            hash-chained personnel file per agent.
          </p>
        </div>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {LIFECYCLE.map((p, i) => (
            <li key={p.phase}>
              <Link
                href={p.href}
                className="group flex h-full items-start gap-3 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4 transition-colors hover:border-primary/40 hover:bg-surface-container"
              >
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20">
                  <span className="material-symbols-outlined text-[20px]">{p.icon}</span>
                </span>
                <div className="min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-[10px] text-on-surface-variant">{(i + 1).toString().padStart(2, "0")}</span>
                    <h3 className="font-heading text-base font-semibold text-on-surface">{p.phase}</h3>
                  </div>
                  <p className="mt-0.5 text-xs text-on-surface-variant">{p.note}</p>
                </div>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="font-heading text-xl font-semibold">By the numbers</h2>
          <p className="mt-1 text-sm text-on-surface-variant">
            Every figure below is measurable from the deployed build — not aspiration.
          </p>
        </div>
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { k: "&lt; 5 ms", v: "Deterministic decision latency per onboarding run (CLI; sub-second incl. live Gemini narration)" },
            { k: "8 / 8", v: "Pre-Boarding fixtures decide correctly across 8 production-shaped risk archetypes" },
            { k: "5", v: "Fail-closed pre-employment-screening checks (OV-001..005)" },
            { k: "29", v: "Live regulatory-citation resolutions in the Compliance matrix (NSA MCP CSI + NIST AI RMF + EU AI Act)" },
            { k: "19 / 19", v: "NSA MCP security baseline tests pass (auth, RBAC, integrity, replay, output filter, audit)" },
            { k: "186", v: "Total tests across unit, integration, evals, and security" },
            { k: "90 %", v: "Code coverage on the gate core (cpoa/services + agents + mcp_servers + app/api)" },
            { k: "6 / 7", v: "AI Workforce Management lifecycle phases shipped; the seventh is continuous attestation" },
          ].map(({ k, v }) => (
            <div key={k} className="rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-4">
              <dt
                className="font-heading text-2xl font-semibold text-primary"
                dangerouslySetInnerHTML={{ __html: k }}
              />
              <dd className="mt-1 text-xs text-on-surface-variant">{v}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="space-y-3">
        <h2 className="font-heading text-xl font-semibold">Built on Google&apos;s agent platform</h2>
        <p className="max-w-3xl text-on-surface-variant">
          Orchestrated with the <strong className="text-on-surface">Agent Development Kit</strong>,
          reasoning with <strong className="text-on-surface">Gemini 3.5 Flash on Vertex AI</strong>,
          tools served over the <strong className="text-on-surface">Model Context Protocol</strong>,
          grounded with <strong className="text-on-surface">Vertex AI Search</strong>, designed in
          <strong className="text-on-surface"> Google Stitch</strong>, observed with
          <strong className="text-on-surface"> Cloud Trace</strong>, persisted in
          <strong className="text-on-surface"> Firestore</strong>, deployed on
          <strong className="text-on-surface"> Cloud Run</strong>, and discoverable via the
          <strong className="text-on-surface"> Agent-to-Agent (A2A)</strong> protocol.
        </p>
        <p className="max-w-3xl text-sm text-on-surface-variant">
          The onboarding decision — score, caps, blockers — is computed deterministically; Gemini
          contributes summaries, rationale, and explanations. Six lifecycle phases are shipped
          here; the seventh, continuous attestation across every running interaction, is the
          roadmap.
        </p>
      </section>
    </div>
  );
}
