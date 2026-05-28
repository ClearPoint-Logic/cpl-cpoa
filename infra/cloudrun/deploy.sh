#!/usr/bin/env bash
# Deploy the three Cloud Run services (API, MCP, Web) to the challenge project.
# Light-touch: scale-to-zero, gemini-2.5-flash, Cloud Run (Agent Engine optional).
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:-clearpoint-operations-agent}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
REPO="cpoa"
AR="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}"
JUDGE_USER="${CPOA_JUDGE_BASIC_AUTH_USER:-judge}"
JUDGE_PASS="${CPOA_JUDGE_BASIC_AUTH_PASS:?set CPOA_JUDGE_BASIC_AUTH_PASS}"
MCP_TOKEN="${CPOA_MCP_AUTH_TOKEN:-$(openssl rand -hex 16)}"

echo "Project=${PROJECT} Region=${REGION}"
gcloud config set project "${PROJECT}"

echo "== Enabling APIs (idempotent) =="
gcloud services enable run.googleapis.com aiplatform.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com

echo "== Artifact Registry repo =="
gcloud artifacts repositories create "${REPO}" --repository-format=docker \
  --location="${REGION}" 2>/dev/null || true
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

build_push() { # name dockerfile [build-args...]
  local name="$1"; local dockerfile="$2"; shift 2
  echo "== Building ${name} =="
  docker build -f "${dockerfile}" -t "${AR}/${name}:latest" "$@" .
  docker push "${AR}/${name}:latest"
}

# 1. MCP server (private; called by the orchestrator)
build_push mcp infra/cloudrun/Dockerfile.mcp
gcloud run deploy cpoa-mcp --image "${AR}/mcp:latest" --region "${REGION}" \
  --no-allow-unauthenticated --min-instances=0 \
  --set-env-vars "CPOA_MCP_TRANSPORT=http,CPOA_MCP_AUTH_TOKEN=${MCP_TOKEN}"

# 2. API backend (deterministic engine + optional Vertex narrative)
build_push api infra/cloudrun/Dockerfile.api
gcloud run deploy cpoa-api --image "${AR}/api:latest" --region "${REGION}" \
  --allow-unauthenticated --min-instances=0 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},CPL_GEMINI_MODEL_FAST=gemini-2.5-flash,CPOA_JUDGE_BASIC_AUTH_USER=${JUDGE_USER},CPOA_JUDGE_BASIC_AUTH_PASS=${JUDGE_PASS},CPOA_CORS_ORIGINS=*"
API_URL="$(gcloud run services describe cpoa-api --region "${REGION}" --format='value(status.url)')"
echo "API_URL=${API_URL}"

# 3. Web UI (proxies /api/* to the API service)
build_push web infra/cloudrun/Dockerfile.web --build-arg "CPOA_API_BASE=${API_URL}"
gcloud run deploy cpoa-web --image "${AR}/web:latest" --region "${REGION}" \
  --allow-unauthenticated --min-instances=0 \
  --set-env-vars "CPOA_API_BASE=${API_URL}"
WEB_URL="$(gcloud run services describe cpoa-web --region "${REGION}" --format='value(status.url)')"

echo ""
echo "Deployed:"
echo "  Web (judge UI): ${WEB_URL}"
echo "  API:            ${API_URL}"
echo "  Judge basic auth: ${JUDGE_USER} / (CPOA_JUDGE_BASIC_AUTH_PASS)"
echo "  MCP auth token:   ${MCP_TOKEN}"
