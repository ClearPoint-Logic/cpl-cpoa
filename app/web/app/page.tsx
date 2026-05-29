import { Fragment } from "react";
import Link from "next/link";

const PAIRS = [
  { human: "ID badge", hIcon: "badge", ai: "Agent Passport", aIcon: "smart_toy", note: "who it is, who owns it, how far it's trusted" },
  { human: "Job description", hIcon: "assignment", ai: "Policy Envelope", aIcon: "gavel", note: "exactly what it's allowed to do" },
  { human: "Résumé", hIcon: "description", ai: "AI Bill of Materials", aIcon: "inventory_2", note: "the models, tools, and dependencies it brings" },
  { human: "Personnel file", hIcon: "folder_shared", ai: "Evidence Bundle", aIcon: "verified_user", note: "the record that follows it everywhere" },
];

const LIFECYCLE = [
  { phase: "Discover", icon: "radar", href: "/workforce", note: "Crawl your A2A Agent Cards for real and catch the agents already running off the books" },
  { phase: "Onboard", icon: "how_to_reg", href: "/agents", note: "A six-stage interview with one clear verdict: Ready, Conditional, or Blocked" },
  { phase: "Manage", icon: "groups", href: "/roster", note: "Your roster and HR Console: place on leave, hand off to a new manager, change a role" },
  { phase: "Govern", icon: "policy", href: "/compliance", note: "Every control mapped live to NSA, NIST, and the EU AI Act" },
  { phase: "Operate", icon: "monitor_heart", href: "/operate", note: "Always-on performance reviews, watched by the Sentinel engine" },
  { phase: "Optimize", icon: "trending_up", href: "/optimize", note: "A growth plan for every agent, one rung up the autonomy ladder at a time" },
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
              Hire your AI agents. <br />
              <span className="text-primary">Don&apos;t just deploy them.</span>
            </h1>
            <p className="text-lg text-on-surface-variant">
              You&apos;d never let a new hire start without an ID badge, a job description, a
              résumé, and a file in HR. Yet AI agents keep showing up to work with none of it.
              <strong className="font-semibold text-on-surface"> ClearPoint Workforce Agent</strong>{" "}
              gives them the same treatment, across the first{" "}
              <strong className="font-semibold text-on-surface">six phases of AI Workforce
              Management</strong>: find the agents already running unsupervised, put new ones
              through a hiring gate that decides the same way every time, then manage, govern,
              operate, and help them grow up the autonomy ladder.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/agents" className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-on-primary shadow-sm transition-colors hover:bg-primary-hover">
                <span className="material-symbols-outlined text-[18px]">how_to_reg</span> Start onboarding
              </Link>
              <Link href="/architecture" className="inline-flex items-center gap-2 rounded-lg border border-outline px-6 py-3 text-sm font-semibold text-on-surface transition-colors hover:bg-surface-container">
                <span className="material-symbols-outlined text-[18px]">account_tree</span> See how it&apos;s built
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="text-center text-xs font-semibold uppercase tracking-widest text-on-surface-variant">When you hire a person</div>
            <div className="text-center text-xs font-semibold uppercase tracking-widest text-primary">When you hire an agent</div>
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
            Six phases, start to finish. Every one of them adds to a single personnel file per
            agent, hash-chained so nothing can be quietly rewritten later.
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
            Real numbers, not promises. Every figure here is measured from the build you&apos;re looking at.
          </p>
        </div>
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { k: "&lt; 5 ms", v: "to reach a decision per onboarding run (CLI; still sub-second with live Gemini narration on top)" },
            { k: "8 / 8", v: "Pre-Boarding candidates land on the right call across 8 production-shaped risk archetypes" },
            { k: "5", v: "fail-closed pre-employment screening checks, every candidate, every time (OV-001..005)" },
            { k: "29", v: "regulatory citations resolved live in the Compliance matrix (NSA MCP CSI, NIST AI RMF, EU AI Act)" },
            { k: "19 / 19", v: "NSA MCP security baseline tests passing (auth, RBAC, integrity, replay, output filter, audit)" },
            { k: "186", v: "tests in all, spanning unit, integration, evals, and security" },
            { k: "90 %", v: "code coverage on the decision core (cpoa/services + agents + mcp_servers + app/api)" },
            { k: "6 / 7", v: "lifecycle phases live today; the seventh, continuous attestation, is next" },
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
          It all runs on Google. The crew is orchestrated with the{" "}
          <strong className="text-on-surface">Agent Development Kit</strong>, thinks with{" "}
          <strong className="text-on-surface">Gemini 3.5 Flash on Vertex AI</strong>, reaches its
          tools over the <strong className="text-on-surface">Model Context Protocol</strong>, stays
          grounded with <strong className="text-on-surface">Vertex AI Search</strong>, is designed in
          <strong className="text-on-surface"> Google Stitch</strong>, watched with
          <strong className="text-on-surface"> Cloud Trace</strong>, remembered in
          <strong className="text-on-surface"> Firestore</strong>, shipped on
          <strong className="text-on-surface"> Cloud Run</strong>, and found by other agents over the
          <strong className="text-on-surface"> Agent-to-Agent (A2A)</strong> protocol.
        </p>
        <p className="max-w-3xl text-sm text-on-surface-variant">
          The verdict itself (the score, the caps, the blockers) is computed deterministically, so it
          lands the same way every time. Gemini handles the parts that benefit from language: the
          summaries, the reasoning, the plain-English explanations. Six phases are live here; the
          seventh, continuous attestation across every running interaction, is what&apos;s next.
        </p>
      </section>
    </div>
  );
}
