"""
Generate four context-format tiers (C-TQL, C-Cypher, C-NL, C-JSONLD)
from production data tables. C-MD baseline is the existing
regulation_context.md (left untouched).

For each fact (e.g. "3급 28호봉 본봉 = 4,419,000원") the tiers express
the same content in different surface forms — the only variable in the
fairness ablation. Article text (조문) is shared across all tiers as a
common prefix; only the structured-data section varies.

Output:
  eval/context_tiers/regulation_tql.md
  eval/context_tiers/regulation_cypher.md
  eval/context_tiers/regulation_nl.md
  eval/context_tiers/regulation_jsonld.md

Stdlib only (data values inlined).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIERS_DIR = ROOT / "eval" / "context_tiers"
TIERS_DIR.mkdir(parents=True, exist_ok=True)

# Production schema for context (조문 + 용어 + 계산 규칙) — copied verbatim.
CONTEXT_MD_PATH = Path(
    "/Users/user/vibe/bok-compensation-regulations/src/bok_compensation_context/regulation_context.md"
)


# ============================================================
# 1. SOURCE OF TRUTH — fact tables (mirror production data_tables.py +
# typedb/insert_data.py supplements). All amounts in won unless noted.
# ============================================================

# 별표1 본봉표 (천원 단위 → 원 단위로 변환)
SALARY_TABLE_K = {
    "3급": [
        100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000,
        3188, 3300, 3642, 3752, 3869, 3984, 4102, 4419, 4530, 4654,
        4763, 5006, 5187, 5312, 5430, 5555, 5690, 5821, 5925, 6032,
        6142, 6229, 6316, 6399, 6495, 6583, 6657, 6738, 6812, 6890,
    ],
    "4급": [
        600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1554, 1600, 1700, 1800, 1900, 2000,
        2343, 2642, 2754, 2867, 2980, 3093, 3204, 3542, 3662, 3780,
        3893, 4095, 4417, 4529, 4650, 4762, 4882, 5057, 5183, 5300,
        5421, 5539, 5669, 5778, 5889, 5992, 6082, 6170, 6257, 6340,
        6428, 6499, 6576, 6657, 6733,
    ],
    "5급": [
        579, 651, 715, 787, 862, 936, 1011, 1096, 1181, 1265,
        1554, 1689, 1837, 1977, 2127, 2307, 2579, 2753, 2858, 2973,
        3081, 3196, 3535, 3658, 3770, 3889, 4002, 4323, 4440, 4549,
        4669, 4780, 4962, 5089, 5209, 5326, 5448, 5574, 5678, 5788,
        5894, 5983, 6063, 6153, 6236, 6327, 6400, 6476, 6555, 6635,
    ],
    "6급": [
        559, 620, 675, 743, 805, 871, 944, 1000, 1045, 1090,
        1509, 1591, 1672, 1757, 1835, 2106, 2196, 2286, 2372, 2462,
        2640, 2730, 2818, 2909, 2999, 3175, 3267, 3353, 3440, 3523,
        3610, 3695, 3782, 3867, 3953, 4035, 4123, 4207, 4290, 4372,
        4451, 4537, 4615, 4699, 4781, 4849, 4914, 4982, 5052, 5122,
    ],
}

# 직위코드 ↔ 직위명
POSITION_NAMES = {
    "P01": "부서장(가)",
    "P02": "부서장(나)",
    "P03": "국소속실장",
    "P04": "부장",
    "P05": "팀장",
    "P06": "반장",
    "P07": "조사역",
    "P08": "주임조사역(C1)",
    "P09": "조사역(C2)",
    "P10": "조사역(C3)",
}

# 별표1-1 직책급표 (직위코드, 직급, 연간 직책급, 천원)
POSITION_PAY_TABLE_K = [
    ("P01", "1급", 18192), ("P01", "2급", 16236),
    ("P02", "1급", 15792), ("P02", "2급", 13836),
    ("P03", "1급", 7692),  ("P03", "2급", 5736),
    ("P04", "2급", 4824),  ("P04", "3급", 2868),
    ("P05", "3급", 1956),  ("P05", "4급", 0),
    ("P07", "2급", 3012),  ("P07", "3급", 1056),
    ("P08", "3급", 1956),  ("P08", "4급", 0),
    ("P09", "4급", 1044),  ("P09", "5급", 0),
    ("P10", "5급", 1044),  ("P10", "6급", 0),
]

# 별표7 연봉제본봉 차등액 (직급, 평가등급, 차등액 천원)
SALARY_DIFF_TABLE_K = [
    ("1급", "EX", 3672), ("1급", "EE", 2448), ("1급", "ME", 1224), ("1급", "BE", 0),
    ("2급", "EX", 3348), ("2급", "EE", 2232), ("2급", "ME", 1116), ("2급", "BE", 0),
    ("3급", "EX", 3024), ("3급", "EE", 2016), ("3급", "ME", 1008), ("3급", "BE", 0),
]

# 별표8 연봉제본봉 상한액 (직급, 천원)
SALARY_CAP_TABLE_K = [("1급", 85728), ("2급", 78540), ("3급", 77724)]

# 별표9 임금피크제 기본급지급률 (적용연차, 지급률)
WAGE_PEAK_TABLE = [(1, 0.9), (2, 0.8), (3, 0.7)]

# 별표1-2 평가상여금 지급률 (직위코드, 평가등급, 지급률)
BONUS_RATE_TABLE = [
    ("P01", "EX", 1.0), ("P01", "EE", 0.85), ("P01", "ME", 0.70), ("P01", "BE", 0.0),
    ("P02", "EX", 1.0), ("P02", "EE", 0.85), ("P02", "ME", 0.70), ("P02", "BE", 0.0),
    ("P05", "EX", 0.85), ("P05", "EE", 0.70), ("P05", "ME", 0.55), ("P05", "BE", 0.0),
    ("P08", "EX", 0.70), ("P08", "EE", 0.55), ("P08", "ME", 0.40), ("P08", "BE", 0.0),
    ("P09", "EX", 0.60), ("P09", "EE", 0.45), ("P09", "ME", 0.30), ("P09", "BE", 0.0),
    ("P10", "EX", 0.60), ("P10", "EE", 0.45), ("P10", "ME", 0.30), ("P10", "BE", 0.0),
]

# 별표1-5 국외본봉 (국가, 직급, 통화, 월액)
OVERSEAS_PAY_TABLE = [
    ("미국", "USD", "1급", 10780), ("미국", "USD", "2급", 9760), ("미국", "USD", "3급", 8620),
    ("일본", "JPY", "1급", 1210000), ("일본", "JPY", "2급", 1097000),
    ("독일", "EUR", "1급", 9100), ("독일", "EUR", "2급", 8240),
    ("영국", "GBP", "1급", 7790), ("영국", "GBP", "2급", 7050),
    ("중국", "CNY", "1급", 76000), ("중국", "CNY", "2급", 68800),
    ("홍콩", "HKD", "1급", 80300), ("홍콩", "HKD", "2급", 72700),
]

# 별표2 초임호봉
STARTING_STEP_TABLE = [
    ("종합기획직원 5급(G5)", 11),
    ("종합기획직원 6급(G6)", 6),
    ("일반사무직원", 1),
    ("별정직원", 4),
    ("서무직원", 6),
    ("청원경찰", 6),
]


def k_to_won(k: int) -> int:
    """천원 → 원."""
    return k * 1000


# ============================================================
# 2. C-TQL — TypeDB v3 insert statements (production schema)
# ============================================================

def gen_tql() -> str:
    lines: list[str] = []
    lines.append("# 보수규정 KG — TypeQL insert dump (TypeDB v3)\n")
    lines.append("# Schema: 직급, 직위, 보수기준, 직책급기준, 연봉차등액기준,")
    lines.append("# 연봉상한액기준, 임금피크제기준, 상여금기준, 국외본봉기준, 초임호봉기준\n\n")
    lines.append("```typeql\n")

    # 직급 entities
    lines.append("# === 직급 ===")
    for i, g in enumerate(["1급", "2급", "3급", "4급", "5급", "6급"], 1):
        lines.append(f'$g{i} isa 직급, has 직급명 "{g}", has 직급서열 {i};')
    lines.append("")

    # 직위 entities
    lines.append("# === 직위 ===")
    for code, name in POSITION_NAMES.items():
        idx = int(code[1:])
        lines.append(f'$p{idx} isa 직위, has 직위코드 "{code}", has 직위명 "{name}", has 직위서열 {idx};')
    lines.append("")

    # 본봉 — 호봉체계구성 (직급, 호봉번호, 호봉금액)
    lines.append("# === 본봉 (호봉체계구성) ===")
    for grade, amounts in SALARY_TABLE_K.items():
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        for step, amt_k in enumerate(amounts, 1):
            lines.append(
                f'$bs_{grade}_{step} isa 보수기준, has 호봉번호 {step}, '
                f'has 호봉금액 {k_to_won(amt_k)};'
            )
            lines.append(
                f'(해당직급: $g{gi}, 적용기준: $bs_{grade}_{step}) isa 호봉체계구성;'
            )
    lines.append("")

    # 직책급 — N-ary (직급, 직위, 직책급액)
    lines.append("# === 직책급 (직책급결정 — hyper-relational) ===")
    for pcode, grade, amt_k in POSITION_PAY_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        pi = int(pcode[1:])
        lines.append(
            f'$pp_{pcode}_{grade} isa 직책급기준, has 직책급액 {k_to_won(amt_k)};'
        )
        lines.append(
            f'(해당직급: $g{gi}, 해당직위: $p{pi}, 적용기준: $pp_{pcode}_{grade}) '
            f'isa 직책급결정;'
        )
    lines.append("")

    # 연봉차등 — N-ary (직급, 평가등급, 차등액)
    lines.append("# === 연봉차등 (연봉차등 — 평가등급별) ===")
    for grade, eg, amt_k in SALARY_DIFF_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        lines.append(f'$ev_{grade}_{eg} isa 평가결과, has 평가등급코드 "{eg}";')
        lines.append(
            f'$sd_{grade}_{eg} isa 연봉차등액기준, has 차등액 {k_to_won(amt_k)};'
        )
        lines.append(
            f'(해당직급: $g{gi}, 해당평가: $ev_{grade}_{eg}, 적용기준: $sd_{grade}_{eg}) '
            f'isa 연봉차등;'
        )
    lines.append("")

    # 연봉상한 (직급, 상한액)
    lines.append("# === 연봉상한 ===")
    for grade, cap_k in SALARY_CAP_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        lines.append(
            f'$sc_{grade} isa 연봉상한액기준, has 연봉상한액 {k_to_won(cap_k)};'
        )
        lines.append(f'(해당직급: $g{gi}, 적용기준: $sc_{grade}) isa 연봉상한;')
    lines.append("")

    # 임금피크 (적용연차, 지급률)
    lines.append("# === 임금피크 ===")
    for year, rate in WAGE_PEAK_TABLE:
        lines.append(
            f'$wp_{year} isa 임금피크제기준, has 적용연차 {year}, '
            f'has 임금피크지급률 {rate};'
        )
    lines.append("")

    # 상여금 (직위, 평가등급, 지급률)
    lines.append("# === 평가상여금 ===")
    for pcode, eg, rate in BONUS_RATE_TABLE:
        pi = int(pcode[1:])
        lines.append(f'$br_{pcode}_{eg} isa 상여금기준, has 상여금지급률 {rate};')
        lines.append(
            f'(해당직위: $p{pi}, 해당평가: $ev_default_{eg}, 적용기준: $br_{pcode}_{eg}) '
            f'isa 상여금결정;'
        )
    lines.append("")

    # 국외본봉 (국가, 통화, 직급, 월액)
    lines.append("# === 국외본봉 (N-ary: 국가, 통화, 직급, 액) ===")
    for country, currency, grade, amt in OVERSEAS_PAY_TABLE:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        slug = f"{country}_{grade}"
        lines.append(
            f'$os_{slug} isa 국외본봉기준, has 국가명 "{country}", '
            f'has 통화단위 "{currency}", has 국외본봉액 {amt};'
        )
        lines.append(
            f'(해당직급: $g{gi}, 적용기준: $os_{slug}) isa 국외본봉결정;'
        )
    lines.append("")

    # 초임호봉
    lines.append("# === 초임호봉 ===")
    for jf, step in STARTING_STEP_TABLE:
        lines.append(
            f'$ss_{step} isa 초임호봉기준, has 직렬명 "{jf}", '
            f'has 초임호봉번호 {step};'
        )
    lines.append("```")
    return "\n".join(lines)


# ============================================================
# 3. C-Cypher — Neo4j CREATE statements
# ============================================================

def gen_cypher() -> str:
    lines: list[str] = []
    lines.append("# 보수규정 KG — Cypher CREATE dump (Neo4j property graph)\n\n")
    lines.append("```cypher\n")

    # JobGrade
    for i, g in enumerate(["1급", "2급", "3급", "4급", "5급", "6급"], 1):
        lines.append(f'CREATE (g{i}:JobGrade {{name: "{g}", order: {i}}});')
    lines.append("")

    # Position
    for code, name in POSITION_NAMES.items():
        idx = int(code[1:])
        lines.append(
            f'CREATE (p{idx}:Position {{code: "{code}", name: "{name}", '
            f'order: {idx}}});'
        )
    lines.append("")

    # BaseSalary
    for grade, amounts in SALARY_TABLE_K.items():
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        for step, amt_k in enumerate(amounts, 1):
            lines.append(
                f'CREATE (g{gi})-[:HAS_BASE_SALARY {{step: {step}}}]->'
                f'(:BaseSalary {{step: {step}, amount: {k_to_won(amt_k)}}});'
            )
    lines.append("")

    # PositionPay (binary edges — hyper-rel 평탄화)
    for pcode, grade, amt_k in POSITION_PAY_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        pi = int(pcode[1:])
        lines.append(
            f'CREATE (pp_{pcode}_{grade}:PositionPay '
            f'{{annual_amount: {k_to_won(amt_k)}}});'
        )
        lines.append(f'CREATE (g{gi})-[:HAS_POSITION_PAY]->(pp_{pcode}_{grade});')
        lines.append(f'CREATE (p{pi})-[:HAS_POSITION_PAY]->(pp_{pcode}_{grade});')
    lines.append("")

    # DifferentialAmount
    for grade, eg, amt_k in SALARY_DIFF_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        lines.append(
            f'CREATE (g{gi})-[:HAS_DIFFERENTIAL_AMOUNT {{eval_grade: "{eg}"}}]->'
            f'(:DifferentialAmount {{amount: {k_to_won(amt_k)}, eval_grade: "{eg}"}});'
        )
    lines.append("")

    # SalaryLimit
    for grade, cap_k in SALARY_CAP_TABLE_K:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        lines.append(
            f'CREATE (g{gi})-[:HAS_SALARY_LIMIT]->'
            f'(:SalaryLimit {{cap_amount: {k_to_won(cap_k)}}});'
        )
    lines.append("")

    # WagePeak
    for year, rate in WAGE_PEAK_TABLE:
        lines.append(
            f'CREATE (:WagePeak {{year: {year}, rate: {rate}}});'
        )
    lines.append("")

    # BonusRate
    for pcode, eg, rate in BONUS_RATE_TABLE:
        pi = int(pcode[1:])
        lines.append(
            f'CREATE (p{pi})-[:HAS_BONUS_RATE {{eval_grade: "{eg}"}}]->'
            f'(:BonusRate {{rate: {rate}, eval_grade: "{eg}"}});'
        )
    lines.append("")

    # OverseasPay (no native multi-key — predicate property)
    for country, currency, grade, amt in OVERSEAS_PAY_TABLE:
        gi = ["1급", "2급", "3급", "4급", "5급", "6급"].index(grade) + 1
        lines.append(
            f'CREATE (g{gi})-[:HAS_OVERSEAS_PAY {{country: "{country}", '
            f'currency: "{currency}"}}]->'
            f'(:OverseasPay {{country: "{country}", currency: "{currency}", '
            f'monthly_amount: {amt}}});'
        )
    lines.append("")

    # StartingStep
    for jf, step in STARTING_STEP_TABLE:
        lines.append(
            f'CREATE (:StartingStep {{job_family: "{jf}", step: {step}}});'
        )
    lines.append("```")
    return "\n".join(lines)


# ============================================================
# 4. C-NL — natural language sentences
# ============================================================

def gen_nl() -> str:
    lines: list[str] = ["# 보수규정 KG — 자연어 요약 (NL summary)\n"]

    lines.append("## 직급과 직위")
    lines.append("- 직급은 1급, 2급, 3급, 4급, 5급, 6급 6단계로 구성된다.")
    pos_list = ", ".join(f"{code}({name})" for code, name in POSITION_NAMES.items())
    lines.append(f"- 직위는 {pos_list} 10단계로 구성된다.\n")

    lines.append("## 본봉 (별표1)")
    for grade, amounts in SALARY_TABLE_K.items():
        for step, amt_k in enumerate(amounts, 1):
            lines.append(
                f"- {grade}의 {step}호봉 본봉은 {k_to_won(amt_k):,}원이다."
            )
    lines.append("")

    lines.append("## 직책급 (별표1-1)")
    for pcode, grade, amt_k in POSITION_PAY_TABLE_K:
        pname = POSITION_NAMES[pcode]
        if amt_k == 0:
            lines.append(f"- {pname} 직위에 있는 {grade} 직원의 연간 직책급은 0원이다 (지급되지 않는다).")
        else:
            lines.append(
                f"- {pname} 직위에 있는 {grade} 직원의 연간 직책급은 {k_to_won(amt_k):,}원이다."
            )
    lines.append("")

    lines.append("## 연봉제본봉 차등액 (별표7)")
    for grade, eg, amt_k in SALARY_DIFF_TABLE_K:
        lines.append(
            f"- {grade} 직원이 {eg} 평가등급을 받았을 때 연봉 차등액은 {k_to_won(amt_k):,}원이다."
        )
    lines.append("")

    lines.append("## 연봉제본봉 상한 (별표8)")
    for grade, cap_k in SALARY_CAP_TABLE_K:
        lines.append(f"- {grade} 직원의 연봉제 본봉 상한액은 {k_to_won(cap_k):,}원이다.")
    lines.append("")

    lines.append("## 임금피크제 (별표9)")
    for year, rate in WAGE_PEAK_TABLE:
        lines.append(f"- 임금피크제 적용 {year}년차의 기본급 지급률은 {rate}이다.")
    lines.append("")

    lines.append("## 평가상여금 지급률 (별표1-2)")
    for pcode, eg, rate in BONUS_RATE_TABLE:
        pname = POSITION_NAMES[pcode]
        lines.append(
            f"- {pname} 직위 직원이 {eg} 등급일 때 평가상여금 지급률은 {rate}이다."
        )
    lines.append("")

    lines.append("## 국외본봉 (별표1-5)")
    for country, currency, grade, amt in OVERSEAS_PAY_TABLE:
        lines.append(
            f"- {country} 주재 {grade} 직원의 월 국외본봉은 {amt:,} {currency}이다."
        )
    lines.append("")

    lines.append("## 초임호봉 (별표2)")
    for jf, step in STARTING_STEP_TABLE:
        lines.append(f"- {jf}의 초임호봉은 {step}호봉이다.")

    return "\n".join(lines)


# ============================================================
# 5. C-JSONLD — nested JSON-LD-like structure
# ============================================================

def gen_jsonld() -> str:
    obj = {
        "@context": "https://example.com/bok-comp/",
        "직급": [
            {"name": g, "order": i}
            for i, g in enumerate(["1급", "2급", "3급", "4급", "5급", "6급"], 1)
        ],
        "직위": [
            {"code": c, "name": n, "order": int(c[1:])}
            for c, n in POSITION_NAMES.items()
        ],
        "본봉": [
            {"직급": grade, "호봉": step, "금액": k_to_won(amt_k)}
            for grade, amounts in SALARY_TABLE_K.items()
            for step, amt_k in enumerate(amounts, 1)
        ],
        "직책급": [
            {
                "직위코드": pcode,
                "직위명": POSITION_NAMES[pcode],
                "직급": grade,
                "연간직책급": k_to_won(amt_k),
            }
            for pcode, grade, amt_k in POSITION_PAY_TABLE_K
        ],
        "연봉차등": [
            {"직급": grade, "평가등급": eg, "차등액": k_to_won(amt_k)}
            for grade, eg, amt_k in SALARY_DIFF_TABLE_K
        ],
        "연봉상한": [
            {"직급": grade, "상한액": k_to_won(cap_k)}
            for grade, cap_k in SALARY_CAP_TABLE_K
        ],
        "임금피크": [
            {"적용연차": year, "지급률": rate}
            for year, rate in WAGE_PEAK_TABLE
        ],
        "평가상여금": [
            {
                "직위코드": pcode,
                "직위명": POSITION_NAMES[pcode],
                "평가등급": eg,
                "지급률": rate,
            }
            for pcode, eg, rate in BONUS_RATE_TABLE
        ],
        "국외본봉": [
            {
                "국가": country,
                "통화": currency,
                "직급": grade,
                "월액": amt,
            }
            for country, currency, grade, amt in OVERSEAS_PAY_TABLE
        ],
        "초임호봉": [
            {"직렬": jf, "호봉": step}
            for jf, step in STARTING_STEP_TABLE
        ],
    }
    return (
        "# 보수규정 KG — JSON-LD\n\n"
        + "```json\n"
        + json.dumps(obj, ensure_ascii=False, indent=2)
        + "\n```\n"
    )


# ============================================================
# 6. Article-text prefix (조문 + 용어 + 계산 규칙) — shared across tiers
# ============================================================

def article_prefix() -> str:
    """Return the article/term/rule sections from regulation_context.md.

    All tiers share this prefix; only the structured-data section after it
    varies. If extraction fails, fall back to embedding the entire MD.
    """
    if not CONTEXT_MD_PATH.exists():
        return ""
    text = CONTEXT_MD_PATH.read_text(encoding="utf-8")
    # Cut the file at the first JSON code block (data section). Sections
    # before it are article / term / rules text.
    cut = text.find("```json")
    if cut > 0:
        return text[:cut].rstrip() + "\n\n"
    return text + "\n\n"


# ============================================================
# 7. Main
# ============================================================

def main() -> int:
    prefix = article_prefix()
    files = {
        "regulation_tql.md": prefix + gen_tql(),
        "regulation_cypher.md": prefix + gen_cypher(),
        "regulation_nl.md": prefix + gen_nl(),
        "regulation_jsonld.md": prefix + gen_jsonld(),
    }
    for name, content in files.items():
        out = TIERS_DIR / name
        out.write_text(content, encoding="utf-8")
        n_lines = content.count("\n")
        n_chars = len(content)
        print(f"wrote {out}  ({n_lines} lines, {n_chars:,} chars)",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
