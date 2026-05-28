# Data & IP boundary

## Data classification
- **All candidate manifests are synthetic** (`fixtures/candidates/`). No real customer data, no
  production telemetry.
- **Grounded corpus is public** (`corpus/`): NSA MCP CSI, NIST AI RMF, EU AI Act (paraphrased,
  attributed), plus CPOA's own demo policy/fixture notes.
- Generated artifacts (passports, bundles) describe synthetic agents only.

## What this repo intentionally excludes (protected IP)
- Main ClearPoint Logic build pack and non-public canonicals.
- Production CAS/ECS scoring weights and tuning logic.
- Anchor signing-key design / production cryptographic attestation internals.
- Continuous Validation Agent Suite implementation (Sentinel, Forensics, Drift, Red Team, Regulatory
  Watch).
- Pricing, roadmap, and customer-specific material.

## Demo-honest labels (enforced in code + docs)
- `not_anchor_certification: true` on every Passport.
- `not_production_cas_or_ecs: true` on every Readiness Score.
- `signature.type: demo_stub` on every evidence event.
- Every Evidence Bundle carries explicit `limitations`.

See [`../../PROPRIETARY.md`](../../PROPRIETARY.md) for the full boundary statement.
