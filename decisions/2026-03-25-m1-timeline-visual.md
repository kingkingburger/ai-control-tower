# M1 일정 — 시각 개요
**삼성중공업 조선소 시뮬레이션 데모**
**마감: 2026-04-30 (2026-03-25 기준 5주)**

```
1주차 (3/25-3/31): 기반 구축과 검증
┌─────────────────────────────────────────────────────┐
│ P0: 엔진 코드 리뷰(차단 작업)           │ 원민호    │
│ ├─ work-smc branch pull                  │ 3/25     │
│ ├─ 기본 예시 실행                        │ 3/25     │
│ ├─ behavior 35개 목록 검증               │ 3/26-27  │
│ ├─ bundle/branch/resource 테스트         │ 3/28-29  │
│ └─ 발견 사항 TIL 작성                    │ 3/30     │
├─────────────────────────────────────────────────────┤
│ P1: Bundle 단위 테스트(병렬)             │ Dev/TBD  │
│ ├─ test_bundle_merge.py 생성             │ 3/25-26  │
│ ├─ test_merge_only.json 생성             │ 3/26-27  │
│ └─ pytest 실행 및 output 검증            │ 3/28-29  │
├─────────────────────────────────────────────────────┤
│ P2: 삼성 미팅 debrief(빠른 작업)         │ 원민호    │
│ ├─ 3/24 미팅 노트 수집                   │ 3/25-26  │
│ ├─ 핵심 질문 3개 답변 확보               │ 3/27     │
│ └─ 제약사항 문서화                       │ 3/30     │
└─────────────────────────────────────────────────────┘
의사결정 게이트: 2주차 전 P0가 성공적으로 완료되어야 함

2-3주차 (4/1-4/14): 시나리오와 통합
┌─────────────────────────────────────────────────────┐
│ P3: M1 Scenario JSON 작성                │ 원민호    │
│ ├─ block 생성 정의(small/med/lg)         │ 4/1-2    │
│ ├─ process별 tact time 정의              │ 4/2-3    │
│ ├─ floor area 제약 정의                  │ 4/3-4    │
│ ├─ routing rule 정의                     │ 4/4-5    │
│ ├─ merge policy(bundle) 정의             │ 4/5-6    │
│ └─ JSON syntax 검증                      │ 4/6-7    │
│ 산출물: /scenarios/m1-demo.json    │
├─────────────────────────────────────────────────────┤
│ P4: End-to-End 통합 테스트               │ 원민호    │
│ ├─ 전체 M1 scenario 실행(500 sim units)  │ 4/8-9    │
│ ├─ 모든 entity 완료 검증                 │ 4/9      │
│ ├─ KPI output 점검                       │ 4/10     │
│ ├─ M1 acceptance criteria 검증           │ 4/10-11  │
│ └─ 오류 문서화                           │ 4/11-12  │
│ 산출물: /results/m1-run.json        │
└─────────────────────────────────────────────────────┘
의사결정 게이트: 4주차 전 P4가 모든 M1 기준을 통과해야 함

4주차 (4/15-4/21): demo 준비
┌─────────────────────────────────────────────────────┐
│ P5: M1 demo 문서화                       │ 원민호    │
│ ├─ demo walkthrough TIL 생성             │ 4/15-16  │
│ ├─ JSON scenario 주석 작성               │ 4/16-17  │
│ └─ sample output 보고서 생성             │ 4/17-18  │
├─────────────────────────────────────────────────────┤
│ P6: CTO 비교 준비                        │ 원민호    │
│ ├─ scenario를 neutral format으로 export  │ 4/15-16  │
│ ├─ comparison baseline 문서화            │ 4/16-17  │
│ └─ 차이 대응 계획 수립                   │ 4/18-19  │
│ 산출물: 04-comparison-setup.md      │
└─────────────────────────────────────────────────────┘
의사결정 게이트: 최종 demo 실행 준비 완료

5주차 (4/22-4/30): M1 demo와 report
┌─────────────────────────────────────────────────────┐
│ P7: M1 demo 실행과 보고                  │ 원민호    │
│ ├─ 최종 scenario 검증(3회 실행)          │ 4/22-24  │
│ ├─ M1 demo report 생성                   │ 4/24-25  │
│ ├─ presentation slides 준비              │ 4/25-26  │
│ ├─ stakeholder feedback 수집             │ 4/27-29  │
│ └─ 최종 전달                        │ 4/30     │
│ 산출물: /research/til/2026-04-30-m1-demo-report.md
└─────────────────────────────────────────────────────┘
```

