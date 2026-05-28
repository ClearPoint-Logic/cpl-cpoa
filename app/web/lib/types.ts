// Discover phase — A2A directory scan results
export interface DiscoveredAgent {
  endpoint: string;
  status: "known" | "unknown" | "unreachable" | "invalid";
  agent_card: Record<string, any> | null;
  candidate_agent_id: string | null;
  matched_registry_entry: Record<string, any> | null;
  error: string | null;
}

export interface DiscoveryScanResult {
  summary: {
    scanned: number;
    known: number;
    unknown: number;
    unreachable: number;
    invalid: number;
  };
  results: DiscoveredAgent[];
  scope: string;
}

// Manage phase — HR Console lifecycle state
export type LifecycleStatus = "active" | "on_leave" | "returning";
export type LifecycleAction =
  | "place_on_leave"
  | "return_from_leave"
  | "manager_handoff"
  | "role_change";

export interface LifecycleEvent {
  event_id: string;
  event_type: string;
  event_hash: string;
  previous_event_hash: string | null;
  summary: string;
  timestamp: string;
  actor: { type: string; id: string };
  signature?: { type: string; value: string };
}

export interface LifecycleState {
  candidate_agent_id: string;
  status: LifecycleStatus;
  owner_email: string | null;
  notes: string;
  updated_at: string;
  event_log: LifecycleEvent[];
  last_event_hash: string | null;
}

export interface LifecycleActionResult {
  state: LifecycleState;
  event: LifecycleEvent;
}

// Lifecycle continuation — advancing through the post-onboarding phases.
export type LifecyclePhase = "manage" | "govern" | "operate" | "optimize";

export interface LifecycleAdvanceResult {
  state: LifecycleState;
  event: LifecycleEvent;
  phase: LifecyclePhase;
}

export interface RunLifecycleResult {
  state: LifecycleState;
  events: (LifecycleEvent & { phase: LifecyclePhase })[];
}

// Compass — in-platform advisor (advise + act on confirm).
export interface CompassCitation {
  source_id: string;
  title: string;
  snippet?: string;
}

export interface CompassAction {
  id: string;
  kind: "navigate" | "advance_lifecycle" | "ask";
  label: string;
  description?: string;
  href?: string; // navigate
  candidate_id?: string; // advance_lifecycle
  prompt?: string; // ask
  confirm?: boolean; // requires an explicit confirm step
}

export interface CompassAnswer {
  answer: string;
  source: "gemini" | "deterministic";
  citations: CompassCitation[];
  suggested_actions: CompassAction[];
}

export interface CompassContextPayload {
  run_id?: string;
  candidate_id?: string;
  page?: string;
  agent_name?: string;
}

// Operate (Sentinel) fleet snapshot — surfaced to Compass's Agent View.
export interface FleetMember {
  candidate_agent_id: string;
  name: string;
  status: string;
  risk_tier: string;
  readiness_score: number;
  onboarding_decision: string;
  open_findings: number;
  anomalies: Array<{ rule_id: string; severity: string; summary: string }>;
}

export interface FleetSnapshot {
  summary: {
    agents: number;
    active: number;
    on_leave: number;
    agents_with_anomalies: number;
    total_anomalies: number;
    by_risk_tier: Record<string, number>;
  };
  members: FleetMember[];
}

export interface FixtureCard {
  name: string;
  agent_name: string;
  origin: string;
  tier: string;
  expected_decision: string;
  business_story: string;
  tools: { name: string; risk_tier: string }[];
  data_classes: string[];
  autonomy: string;
}

export interface Finding {
  test_id: string;
  severity: string;
  confidence?: string;
  title: string;
  description?: string;
  recommended_remediation: string;
  blocks_ready_decision: boolean;
}

export interface GroundingRef {
  source_id: string;
  source_title: string;
  snippet?: string;
}

export interface EvidenceEvent {
  event_type: string;
  summary: string;
  event_hash: string;
  previous_event_hash: string | null;
  actor: { type: string; id: string };
  timestamp: string;
}

export interface Run {
  run_id: string;
  agent_name: string;
  candidate_agent_id: string;
  decision: string;
  blockers: string[];
  conditions: string[];
  // deep artifact objects rendered loosely
  score: { score: number; band: string; components: Record<string, number>; rationale: string[] };
  discovery: Record<string, any>;
  passport: Record<string, any>;
  ai_bom: Record<string, any>;
  policy: Record<string, any>;
  validation_run: { findings: Finding[]; summary: string; passed: boolean; tests_run: string[] };
  approval_card: Record<string, any>;
  evidence_bundle: Record<string, any>;
  events: EvidenceEvent[];
  narrative: {
    headline: string;
    workforce_lines: string[];
    reasons: string[];
    findings: string[];
    grounded_sources: string[];
  };
  candidate_manifest: Record<string, any>;
}
