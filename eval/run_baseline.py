"""
BoK-Comp baseline runner.

Runs one (backend, llm) pair over the gold set and writes JSONL predictions.
Designed to be invoked once per (backend, llm) so the production agent's LLM
client is initialized cleanly with the right env vars (HCX vs GPT-4o swap is
done by overwriting OPENAI_* before importing the agent module).

Usage:
    python eval/run_baseline.py --backend typedb     --llm hcx
    python eval/run_baseline.py --backend neo4j      --llm hcx
    python eval/run_baseline.py --backend context    --llm hcx
    python eval/run_baseline.py --backend closed_book --llm hcx
    # then repeat for --llm gpt4o

Output: predictions/{backend}_{llm}.jsonl
        each line: {"qid", "answer", "latency_s", "backend", "llm", "model", "error"?}

Resume:
    --resume skips qids already present (with non-error answer) in the output file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parent
PRED_DIR = ROOT / "predictions"


# ---------- env loading ----------

def load_dotenv_from_root() -> None:
    """Minimal .env loader (stdlib only). Does not override existing env."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


# Short alias -> exact model name on the in-house OpenAI-compatible gateway.
# All gateway models share HCX_BASE_URL / HCX_API_KEY (single key, model swap).
GATEWAY_MODELS: dict[str, str] = {
    "hcx":          "HyperCLOVAX-SEED-32B-Think-Text",
    "hcx14b":       "HyperCLOVAX-SEED-Think-14B",
    "hcx1.5b":      "HyperCLOVAX-SEED-Text-Instruct-1.5B",
    "qwen":         "Qwen3-235B-A22B-Instruct-2507-FP8",
    "qwen397b":     "Qwen3.5-397B-A17B-FP8",
    "qwen3-32b":    "Qwen3-32B",
    "qwen3.5-27b":  "Qwen3.5-27B",
    "qwen3.6-35b":  "Qwen3.6-35B-A3B",
    "qwen3-next-80b": "Qwen3-Next-80B-A3B-Instruct",
    "llama4":       "Llama-4-Scout-17B-16E-Instruct",
    "gemma4":       "gemma-4-31B-it",
    "glm":          "GLM-4.6-FP8",
    "minimax":      "MiniMax-M2.5",
    "gpt-oss-120b": "gpt-oss-120b",
    "gpt-oss-20b":  "gpt-oss-20b",
}


def setup_llm_env(llm: str) -> str:
    """Map --llm choice into the OPENAI_* env vars consumed by production agents.

    Production's create_chat_model() reads OPENAI_BASE_URL / OPENAI_API_KEY /
    OPENAI_MODEL when LLM_PROVIDER=openai-compatible. We swap by overwriting
    those before any production module is imported.

    The in-house gateway uses a single (BASE_URL, API_KEY) pair — model name
    is the only variable. A literal model name is also accepted as `--llm`.
    """
    os.environ["LLM_PROVIDER"] = "openai-compatible"

    if llm == "gpt4o":
        if not os.environ.get("OPENAI_API_KEY"):
            sys.exit("[runner] missing OPENAI_API_KEY in .env — required for --llm gpt4o")
        os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
        os.environ.setdefault("OPENAI_MODEL", "gpt-4o")
        return os.environ["OPENAI_MODEL"]

    base_url = os.environ.get("HCX_BASE_URL")
    api_key = os.environ.get("HCX_API_KEY")
    if not base_url or not api_key:
        sys.exit("[runner] missing HCX_BASE_URL or HCX_API_KEY — required for gateway models")

    if llm in GATEWAY_MODELS:
        model = GATEWAY_MODELS[llm]
    else:
        model = llm  # literal model name passthrough

    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL"] = model
    return model


# ---------- backend dispatch ----------

