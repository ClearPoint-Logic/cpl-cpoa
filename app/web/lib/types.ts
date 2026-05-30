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

export interface Remediation {
  phase: LifecyclePhase;
  ref_id: string;
  title: string;
  summary: string;
  event_id: string;
  actor: string;
  resolved_at: string;
}

export interface LifecycleState {
  candidate_agent_id: string;
  status: LifecycleStatus;
  owner_email: string | null;
  notes: string;
  updated_at: string;
  event_log: LifecycleEvent[];
  last_event_hash: string | null;
  remediations?: Remediation[];
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

// Lifecycle detail — rich per-phase cards on the run page. Each phase carries a
// pass/flagged status plus the real data that phase assessed.
export type PhaseStatus = "pass" | "flagged";

export interface ManagePhaseDetail {
  status: PhaseStatus;
  manager_name: string | null;
  manager_email: string | null;
  team: string | null;
  role: string | null;
  owner_status: string | null;
  trust_tier: string | null;
  autonomy: string | null;
  runtime: string | null;
  deployment: string | null;
  region: string | null;
  kill_switch: string | null;
  roster_status: string | null;
}

export interface GovernGap {
  control_id: string;
  control_name: string;
  finding_id: string;
  title: string;
  severity: string;
  requirement?: string | null;
  observed?: string | null;
  remediation: string;
  blocks: boolean;
  resolved: boolean;
}

export interface GovernPhaseDetail {
  status: PhaseStatus;
  controls: number;
  frameworks: number;
  citations: number;
  framework_names: string[];
  control_list: { control_id: string; name: string; category: string }[];
  gaps: GovernGap[];
}

export interface OperateAnomaly {
  rule_id: string;
  severity: string;
  summary: string;
  resolved?: boolean;
}

export interface OperatePhaseDetail {
  status: PhaseStatus;
  anomalies: OperateAnomaly[];
  readiness_score: number | null;
  open_findings: number | null;
  blocking_findings: number | null;
  risk_tier: string | null;
  autonomy_level: string | null;
  onboarding_decision: string | null;
  lifecycle_events_30d: number | null;
}

export interface DevelopmentItem {
  finding_id: string;
  title: string;
  severity: string;
  remediation: string;
  blocks_promotion?: boolean;
  resolved?: boolean;
}

export interface OptimizePhaseDetail {
  status: PhaseStatus;
  current_autonomy: string | null;
  next_autonomy: string | null;
  ready_for_promotion: boolean;
  development_items: DevelopmentItem[];
  promotion_blockers: DevelopmentItem[];
  monthly_budget_usd: number | null;
  tools: string[];
}

export interface LifecycleDetail {
  candidate_agent_id: string;
  manage: ManagePhaseDetail;
  govern: GovernPhaseDetail;
  operate: OperatePhaseDetail;
  optimize: OptimizePhaseDetail;
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
  // Onboarding remediation loop (prompt-injection hero). Present only on runs
  // that are part of a remediation: the original Blocked run gets
  // `remediated_by_run_id`; the cleared re-run gets `remediates_run_id` +
  // `remediation_applied` (the quarantine record).
  remediates_run_id?: string;
  remediated_by_run_id?: string;
  remediation_applied?: RemediationApplied[];
}

export interface RemediationApplied {
  tool_id: string;
  control: string;
  phrases: string[];
  action: string;
}