---

## 핵심 경로 시각화

```
직렬 의존 관계(blocking chain):
P0 (엔진 리뷰)
    ↓
P3 (M1 Scenario JSON) + P2 (삼성 Debrief)
    ↓
P4 (통합 테스트)
    ↓
P5 + P6 (demo 준비)
    ↓
P7 (최종 demo)

병렬 가능 구간:
┌─ P0 (2-3d) ──────────────────┐
│  P1 (1.5d) 병렬 ─────┐      │
│  P2 (0.5d) 병렬 ─────┤      │
└─────────────────────→ P3 (2-3d) → P4 (2d) → P5/P6 → P7 (2-3d)

핵심 경로(직렬): 8-11일
병렬 작업 적용 시: 약 7일 calendar(P1 + P2가 P0와 겹침)
```

---

## 주차별 마일스톤과 게이트

| 주차 | 마감일 | 마일스톤 | 게이트 |
|------|----------|----------|-------|
| **1** | 3/31 | P0 engine review 완료, P1/P2 시작 | YES: P0 통과 필요 |
| **2-3** | 4/14 | P3 JSON 완료, P4 integration test 통과 | YES: P4 기준 충족 |
| **4** | 4/21 | P5/P6 문서 준비, demo prep 완료 | YES: demo 준비 완료 |
| **5** | 4/30 | P7 M1 demo 전달, report 발행 | FINAL: M1 성공 |

---

## 작업 의존성 지도

```
비동기(세션 전):
  Samsung 3/24 미팅 노트 ──→ P2 (Meeting Debrief)

세션 1 (1주차):
  P0 (엔진 리뷰) ─────────┬→ GATE ──→ 세션 2 진행
  P1 (Bundle 테스트) ─────┴─→ 검증
  P2 (Meeting Debrief) ──────→ 확인

세션 2+ (2-3주차):
  P0 결과 + P2 결과 ───────→ P3 (JSON Scenario)
                              ↓
                          P4 (통합 테스트)
                              ↓
                          GATE: 기준 충족? ──→ 세션 3

세션 3 (4주차):
  P4 결과 ──→ P5 (demo 문서화)
              P6 (CTO 비교 준비)

세션 4 (5주차):
  P5/P6 결과 ──→ P7 (최종 demo와 report)
                      ↓
                   M1 전달(4/30)
```

---

## 리소스 배분 모델

### 단독 모드(원민호 only)
```
1주차:  P0(차단 작업) + P2(빠른 작업) = 2.5일 → P1 생략
2-3주차: P3(2-3일) + P4(2일) = 4-5일
4주차:  P5(1.5일) + P6(1.5일) = 3일
5주차:  P7(2-3일) = demo

합계: 약 11-13일을 5주에 분산(마감 가능)
위험: 병렬성 없음, backup 없음
```

### 팀 모드 (원민호 + Dev team)
```
1주차:  P0(원민호) || P1(Dev team) || P2(원민호) = 2.5일 병렬
2-3주차: P3(원민호) + P4(원민호) = 4-5일(P1 결과 사용 가능)
4주차:  P5(원민호) + P6(원민호) = 3일
5주차:  P7(원민호 + PM) = demo + stakeholder feedback

합계: 실제 작업 약 7일, calendar 기준 약 5주(안전 buffer)
위험: 분산 처리, P1 결과가 P3/P4를 가속
```

---

## M1 인수 기준 최종 체크리스트

성공적인 M1 데모를 검증할 때 이 목록을 사용한다:

