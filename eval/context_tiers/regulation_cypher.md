# 한국은행 보수규정 전처리 문서

이 문서는 LLM이 그래프 DB 없이 보수규정 질의에 답하도록 하기 위한 비교용 컨텍스트 문서다.
조문은 텍스트로 정리했고, 계산과 조회에 직접 필요한 표는 JSON으로, 사람이 읽는 참고 표는 마크다운 테이블로 정리했다.
금액 단위는 별도 표기가 없으면 원이다.

## 문서 사용 원칙

- 답변은 반드시 이 문서에 있는 규정, 표, 계산 규칙만 근거로 한다.
- 계산 질문에서는 JSON 블록의 값을 우선 사용한다.
- 같은 정보가 JSON과 마크다운 표에 모두 있으면 JSON을 기준값으로 사용하고, 마크다운 표는 참고용으로만 본다.
- 질문에 이미 금액이 주어지면 그 금액은 계산 입력값으로 취급한다.
- 질문에 평가등급이 직접 주어지면 직급평점 수치는 보조 힌트로만 보고, 실제 계산은 평가등급 열(EX, EE, ME, BE)을 기준으로 한다.
- 질문에 직책이 함께 주어져도, 별도 지시가 없으면 연봉제본봉 조정 계산에는 직책급을 자동 합산하지 않는다.
- 질문에 기준일이 포함되어 있어도 이미 해당 시점의 평가등급이 주어졌다면 계산에는 그 평가등급을 그대로 사용한다.

## 용어 정규화

- G5 = 종합기획직원 5급 = 종합기획 5급
- G3 = 종합기획직원 3급 = 종합기획 3급
- 직급평점 = 성과평가 점수 = 평가 결과 산정 점수
- 성과평가 결과 = 평가등급
- 본봉 조정 = 연봉제본봉 조정
- 국외본봉 = 해외 기본급 = 주재 본봉

## 적용 제외 및 주의사항

- 기한부 고용계약자는 제14조에 따라 제2장 보수와 제3장 상여금 규정을 적용하지 않으므로 상여금을 받을 수 없다.
- 임금피크제본봉은 잔여근무기간이 3년 이하인 직원을 대상으로 한다.
- 연봉 차등액표는 1급, 2급, 3급 직원의 연봉제본봉 조정 계산에 사용한다.
- 직책급표는 직책급 조회에 사용하며, 연봉제본봉 조정 계산에는 직접 합산하지 않는다.
- 평가상여금 지급률표는 상여금 계산에 사용하며, 연봉제본봉 조정 계산에는 직접 사용하지 않는다.
- 연봉 상한액표는 질문이 상한 적용 여부를 묻는 경우에만 사용한다.

## 계산 규칙

### 연봉제본봉 조정

- 적용 조건: 연봉제 적용대상 직원
- 입력값:
	- 현재 연봉제 본봉
	- 직급
	- 평가등급
- 조회값:
	- 연봉 차등액표의 해당 직급 + 평가등급 차등액
- 공식:
	- 조정 후 연봉제 본봉 = 현재 연봉제 본봉 + 해당 직급/평가등급의 연봉 차등액
- 비합산 항목:
	- 직책급
	- 상여금
	- 국외본봉
- 예시:
	- 현재 연봉제 본봉이 70,000,000원이고 3급 EE이면 차등액 2,016,000원을 더해 72,016,000원이다.

## 질의 해석 메모

- 기한부 고용계약자는 제14조에 따라 제2장 보수와 제3장 상여금 규정을 적용하지 않으므로 상여금을 받을 수 없다.
- G5 직원의 초봉은 종합기획직원 5급 초임호봉 11호봉이며, 5급 11호봉 본봉은 1,554,000원이다.
- 미국 주재 1급 직원의 국외본봉은 10,780 USD이고, 미국 주재 2급 직원의 국외본봉은 9,760 USD이다.
- 임금피크제 2년차 기본급 지급률은 0.8이다.
- 현재 전처리 문서에 정리된 개정이력은 9건이다.

## 질의 예시

Q. G5 직원의 초봉은?
A. 종합기획직원 5급의 초임호봉은 11호봉이며, 5급 11호봉 본봉은 1,554,000원이다.

Q. 기한부 고용계약자는 상여금을 받을 수 있어?
A. 받을 수 없다. 기한부 고용계약자는 제14조에 따라 제2장 보수 및 제3장 상여금 규정을 적용하지 않는다.

Q. 미국 주재 2급 직원의 국외본봉은?
A. 미국 주재 2급 직원의 월 국외본봉은 9,760 USD이다.

Q. 임금피크제 2년차 지급률은?
A. 임금피크제 2년차 기본급 지급률은 0.8이다.

