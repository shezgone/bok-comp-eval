"""
Generate guided variants of TQL / Cypher / JSON-LD tiers.

Each variant prepends a short syntax / structure guide to the existing
tier dump, so the LLM does not have to infer the syntax from scratch.
NL doesn't need a guide — natural language already.

Output:
  eval/context_tiers/regulation_tql_guide.md
  eval/context_tiers/regulation_cypher_guide.md
  eval/context_tiers/regulation_jsonld_guide.md
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIERS_DIR = ROOT / "eval" / "context_tiers"


TQL_GUIDE = """
## 자료 형식 안내 (TypeDB TypeQL — 하이퍼릴레이션 KG)

다음 자료는 TypeDB v3의 TypeQL `insert` 문 형식이다. 읽는 방법:

- `$var isa Type, has attr value;` — entity 정의. 변수($var)에 type과 attribute 부여.
- `(role1: $a, role2: $b, role3: $c) isa Relation;` — N-ary 관계. 여러 entity가 각자 역할로 하나의 사실에 동시 참여.
- 한 사실 (예: "부서장(가) 1급의 직책급 18,192,000원")은 (직급, 직위, 직책급기준) 셋이 동시에 묶인 N-ary로 표현된다.
- 같은 변수($g3, $p1 등)가 여러 statement에서 다시 참조되어 동일 entity를 가리킨다.

읽을 때:
1. attribute 값(숫자, 문자열)을 기준으로 entity 식별
2. relation에서 role: $var 매핑을 따라 함께 참여하는 entity들 찾기
3. 그 조합이 정답에 필요한 fact

"""

CYPHER_GUIDE = """
## 자료 형식 안내 (Cypher — Neo4j property graph)

다음 자료는 Neo4j의 Cypher `CREATE` 문 형식이다. 읽는 방법:

- `CREATE (var:Label {prop: value, ...})` — 노드 정의. Label이 type, {} 안이 properties.
- `CREATE (a)-[:REL_TYPE {prop: value}]->(b)` — 관계 정의. 화살표 방향 있는 binary edge.
- 관계는 항상 두 노드 사이 (binary). 세 개 이상의 entity가 묶인 fact는 중간 노드 + 두 binary edge로 평탄화되어 있을 수 있다.

읽을 때:
1. 노드의 Label과 properties로 entity 식별
2. 관계 (a)-[:R]->(b)로 두 entity 연결
3. 같은 변수가 여러 CREATE에서 재참조되면 동일 노드

"""

JSONLD_GUIDE = """
## 자료 형식 안내 (JSON-LD nested 구조)

다음 자료는 JSON 형식으로 정리된 보수규정 fact의 집합이다. 읽는 방법:

- 최상위 객체의 각 키(`직급`, `직위`, `본봉`, `직책급` 등)는 한 종류의 entity 또는 fact 카테고리.
- 각 카테고리의 값은 객체 배열. 한 객체 = 한 row = 한 fact.
- 중첩 fact는 한 객체 안에 여러 키 (e.g. `{"직급": "1급", "직위명": "부서장(가)", "연간직책급": 18192000}`).

읽을 때:
1. 카테고리(최상위 키)에서 관련 fact 종류 찾기
2. 배열에서 조건에 맞는 객체 선택 (예: 직급=1급 AND 직위코드=P01)
3. 객체의 정답 키(연간직책급, 금액 등)에서 값 추출

"""


GUIDES = {
    "tql": TQL_GUIDE,
    "cypher": CYPHER_GUIDE,
    "jsonld": JSONLD_GUIDE,
}


def main() -> int:
    for tier, guide in GUIDES.items():
        src = TIERS_DIR / f"regulation_{tier}.md"
        dst = TIERS_DIR / f"regulation_{tier}_guide.md"
        if not src.exists():
            print(f"[skip] {src} missing — run dump_context_tiers.py first",
                  file=sys.stderr)
            continue
        original = src.read_text(encoding="utf-8")
        # Insert guide right after the article-text prefix and before the
        # data section. The data section starts at the first '# ' heading
        # introducing the dump. Simplest: prepend guide at the very top of
        # the file — LLM reads guide first, then everything else.
        merged = guide + "\n" + original
        dst.write_text(merged, encoding="utf-8")
        n_chars = len(merged)
        added = len(guide)
        print(f"wrote {dst}  (+{added:,} guide chars, total {n_chars:,})",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
