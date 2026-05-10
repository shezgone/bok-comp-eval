"""
BoK-Comp-QA scorer.

Usage:
    python eval/scorer.py --validate
        Validate the dataset (qid uniqueness, schema-consistent normalized answers).

    python eval/scorer.py --gold eval/seed_questions.jsonl --pred path/to/preds.jsonl
        Score predictions against the gold set. Predictions are JSONL with at minimum:
            {"qid": "C1-001", "answer": "0.8"}
        Optional fields: "evidence" (list of strings), "backend" (which backend produced it).

Stdlib only — no external deps.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# ---------- Normalization helpers ----------

CURRENCY_TOKENS = {
    "원": "KRW", "krw": "KRW", "₩": "KRW",
    "usd": "USD", "$": "USD", "달러": "USD",
    "eur": "EUR", "€": "EUR", "유로": "EUR",
    "jpy": "JPY", "¥": "JPY", "엔": "JPY",
    "gbp": "GBP", "£": "GBP", "파운드": "GBP",
    "hkd": "HKD",
    "cny": "CNY", "위안": "CNY",
}

REFUSAL_PATTERNS = [
    r"명시(되|돼)(어 있)?지\s*않",
    r"해당\s*없",
    r"알\s*수\s*없",
    r"답할\s*수\s*없",
    r"찾을\s*수\s*없",
    r"범위\s*외",
    r"규정에\s*없",
    r"존재하지\s*않",
    r"확인할\s*수\s*없",
]

TRUE_PATTERNS = [
    r"\b(true|yes)\b",
    r"맞(다|음)",
    r"받을\s*수\s*있",
    r"가능(하|함)",
    r"적용(된다|됨|함)",
    r"대상(이다|임|이야)",
    r"초과(한다|함|함\b|임)",
    r"넘는다",
]
FALSE_PATTERNS = [
    r"\b(false|no)\b",
    r"아(니다|님|냐)",
    r"받을\s*수\s*없",
    r"불가능",
    r"적용(되지|하지)\s*않",
    r"대상\s*아님",
    r"초과하지\s*않",
    r"넘지\s*않",
]


def _strip(s: str) -> str:
    return s.strip().lower() if isinstance(s, str) else s


def _extract_numbers(text: str) -> list[float]:
    """All numeric tokens in text, ignoring commas. Returns floats."""
    cleaned = text.replace(",", "")
    # Match int, decimal, scientific
    matches = re.findall(r"-?\d+(?:\.\d+)?", cleaned)
    return [float(m) for m in matches]


def _detect_currency(text: str) -> str | None:
    low = text.lower()
    # Order matters — try multi-char first
    for token, code in sorted(CURRENCY_TOKENS.items(), key=lambda x: -len(x[0])):
        if token in low:
            return code
    return None


def _matches_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _is_refusal(text: str) -> bool:
    return _matches_any(text, REFUSAL_PATTERNS)


def _to_bool(text: str) -> bool | None:
    t = text.strip()
    has_neg = _matches_any(t, FALSE_PATTERNS)
    has_pos = _matches_any(t, TRUE_PATTERNS)
    if has_neg and not has_pos:
        return False
    if has_pos and not has_neg:
        return True
    # If both or neither, ambiguous
    return None


# ---------- Comparison per type ----------

@dataclass
class ScoreResult:
    qid: str
    category: str
    correct: bool
    reason: str
    pred_normalized: Any = None
    gold_normalized: Any = None


def _money_close(pred_val: float, gold_val: float) -> bool:
    # Exact match for currency amounts (no tolerance — regulations are exact)
    return pred_val == gold_val


def score_item(gold: dict, pred_answer: str) -> ScoreResult:
    qid = gold["qid"]
    cat = gold["category"]
    gn = gold["gold_answer_normalized"]
    gtype = gn["type"]
    pred_text = pred_answer if isinstance(pred_answer, str) else str(pred_answer)

    # Refusal handling — must come first; refusal in either pred or gold short-circuits
    if gtype == "refusal":
        ok = _is_refusal(pred_text)
        return ScoreResult(qid, cat, ok,
                           "refusal_correct" if ok else "expected_refusal_got_answer",
                           pred_normalized="<refusal>" if ok else pred_text,
                           gold_normalized="<refusal>")
    if _is_refusal(pred_text):
        return ScoreResult(qid, cat, False, "unexpected_refusal",
                           pred_normalized="<refusal>", gold_normalized=gn)

    if gtype == "money":
        nums = _extract_numbers(pred_text)
        if not nums:
            return ScoreResult(qid, cat, False, "no_number_in_prediction",
                               pred_normalized=pred_text, gold_normalized=gn)
        # Closest-to-gold: credit the answer if it appears anywhere, even alongside
        # incidental numbers like cap thresholds, grade labels (3급), or year stamps.
        target = gn["value"]
        pred_val = min(nums, key=lambda x: abs(x - target))
        amount_ok = _money_close(pred_val, gn["value"])
        # Currency check: required if gold specifies non-KRW
        gold_cur = gn.get("currency", "KRW")
        pred_cur = _detect_currency(pred_text) or "KRW"
        cur_ok = (pred_cur == gold_cur) or (gold_cur == "KRW" and pred_cur == "KRW")
        ok = amount_ok and cur_ok
        reason = ("ok" if ok
                  else f"amount={pred_val} vs gold={gn['value']}, cur={pred_cur} vs gold={gold_cur}")
        return ScoreResult(qid, cat, ok, reason,
                           pred_normalized={"value": pred_val, "currency": pred_cur},
                           gold_normalized=gn)

    if gtype == "number":
        nums = _extract_numbers(pred_text)
        if not nums:
            return ScoreResult(qid, cat, False, "no_number_in_prediction",
                               pred_normalized=pred_text, gold_normalized=gn)
        # For "count" / "year" / "step" etc., pick the closest match to gold (handles
        # cases where the pred phrase contains incidental numbers like "별표1-1").
        target = gn["value"]
        pred_val = min(nums, key=lambda x: abs(x - target))
        ok = pred_val == target
        return ScoreResult(qid, cat, ok,
                           "ok" if ok else f"value={pred_val} vs gold={target}",
                           pred_normalized=pred_val, gold_normalized=target)

    if gtype == "ratio":
        nums = _extract_numbers(pred_text)
        if not nums:
            return ScoreResult(qid, cat, False, "no_number_in_prediction",
                               pred_normalized=pred_text, gold_normalized=gn)
        target = gn["value"]
        # Allow percent form: "80%" -> 0.8
        candidates = list(nums) + [n / 100 for n in nums if n > 1]
        pred_val = min(candidates, key=lambda x: abs(x - target))
        ok = abs(pred_val - target) < 1e-9
        return ScoreResult(qid, cat, ok,
                           "ok" if ok else f"value={pred_val} vs gold={target}",
                           pred_normalized=pred_val, gold_normalized=target)

    if gtype == "boolean":
        pred_bool = _to_bool(pred_text)
        if pred_bool is None:
            return ScoreResult(qid, cat, False, "ambiguous_boolean",
                               pred_normalized=pred_text, gold_normalized=gn["value"])
        ok = pred_bool == gn["value"]
        return ScoreResult(qid, cat, ok, "ok" if ok else "wrong_polarity",
                           pred_normalized=pred_bool, gold_normalized=gn["value"])

    if gtype == "set":
        gold_set = {s.strip() for s in gn["value"]}
        # naive: check each gold token appears as substring in pred
        missing = [s for s in gold_set if s not in pred_text]
        # Also check no obviously wrong extras: count unique tokens that look like list items
        ok = not missing
        return ScoreResult(qid, cat, ok,
                           "ok" if ok else f"missing={missing}",
                           pred_normalized=pred_text, gold_normalized=sorted(gold_set))

    if gtype == "string":
        candidates = [gn["value"], *gn.get("aliases", [])]
        ok = any(c in pred_text for c in candidates)
        return ScoreResult(qid, cat, ok,
                           "ok" if ok else f"none_of {candidates} found",
                           pred_normalized=pred_text, gold_normalized=candidates)

    return ScoreResult(qid, cat, False, f"unknown_gold_type={gtype}",
                       pred_normalized=pred_text, gold_normalized=gn)


# ---------- I/O ----------

def load_jsonl(path: Path) -> list[dict]:
    items = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{i} invalid JSON: {e}") from e
    return items


# ---------- Validation ----------

def validate_dataset(gold: list[dict]) -> list[str]:
    errs: list[str] = []
    seen_qids: set[str] = set()
    qid_re = re.compile(r"^C(10|[1-9])-\d{3}$")
    valid_types = {"money", "number", "ratio", "boolean", "set", "string", "refusal"}
    valid_cats = {
        "single_lookup", "join_2key", "multihop_3key", "calculation",
        "article_text", "negation_exception", "aggregation", "comparison",
        "term_normalization", "out_of_scope",
    }

    for item in gold:
        qid = item.get("qid", "<missing>")
        if not qid_re.match(qid):
            errs.append(f"{qid}: malformed qid")
        if qid in seen_qids:
            errs.append(f"{qid}: duplicate qid")
        seen_qids.add(qid)

        for k in ("category", "difficulty", "question", "gold_answer",
                  "gold_answer_normalized", "evidence", "expected_backend"):
            if k not in item:
                errs.append(f"{qid}: missing field '{k}'")

        if item.get("category") not in valid_cats:
            errs.append(f"{qid}: bad category {item.get('category')!r}")

        gn = item.get("gold_answer_normalized", {})
        if gn.get("type") not in valid_types:
            errs.append(f"{qid}: bad gold_answer_normalized.type {gn.get('type')!r}")

        ev = item.get("evidence")
        if not isinstance(ev, list) or len(ev) < 1:
            errs.append(f"{qid}: evidence must be non-empty list")

    return errs


# ---------- Main ----------

def cmd_validate(args) -> int:
    gold_path = Path(args.gold)
    gold = load_jsonl(gold_path)
    errs = validate_dataset(gold)
    if errs:
        for e in errs:
            print(f"ERROR  {e}", file=sys.stderr)
        print(f"\n{len(errs)} validation error(s) in {len(gold)} items.", file=sys.stderr)
        return 1
    by_cat: dict[str, int] = defaultdict(int)
    for item in gold:
        by_cat[item["category"]] += 1
    print(f"OK  {len(gold)} items, no errors.")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat:24s} {n:3d}")
    return 0


def cmd_score(args) -> int:
    gold = {item["qid"]: item for item in load_jsonl(Path(args.gold))}
    preds = load_jsonl(Path(args.pred))
    pred_by_qid = {p["qid"]: p for p in preds}

    results: list[ScoreResult] = []
    for qid, item in gold.items():
        if qid not in pred_by_qid:
            results.append(ScoreResult(qid, item["category"], False, "missing_prediction"))
            continue
        results.append(score_item(item, pred_by_qid[qid].get("answer", "")))

    by_cat_total: dict[str, int] = defaultdict(int)
    by_cat_correct: dict[str, int] = defaultdict(int)
    for r in results:
        by_cat_total[r.category] += 1
        if r.correct:
            by_cat_correct[r.category] += 1

    total = len(results)
    correct = sum(1 for r in results if r.correct)

    print(f"# BoK-Comp-QA scoring report\n")
    print(f"Overall: {correct}/{total} = {correct/total*100:.1f}%\n")
    print("| category | correct | total | acc |")
    print("|---|---:|---:|---:|")
    for cat in sorted(by_cat_total):
        c, t = by_cat_correct[cat], by_cat_total[cat]
        print(f"| {cat} | {c} | {t} | {c/t*100:.1f}% |")

    failures = [r for r in results if not r.correct]
    if failures:
        print(f"\n## Failures ({len(failures)})\n")
        for r in failures:
            print(f"- **{r.qid}** [{r.category}] — {r.reason}")
            print(f"    pred: {r.pred_normalized!r}")
            print(f"    gold: {r.gold_normalized!r}")
    return 0 if not failures else 1


def main() -> int:
    p = argparse.ArgumentParser(description="BoK-Comp-QA scorer")
    p.add_argument("--gold", default="eval/seed_questions.jsonl",
                   help="Path to gold JSONL (default: eval/seed_questions.jsonl)")
    p.add_argument("--pred", help="Path to predictions JSONL")
    p.add_argument("--validate", action="store_true",
                   help="Validate dataset structure and exit")
    args = p.parse_args()

    if args.validate:
        return cmd_validate(args)
    if not args.pred:
        p.error("--pred is required unless --validate is used")
    return cmd_score(args)


if __name__ == "__main__":
    sys.exit(main())