Q. 임금피크제 적용 대상과 연차별 지급률은?
A. 임금피크제본봉은 잔여근무기간이 3년 이하인 직원을 대상으로 한다. 연차별 기본급 지급률은 1년차 0.9, 2년차 0.8, 3년차 0.7이다.

Q. 보수규정 개정이력은 몇 건이야?
A. 현재 전처리 문서에 정리된 개정이력은 9건이다.

Q. 3급 EE 등급의 연봉 차등액은?
A. 3급 EE 등급의 연봉 차등액은 2,016,000원이다.

Q. 현재 연봉제 본봉이 70,000,000원이고 3급 EE이면 조정 후 연봉제 본봉은?
A. 연봉 차등액표에서 3급 EE 차등액은 2,016,000원이므로, 70,000,000원 + 2,016,000원 = 72,016,000원이다.

Q. 종합기획 3급(G3) 직원이 직급평점 3024점 이상이고, 반장 직책을 맡고 있으며, 연봉제 본봉이 70,000,000원일 때, 성과평가 결과가 EE등급이라면 조정 후 연봉제 본봉은 얼마인가?
A. 조정 후 연봉제 본봉은 72,016,000원이다. 계산에는 현재 연봉제 본봉 70,000,000원과 3급 EE 차등액 2,016,000원을 사용한다. 반장 직책은 연봉제본봉 조정 공식에 직접 합산하지 않으며, 직급평점 수치와 기준일은 이미 EE등급이 주어진 경우 계산 결과를 바꾸지 않는다.

Q. 현재 연봉제 본봉이 77,000,000원인 3급 직원이 EE등급이면 상한을 넘는가?
A. 3급 EE 차등액 2,016,000원을 더하면 79,016,000원이다. 3급 연봉 상한액 77,724,000원을 초과한다.

Q. 팀장 3급 직책급은?
A. 팀장 직위의 3급 연간 직책급액은 1,956,000원이다.

## 주요 조문

### 제1조 목적
- 이 규정은 한국은행법과 한국은행정관에 따라 금융통화위원회 위원, 집행간부, 감사 및 직원의 보수 및 상여금에 관한 사항을 규정함을 목적으로 한다.

### 제2조 정의
- 보수란 위원·집행간부·감사에 대하여는 기본급을 말하며, 직원에 대하여는 기본급 및 제수당을 말한다.
- 기본급이란 본봉과 직책급을 말한다.
- 제수당이란 국내직원의 경우 업무수당 및 시간외근무수당을 말하며, 해외직원의 경우에는 조정수당을 말한다.

### 제4조 본봉
- 위원, 집행간부, 감사의 본봉은 별표1의 1.로 한다.
- 직원의 본봉은 직급 및 호봉에 따라 결정되는 별표1의 2.부터 5.의 본봉, 성과평가결과를 기준으로 결정되는 연봉제본봉 및 잔여근무기간을 기준으로 결정되는 임금피크제본봉으로 한다.
- 연봉제본봉은 직전 연봉제본봉에 별표7의 평가등급별 차등액을 합한 금액으로 하되, 평가등급은 매년 1회 산출된 성과평가결과를 기준으로 정한다.
- 임금피크제본봉은 잔여근무기간이 3년 이하인 직원을 대상으로 한다.
- 임금피크제본봉은 적용 직전 월말일 현재의 본봉에 별표9의 임금피크제 적용연차별 기본급지급률을 곱한 금액으로 한다.
- 직원에 대한 직책급은 직책 및 직급에 따라 결정되는 별표1-1의 직책급과 잔여근무기간을 기준으로 결정되는 임금피크제직책급으로 한다.

### 제5조 승급
- 1개 호봉간의 승급에 필요한 최저근무기간은 1년을 원칙으로 한다.
- 승급의 제한 또는 조정은 총재가 정한다.

### 제6조 초임호봉 및 연봉제본봉
- 신규채용자의 초임호봉은 별표2와 같다.
- 다만, 총재는 학력이나 경력 또는 자격을 고려하여 초임호봉을 조정할 수 있다.

### 제7조 업무수당
- 종사업무별로 해당 업무 또는 기술분야에 직접 종사하는 직원에 대하여는 별표3의 업무수당을 지급한다.
- 다만, 장기근속자에 대하여는 가산 지급할 수 있다.

### 제9조 시간외근무수당
- 은행업무와 관련하여 시간외근무에 대해서는 동 근무 매시간에 대하여 시간당 보수의 1.5배에 해당하는 금액을 지급한다.
- 시간당 보수는 통상임금 월지급액의 209분의 1로 한다.

