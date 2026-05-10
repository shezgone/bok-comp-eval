"""
BoK-Comp pilot analysis.

Reads predictions/*.jsonl, scores each run, and produces:
  1. Overall accuracy per (backend, llm) with 95% bootstrap CI
  2. Per-category accuracy table (rows = backend×llm, cols = category)
  3. McNemar (exact two-sided binomial) for the H1-relevant pairs:
       typedb_X  vs context_X
       neo4j_X   vs context_X
       <RAG>_X   vs closed_book_X   (RAG-effect, partly leakage signal)
  4. KG advantage on multi-key categories (multihop_3key, comparison)
  5. Closed-book accuracy as a leakage warning

Usage:
    python eval/analyze_pilot.py
    python eval/analyze_pilot.py --pred-dir predictions --gold eval/seed_questions.jsonl

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from eval.scorer import load_jsonl, score_item  # noqa: E402

BACKENDS = [
    "typedb", "neo4j", "context", "closed_book",
    "context_tql", "context_cypher", "context_nl", "context_jsonld",
]
KG_BACKENDS = ["typedb", "neo4j"]
CONTEXT_TIER_BACKENDS = [
    "context", "context_tql", "context_cypher", "context_nl", "context_jsonld",
]
MULTI_KEY_CATS = {"multihop_3key", "comparison", "calculation"}


# ---------- core scoring ----------

def score_run(gold: list[dict], preds: list[dict]) -> dict[str, bool]:
    pred_by_qid = {p["qid"]: p for p in preds}
    out: dict[str, bool] = {}
    for item in gold:
        qid = item["qid"]
        p = pred_by_qid.get(qid)
        if not p or p.get("error"):
            out[qid] = False
        else:
            out[qid] = score_item(item, p.get("answer", "")).correct
    return out


# ---------- statistics ----------

def overall_acc(scores: dict[str, bool]) -> float:
    n = len(scores)
    if n == 0:
        return 0.0
    return sum(1 for v in scores.values() if v) / n


def bootstrap_ci(scores: dict[str, bool], n_iter: int = 2000, seed: int = 0
                 ) -> tuple[float, float, float]:
    qids = list(scores.keys())
    n = len(qids)
    if n == 0:
        return (0.0, 0.0, 0.0)
    point = overall_acc(scores)
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n_iter):
        sub_correct = sum(1 for _ in range(n) if scores[rng.choice(qids)])
        samples.append(sub_correct / n)
    samples.sort()
    lo = samples[int(0.025 * n_iter)]
    hi = samples[min(int(0.975 * n_iter), n_iter - 1)]
    return (point, lo, hi)


def mcnemar_exact(a: dict[str, bool], b: dict[str, bool]) -> tuple[int, int, float]:
    """Exact two-sided binomial test on discordant pairs. Returns (a_only, b_only, p)."""
    qids = sorted(set(a) & set(b))
    a_only = sum(1 for q in qids if a[q] and not b[q])
    b_only = sum(1 for q in qids if b[q] and not a[q])
    n = a_only + b_only
    if n == 0:
        return (a_only, b_only, 1.0)
    k = min(a_only, b_only)
    cum = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    p = min(1.0, 2 * cum)
    return (a_only, b_only, p)


def per_category(gold: list[dict], scores: dict[str, bool]) -> dict[str, tuple[int, int]]:
    cats: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for item in gold:
        cat = item["category"]
        cats[cat][1] += 1
        if scores.get(item["qid"]):
            cats[cat][0] += 1
    return {k: (v[0], v[1]) for k, v in cats.items()}


# ---------- io ----------

def load_runs(pred_dir: Path) -> dict[tuple[str, str], list[dict]]:
    """Discover (backend, llm) pairs from filenames `{backend}_{llm}.jsonl`.

    Backend is matched from the known BACKENDS list (longest prefix wins so
    `closed_book_qwen` parses as backend=`closed_book`, llm=`qwen`). Anything
    after the backend is treated as the LLM tag, allowing arbitrary model
    aliases to flow through without code changes.
    """
    runs: dict[tuple[str, str], list[dict]] = {}
    sorted_backends = sorted(BACKENDS, key=len, reverse=True)
    for path in sorted(pred_dir.glob("*.jsonl")):
        stem = path.stem
        for backend in sorted_backends:
            prefix = f"{backend}_"
            if stem.startswith(prefix) and len(stem) > len(prefix):
                llm = stem[len(prefix):]
                runs[(backend, llm)] = load_jsonl(path)
                break
    return runs


def discover_llms(runs: dict[tuple[str, str], list[dict]]) -> list[str]:
    return sorted({llm for _, llm in runs})


# ---------- printing ----------

def fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def print_overall_table(scores_map: dict[tuple[str, str], dict[str, bool]],
                        llms: list[str]) -> None:
    print("\n## 1. Overall accuracy (95% bootstrap CI, 2000 iter)\n")
    print("| backend | LLM | n | acc | 95% CI |")
    print("|---|---|---:|---:|---|")
    for llm in llms:
        for backend in BACKENDS:
            key = (backend, llm)
            if key not in scores_map:
                continue
            s = scores_map[key]
            point, lo, hi = bootstrap_ci(s)
            print(f"| {backend} | {llm} | {len(s)} | {fmt_pct(point)} | "
                  f"[{fmt_pct(lo)}, {fmt_pct(hi)}] |")


def print_category_table(gold: list[dict],
                         scores_map: dict[tuple[str, str], dict[str, bool]],
                         llms: list[str]) -> None:
    cats = sorted({item["category"] for item in gold})
    print("\n## 2. Per-category accuracy\n")
    header = "| run | " + " | ".join(c[:6] for c in cats) + " |"
    sep = "|---|" + "---:|" * len(cats)
    print(header)
    print(sep)
    for llm in llms:
        for backend in BACKENDS:
            key = (backend, llm)
            if key not in scores_map:
                continue
            cells = []
            pc = per_category(gold, scores_map[key])
            for c in cats:
                cor, tot = pc.get(c, (0, 0))
                cells.append(fmt_pct(cor / tot) if tot else "—")
            print(f"| {backend}_{llm} | " + " | ".join(cells) + " |")
    print(f"\n_Categories: {', '.join(cats)}_")


def print_mcnemar_table(scores_map: dict[tuple[str, str], dict[str, bool]],
                        llms: list[str]) -> None:
    print("\n## 3. McNemar (exact two-sided binomial) — H1-relevant pairs\n")
    print("| comparison | LLM | A wins | B wins | p |")
    print("|---|---|---:|---:|---:|")
    pairs: list[tuple[str, str]] = [
        ("typedb", "context"),
        ("neo4j", "context"),
        ("typedb", "closed_book"),
        ("neo4j", "closed_book"),
        ("context", "closed_book"),
    ]
    for llm in llms:
        for a, b in pairs:
            ka, kb = (a, llm), (b, llm)
            if ka not in scores_map or kb not in scores_map:
                continue
            a_wins, b_wins, p = mcnemar_exact(scores_map[ka], scores_map[kb])
            print(f"| {a} vs {b} | {llm} | {a_wins} | {b_wins} | {p:.3f} |")


def print_kg_advantage(gold: list[dict],
                       scores_map: dict[tuple[str, str], dict[str, bool]],
                       llms: list[str]) -> None:
    print("\n## 4. KG advantage on multi-key categories (H1-m2 signal)\n")
    multi_qids = {it["qid"] for it in gold if it["category"] in MULTI_KEY_CATS}
    print(f"_Subset: {sorted(MULTI_KEY_CATS)}, n = {len(multi_qids)}_\n")
    print("| LLM | typedb | neo4j | context | closed_book |")
    print("|---|---:|---:|---:|---:|")
    for llm in llms:
        cells = []
        for backend in BACKENDS:
            key = (backend, llm)
            if key not in scores_map:
                cells.append("—")
                continue
            s = scores_map[key]
            sub = {q: s[q] for q in s if q in multi_qids}
            cells.append(fmt_pct(overall_acc(sub)) if sub else "—")
        print(f"| {llm} | " + " | ".join(cells) + " |")


def print_leakage_warning(scores_map: dict[tuple[str, str], dict[str, bool]],
                          llms: list[str]) -> None:
    print("\n## 5. Closed-book leakage signal\n")
    print("> Closed-book accuracy is a lower bound on what the LLM already knows.")
    print("> If high (≥30-40%), the RAG effect on this dataset is partly explained")
    print("> by the model's pretraining — flag in paper limitations.\n")
    print("| LLM | closed_book acc | n |")
    print("|---|---:|---:|")
    for llm in llms:
        key = ("closed_book", llm)
        if key not in scores_map:
            continue
        s = scores_map[key]
        print(f"| {llm} | {fmt_pct(overall_acc(s))} | {len(s)} |")


# ---------- main ----------

def main() -> int:
    p = argparse.ArgumentParser(description="BoK-Comp pilot analyzer")
    p.add_argument("--gold", default=str(ROOT / "eval" / "seed_questions.jsonl"))
    p.add_argument("--pred-dir", default=str(ROOT / "predictions"))
    args = p.parse_args()

    gold = load_jsonl(Path(args.gold))
    pred_dir = Path(args.pred_dir)
    if not pred_dir.exists():
        print(f"[analyze] no prediction dir at {pred_dir} — run eval/run_baseline.py first",
              file=sys.stderr)
        return 1

    runs = load_runs(pred_dir)
    if not runs:
        print(f"[analyze] no matching files in {pred_dir} (expected {{backend}}_{{llm}}.jsonl)",
              file=sys.stderr)
        return 1

    scores_map = {key: score_run(gold, preds) for key, preds in runs.items()}
    llms = discover_llms(runs)

    print(f"# BoK-Comp pilot analysis  (n_gold={len(gold)}, n_runs={len(runs)}, "
          f"llms={llms})")
    print_overall_table(scores_map, llms)
    print_category_table(gold, scores_map, llms)
    print_mcnemar_table(scores_map, llms)
    print_kg_advantage(gold, scores_map, llms)
    print_leakage_warning(scores_map, llms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
