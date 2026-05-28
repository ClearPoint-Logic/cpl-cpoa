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