```
기능 요구사항:
[ ] 3종 block(small/medium/large)이 Source에서 생성됨
[ ] 각 block type이 올바른 process route를 따름:
    [ ] Small: junjo → daejo → erection
    [ ] Medium: junjo → pre_outfitting → daejo → erection
    [ ] Large: junjo → pre_outfitting → daejo → pre_painting → erection
[ ] Merge 발생: small block 3개 → assembled_medium 1개
[ ] Entity lifecycle: Source → Processes → Merge → Sink(갇힌 entity 없음)
[ ] Lot tracking: assembled_medium.contents에 원래 block ID 3개 표시

제약 요구사항:
[ ] Floor area capacity 적용(full 상태면 block queue)
[ ] Resource allocation 작동(junjo/daejo 등으로 block 배정)
[ ] Process별 tact time이 올바르게 적용됨
[ ] Deadlock 없음(모든 entity가 결국 Sink 도달)

KPI 보고:
[ ] Total throughput: 완료 entity N개
[ ] Process별 평균 대기 시간: 표 형식
[ ] Process별 활용률: busy time 비율
[ ] Queue statistics: process별 max depth, avg length

구현 요구사항:
[ ] 새 custom Python code 0개(JSON + v3 behaviors only)
[ ] Scenario 재현 가능(동일 JSON → 3회 실행 기준 ±5% variance)
[ ] Output format이 유효한 JSON
[ ] Simulation이 오류 없이 끝까지 실행됨

문서화 요구사항:
[ ] M1 demo report 발행
[ ] Scenario walkthrough 문서화
[ ] KPI output 설명
[ ] 알려진 한계 명시
[ ] M2 recommendation 포함
```

---

## 스탠드업용 1쪽 요약

**질문: 계획은 무엇인가?**
답변: Octopus v3 engine과 JSON scenario로 M1 demo를 전달하는 5주 sprint.

**질문: 무엇을 먼저 하는가?**
답변: Engine code review(P0) — v3에 bundle/branch/resource behavior가 있는지 검증해야 함.

**질문: 마감은 언제인가?**
답변: 2026-04-30(5주, 약 35일).

**질문: 병렬화 가능한가?**
답변: 가능 — P0 실행 중 P1(단위 테스트)과 P2(미팅 debrief)를 병렬 진행할 수 있음.

**질문: P0가 실패하면 어떻게 되는가?**
답변: v3 engine에 핵심 기능이 없다는 뜻 → 재설계 필요. 1주차 gate에서 판단.

**질문: 누가 무엇을 맡는가?**
답변: 원민호가 P0/P3/P4/P7 직렬 구간을 이끌고, Dev team은 P1 병렬 작업을 맡는다. P5/P6는 함께 준비한다.

**질문: 가장 큰 위험은?**
답변: v3 engine이 Merge 또는 routing을 지원하지 않을 가능성이다. 초기 코드 리뷰(P0)로 완화한다.

---

## 빠른 시작 명령 (1주차)

```bash
# 세션 1, 1일차: P0 시작(Engine Review)
cd /octopus-v3-engine
git checkout work-smc
git pull origin work-smc
pip install -r requirements.txt
python examples/run_basic_sim.py   # engine boot 확인

# behavior 개수 세기
find core/behavior -name "*.py" | wc -l

# 핵심 behavior 검색
grep -n "def bundle" core/behavior/handlers/transform_handlers.py
grep -n "def branch" core/behavior/handlers/control_handlers.py
grep -n "def acquire_resource" core/behavior/handlers/resource_handlers.py

# 발견 사항 문서 생성
cat > /d/reference2/ai-control-tower/research/til/2026-03-26-engine-review-findings.md << 'EOF'
# Engine Review 발견 사항 — 2026-03-26

## Behavior 검증
- [ ] bundle: ✓ core/behavior/handlers/transform_handlers.py:150에서 발견
- [ ] branch: ✓ core/behavior/handlers/control_handlers.py:XXX에서 발견
- [ ] acquire_resource: ✓ core/behavior/handlers/resource_handlers.py:XXX에서 발견
- [ ] release_resource: ✓ 발견

## Behavior 테스트 결과
- [ ] bundle이 올바른 prefab으로 새 Entity를 생성
- [ ] bundle이 Lot을 추적(contents field)
- [ ] branch가 entity.prefab 조건에 따라 route
- [ ] acquire_resource가 capacity 초과 시 block
- [ ] release_resource가 queue block 해제

## 발견된 issue(있는 경우)
- 없을 것으로 예상하지만, 오류가 있으면 여기에 문서화

## 권고
✓ P3(JSON scenario) 진행 준비 완료
EOF
```

---

## 다음 단계

1. **이 페이지 출력** — standup 또는 team chat에 붙여넣기
2. **마감 확인** — 4/30이 정말 고정 마감인지 확인
3. **리소스 배정** — P1 담당자 결정
4. **삼성 미팅 노트 확보** — 1주차 시작 전 비동기 준비
5. **work-smc 가져오기** — Day 1 첫 명령
6. **의사결정 게이트 예약** — P0→P3(1주차), P4→P5(4주차)
