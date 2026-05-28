import type {
  CompassAnswer,
  CompassContextPayload,
  DiscoveryScanResult,
  FixtureCard,
  FleetSnapshot,
  LifecycleAction,
  LifecycleActionResult,
  LifecycleAdvanceResult,
  LifecycleDetail,
  LifecyclePhase,
  LifecycleState,
  Run,
  RunLifecycleResult,
} from "./types";

// Relative paths; next.config rewrites /api/* to the FastAPI backend (dev + deploy).
async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { cache: "no-store", ...init });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  listFixtures: () => j<FixtureCard[]>("/api/fixtures"),
  getRun: (id: string) => j<Run>(`/api/runs/${id}`),
  createRun: (fixture: string) =>
    j<Run>("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fixture }),
    }),
  // Remediate a Blocked run: quarantine the prompt-injection and re-run
  // onboarding on the sanitized manifest. Returns the new (cleared) run.
  remediateRun: (runId: string) =>
    j<Run>(`/api/runs/${encodeURIComponent(runId)}/remediate`, { method: "POST" }),
  grounding: (name: string) =>
    j<{ ungrounded: any; grounded: any }>(`/api/grounding-comparison/${name}`),
  narrate: (id: string) =>
    j<{ narrative: string; source: string; model: string }>(`/api/runs/${id}/narrate`, {
      method: "POST",
    }),
  downloadUrl: (id: string, fmt: "json" | "md" | "pdf") => `/api/runs/${id}/download/${fmt}`,
  discoveryScan: (endpoints?: string[]) =>
    j<DiscoveryScanResult>("/api/discovery/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(endpoints ? { endpoints } : {}),
    }),
  getLifecycleState: (candidateId: string) =>
    j<LifecycleState>(`/api/workforce/${encodeURIComponent(candidateId)}/state`),
  applyLifecycleAction: (
    candidateId: string,
    action: LifecycleAction,
    payload: Record<string, unknown>,
    actorId?: string,
  ) =>
    j<LifecycleActionResult>(`/api/workforce/${encodeURIComponent(candidateId)}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, payload, actor_id: actorId }),
    }),
  // Lifecycle continuation
  advanceLifecycle: (candidateId: string, phase: LifecyclePhase) =>
    j<LifecycleAdvanceResult>(`/api/workforce/${encodeURIComponent(candidateId)}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phase }),
    }),
  runFullLifecycle: (candidateId: string) =>
    j<RunLifecycleResult>(`/api/workforce/${encodeURIComponent(candidateId)}/run-lifecycle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    }),
  lifecycleDetail: (candidateId: string, runId?: string) =>
    j<LifecycleDetail>(
      `/api/workforce/${encodeURIComponent(candidateId)}/lifecycle-detail` +
        (runId ? `?run_id=${encodeURIComponent(runId)}` : ""),
    ),
  // Resolve a flagged lifecycle item (Govern gap / Operate anomaly / Optimize
  // growth item). Writes a real signed, hash-chained remediation event.
  remediate: (
    candidateId: string,
    phase: LifecyclePhase,
    refId: string,
    title: string,
    summary: string,
  ) =>
    j<LifecycleActionResult>(`/api/workforce/${encodeURIComponent(candidateId)}/remediate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phase, ref_id: refId, title, summary }),
    }),
  // Compass advisor + Sentinel feed
  askCompass: (message: string, context?: CompassContextPayload) =>
    j<CompassAnswer>("/api/compass/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, context: context ?? {} }),
    }),
  operateFleet: () => j<FleetSnapshot>("/api/operate/fleet"),
};
