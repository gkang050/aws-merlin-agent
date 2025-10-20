#!/usr/bin/env bash
set -euo pipefail

ENV="${1:-dev}"

CONTEXT_OPTS="-c env=${ENV}"

if [[ -n "${FORECAST_MODEL_ARTIFACT:-}" ]]; then
  CONTEXT_OPTS="${CONTEXT_OPTS} -c forecastModelArtifact=${FORECAST_MODEL_ARTIFACT}"
fi

if [[ -n "${FORECAST_ENDPOINT_NAME:-}" ]]; then
  CONTEXT_OPTS="${CONTEXT_OPTS} -c forecastEndpointName=${FORECAST_ENDPOINT_NAME}"
fi

if [[ "${DEPLOY_UI:-false}" == "true" ]]; then
  CONTEXT_OPTS="${CONTEXT_OPTS} -c deployUI=true"
fi

poetry run cdk bootstrap ${CONTEXT_OPTS} || true
poetry run cdk deploy ${CONTEXT_OPTS} --require-approval never "MerlinDataPlatformStack-${ENV}" "MerlinAgentStack-${ENV}"
