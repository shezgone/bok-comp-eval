#!/usr/bin/env bash
# Extension: add Llama-4-Scout + gpt-oss-120b (Tier 1 family diversity).
# Runs in parallel. Per-process retry 3x.
set -u

cd "$(dirname "$0")/.."

GOLD="eval/full_questions.jsonl"

combos=(
  "typedb llama4" "typedb gpt-oss-120b"
  "neo4j llama4" "neo4j gpt-oss-120b"
  "context llama4" "context gpt-oss-120b"
  "closed_book llama4" "closed_book gpt-oss-120b"
  "context_tql llama4" "context_tql gpt-oss-120b"
  "context_cypher llama4" "context_cypher gpt-oss-120b"
  "context_nl llama4" "context_nl gpt-oss-120b"
  "context_jsonld llama4" "context_jsonld gpt-oss-120b"
)

run_one() {
  local backend="$1" llm="$2"
  local label="${backend}_${llm}"
  for try in 1 2 3; do
    if .venv/bin/python eval/run_baseline.py \
         --backend "$backend" --llm "$llm" \
         --gold "$GOLD" --resume > "/tmp/extra_${label}.log" 2>&1; then
      echo "[done] ${label} (try=${try})"
      return 0
    fi
    echo "[retry] ${label} try=${try} failed, sleeping 30s..."
    sleep 30
  done
  echo "[FAIL] ${label} after 3 tries — see /tmp/extra_${label}.log"
  return 1
}

for combo in "${combos[@]}"; do
  read -r b l <<<"$combo"
  run_one "$b" "$l" &
done
wait
echo "[extra_llms] all 16 runs returned"
