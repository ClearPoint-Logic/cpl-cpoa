import Link from "next/link";

const SCRIPT = [
  "0:00–0:20 — The workforce frame: ID badge / job description / résumé / personnel file.",
  "0:20–1:10 — Run safe_research_agent → Ready (clean intake, evidence bundle).",
  "1:10–1:55 — Run prompt_injected_mcp_agent → Blocked, citing the NSA MCP CSI source; fail-closed.",
  "1:55–2:00 — Onboarding gate today; continuous attestation is the AI Workforce Management roadmap.",
];

const LIMITS = [
  "Net-new Track 1 agent inspired by the ClearPoint Meridian architecture — not a claim that Meridian is live.",
  "Implements the onboarding gate only; continuous attestation is roadmap.",
  "Synthetic fixtures; demo-stub signatures (not production cryptographic attestation).",
  "Passport Readiness Score is demonstration-grade — not the proprietary production scoring system.",
  "Onboarding recommendation, not certified legal or compliance approval.",
];

export default function Judge() {
  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-semibold">Judge access &amp; testing</h1>
        <p className="text-on-surface-variant">
          Everything needed to evaluate the AI Workforce Management onboarding gate in under four
          minutes.
        </p>
      </div>

      <section className="space-y-2 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Testing access
        </h2>
        <p className="text-sm text-on-surface-variant">
          The hosted UI is protected by HTTP basic auth. Credentials are provided in the Devpost
          submission and in{" "}
          <code className="rounded bg-surface-container px-1 text-on-surface">docs/submission/JUDGE_RUNBOOK.md</code>.
          No CLI is required — every fixture runs from the Agent Zoo.
        </p>
      </section>

      <section className="space-y-2 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Fixture shortcuts
        </h2>
        <p className="text-sm text-on-surface-variant">
          Open the{" "}
          <Link href="/agents" className="text-primary underline">
            Agent Zoo
          </Link>{" "}
          and run any fixture end-to-end. Suggested order:{" "}
          <strong className="text-on-surface">safe_research_agent</strong> (Ready) →{" "}
          <strong className="text-on-surface">prompt_injected_mcp_agent</strong> (Blocked) →{" "}
          <strong className="text-on-surface">healthcare_phi_support_agent</strong> (Conditional).
        </p>
      </section>

      <section className="space-y-2 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          2-minute demo script
        </h2>
        <ul className="space-y-1 text-sm text-on-surface-variant">
          {SCRIPT.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-2 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Interoperability &amp; exports
        </h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-on-surface-variant">
          <li>
            <strong className="text-on-surface">Agent-to-Agent (A2A):</strong> Agent Card at{" "}
            <code className="rounded bg-surface-container px-1 text-on-surface">/.well-known/agent.json</code>;
            tasks accepted at{" "}
            <code className="rounded bg-surface-container px-1 text-on-surface">/a2a/v1/message:send</code> —
            discoverable by other enterprise agents.
          </li>
          <li>
            <strong className="text-on-surface">Live Gemini narration:</strong> each run offers an
            &ldquo;Explain with Gemini&rdquo; action (real Vertex AI call; the decision stays deterministic).
          </li>
          <li>
            <strong className="text-on-surface">Evidence export:</strong> every bundle downloads as
            JSON, Markdown, or PDF.
          </li>
          <li>
            <strong className="text-on-surface">Observability:</strong> onboarding emits Cloud Trace
            spans alongside the SHA-256 hash-chained evidence log.
          </li>
          <li>
            <strong className="text-on-surface">Durable runs:</strong> Firestore-backed run storage
            survives Cloud Run scale-to-zero.
          </li>
        </ul>
      </section>

      <section className="space-y-2 rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          Known limitations (honest scope)
        </h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-on-surface-variant">
          {LIMITS.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
