# CLAUDE.md

## 프로젝트 목적
한국은행 보수규정 KG-RAG 시스템의 정량 평가 및 논문화 작업.
대상 시스템(production)은 본 repo의 **자매 디렉토리**에 위치.

## Production 시스템 위치
`/Users/user/vibe/bok-compensation-regulations/`

해당 repo에 다음이 있음:
- `src/bok_compensation_typedb/` — TypeDB 백엔드 (하이퍼릴레이션 KG)
- `src/bok_compensation_neo4j/` — Neo4j 백엔드 (프로퍼티그래프)
- `src/bok_compensation_context/` — Context-only RAG (`regulation_context.md` 포함)
- `src/bok_compensation/hybrid_router_graph.py` — Hybrid 라우터 (현재 시뮬레이션)
- `schema/compensation_regulation.tql` — TypeDB 온톨로지
- `docs/보수규정 전문(20250213).pdf` — 원본 데이터 (공개 자료)

## 핵심 가설 (메모리 참조)
**H1 — Context-RAG ceiling을 넘는 KG 우위**: 마크다운+JSON+용어정규화로 *최대 전처리된* Context-RAG보다 하이퍼릴레이션 KG(TypeDB)가 다항관계 질의에서 더 좋다는 counterintuitive 주장.

전체 가설 frame, 보조가설(H1-m1~m4), 평가셋과의 매핑은 메모리의 `paper_central_hypothesis.md` 참조.

## 현재 파일 상태
```
eval/
  schema.json           # QA 어노테이션 JSON Schema
  seed_questions.jsonl  # 시드 30문항 (10 카테고리 균등)
  scorer.py             # EM + 숫자/통화 정규화 자동 채점기 (stdlib only)
pyproject.toml          # 패키지 메타 (runner/analysis는 optional deps)
.env.example            # LLM API 키 + DB 연결 템플릿
.gitignore              # predictions/, results/, .env 등 제외
```

## 검증 / 실행
```bash
python3 eval/scorer.py --validate
python3 eval/scorer.py --pred path/to/preds.jsonl
```

예측 JSONL 형식: `{"qid": "C1-001", "answer": "0.8"}` 한 줄당 한 항목.

## 다음 작업 후보 (우선순위순)
1. **Baseline runner 작성** (`eval/run_baseline.py`)
   - 4 백엔드 × N LLM에 평가셋 일괄 실행
   - 출력: `predictions/{backend}_{llm}.jsonl`
   - production repo의 agent를 import해서 호출
2. **Pilot 실험 — Tier 1**: HCX + GPT-4o(또는 Claude) 두 LLM × 4 백엔드
   - H1이 두 LLM 모두에서 보이는지 먼저 확인
3. **평가셋 70문항 자동 확장**: `eval/gen_questions.py`로 본봉표·국외본봉표·직책급표 순회 생성
4. **Adversarial 30문항 추가**: 단위 함정(월/연), 표 외 행, 정의 함정
5. **Context-RAG ablation 4-tier 설계**: 원본 PDF / MD only / MD+JSON / MD+JSON+규칙 — H1 ceiling 입증용
6. **메커니즘 검증 실험**: H1-m1~m4 (테이블 행 수, 키 차수, 값 환각 분포, 정답 위치)

## Production 연결 방법 (Baseline runner 작성 시)
세 가지 옵션 중 하나 선택:
```bash
# (1) editable install — 권장
pip install -e /Users/user/vibe/bok-compensation-regulations

# (2) PYTHONPATH
export PYTHONPATH=/Users/user/vibe/bok-compensation-regulations/src:$PYTHONPATH

# (3) sys.path.insert in runner script (덜 깔끔)
```

## 규칙
- **시드 30문항(`eval/seed_questions.jsonl`) 정답은 PDF 원본 대비 검증된 값** — 임의 수정 금지. 새 문항 추가는 별도 파일에.
- **LLM API 키는 `.env`에만** — 절대 커밋 금지 (gitignore 처리됨)
- **`predictions/`, `results/`는 gitignore** — 실험 raw output은 버전관리 대상 아님. 분석 결과(요약 표/플롯)만 `analysis/` 디렉토리에 따로 커밋
- **Production 코드 수정 금지** — 본 repo는 평가만, production은 `bok-compensation-regulations`에서

## Known issues (production에서 상속)
- production의 `tests/test_intent_extraction.py`가 깨져 있음 (삭제된 `nl_query` 모듈 참조)
- production의 Neo4j config가 `NEO4J_USER` 사용, `.env.example`은 `NEO4J_USERNAME`
- production agent `build_*_agent()`에 LLM 엔드포인트 하드코딩 — runner 작성 시 우회 필요
