import type {
  DiscoveryScanResult,
  FixtureCard,
  LifecycleAction,
  LifecycleActionResult,
  LifecycleState,
  Run,
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
};
