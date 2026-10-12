#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/backend"
exec python -m uvicorn api_service.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
