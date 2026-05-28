#!/usr/bin/env bash
# Deploy API + MCP + Web to Cloud Run via Cloud Build (amd64). Light-touch:
# scale-to-zero, gemini-2.5-flash, Cloud Run orchestrator runtime (Agent Engine is
# the documented primary per CPOA-D019 / NFR-015). Prints the live URL + judge creds.
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:-clearpoint-operations-agent}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
REPO="cpoa"
AR="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}"
CB="infra/cloudrun/cloudbuild.yaml"
JUDGE_USER="${CPOA_JUDGE_BASIC_AUTH_USER:-judge}"
JUDGE_PASS="${CPOA_JUDGE_BASIC_AUTH_PASS:-$(openssl rand -base64 18 | tr -dc 'A-Za-z0-9' | cut -c1-16)}"
MCP_TOKEN="${CPOA_MCP_AUTH_TOKEN:-$(openssl rand -hex 16)}"

gcloud config set project "${PROJECT}" -q
echo "== Enabling APIs =="
gcloud services enable run.googleapis.com aiplatform.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com -q
echo "== Artifact Registry =="
gcloud artifacts repositories create "${REPO}" --repository-format=docker \
  --location="${REGION}" -q 2>/dev/null || true

submit() { # image dockerfile [api_base]
  gcloud builds submit --config "${CB}" \
    --substitutions=_IMAGE="$1",_DOCKERFILE="$2",_API_BASE="${3:-}" -q .
}

echo "== Build + deploy MCP (private) =="
submit "${AR}/mcp:latest" infra/cloudrun/Dockerfile.mcp
gcloud run deploy cpoa-mcp --image "${AR}/mcp:latest" --region "${REGION}" \
  --no-allow-unauthenticated --min-instances=0 \
  --set-env-vars "CPOA_MCP_TRANSPORT=http,CPOA_MCP_AUTH_TOKEN=${MCP_TOKEN}" -q

echo "== Build + deploy API =="
submit "${AR}/api:latest" infra/cloudrun/Dockerfile.api
gcloud run deploy cpoa-api --image "${AR}/api:latest" --region "${REGION}" \
  --allow-unauthenticated --min-instances=0 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},CPL_GEMINI_MODEL_FAST=gemini-2.5-flash,CPOA_JUDGE_BASIC_AUTH_USER=${JUDGE_USER},CPOA_JUDGE_BASIC_AUTH_PASS=${JUDGE_PASS},CPOA_CORS_ORIGINS=*" -q
API_URL="$(gcloud run services describe cpoa-api --region "${REGION}" --format='value(status.url)')"
echo "API_URL=${API_URL}"

echo "== Build + deploy Web (judge UI) =="
submit "${AR}/web:latest" infra/cloudrun/Dockerfile.web "${API_URL}"
gcloud run deploy cpoa-web --image "${AR}/web:latest" --region "${REGION}" \
  --allow-unauthenticated --min-instances=0 \
  --set-env-vars "CPOA_API_BASE=${API_URL},CPOA_JUDGE_BASIC_AUTH_USER=${JUDGE_USER},CPOA_JUDGE_BASIC_AUTH_PASS=${JUDGE_PASS}" -q
WEB_URL="$(gcloud run services describe cpoa-web --region "${REGION}" --format='value(status.url)')"

echo ""
echo "============================================================"
echo "  Judge UI : ${WEB_URL}"
echo "  API      : ${API_URL}"
echo "  Login    : ${JUDGE_USER} / ${JUDGE_PASS}"
echo "  MCP token: ${MCP_TOKEN}"
echo "============================================================"