### 제11조 조정수당
- 해외직원이 국내외에서 납부하는 소득세가 국내 근무 시 납세액을 초과할 때에는 그 초과분의 범위에서 총재가 정하는 바에 따라 조정수당을 지급할 수 있다.

### 제12조 상여금의 지급
- 위원, 집행간부, 감사 및 직원에 대하여 상여금을 지급한다.
- 직원에 대한 상여금은 정기상여금 및 평가상여금으로 구분하고, 지급기준일 현재의 기본급에 지급률을 곱한 금액을 지급한다.
- 정기상여금은 연간지급률 380%로서 6월, 12월의 초일을 지급기준일로 하여 각각 150%, 설·추석 연휴시작일의 2영업일 전일을 지급기준일로 하여 각각 40%를 지급한다.
- 평가상여금은 직전년도 성과평가결과에 의한 평가등급에 따라 별표1-2의 지급률을 기본급에 곱한 금액을 지급한다.

### 제13조 비밀유지
- 직원은 자신의 보수를 다른 직원에게 알려주거나 다른 직원의 보수를 알려는 행위를 하여서는 아니 된다.

### 제14조 일반기능직원등의 보수
- 일반기능직원, 전문직원 및 종합기획직원 중 기한부 고용계약자에 대하여는 제2장 보수 및 제3장 상여금에 관한 규정을 적용하지 아니한다.

### 제15조 위임
- 파견자, 휴직자, 휴가자, 전근자, 해외현지채용직원 및 인사경영국 소속직원의 보수 등에 관한 사항 및 이 규정 시행에 필요한 세부사항은 총재가 정한다.

## 개정 이력

| 개정일 | 설명 |
| --- | --- |
| 1998-04-16 | 보수규정 제정 |
| 2000-01-01 | 보수규정 개정 |
| 2005-01-01 | 보수규정 개정 |
| 2010-01-01 | 보수규정 개정 |
| 2015-01-01 | 보수규정 개정 |
| 2019-01-01 | 보수규정 개정 (직책급표 반영) |
| 2023-01-01 | 보수규정 개정 |
| 2024-01-18 | 보수규정 개정 |
| 2025-02-13 | 보수규정 최종 개정 (현행) |

## 계산용 구조화 데이터(JSON)

### 초임호봉 조회 데이터

# 보수규정 KG — Cypher CREATE dump (Neo4j property graph)


