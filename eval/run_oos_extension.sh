#!/usr/bin/env bash
# Extended evaluation: 124 questions (100 main + 24 new out_of_scope).
# Each (backend, llm) run resumes from existing 100-question predictions
# and adds the 24 new oos qids.
set -u
cd "$(dirname "$0")/.."

GOLD="eval/full_questions_v2.jsonl"

combos=(
  "typedb hcx" "typedb qwen" "typedb llama4" "typedb gpt-oss-120b"
  "neo4j hcx" "neo4j qwen" "neo4j llama4" "neo4j gpt-oss-120b"
  "context hcx" "context qwen" "context llama4" "context gpt-oss-120b"
  "closed_book hcx" "closed_book qwen" "closed_book llama4" "closed_book gpt-oss-120b"
  "context_tql hcx" "context_tql qwen" "context_tql llama4" "context_tql gpt-oss-120b"
  "context_cypher hcx" "context_cypher qwen" "context_cypher llama4" "context_cypher gpt-oss-120b"
  "context_nl hcx" "context_nl qwen" "context_nl llama4" "context_nl gpt-oss-120b"
  "context_jsonld hcx" "context_jsonld qwen" "context_jsonld llama4" "context_jsonld gpt-oss-120b"
)

run_one() {
  local backend="$1" llm="$2"
  local label="${backend}_${llm}"
  for try in 1 2 3; do
    if .venv/bin/python eval/run_baseline.py \
         --backend "$backend" --llm "$llm" \
         --gold "$GOLD" --resume > "/tmp/oos_${label}.log" 2>&1; then
      echo "[done] ${label}"
      return 0
    fi
    echo "[retry] ${label} try=${try} failed, sleeping 30s..."
    sleep 30
  done
  echo "[FAIL] ${label} after 3 tries"
  return 1
}

for combo in "${combos[@]}"; do
  read -r b l <<<"$combo"
  run_one "$b" "$l" &
done
wait
echo "[oos_extension] all 32 runs returned"
