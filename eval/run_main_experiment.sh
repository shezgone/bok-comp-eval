#!/usr/bin/env bash
# Main experiment: 100 questions × 8 backends × 2 LLMs = 1600 calls.
# Existing 30 seed predictions are kept (resume), only the 70 expanded
# questions are added. Each (backend,llm) runs in parallel with up to 3
# retries to ride out rate-limit hiccups.
set -u

cd "$(dirname "$0")/.."

GOLD="eval/full_questions.jsonl"

combos=(
  "typedb hcx" "typedb qwen"
  "neo4j hcx" "neo4j qwen"
  "context hcx" "context qwen"
  "closed_book hcx" "closed_book qwen"
  "context_tql hcx" "context_tql qwen"
  "context_cypher hcx" "context_cypher qwen"
  "context_nl hcx" "context_nl qwen"
  "context_jsonld hcx" "context_jsonld qwen"
)

run_one() {
  local backend="$1" llm="$2"
  local label="${backend}_${llm}"
  for try in 1 2 3; do
    if .venv/bin/python eval/run_baseline.py \
         --backend "$backend" --llm "$llm" \
         --gold "$GOLD" --resume > "/tmp/main_${label}.log" 2>&1; then
      echo "[done] ${label} (try=${try})"
      return 0
    fi
    echo "[retry] ${label} try=${try} failed, sleeping 30s..."
    sleep 30
  done
  echo "[FAIL] ${label} after 3 tries — see /tmp/main_${label}.log"
  return 1
}

for combo in "${combos[@]}"; do
  read -r b l <<<"$combo"
  run_one "$b" "$l" &
done
wait
echo "[main_experiment] all 16 runs returned"