```cypher

CREATE (g1:JobGrade {name: "1급", order: 1});
CREATE (g2:JobGrade {name: "2급", order: 2});
CREATE (g3:JobGrade {name: "3급", order: 3});
CREATE (g4:JobGrade {name: "4급", order: 4});
CREATE (g5:JobGrade {name: "5급", order: 5});
CREATE (g6:JobGrade {name: "6급", order: 6});

CREATE (p1:Position {code: "P01", name: "부서장(가)", order: 1});
CREATE (p2:Position {code: "P02", name: "부서장(나)", order: 2});
CREATE (p3:Position {code: "P03", name: "국소속실장", order: 3});
CREATE (p4:Position {code: "P04", name: "부장", order: 4});
CREATE (p5:Position {code: "P05", name: "팀장", order: 5});
CREATE (p6:Position {code: "P06", name: "반장", order: 6});
CREATE (p7:Position {code: "P07", name: "조사역", order: 7});
CREATE (p8:Position {code: "P08", name: "주임조사역(C1)", order: 8});
CREATE (p9:Position {code: "P09", name: "조사역(C2)", order: 9});
CREATE (p10:Position {code: "P10", name: "조사역(C3)", order: 10});

CREATE (g3)-[:HAS_BASE_SALARY {step: 1}]->(:BaseSalary {step: 1, amount: 100000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 2}]->(:BaseSalary {step: 2, amount: 200000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 3}]->(:BaseSalary {step: 3, amount: 300000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 4}]->(:BaseSalary {step: 4, amount: 400000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 5}]->(:BaseSalary {step: 5, amount: 500000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 6}]->(:BaseSalary {step: 6, amount: 600000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 7}]->(:BaseSalary {step: 7, amount: 700000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 8}]->(:BaseSalary {step: 8, amount: 800000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 9}]->(:BaseSalary {step: 9, amount: 900000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 10}]->(:BaseSalary {step: 10, amount: 1000000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 11}]->(:BaseSalary {step: 11, amount: 1100000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 12}]->(:BaseSalary {step: 12, amount: 1200000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 13}]->(:BaseSalary {step: 13, amount: 1300000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 14}]->(:BaseSalary {step: 14, amount: 1400000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 15}]->(:BaseSalary {step: 15, amount: 1500000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 16}]->(:BaseSalary {step: 16, amount: 1600000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 17}]->(:BaseSalary {step: 17, amount: 1700000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 18}]->(:BaseSalary {step: 18, amount: 1800000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 19}]->(:BaseSalary {step: 19, amount: 1900000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 20}]->(:BaseSalary {step: 20, amount: 2000000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 21}]->(:BaseSalary {step: 21, amount: 3188000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 22}]->(:BaseSalary {step: 22, amount: 3300000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 23}]->(:BaseSalary {step: 23, amount: 3642000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 24}]->(:BaseSalary {step: 24, amount: 3752000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 25}]->(:BaseSalary {step: 25, amount: 3869000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 26}]->(:BaseSalary {step: 26, amount: 3984000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 27}]->(:BaseSalary {step: 27, amount: 4102000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 28}]->(:BaseSalary {step: 28, amount: 4419000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 29}]->(:BaseSalary {step: 29, amount: 4530000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 30}]->(:BaseSalary {step: 30, amount: 4654000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 31}]->(:BaseSalary {step: 31, amount: 4763000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 32}]->(:BaseSalary {step: 32, amount: 5006000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 33}]->(:BaseSalary {step: 33, amount: 5187000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 34}]->(:BaseSalary {step: 34, amount: 5312000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 35}]->(:BaseSalary {step: 35, amount: 5430000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 36}]->(:BaseSalary {step: 36, amount: 5555000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 37}]->(:BaseSalary {step: 37, amount: 5690000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 38}]->(:BaseSalary {step: 38, amount: 5821000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 39}]->(:BaseSalary {step: 39, amount: 5925000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 40}]->(:BaseSalary {step: 40, amount: 6032000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 41}]->(:BaseSalary {step: 41, amount: 6142000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 42}]->(:BaseSalary {step: 42, amount: 6229000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 43}]->(:BaseSalary {step: 43, amount: 6316000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 44}]->(:BaseSalary {step: 44, amount: 6399000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 45}]->(:BaseSalary {step: 45, amount: 6495000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 46}]->(:BaseSalary {step: 46, amount: 6583000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 47}]->(:BaseSalary {step: 47, amount: 6657000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 48}]->(:BaseSalary {step: 48, amount: 6738000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 49}]->(:BaseSalary {step: 49, amount: 6812000});
CREATE (g3)-[:HAS_BASE_SALARY {step: 50}]->(:BaseSalary {step: 50, amount: 6890000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 1}]->(:BaseSalary {step: 1, amount: 600000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 2}]->(:BaseSalary {step: 2, amount: 700000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 3}]->(:BaseSalary {step: 3, amount: 800000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 4}]->(:BaseSalary {step: 4, amount: 900000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 5}]->(:BaseSalary {step: 5, amount: 1000000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 6}]->(:BaseSalary {step: 6, amount: 1100000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 7}]->(:BaseSalary {step: 7, amount: 1200000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 8}]->(:BaseSalary {step: 8, amount: 1300000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 9}]->(:BaseSalary {step: 9, amount: 1400000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 10}]->(:BaseSalary {step: 10, amount: 1554000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 11}]->(:BaseSalary {step: 11, amount: 1600000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 12}]->(:BaseSalary {step: 12, amount: 1700000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 13}]->(:BaseSalary {step: 13, amount: 1800000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 14}]->(:BaseSalary {step: 14, amount: 1900000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 15}]->(:BaseSalary {step: 15, amount: 2000000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 16}]->(:BaseSalary {step: 16, amount: 2343000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 17}]->(:BaseSalary {step: 17, amount: 2642000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 18}]->(:BaseSalary {step: 18, amount: 2754000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 19}]->(:BaseSalary {step: 19, amount: 2867000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 20}]->(:BaseSalary {step: 20, amount: 2980000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 21}]->(:BaseSalary {step: 21, amount: 3093000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 22}]->(:BaseSalary {step: 22, amount: 3204000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 23}]->(:BaseSalary {step: 23, amount: 3542000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 24}]->(:BaseSalary {step: 24, amount: 3662000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 25}]->(:BaseSalary {step: 25, amount: 3780000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 26}]->(:BaseSalary {step: 26, amount: 3893000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 27}]->(:BaseSalary {step: 27, amount: 4095000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 28}]->(:BaseSalary {step: 28, amount: 4417000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 29}]->(:BaseSalary {step: 29, amount: 4529000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 30}]->(:BaseSalary {step: 30, amount: 4650000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 31}]->(:BaseSalary {step: 31, amount: 4762000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 32}]->(:BaseSalary {step: 32, amount: 4882000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 33}]->(:BaseSalary {step: 33, amount: 5057000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 34}]->(:BaseSalary {step: 34, amount: 5183000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 35}]->(:BaseSalary {step: 35, amount: 5300000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 36}]->(:BaseSalary {step: 36, amount: 5421000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 37}]->(:BaseSalary {step: 37, amount: 5539000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 38}]->(:BaseSalary {step: 38, amount: 5669000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 39}]->(:BaseSalary {step: 39, amount: 5778000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 40}]->(:BaseSalary {step: 40, amount: 5889000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 41}]->(:BaseSalary {step: 41, amount: 5992000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 42}]->(:BaseSalary {step: 42, amount: 6082000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 43}]->(:BaseSalary {step: 43, amount: 6170000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 44}]->(:BaseSalary {step: 44, amount: 6257000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 45}]->(:BaseSalary {step: 45, amount: 6340000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 46}]->(:BaseSalary {step: 46, amount: 6428000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 47}]->(:BaseSalary {step: 47, amount: 6499000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 48}]->(:BaseSalary {step: 48, amount: 6576000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 49}]->(:BaseSalary {step: 49, amount: 6657000});
CREATE (g4)-[:HAS_BASE_SALARY {step: 50}]->(:BaseSalary {step: 50, amount: 6733000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 1}]->(:BaseSalary {step: 1, amount: 579000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 2}]->(:BaseSalary {step: 2, amount: 651000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 3}]->(:BaseSalary {step: 3, amount: 715000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 4}]->(:BaseSalary {step: 4, amount: 787000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 5}]->(:BaseSalary {step: 5, amount: 862000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 6}]->(:BaseSalary {step: 6, amount: 936000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 7}]->(:BaseSalary {step: 7, amount: 1011000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 8}]->(:BaseSalary {step: 8, amount: 1096000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 9}]->(:BaseSalary {step: 9, amount: 1181000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 10}]->(:BaseSalary {step: 10, amount: 1265000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 11}]->(:BaseSalary {step: 11, amount: 1554000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 12}]->(:BaseSalary {step: 12, amount: 1689000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 13}]->(:BaseSalary {step: 13, amount: 1837000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 14}]->(:BaseSalary {step: 14, amount: 1977000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 15}]->(:BaseSalary {step: 15, amount: 2127000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 16}]->(:BaseSalary {step: 16, amount: 2307000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 17}]->(:BaseSalary {step: 17, amount: 2579000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 18}]->(:BaseSalary {step: 18, amount: 2753000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 19}]->(:BaseSalary {step: 19, amount: 2858000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 20}]->(:BaseSalary {step: 20, amount: 2973000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 21}]->(:BaseSalary {step: 21, amount: 3081000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 22}]->(:BaseSalary {step: 22, amount: 3196000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 23}]->(:BaseSalary {step: 23, amount: 3535000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 24}]->(:BaseSalary {step: 24, amount: 3658000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 25}]->(:BaseSalary {step: 25, amount: 3770000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 26}]->(:BaseSalary {step: 26, amount: 3889000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 27}]->(:BaseSalary {step: 27, amount: 4002000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 28}]->(:BaseSalary {step: 28, amount: 4323000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 29}]->(:BaseSalary {step: 29, amount: 4440000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 30}]->(:BaseSalary {step: 30, amount: 4549000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 31}]->(:BaseSalary {step: 31, amount: 4669000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 32}]->(:BaseSalary {step: 32, amount: 4780000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 33}]->(:BaseSalary {step: 33, amount: 4962000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 34}]->(:BaseSalary {step: 34, amount: 5089000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 35}]->(:BaseSalary {step: 35, amount: 5209000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 36}]->(:BaseSalary {step: 36, amount: 5326000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 37}]->(:BaseSalary {step: 37, amount: 5448000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 38}]->(:BaseSalary {step: 38, amount: 5574000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 39}]->(:BaseSalary {step: 39, amount: 5678000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 40}]->(:BaseSalary {step: 40, amount: 5788000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 41}]->(:BaseSalary {step: 41, amount: 5894000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 42}]->(:BaseSalary {step: 42, amount: 5983000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 43}]->(:BaseSalary {step: 43, amount: 6063000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 44}]->(:BaseSalary {step: 44, amount: 6153000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 45}]->(:BaseSalary {step: 45, amount: 6236000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 46}]->(:BaseSalary {step: 46, amount: 6327000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 47}]->(:BaseSalary {step: 47, amount: 6400000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 48}]->(:BaseSalary {step: 48, amount: 6476000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 49}]->(:BaseSalary {step: 49, amount: 6555000});
CREATE (g5)-[:HAS_BASE_SALARY {step: 50}]->(:BaseSalary {step: 50, amount: 6635000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 1}]->(:BaseSalary {step: 1, amount: 559000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 2}]->(:BaseSalary {step: 2, amount: 620000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 3}]->(:BaseSalary {step: 3, amount: 675000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 4}]->(:BaseSalary {step: 4, amount: 743000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 5}]->(:BaseSalary {step: 5, amount: 805000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 6}]->(:BaseSalary {step: 6, amount: 871000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 7}]->(:BaseSalary {step: 7, amount: 944000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 8}]->(:BaseSalary {step: 8, amount: 1000000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 9}]->(:BaseSalary {step: 9, amount: 1045000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 10}]->(:BaseSalary {step: 10, amount: 1090000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 11}]->(:BaseSalary {step: 11, amount: 1509000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 12}]->(:BaseSalary {step: 12, amount: 1591000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 13}]->(:BaseSalary {step: 13, amount: 1672000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 14}]->(:BaseSalary {step: 14, amount: 1757000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 15}]->(:BaseSalary {step: 15, amount: 1835000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 16}]->(:BaseSalary {step: 16, amount: 2106000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 17}]->(:BaseSalary {step: 17, amount: 2196000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 18}]->(:BaseSalary {step: 18, amount: 2286000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 19}]->(:BaseSalary {step: 19, amount: 2372000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 20}]->(:BaseSalary {step: 20, amount: 2462000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 21}]->(:BaseSalary {step: 21, amount: 2640000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 22}]->(:BaseSalary {step: 22, amount: 2730000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 23}]->(:BaseSalary {step: 23, amount: 2818000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 24}]->(:BaseSalary {step: 24, amount: 2909000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 25}]->(:BaseSalary {step: 25, amount: 2999000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 26}]->(:BaseSalary {step: 26, amount: 3175000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 27}]->(:BaseSalary {step: 27, amount: 3267000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 28}]->(:BaseSalary {step: 28, amount: 3353000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 29}]->(:BaseSalary {step: 29, amount: 3440000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 30}]->(:BaseSalary {step: 30, amount: 3523000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 31}]->(:BaseSalary {step: 31, amount: 3610000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 32}]->(:BaseSalary {step: 32, amount: 3695000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 33}]->(:BaseSalary {step: 33, amount: 3782000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 34}]->(:BaseSalary {step: 34, amount: 3867000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 35}]->(:BaseSalary {step: 35, amount: 3953000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 36}]->(:BaseSalary {step: 36, amount: 4035000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 37}]->(:BaseSalary {step: 37, amount: 4123000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 38}]->(:BaseSalary {step: 38, amount: 4207000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 39}]->(:BaseSalary {step: 39, amount: 4290000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 40}]->(:BaseSalary {step: 40, amount: 4372000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 41}]->(:BaseSalary {step: 41, amount: 4451000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 42}]->(:BaseSalary {step: 42, amount: 4537000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 43}]->(:BaseSalary {step: 43, amount: 4615000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 44}]->(:BaseSalary {step: 44, amount: 4699000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 45}]->(:BaseSalary {step: 45, amount: 4781000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 46}]->(:BaseSalary {step: 46, amount: 4849000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 47}]->(:BaseSalary {step: 47, amount: 4914000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 48}]->(:BaseSalary {step: 48, amount: 4982000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 49}]->(:BaseSalary {step: 49, amount: 5052000});
CREATE (g6)-[:HAS_BASE_SALARY {step: 50}]->(:BaseSalary {step: 50, amount: 5122000});

CREATE (pp_P01_1급:PositionPay {annual_amount: 18192000});
CREATE (g1)-[:HAS_POSITION_PAY]->(pp_P01_1급);
CREATE (p1)-[:HAS_POSITION_PAY]->(pp_P01_1급);
CREATE (pp_P01_2급:PositionPay {annual_amount: 16236000});
CREATE (g2)-[:HAS_POSITION_PAY]->(pp_P01_2급);
CREATE (p1)-[:HAS_POSITION_PAY]->(pp_P01_2급);
CREATE (pp_P02_1급:PositionPay {annual_amount: 15792000});
CREATE (g1)-[:HAS_POSITION_PAY]->(pp_P02_1급);
CREATE (p2)-[:HAS_POSITION_PAY]->(pp_P02_1급);
CREATE (pp_P02_2급:PositionPay {annual_amount: 13836000});
CREATE (g2)-[:HAS_POSITION_PAY]->(pp_P02_2급);
CREATE (p2)-[:HAS_POSITION_PAY]->(pp_P02_2급);
CREATE (pp_P03_1급:PositionPay {annual_amount: 7692000});
CREATE (g1)-[:HAS_POSITION_PAY]->(pp_P03_1급);
CREATE (p3)-[:HAS_POSITION_PAY]->(pp_P03_1급);
CREATE (pp_P03_2급:PositionPay {annual_amount: 5736000});
CREATE (g2)-[:HAS_POSITION_PAY]->(pp_P03_2급);
CREATE (p3)-[:HAS_POSITION_PAY]->(pp_P03_2급);
CREATE (pp_P04_2급:PositionPay {annual_amount: 4824000});
CREATE (g2)-[:HAS_POSITION_PAY]->(pp_P04_2급);
CREATE (p4)-[:HAS_POSITION_PAY]->(pp_P04_2급);
CREATE (pp_P04_3급:PositionPay {annual_amount: 2868000});
CREATE (g3)-[:HAS_POSITION_PAY]->(pp_P04_3급);
CREATE (p4)-[:HAS_POSITION_PAY]->(pp_P04_3급);
CREATE (pp_P05_3급:PositionPay {annual_amount: 1956000});
CREATE (g3)-[:HAS_POSITION_PAY]->(pp_P05_3급);
CREATE (p5)-[:HAS_POSITION_PAY]->(pp_P05_3급);
CREATE (pp_P05_4급:PositionPay {annual_amount: 0});
CREATE (g4)-[:HAS_POSITION_PAY]->(pp_P05_4급);
CREATE (p5)-[:HAS_POSITION_PAY]->(pp_P05_4급);
CREATE (pp_P07_2급:PositionPay {annual_amount: 3012000});
CREATE (g2)-[:HAS_POSITION_PAY]->(pp_P07_2급);
CREATE (p7)-[:HAS_POSITION_PAY]->(pp_P07_2급);
CREATE (pp_P07_3급:PositionPay {annual_amount: 1056000});
CREATE (g3)-[:HAS_POSITION_PAY]->(pp_P07_3급);
CREATE (p7)-[:HAS_POSITION_PAY]->(pp_P07_3급);
CREATE (pp_P08_3급:PositionPay {annual_amount: 1956000});
CREATE (g3)-[:HAS_POSITION_PAY]->(pp_P08_3급);
CREATE (p8)-[:HAS_POSITION_PAY]->(pp_P08_3급);
CREATE (pp_P08_4급:PositionPay {annual_amount: 0});
CREATE (g4)-[:HAS_POSITION_PAY]->(pp_P08_4급);
CREATE (p8)-[:HAS_POSITION_PAY]->(pp_P08_4급);
CREATE (pp_P09_4급:PositionPay {annual_amount: 1044000});
CREATE (g4)-[:HAS_POSITION_PAY]->(pp_P09_4급);
CREATE (p9)-[:HAS_POSITION_PAY]->(pp_P09_4급);
CREATE (pp_P09_5급:PositionPay {annual_amount: 0});
CREATE (g5)-[:HAS_POSITION_PAY]->(pp_P09_5급);
CREATE (p9)-[:HAS_POSITION_PAY]->(pp_P09_5급);
CREATE (pp_P10_5급:PositionPay {annual_amount: 1044000});
CREATE (g5)-[:HAS_POSITION_PAY]->(pp_P10_5급);
CREATE (p10)-[:HAS_POSITION_PAY]->(pp_P10_5급);
CREATE (pp_P10_6급:PositionPay {annual_amount: 0});
CREATE (g6)-[:HAS_POSITION_PAY]->(pp_P10_6급);
CREATE (p10)-[:HAS_POSITION_PAY]->(pp_P10_6급);

CREATE (g1)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EX"}]->(:DifferentialAmount {amount: 3672000, eval_grade: "EX"});
CREATE (g1)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EE"}]->(:DifferentialAmount {amount: 2448000, eval_grade: "EE"});
CREATE (g1)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "ME"}]->(:DifferentialAmount {amount: 1224000, eval_grade: "ME"});
CREATE (g1)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "BE"}]->(:DifferentialAmount {amount: 0, eval_grade: "BE"});
CREATE (g2)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EX"}]->(:DifferentialAmount {amount: 3348000, eval_grade: "EX"});
CREATE (g2)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EE"}]->(:DifferentialAmount {amount: 2232000, eval_grade: "EE"});
CREATE (g2)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "ME"}]->(:DifferentialAmount {amount: 1116000, eval_grade: "ME"});
CREATE (g2)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "BE"}]->(:DifferentialAmount {amount: 0, eval_grade: "BE"});
CREATE (g3)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EX"}]->(:DifferentialAmount {amount: 3024000, eval_grade: "EX"});
CREATE (g3)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "EE"}]->(:DifferentialAmount {amount: 2016000, eval_grade: "EE"});
CREATE (g3)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "ME"}]->(:DifferentialAmount {amount: 1008000, eval_grade: "ME"});
CREATE (g3)-[:HAS_DIFFERENTIAL_AMOUNT {eval_grade: "BE"}]->(:DifferentialAmount {amount: 0, eval_grade: "BE"});

CREATE (g1)-[:HAS_SALARY_LIMIT]->(:SalaryLimit {cap_amount: 85728000});
CREATE (g2)-[:HAS_SALARY_LIMIT]->(:SalaryLimit {cap_amount: 78540000});
CREATE (g3)-[:HAS_SALARY_LIMIT]->(:SalaryLimit {cap_amount: 77724000});

CREATE (:WagePeak {year: 1, rate: 0.9});
CREATE (:WagePeak {year: 2, rate: 0.8});
CREATE (:WagePeak {year: 3, rate: 0.7});

CREATE (p1)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 1.0, eval_grade: "EX"});
CREATE (p1)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.85, eval_grade: "EE"});
CREATE (p1)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.7, eval_grade: "ME"});
CREATE (p1)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});
CREATE (p2)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 1.0, eval_grade: "EX"});
CREATE (p2)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.85, eval_grade: "EE"});
CREATE (p2)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.7, eval_grade: "ME"});
CREATE (p2)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});
CREATE (p5)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 0.85, eval_grade: "EX"});
CREATE (p5)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.7, eval_grade: "EE"});
CREATE (p5)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.55, eval_grade: "ME"});
CREATE (p5)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});
CREATE (p8)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 0.7, eval_grade: "EX"});
CREATE (p8)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.55, eval_grade: "EE"});
CREATE (p8)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.4, eval_grade: "ME"});
CREATE (p8)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});
CREATE (p9)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 0.6, eval_grade: "EX"});
CREATE (p9)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.45, eval_grade: "EE"});
CREATE (p9)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.3, eval_grade: "ME"});
CREATE (p9)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});
CREATE (p10)-[:HAS_BONUS_RATE {eval_grade: "EX"}]->(:BonusRate {rate: 0.6, eval_grade: "EX"});
CREATE (p10)-[:HAS_BONUS_RATE {eval_grade: "EE"}]->(:BonusRate {rate: 0.45, eval_grade: "EE"});
CREATE (p10)-[:HAS_BONUS_RATE {eval_grade: "ME"}]->(:BonusRate {rate: 0.3, eval_grade: "ME"});
CREATE (p10)-[:HAS_BONUS_RATE {eval_grade: "BE"}]->(:BonusRate {rate: 0.0, eval_grade: "BE"});

CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "미국", currency: "USD"}]->(:OverseasPay {country: "미국", currency: "USD", monthly_amount: 10780});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "미국", currency: "USD"}]->(:OverseasPay {country: "미국", currency: "USD", monthly_amount: 9760});
CREATE (g3)-[:HAS_OVERSEAS_PAY {country: "미국", currency: "USD"}]->(:OverseasPay {country: "미국", currency: "USD", monthly_amount: 8620});
CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "일본", currency: "JPY"}]->(:OverseasPay {country: "일본", currency: "JPY", monthly_amount: 1210000});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "일본", currency: "JPY"}]->(:OverseasPay {country: "일본", currency: "JPY", monthly_amount: 1097000});
CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "독일", currency: "EUR"}]->(:OverseasPay {country: "독일", currency: "EUR", monthly_amount: 9100});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "독일", currency: "EUR"}]->(:OverseasPay {country: "독일", currency: "EUR", monthly_amount: 8240});
CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "영국", currency: "GBP"}]->(:OverseasPay {country: "영국", currency: "GBP", monthly_amount: 7790});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "영국", currency: "GBP"}]->(:OverseasPay {country: "영국", currency: "GBP", monthly_amount: 7050});
CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "중국", currency: "CNY"}]->(:OverseasPay {country: "중국", currency: "CNY", monthly_amount: 76000});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "중국", currency: "CNY"}]->(:OverseasPay {country: "중국", currency: "CNY", monthly_amount: 68800});
CREATE (g1)-[:HAS_OVERSEAS_PAY {country: "홍콩", currency: "HKD"}]->(:OverseasPay {country: "홍콩", currency: "HKD", monthly_amount: 80300});
CREATE (g2)-[:HAS_OVERSEAS_PAY {country: "홍콩", currency: "HKD"}]->(:OverseasPay {country: "홍콩", currency: "HKD", monthly_amount: 72700});

CREATE (:StartingStep {job_family: "종합기획직원 5급(G5)", step: 11});
CREATE (:StartingStep {job_family: "종합기획직원 6급(G6)", step: 6});
CREATE (:StartingStep {job_family: "일반사무직원", step: 1});
CREATE (:StartingStep {job_family: "별정직원", step: 4});
CREATE (:StartingStep {job_family: "서무직원", step: 6});
CREATE (:StartingStep {job_family: "청원경찰", step: 6});
```