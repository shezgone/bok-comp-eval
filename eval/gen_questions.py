"""
Auto-expand the eval set by 70 items.

Strategy: import the data tables already defined in dump_context_tiers.py
(single source of truth) and walk them with category-specific templates.
Each generated item carries a deterministic gold_answer derived from the
table — no LLM in the loop, no fuzziness.

Distribution (70 total) — weighted toward multi-key for H1 power:
  multihop_3key       12   (3-key country+grade+currency, position+grade)
  calculation         10   (input salary + diff, overtime, etc.)
  comparison          10   (Δ between two table rows)
  join_2key            7
  single_lookup        7
  aggregation          7
  out_of_scope         4
  term_normalization   3
  negation_exception   5   (semi-auto via known boundary cases)
  article_text         5   (semi-auto from regulation_context.md article quotes)

Total: 70.

QID range: C{cat}-1xx (seed uses 0xx) so no collision with seed.

Output: eval/expanded_questions.jsonl
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from dump_context_tiers import (  # type: ignore  # noqa: E402
    SALARY_TABLE_K, POSITION_NAMES, POSITION_PAY_TABLE_K, SALARY_DIFF_TABLE_K,
    SALARY_CAP_TABLE_K, WAGE_PEAK_TABLE, BONUS_RATE_TABLE,
    OVERSEAS_PAY_TABLE, STARTING_STEP_TABLE, k_to_won,
)

OUT_PATH = ROOT / "eval" / "expanded_questions.jsonl"
SEED_PATH = ROOT / "eval" / "seed_questions.jsonl"

GRADES = ["1급", "2급", "3급", "4급", "5급", "6급"]
EVAL_GRADES = ["EX", "EE", "ME", "BE"]


# ============================================================
# QID factory — ensure no collision with seed (which uses Cn-0xx)
# ============================================================

CAT_PREFIX = {
    "single_lookup": "C1",
    "join_2key": "C2",
    "multihop_3key": "C3",
    "calculation": "C4",
    "article_text": "C5",
    "negation_exception": "C6",
    "aggregation": "C7",
    "comparison": "C8",
    "term_normalization": "C9",
    "out_of_scope": "C10",
}


def make_qid(cat: str, idx: int) -> str:
    return f"{CAT_PREFIX[cat]}-1{idx:02d}"  # 100..199


# ============================================================
# Item factory — minimal valid schema with sensible defaults
# ============================================================

def item(*, qid: str, category: str, difficulty: str, question: str,
         gold_answer: str, gold_normalized: dict, evidence: list,
         required_keys: list, expected_backend: str = "any",
         requires_calculation: bool = False, requires_text_reasoning: bool = False,
         paraphrases: list | None = None, distractors: list | None = None) -> dict:
    return {
        "qid": qid,
        "category": category,
        "difficulty": difficulty,
        "question": question,
        "gold_answer": gold_answer,
        "gold_answer_normalized": gold_normalized,
        "evidence": evidence,
        "required_keys": required_keys,
        "expected_backend": expected_backend,
        "requires_calculation": requires_calculation,
        "requires_text_reasoning": requires_text_reasoning,
        "paraphrases": paraphrases or [],
        "negative_distractors": distractors or [],
    }


# ============================================================
# Generators
# ============================================================

rng = random.Random(20260510)


def gen_single_lookup() -> list[dict]:
    """Pure 1-key lookup. 7 items."""
    out = []
    # 4 from SALARY_TABLE — pick step in mid range to avoid edge effects
    grade_step_picks = [
        ("3급", 27, 4102), ("4급", 30, 3780),
        ("5급", 35, 4669), ("6급", 40, 4372),
    ]
    for i, (g, step, amt_k) in enumerate(grade_step_picks):
        amt = k_to_won(amt_k)
        out.append(item(
            qid=make_qid("single_lookup", len(out) + 1),
            category="single_lookup",
            difficulty="easy",
            question=f"{g} {step}호봉의 본봉은 얼마인가?",
            gold_answer=f"{amt:,}원",
            gold_normalized={"type": "money", "value": amt,
                              "currency": "KRW", "period": "monthly"},
            evidence=[{"source": "별표1 본봉표 / " + g, "row": {"호봉": step}}],
            required_keys=["grade", "step"],
        ))
    # 1 cap, 1 wage peak, 1 starting step
    out.append(item(
        qid=make_qid("single_lookup", len(out) + 1),
        category="single_lookup",
        difficulty="easy",
        question="2급 직원의 연봉 상한액은 얼마인가?",
        gold_answer="78,540,000원",
        gold_normalized={"type": "money", "value": 78540000,
                          "currency": "KRW", "period": "annual"},
        evidence=[{"source": "별표8 연봉 상한액표", "row": {"직급": "2급"}}],
        required_keys=["grade"],
    ))
    out.append(item(
        qid=make_qid("single_lookup", len(out) + 1),
        category="single_lookup",
        difficulty="easy",
        question="임금피크제 3년차의 기본급 지급률은?",
        gold_answer="0.7",
        gold_normalized={"type": "ratio", "value": 0.7},
        evidence=[{"source": "별표9 임금피크제 기본급 지급률표",
                   "row": {"적용연차": 3}}],
        required_keys=["year"],
    ))
    out.append(item(
        qid=make_qid("single_lookup", len(out) + 1),
        category="single_lookup",
        difficulty="easy",
        question="별정직원의 초임호봉은 몇 호봉인가?",
        gold_answer="4호봉",
        gold_normalized={"type": "number", "value": 4, "unit": "step"},
        evidence=[{"source": "별표2 초임호봉표", "row": {"직렬": "별정직원"}}],
        required_keys=["job_family"],
    ))
    return out


def gen_join_2key() -> list[dict]:
    """2-key joins. 7 items."""
    out = []
    # SALARY_TABLE rows (grade, step) — pick scattered
    salary_picks = [("4급", 25, 3780), ("5급", 22, 3535), ("6급", 26, 3175)]
    for g, step, amt_k in salary_picks:
        amt = k_to_won(amt_k)
        out.append(item(
            qid=make_qid("join_2key", len(out) + 1),
            category="join_2key",
            difficulty="easy",
            question=f"{g} {step}호봉 본봉은 얼마인가?",
            gold_answer=f"{amt:,}원",
            gold_normalized={"type": "money", "value": amt,
                              "currency": "KRW", "period": "monthly"},
            evidence=[{"source": "별표1 본봉표 / " + g,
                       "row": {"직급": g, "호봉": step}}],
            required_keys=["grade", "step"],
        ))
    # SALARY_DIFF_TABLE rows (grade, eval_grade)
    diff_picks = [("1급", "EE"), ("2급", "EX"), ("2급", "ME"), ("3급", "EX")]
    for g, eg in diff_picks:
        amt_k = next(d for (gg, ee, d) in SALARY_DIFF_TABLE_K if gg == g and ee == eg)
        amt = k_to_won(amt_k)
        out.append(item(
            qid=make_qid("join_2key", len(out) + 1),
            category="join_2key",
            difficulty="easy",
            question=f"{g} {eg} 등급의 연봉 차등액은?",
            gold_answer=f"{amt:,}원",
            gold_normalized={"type": "money", "value": amt,
                              "currency": "KRW", "period": "annual"},
            evidence=[{"source": "별표7 연봉 차등액표",
                       "row": {"직급": g, "평가등급": eg}}],
            required_keys=["grade", "evaluation_grade"],
        ))
    return out


def gen_multihop_3key() -> list[dict]:
    """3-key joins (H1 핵심). 12 items: 8 overseas + 4 position-pay."""
    out = []
    # Overseas: country + grade + currency
    overseas_picks = [
        ("미국", "USD", "1급", 10780), ("미국", "USD", "3급", 8620),
        ("일본", "JPY", "2급", 1097000),
        ("독일", "EUR", "1급", 9100),
        ("영국", "GBP", "1급", 7790), ("영국", "GBP", "2급", 7050),
        ("중국", "CNY", "2급", 68800),
        ("홍콩", "HKD", "1급", 80300),
    ]
    for country, currency, g, amt in overseas_picks:
        out.append(item(
            qid=make_qid("multihop_3key", len(out) + 1),
            category="multihop_3key",
            difficulty="medium",
            question=f"{country} 주재 {g} 직원의 월 국외본봉은 통화 단위까지 포함해 얼마인가?",
            gold_answer=f"{amt:,} {currency}",
            gold_normalized={"type": "money", "value": amt,
                              "currency": currency, "period": "monthly"},
            evidence=[{"source": "별표1-5 국외본봉표",
                       "row": {"국가": country, "직급": g}}],
            required_keys=["country", "grade", "currency"],
            expected_backend="typedb",
        ))
    # Position pay: position_code + position_name + grade
    position_picks = [
        ("P02", "1급", 15792),  # 부서장(나) 1급
        ("P03", "2급", 5736),   # 국소속실장 2급
        ("P04", "3급", 2868),   # 부장 3급
        ("P07", "2급", 3012),   # 조사역 2급
    ]
    for pcode, g, amt_k in position_picks:
        pname = POSITION_NAMES[pcode]
        amt = k_to_won(amt_k)
        out.append(item(
            qid=make_qid("multihop_3key", len(out) + 1),
            category="multihop_3key",
            difficulty="medium",
            question=f"{pname} 직위의 {g} 직원의 연간 직책급은 얼마인가?",
            gold_answer=f"{amt:,}원",
            gold_normalized={"type": "money", "value": amt,
                              "currency": "KRW", "period": "annual"},
            evidence=[{"source": "별표1-1 직책급표",
                       "row": {"직위": pname, "직급": g}}],
            required_keys=["position", "grade"],
            expected_backend="typedb",
        ))
    return out


def gen_calculation() -> list[dict]:
    """Calculation. 10 items."""
    out = []
    # Salary diff calc — current + diff for 1급/2급/3급 × 등급
    cases = [
        ("1급", "EE", 75_000_000),
        ("2급", "EX", 70_000_000),
        ("2급", "ME", 65_000_000),
        ("3급", "EX", 65_000_000),
        ("3급", "ME", 60_000_000),
    ]
    for g, eg, current in cases:
        diff_k = next(d for (gg, ee, d) in SALARY_DIFF_TABLE_K
                      if gg == g and ee == eg)
        diff = k_to_won(diff_k)
        result = current + diff
        out.append(item(
            qid=make_qid("calculation", len(out) + 1),
            category="calculation",
            difficulty="medium",
            question=f"현재 연봉제 본봉이 {current:,}원인 {g} 직원의 평가등급이 "
                     f"{eg}이면, 조정 후 연봉제 본봉은 얼마인가?",
            gold_answer=f"{result:,}원",
            gold_normalized={"type": "money", "value": result,
                              "currency": "KRW", "period": "annual"},
            evidence=[
                {"source": "제4조"},
                {"source": "별표7 연봉 차등액표",
                 "row": {"직급": g, "평가등급": eg}},
            ],
            required_keys=["current_salary", "grade", "evaluation_grade"],
            expected_backend="hybrid",
            requires_calculation=True,
            requires_text_reasoning=True,
        ))
    # Cap-clamping cases
    cap_cases = [
        ("1급", "EX", 84_000_000),  # 84M + 3672K = 87672K, exceeds cap 85728K
        ("2급", "EX", 76_000_000),  # 76M + 3348K = 79348K, exceeds 78540K
    ]
    for g, eg, current in cap_cases:
        diff_k = next(d for (gg, ee, d) in SALARY_DIFF_TABLE_K
                      if gg == g and ee == eg)
        diff = k_to_won(diff_k)
        cap_k = next(c for (gg, c) in SALARY_CAP_TABLE_K if gg == g)
        cap = k_to_won(cap_k)
        raw = current + diff
        clamped = min(raw, cap)
        out.append(item(
            qid=make_qid("calculation", len(out) + 1),
            category="calculation",
            difficulty="medium",
            question=f"현재 연봉제 본봉이 {current:,}원인 {g} 직원이 {eg} 등급을 "
                     f"받았을 때 조정 후 연봉제 본봉은 얼마인가? (상한 적용 후)",
            gold_answer=f"{clamped:,}원",
            gold_normalized={"type": "money", "value": clamped,
                              "currency": "KRW", "period": "annual"},
            evidence=[
                {"source": "제4조"},
                {"source": "별표7", "row": {"직급": g, "평가등급": eg}},
                {"source": "별표8", "row": {"직급": g}},
            ],
            required_keys=["current_salary", "grade", "evaluation_grade"],
            expected_backend="hybrid",
            requires_calculation=True,
            requires_text_reasoning=True,
        ))
    # Overtime: 통상임금 / 209 * 1.5 * hours
    overtime_cases = [(3_762_000, 8), (4_180_000, 5), (5_016_000, 12)]
    for wage, hours in overtime_cases:
        per_hour = round(wage / 209)
        result = round(per_hour * 1.5 * hours)
        # Round to nearest thousand for cleaner gold (production rounds too)
        result = round(result / 1000) * 1000
        out.append(item(
            qid=make_qid("calculation", len(out) + 1),
            category="calculation",
            difficulty="medium",
            question=f"통상임금 월지급액이 {wage:,}원인 직원이 시간외근무를 "
                     f"{hours}시간 했을 때 시간외근무수당은 얼마인가?",
            gold_answer=f"{result:,}원",
            gold_normalized={"type": "money", "value": result,
                              "currency": "KRW", "period": "lumpsum"},
            evidence=[{"source": "제9조"}],
            required_keys=["monthly_wage", "overtime_hours"],
            expected_backend="context",
            requires_calculation=True,
            requires_text_reasoning=True,
        ))
    return out


def gen_comparison() -> list[dict]:
    """Comparison (Δ between rows). 10 items."""
    out = []
    # Overseas Δ (same country, two grades)
    overseas_pairs = [
        ("일본", "JPY", "1급", 1210000, "2급", 1097000),
        ("독일", "EUR", "1급", 9100, "2급", 8240),
        ("중국", "CNY", "1급", 76000, "2급", 68800),
        ("홍콩", "HKD", "1급", 80300, "2급", 72700),
        ("영국", "GBP", "1급", 7790, "2급", 7050),
    ]
    for country, currency, g1, a1, g2, a2 in overseas_pairs:
        delta = a1 - a2
        out.append(item(
            qid=make_qid("comparison", len(out) + 1),
            category="comparison",
            difficulty="easy",
            question=f"{country} 주재 {g1}과 {g2} 직원의 월 국외본봉 차액은?",
            gold_answer=f"{delta:,} {currency}",
            gold_normalized={"type": "money", "value": delta,
                              "currency": currency, "period": "monthly"},
            evidence=[
                {"source": "별표1-5 국외본봉표",
                 "row": {"국가": country, "직급": g1}},
                {"source": "별표1-5 국외본봉표",
                 "row": {"국가": country, "직급": g2}},
            ],
            required_keys=["country", "grade"],
            expected_backend="neo4j",
            requires_calculation=True,
        ))
    # Salary diff Δ (same eval grade, different job grade)
    diff_pairs = [
        ("1급", "EE", "3급", "EE"),
        ("1급", "ME", "3급", "ME"),
        ("2급", "EX", "3급", "EX"),
        ("1급", "EX", "2급", "EX"),
        ("2급", "EE", "3급", "EE"),
    ]
    for g1, eg1, g2, eg2 in diff_pairs:
        a1_k = next(d for (gg, ee, d) in SALARY_DIFF_TABLE_K
                    if gg == g1 and ee == eg1)
        a2_k = next(d for (gg, ee, d) in SALARY_DIFF_TABLE_K
                    if gg == g2 and ee == eg2)
        delta = k_to_won(a1_k - a2_k)
        out.append(item(
            qid=make_qid("comparison", len(out) + 1),
            category="comparison",
            difficulty="easy",
            question=f"{g1} {eg1} 등급과 {g2} {eg2} 등급의 연봉 차등액 차이는?",
            gold_answer=f"{delta:,}원",
            gold_normalized={"type": "money", "value": delta,
                              "currency": "KRW", "period": "annual"},
            evidence=[
                {"source": "별표7", "row": {"직급": g1, "평가등급": eg1}},
                {"source": "별표7", "row": {"직급": g2, "평가등급": eg2}},
            ],
            required_keys=["grade", "evaluation_grade"],
            expected_backend="neo4j",
            requires_calculation=True,
        ))
    return out


def gen_aggregation() -> list[dict]:
    """Aggregation. 7 items."""
    out = []
    # 1) Number of grades
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="easy",
        question="보수규정의 직급은 몇 개로 구성되어 있는가?",
        gold_answer="6개",
        gold_normalized={"type": "number", "value": 6, "unit": "count"},
        evidence=[{"source": "별표1 본봉표 / 직급 목록"}],
        required_keys=[],
    ))
    # 2) Number of position codes
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="medium",
        question="보수규정에 정의된 직위 종류는 몇 개인가?",
        gold_answer=f"{len(POSITION_NAMES)}개",
        gold_normalized={"type": "number", "value": len(POSITION_NAMES),
                          "unit": "count"},
        evidence=[{"source": "별표1-1 직책급표 / 직위 목록"}],
        required_keys=[],
    ))
    # 3) Distinct (grade, eval_grade) combos with non-zero diff
    nz_diff = sum(1 for (_, _, d) in SALARY_DIFF_TABLE_K if d > 0)
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="medium",
        question="연봉 차등액표에서 차등액이 0이 아닌 (직급, 평가등급) 조합의 수는?",
        gold_answer=f"{nz_diff}개",
        gold_normalized={"type": "number", "value": nz_diff, "unit": "count"},
        evidence=[{"source": "별표7", "row": {"조건": "differential > 0"}}],
        required_keys=["grade", "evaluation_grade", "differential"],
        expected_backend="neo4j",
        requires_calculation=True,
    ))
    # 4) Number of overseas country
    countries = sorted({c for (c, _, _, _) in OVERSEAS_PAY_TABLE})
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="medium",
        question="국외본봉표에 포함된 국가는 몇 개국인가?",
        gold_answer=f"{len(countries)}개국",
        gold_normalized={"type": "number", "value": len(countries),
                          "unit": "count"},
        evidence=[{"source": "별표1-5 국외본봉표 / 국가 목록"}],
        required_keys=["country"],
        expected_backend="neo4j",
    ))
    # 5) Position counts for grade 2급
    g2_positions = sorted({POSITION_NAMES[p] for (p, gg, _) in POSITION_PAY_TABLE_K
                           if gg == "2급"})
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="medium",
        question="직책급표에 따르면 2급 직원이 가질 수 있는 직위는 몇 개인가?",
        gold_answer=f"{len(g2_positions)}개",
        gold_normalized={"type": "number", "value": len(g2_positions),
                          "unit": "count"},
        evidence=[{"source": "별표1-1 직책급표", "row": {"직급": "2급"}}],
        required_keys=["grade", "position"],
        expected_backend="neo4j",
    ))
    # 6) Distinct currencies
    currencies = sorted({cur for (_, cur, _, _) in OVERSEAS_PAY_TABLE})
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="medium",
        question="국외본봉표에 사용된 통화 종류는 몇 개인가?",
        gold_answer=f"{len(currencies)}개",
        gold_normalized={"type": "number", "value": len(currencies),
                          "unit": "count"},
        evidence=[{"source": "별표1-5 국외본봉표 / 통화 목록"}],
        required_keys=["currency"],
        expected_backend="neo4j",
    ))
    # 7) Wage peak years
    out.append(item(
        qid=make_qid("aggregation", len(out) + 1),
        category="aggregation",
        difficulty="easy",
        question="임금피크제 적용 가능한 연차는 최대 몇 년인가?",
        gold_answer=f"{max(y for y, _ in WAGE_PEAK_TABLE)}년",
        gold_normalized={"type": "number", "value": max(y for y, _ in WAGE_PEAK_TABLE),
                          "unit": "year"},
        evidence=[{"source": "별표9 임금피크제 기본급 지급률표"}],
        required_keys=[],
    ))
    return out


def gen_out_of_scope() -> list[dict]:
    """Combinations not present in tables. 4 items."""
    out = []
    # (직위, 직급) not in POSITION_PAY_TABLE
    valid_pp = {(p, g) for (p, g, _) in POSITION_PAY_TABLE_K}
    # 부서장(가) only has 1급/2급 — ask 3급
    cases = [
        ("P01", "3급", "부서장(가)"),  # not present
        ("P05", "5급", "팀장"),         # not present
        ("P09", "3급", "조사역(C2)"),   # not present
    ]
    for pcode, g, pname in cases:
        assert (pcode, g) not in valid_pp
        out.append(item(
            qid=make_qid("out_of_scope", len(out) + 1),
            category="out_of_scope",
            difficulty="medium",
            question=f"{pname} 직위의 {g} 직원의 연간 직책급은?",
            gold_answer=f"직책급표에 ({pname}, {g}) 조합이 없음 — 해당 없음",
            gold_normalized={"type": "refusal"},
            evidence=[{"source": "별표1-1 직책급표",
                       "quote": f"{pname}은 해당 직급에 정의되어 있지 않음"}],
            required_keys=["position", "grade"],
        ))
    # Country not in overseas table
    out.append(item(
        qid=make_qid("out_of_scope", len(out) + 1),
        category="out_of_scope",
        difficulty="medium",
        question="프랑스 주재 1급 직원의 월 국외본봉은?",
        gold_answer="국외본봉표에 프랑스가 없음 — 명시되지 않음",
        gold_normalized={"type": "refusal"},
        evidence=[{"source": "별표1-5 국외본봉표",
                   "quote": "프랑스는 표에 포함되어 있지 않음"}],
        required_keys=["country", "grade"],
    ))
    return out


def gen_term_normalization() -> list[dict]:
    """Term aliases. 3 items."""
    out = [
        item(
            qid=make_qid("term_normalization", 1),
            category="term_normalization",
            difficulty="easy",
            question="'종합기획 5급'을 부르는 약어 코드는?",
            gold_answer="G5",
            gold_normalized={"type": "string", "value": "G5",
                              "aliases": ["G5", "지파이브"]},
            evidence=[{"source": "regulation_context.md#용어 정규화",
                       "quote": "G5 = 종합기획직원 5급 = 종합기획 5급"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("term_normalization", 2),
            category="term_normalization",
            difficulty="easy",
            question="보수규정에서 '국외본봉'은 다른 어떤 용어로도 불리는가?",
            gold_answer="해외 기본급",
            gold_normalized={"type": "string", "value": "해외 기본급",
                              "aliases": ["해외 기본급", "주재 본봉"]},
            evidence=[{"source": "regulation_context.md#용어 정규화"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("term_normalization", 3),
            category="term_normalization",
            difficulty="easy",
            question="'성과평가 결과'는 보수규정에서 무엇과 동일한 개념인가?",
            gold_answer="평가등급",
            gold_normalized={"type": "string", "value": "평가등급",
                              "aliases": ["평가등급", "EX/EE/ME/BE"]},
            evidence=[{"source": "regulation_context.md#용어 정규화",
                       "quote": "성과평가 결과 = 평가등급"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
    ]
    return out


def gen_negation_exception() -> list[dict]:
    """Boundary / exception cases. 5 items."""
    out = []
    # P05 (팀장) 4급 → 직책급 0
    out.append(item(
        qid=make_qid("negation_exception", 1),
        category="negation_exception",
        difficulty="medium",
        question="조사역(C2) 직위의 5급 직원의 연간 직책급은?",
        gold_answer="0원",
        gold_normalized={"type": "money", "value": 0,
                          "currency": "KRW", "period": "annual"},
        evidence=[{"source": "별표1-1 직책급표",
                   "row": {"직위": "조사역(C2)", "직급": "5급"}}],
        required_keys=["position", "grade"],
    ))
    # 잔여근무기간 boundary
    out.append(item(
        qid=make_qid("negation_exception", 2),
        category="negation_exception",
        difficulty="medium",
        question="잔여근무기간이 정확히 3년인 직원은 임금피크제 적용 대상인가?",
        gold_answer="대상이다",
        gold_normalized={"type": "boolean", "value": True},
        evidence=[{"source": "제4조",
                   "quote": "임금피크제본봉은 잔여근무기간이 3년 이하인 직원을 대상으로 한다"}],
        required_keys=[],
        expected_backend="context",
        requires_text_reasoning=True,
    ))
    # 1급 직원 EE면 본봉 차등 ↑하지만 상한 가능성 — 큰 입력
    out.append(item(
        qid=make_qid("negation_exception", 3),
        category="negation_exception",
        difficulty="medium",
        question="현재 연봉제 본봉이 90,000,000원이라고 잘못 주어진 1급 직원의 조정은? "
                  "(상한액 초과 시 어떻게 되는가)",
        gold_answer="조정 후도 1급 상한액 85,728,000원으로 캡 적용",
        gold_normalized={"type": "money", "value": 85728000,
                          "currency": "KRW", "period": "annual"},
        evidence=[{"source": "별표8 연봉 상한액표", "row": {"직급": "1급"}}],
        required_keys=["current_salary", "grade"],
        requires_calculation=True,
        requires_text_reasoning=True,
    ))
    # P10 6급 → 0원
    out.append(item(
        qid=make_qid("negation_exception", 4),
        category="negation_exception",
        difficulty="medium",
        question="조사역(C3) 직위의 6급 직원의 연간 직책급은?",
        gold_answer="0원",
        gold_normalized={"type": "money", "value": 0,
                          "currency": "KRW", "period": "annual"},
        evidence=[{"source": "별표1-1 직책급표",
                   "row": {"직위": "조사역(C3)", "직급": "6급"}}],
        required_keys=["position", "grade"],
    ))
    # BE 등급은 차등 0
    out.append(item(
        qid=make_qid("negation_exception", 5),
        category="negation_exception",
        difficulty="medium",
        question="2급 직원이 BE 등급을 받았을 때 연봉 차등액은?",
        gold_answer="0원",
        gold_normalized={"type": "money", "value": 0,
                          "currency": "KRW", "period": "annual"},
        evidence=[{"source": "별표7", "row": {"직급": "2급", "평가등급": "BE"}}],
        required_keys=["grade", "evaluation_grade"],
    ))
    return out


def gen_article_text() -> list[dict]:
    """Article-text questions sourced from regulation_context.md article quotes.
    Hand-crafted (5)."""
    out = [
        item(
            qid=make_qid("article_text", 1),
            category="article_text",
            difficulty="easy",
            question="제2조에서 '제수당'은 국내직원의 경우 어떤 수당으로 정의되는가?",
            gold_answer="업무수당 및 시간외근무수당",
            gold_normalized={"type": "set", "value": ["업무수당", "시간외근무수당"]},
            evidence=[{"source": "제2조",
                       "quote": "제수당이란 국내직원의 경우 업무수당 및 시간외근무수당을 말하며"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("article_text", 2),
            category="article_text",
            difficulty="easy",
            question="해외직원의 경우 '제수당'은 어떤 수당을 말하는가?",
            gold_answer="조정수당",
            gold_normalized={"type": "string", "value": "조정수당",
                              "aliases": ["조정수당"]},
            evidence=[{"source": "제2조"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("article_text", 3),
            category="article_text",
            difficulty="easy",
            question="시간외근무수당 계산에서 시간당 보수는 통상임금 월지급액의 몇 분의 1로 산정되는가?",
            gold_answer="209분의 1",
            gold_normalized={"type": "number", "value": 209, "unit": "fraction"},
            evidence=[{"source": "제9조",
                       "quote": "시간당 보수는 통상임금 월지급액의 209분의 1로 한다"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("article_text", 4),
            category="article_text",
            difficulty="easy",
            question="기한부 고용계약자에게 적용되지 않는 규정 장은 무엇인가?",
            gold_answer="제2장 보수 및 제3장 상여금",
            gold_normalized={"type": "set", "value": ["제2장 보수", "제3장 상여금"]},
            evidence=[{"source": "제14조",
                       "quote": "기한부 고용계약자에 대하여는 제2장 보수 및 제3장 상여금에 관한 규정을 적용하지 아니한다"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
        item(
            qid=make_qid("article_text", 5),
            category="article_text",
            difficulty="easy",
            question="연봉제본봉 계산에서 직전 연봉제본봉에 합하는 것은 무엇인가?",
            gold_answer="별표7의 평가등급별 차등액",
            gold_normalized={"type": "string", "value": "별표7의 평가등급별 차등액",
                              "aliases": ["평가등급별 차등액", "연봉 차등액"]},
            evidence=[{"source": "제4조",
                       "quote": "연봉제본봉은 직전 연봉제본봉에 별표7의 평가등급별 차등액을 합한 금액으로 한다"}],
            required_keys=[],
            expected_backend="context",
            requires_text_reasoning=True,
        ),
    ]
    return out


# ============================================================
# Main
# ============================================================

def main() -> int:
    items: list[dict] = []
    items += gen_single_lookup()
    items += gen_join_2key()
    items += gen_multihop_3key()
    items += gen_calculation()
    items += gen_comparison()
    items += gen_aggregation()
    items += gen_out_of_scope()
    items += gen_term_normalization()
    items += gen_negation_exception()
    items += gen_article_text()

    # Quick collision check vs seed
    seed_qids = set()
    if SEED_PATH.exists():
        for line in SEED_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                seed_qids.add(json.loads(line)["qid"])
    for it in items:
        if it["qid"] in seed_qids:
            sys.exit(f"qid collision with seed: {it['qid']}")

    # Write output
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    # Distribution report
    from collections import Counter
    cats = Counter(it["category"] for it in items)
    print(f"wrote {OUT_PATH} ({len(items)} items)")
    for cat in sorted(cats):
        print(f"  {cat:24s} {cats[cat]:3d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