def get_runner(backend: str):
    """Returns a callable: question:str -> answer:str. Imports happen here so
    LLM env vars are already set when production modules load."""
    # Production self-imports use `from src.bok_compensation_typedb.llm ...`
    # which is broken (renamed to llm_template). Install shims first.
    # When running `python eval/run_baseline.py`, eval/ is on sys.path[0].
    from _production_shims import install as install_shims  # type: ignore
    install_shims()

    if backend == "typedb":
        from bok_compensation_typedb.agent import run_query  # noqa: WPS433

        def call(q: str) -> str:
            return (run_query(q) or {}).get("answer", "")
        return call

    if backend == "neo4j":
        from bok_compensation_neo4j.agent import run_query  # noqa: WPS433

        def call(q: str) -> str:
            return (run_query(q) or {}).get("answer", "")
        return call

    if backend == "context":
        from bok_compensation_context.context_query import run_with_trace  # noqa: WPS433

        def call(q: str) -> str:
            return (run_with_trace(q) or {}).get("answer", "")
        return call

    if backend == "closed_book":
        from langchain_core.messages import HumanMessage, SystemMessage  # noqa: WPS433
        from bok_compensation_typedb.llm_template import create_chat_model  # noqa: WPS433

        model = create_chat_model(temperature=0.0)
        sys_prompt = (
            "당신은 한국은행 보수규정에 대한 질문에 답하는 어시스턴트입니다. "
            "외부 자료 없이 사전지식만으로 답하세요. "
            "구체적인 금액·비율·연도 등은 가능한 한 정확하게 답하되, 모르거나 "
            "규정에 없으면 '명시되지 않음'이라고 답하세요."
        )

        def call(q: str) -> str:
            resp = model.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=q)])
            return getattr(resp, "content", "") or ""
        return call

    if backend.startswith("context_"):
        # Fairness ablation: feed an alternate context tier (TQL/Cypher/NL/
        # JSONLD) directly to the chat LLM, without going through any
        # production agent. Same LLM and prompt scaffold as closed_book —
        # the only variable is the surface form of the structured data.
        tier = backend[len("context_"):]
        tier_path = ROOT / "eval" / "context_tiers" / f"regulation_{tier}.md"
        if not tier_path.exists():
            sys.exit(f"[runner] missing tier file: {tier_path}. Run "
                     f"eval/dump_context_tiers.py first.")

        from langchain_core.messages import HumanMessage, SystemMessage  # noqa: WPS433
        from bok_compensation_typedb.llm_template import create_chat_model  # noqa: WPS433

        tier_text = tier_path.read_text(encoding="utf-8")
        model = create_chat_model(temperature=0.0)
        sys_prompt = (
            "당신은 한국은행 보수규정 자료를 보고 질문에 답하는 어시스턴트입니다. "
            "아래 자료에서 근거를 찾아 정확한 단답형으로 답하세요. "
            "자료에 없으면 '명시되지 않음'이라고 답하세요.\n\n"
            "=== 자료 시작 ===\n" + tier_text + "\n=== 자료 끝 ==="
        )

        def call(q: str) -> str:
            resp = model.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=q)])
            return getattr(resp, "content", "") or ""
        return call

    sys.exit(f"[runner] unknown --backend {backend}")


# ---------- io ----------

def load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{i} invalid JSON: {e}") from e
    return items


def already_done(out_path: Path) -> set[str]:
    if not out_path.exists():
        return set()
    seen: set[str] = set()
    for line in out_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("qid") and obj.get("answer") and not obj.get("error"):
            seen.add(obj["qid"])
    return seen


# ---------- main ----------

def main() -> int:
    p = argparse.ArgumentParser(description="BoK-Comp baseline runner")
    p.add_argument("--backend", required=True,
                   help="typedb | neo4j | context | closed_book | context_tql | "
                        "context_cypher | context_nl | context_jsonld")
    p.add_argument("--llm", required=True,
                   help=f"alias from {sorted(GATEWAY_MODELS) + ['gpt4o']} or literal model name")
    p.add_argument("--gold", default=str(EVAL_DIR / "seed_questions.jsonl"))
    p.add_argument("--limit", type=int, default=0,
                   help="max questions to run (0 = all)")
    p.add_argument("--out", default=None,
                   help="output jsonl (default: predictions/{backend}_{llm}.jsonl)")
    p.add_argument("--resume", action="store_true",
                   help="skip qids already present (with non-error answer) in the output")
    args = p.parse_args()

    load_dotenv_from_root()
    model_name = setup_llm_env(args.llm)
    print(f"[runner] backend={args.backend} llm={args.llm} model={model_name}",
          file=sys.stderr)

    PRED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else PRED_DIR / f"{args.backend}_{args.llm}.jsonl"

    seen = already_done(out_path) if args.resume else set()
    if seen:
        print(f"[runner] resume: skipping {len(seen)} completed qids", file=sys.stderr)

    runner = get_runner(args.backend)

    items = load_jsonl(Path(args.gold))
    if args.limit:
        items = items[: args.limit]

    mode = "a" if args.resume and out_path.exists() else "w"
    n_total = len(items)
    n_run = n_err = 0
    with out_path.open(mode, encoding="utf-8") as fout:
        for i, item in enumerate(items, 1):
            qid = item["qid"]
            if qid in seen:
                continue
            q = item["question"]
            t0 = time.time()
            try:
                ans = runner(q)
                err = None
            except Exception as e:  # noqa: BLE001
                ans = ""
                err = f"{type(e).__name__}: {e}"
                n_err += 1
            dt = time.time() - t0
            rec: dict = {
                "qid": qid,
                "answer": ans,
                "latency_s": round(dt, 3),
                "backend": args.backend,
                "llm": args.llm,
                "model": model_name,
            }
            if err:
                rec["error"] = err
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            n_run += 1
            preview = (ans[:120] + "…") if len(ans) > 120 else ans
            tag = " ERR" if err else ""
            print(f"  [{i}/{n_total}] {qid} ({dt:.1f}s){tag}: {preview}",
                  file=sys.stderr)

    print(f"[runner] wrote {out_path}  (run={n_run}, err={n_err})", file=sys.stderr)
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
