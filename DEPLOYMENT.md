# Deployment Guide — ClearPoint Onboarding Agent

End-to-end deploy of CPOA to Google Cloud Run with a custom domain, Firestore
persistence, Vertex AI Search grounding, and Cloud Trace observability.

## Prerequisites

- A Google Cloud project (e.g. `clearpoint-operations-agent`) with billing enabled.
- `gcloud` CLI authenticated and pointed at that project.
- DNS control over the target domain (this deployment uses `cpoa.clearpointlogic.com`).
- `gh` CLI authenticated if pushing the repo.

## One-time setup

### 1 — Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  cloudtrace.googleapis.com \
  discoveryengine.googleapis.com   # only if seeding Vertex AI Search
```

### 2 — IAM roles for the Compute Engine default service account

Cloud Build uses this SA by default; Cloud Run pods run as it.

```bash
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT \
  --format="value(projectNumber)")
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for role in \
  roles/cloudbuild.builds.builder \
  roles/storage.objectViewer \
  roles/artifactregistry.writer \
  roles/logging.logWriter \
  roles/cloudtrace.agent \
  roles/datastore.user \
  roles/aiplatform.user ; do
  gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:${SA}" --role="$role"
done
```

### 3 — Custom domain mapping

Map the domain to the `cpoa-web` Cloud Run service. Google issues a managed
TLS certificate automatically once DNS resolves.

```bash
gcloud beta run domain-mappings create \
  --service cpoa-web \
  --domain cpoa.clearpointlogic.com \
  --region us-central1
```

Cloudflare DNS (or equivalent) needs a CNAME record pointing `cpoa` →
`ghs.googlehosted.com` with proxying **disabled** (DNS-only). Cert provisioning
typically completes within minutes once DNS propagates.

### 4 — Organization policy (only if `allUsers` invocations are blocked)

If `iam.allowedPolicyMemberDomains` is enforced and blocks `allUsers`, relax
it at the project scope:

```yaml
# infra/org_policy_allow_public.yaml
name: projects/<PROJECT_NUMBER>/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
  - allowAll: true
```

```bash
gcloud org-policies set-policy infra/org_policy_allow_public.yaml
```

Reversible: `gcloud org-policies delete iam.allowedPolicyMemberDomains --project=$GOOGLE_CLOUD_PROJECT`.

## Deploying

The full deploy script lives at [`infra/cloudrun/deploy.sh`](infra/cloudrun/deploy.sh)
and builds + deploys all three services (MCP, API, Web). Run from the repo root:

```bash
# Required env (omit to auto-generate; set to keep credentials stable across redeploys):
export CPOA_JUDGE_BASIC_AUTH_USER=judge
export CPOA_JUDGE_BASIC_AUTH_PASS='<your-credential>'
export CPOA_MCP_AUTH_TOKEN='<your-mcp-token>'

# Optional:
export GOOGLE_CLOUD_PROJECT=clearpoint-operations-agent     # default in deploy.sh
export GOOGLE_CLOUD_LOCATION=us-central1                    # Cloud Run region
export CPL_VERTEX_LOCATION=global                           # Gemini 3.5 Flash region
export CPOA_GROUNDING_MODE=vertex_ai_search                 # or `local` to fall back

bash infra/cloudrun/deploy.sh
```

Output prints the live URLs and credentials. The script:

1. Enables APIs (idempotent).
2. Builds three container images via Cloud Build → Artifact Registry.
3. Deploys `cpoa-mcp` (private), `cpoa-api` (public), `cpoa-web` (public) in order.

## Environment variables (Cloud Run)

| Variable | Service | Purpose |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI=TRUE` | api | Force Vertex backend (AI Studio is not eligible per challenge rules) |
| `GOOGLE_CLOUD_PROJECT` | api | Vertex project |
| `GOOGLE_CLOUD_LOCATION=global` | api | Gemini 3.5 Flash region |
| `CPL_GEMINI_MODEL_FAST=gemini-3.5-flash` | api | Live narration model |
| `CPOA_STORAGE_MODE=firestore` | api | Durable run store |
| `CPOA_GROUNDING_MODE=vertex_ai_search` | api | Live grounding retriever (falls back to local if datastore unconfigured) |
| `CPOA_SIGNING_MODE=local_hmac` | api | Evidence signature mode (`kms` available once KMS keyring is set up) |
| `CPOA_JUDGE_BASIC_AUTH_USER` | web, api | Judge gate user |
| `CPOA_JUDGE_BASIC_AUTH_PASS` | web, api | Judge gate password |
| `CPOA_MCP_AUTH_TOKEN` | mcp, api | MCP bearer token |
| `CPOA_API_BASE` | web | Internal URL of the API service |
| `CPOA_CORS_ORIGINS` | api | Allowed CORS origins (default `*` — narrow for production) |

## Verifying a deploy

```bash
# Health probe publishes the runtime modes envelope
curl -sS https://cpoa.clearpointlogic.com/api/health | jq .

# A2A Agent Card is open
curl -sS https://cpoa.clearpointlogic.com/.well-known/agent.json | jq .

# Web UI is gated by basic auth
curl -sI -u "$CPOA_JUDGE_BASIC_AUTH_USER:$CPOA_JUDGE_BASIC_AUTH_PASS" \
  https://cpoa.clearpointlogic.com/
# Expect: HTTP/2 200 + Strict-Transport-Security + Content-Security-Policy headers
```

## Rollback

Cloud Run keeps every revision; route traffic back to the last good one:

```bash
gcloud run services update-traffic cpoa-web \
  --to-revisions cpoa-web-00007-xxx=100 --region us-central1
```

## Monitoring

- **Cloud Trace** dashboard for the project shows onboarding spans
- **Cloud Logging** — filter on `resource.type="cloud_run_revision"` and
  service name
- **Cloud Run Metrics** dashboard for request/latency/error rates

## Teardown

```bash
gcloud run services delete cpoa-web --region us-central1 -q
gcloud run services delete cpoa-api --region us-central1 -q
gcloud run services delete cpoa-mcp --region us-central1 -q
gcloud beta run domain-mappings delete \
  --domain cpoa.clearpointlogic.com --region us-central1 -q
```

(Firestore documents persist independently — delete them via the console if
desired.)
