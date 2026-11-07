#!/usr/bin/env bash
# Run SEA-HELM's BATAYAN task group (Filipino, 3,800 items) against a llama.cpp server running Gemma 4 E4B.
# Usage: bash run_batayan.sh <work_dir> <output_dir> [--limit N]
#   <work_dir>   folder holding sea-helm/ (patched clone), .venv/ and .env (HF_TOKEN=...). See ../README.md.
#   <output_dir> results folder; relative paths are relative to <work_dir>/sea-helm. Reuse the same folder to resume.
#   --limit N    optional: only N items per task (pilot).
# Optional environment overrides: MODEL_URL (default http://127.0.0.1:18088/v1), MODEL_NAME.
# The HF token is read from <work_dir>/.env and never printed.
set -euo pipefail
WORK="$(cd "$1" && pwd)"; OUT="$2"; shift 2
MODEL_URL="${MODEL_URL:-http://127.0.0.1:18088/v1}"
MODEL_NAME="${MODEL_NAME:-gemma-4-E4B-it-UD-Q4_K_XL}"
if [ -x "$WORK/.venv/Scripts/python" ]; then PY="$WORK/.venv/Scripts/python"; else PY="$WORK/.venv/bin/python"; fi
HF_TOKEN="$(grep '^HF_TOKEN=' "$WORK/.env" | cut -d= -f2- | tr -d '\r')"
export HF_TOKEN
export PYTHONIOENCODING=utf-8 PYTHONUTF8=1
cd "$WORK/sea-helm"
"$PY" -m src.seahelm_evaluation --tasks batayan --output_dir "$OUT" \
  --model_type local_openai --model_name "$MODEL_NAME" \
  --model_args "base_url=$MODEL_URL,api_key=none,max_workers=2" \
  --skip_tokenize_prompts --run 0 "$@"
