# M1 우선순위 작업 로드맵 — 삼성중공업 조선소 시뮬레이션
## 삼성중공업 거제조선소 Capacity Planning Simulation M1 우선순위

**마감:** 2026-04-30 (2026-03-25 기준 5주)
**담당:** 원민호
**문서 작성일:** 2026-03-25

---

## 요약

Ouroboros Phase 1-3 문서 완료. 이제 엔진 검증과 실제 동작 테스트 단계. 5주 내 M1 데모 완성을 위해서는 **병렬 작업** 필요. 다음 세션부터는 팀 내 협력 가능한 작업들이 있으므로 작업 분담 추천.

---

## 1주차 (3/25 - 3/31): 엔진 검증과 PoC 기반 구축

### P0: 엔진 코드 리뷰 — v3 behavior 검증
**의존 관계:** 완료 전까지 다른 작업 전체를 차단
**예상 공수:** 2-3일
**차단 요소:** 없음
**다음 단계:** 이후 모든 작업이 여기에 의존

#### 세부 작업
1. **work-smc 브랜치 pull 및 로컬 실행 검증**
   - [ ] 복제: work-smc branch
   - [ ] 실행: 기존 예시 simulation
   - [ ] 확인: v3 engine이 오류 없이 부팅되는지
   - [ ] 문서화: Python version, dependencies, installation steps

2. **35개 behavior 목록 확인 및 조선소 매핑**
   - [ ] 목록화: behavior/* 파일 전체(예상 약 35개)
   - [ ] 매핑: to requirements: `bundle`, `branch`, `acquire_resource`, `release_resource`
   - [ ] 검증: 각 behavior의 JSON schema
   - [ ] 문서화: 경계 사례(예: count mismatch가 있는 bundle)

3. **Bundle behavior behavior 상세 검증**
   - [ ] Read `core/behavior/handlers/transform_handlers.py:150` (bundle impl)
   - [ ] Lot tracking을 위해 `wait_for_items` + `pop` 로직 추적
   - [ ] 테스트: small block 3개 merge → `contents` field 추적 확인
   - [ ] 테스트: incomplete merge → simulation 종료 시 crash 없음 확인

4. **라우팅용 branch behavior**
   - [ ] 확인: `branch(condition=...)`가 prefab 검사와 함께 작동하는지
   - [ ] 테스트: small/medium/large block이 올바르게 route되는지
   - [ ] 경계 사례: condition이 항상 false이면 어떻게 되는지

5. **리소스 제약(acquire/release)**
   - [ ] 검증: `sim.Resource` capacity model
   - [ ] 테스트: capacity 초과 시 queue 형성
   - [ ] 측정: avg_wait_time metric 생성

**검증 계획:**
```python
# test_v3_engine_basics.py
def test_bundle_behavior():
    # 작은 블록 3개 → 조립된 블록 1개
    # 검증: contents tracking, prefab transformation
    pass

def test_branch_routing():
    # 블록 유형 3개 → 경로 3개
    # 검증: small이 pre_painting을 방문하지 않음 등
    pass

def test_resource_capacity():
    # 바닥 면적 초과 → 큐 생성
    # 검증: blocking과 release logic
    pass
```

---

### P1: Bundle behavior 단위 테스트 (P0와 병렬)
**의존 관계:** P0 code review 진행 중
**예상 공수:** 1.5일
**담당:** 팀이 가능하면 위임 가능
**다음 단계:** Phase 2 design 조정에 반영

#### 세부 작업
1. **`tests/test_bundle_merge.py` 생성**
   - [ ] 테스트 케이스 1: small block 3개 → assembled_block 1개
     - 입력: Entity(prefab="small_block") ×3
     - 기대 결과: Entity(prefab="assembled_block"), contents=[id1, id2, id3]

   - [ ] 테스트 케이스 2: block 6개 → assembly 2개(batch processing)
     - 입력: small block 6개
     - 기대 결과: assembled_block 2개가 순차 생성됨

   - [ ] 테스트 케이스 3: sim 종료 시 incomplete bundle 처리
     - 입력: block 2개, count=3, simulation 종료
     - 기대 결과: crash 없이 graceful shutdown

   - [ ] 테스트 케이스 4: Merge가 새 Lot 계층 생성
     - 입력: tags=[component_id]가 있는 small block 3개
     - 기대 결과: new_block.contents가 모든 tag를 포함

2. **JSON 테스트 시나리오 `scenarios/test_merge_only.json` 생성**
   - Source가 small block 3개를 생성(time: 0, 10, 20)
   - Bundle이 3개를 모두 기다린 뒤 assembled_block 생성
   - entity lifecycle 기록

3. **테스트 출력 구조 검증**
   - [ ] Entity registry 형식
   - [ ] Event log schema(이벤트 로그 스키마)
   - [ ] KPI fields(throughput, wait_time, utilization) 정의

**성공 기준:**
- 테스트 케이스 4개 모두 통과
- test_merge_only.json simulation이 끝까지 실행됨
- output에서 Lot tracking 확인

---

### P2: 삼성 미팅 debrief — 3/24 결과 확인
**의존 관계:** 없음
**예상 공수:** 0.5일
**담당:** 원민호(또는 team lead에게 위임)
**다음 단계:** data format과 Merge policy에 반영

#### 세부 작업
1. **3/24 CTO 서경민 미팅 노트 수집**
   - [ ] 확인: block data format(CSV, JSON, raw 중 무엇을 제공하는가?)
   - [ ] 명확화: Merge policy: "모두 모이고 시작" vs. "첫 N개부터 병렬 시작"?
   - [ ] 질문: tact time data source(공정표, 실제 기록, 추정?)
   - [ ] 확인: floor area metrics(m², relative units, sim slots 중 무엇인가?)

2. **새 제약이나 명확화 사항 문서화**
   - [ ] 조건부 처리: data format이 가정과 다르면 Phase 2 design doc 갱신
   - [ ] 조건부 처리: Merge policy가 바뀌면 bundle behavior test 갱신

3. **Simio/DEVS 비교 범위 확인 받기**
   - [ ] 확인할 항목: CTO team이 검증할 metric은 무엇인가? (throughput, avg_wait, utilization?)
   - [ ] 확인할 내용: "same scenario" 기준은 무엇인가? (block mix, tact times, floor areas?)
   - [ ] 일정: CTO comparison result 확보 시점

**성공 기준:**
- 질문 3개 모두 서면 답변 확보
- 모든 design 변경사항 문서화
- CTO 비교 검증 timeline 확인

---

## 2-3주차 (4/1 - 4/14): JSON 시나리오 작성과 통합 테스트

### P3: M1 시나리오 JSON 작성
**의존 관계:** P0 (engine validation), P2 (data format confirmed)
**예상 공수:** 2-3 days
**담당:** 원민호
**다음 단계:** M1 demo execution

#### 세부 작업
1. **`scenarios/m1-demo.json` 생성 — 전체 M1 시나리오**

   구조:
   ```json
   {
     "simulation": {
       "duration": 500,  // sim time units
       "random_seed": 42
     },
     "entities": {
       "small_block": { "properties": {...} },
       "medium_block": { "properties": {...} },
       "large_block": { "properties": {...} },
       "assembled_block": { "properties": {...} }
     },
     "components": [
       { "name": "block_generator", "type": "Source", "params": {...} },
       { "name": "junjo", "type": "Process", "params": {...} },
       { "name": "pre_outfitting", "type": "Process", "params": {...} },
       ...
     ]
   }
   ```

2. **블록 생성 timeline 정의**
   - [ ] 소형 block: 10 time units마다 1개 생성(source가 500 units 동안 30개 생성)
   - [ ] 중형 block: 15 time units마다 1개 생성
   - [ ] 대형 block: 20 time units마다 1개 생성
   - merge 테스트를 위해 소형 block 3개가 맞물리도록 정렬

3. **공정 tact time 정의**
   - [ ] junjo (중조): block당 30 time units(기준)
   - [ ] pre_outfitting (선행의장): 25 time units
   - [ ] daejo (대조): 35 time units
   - [ ] pre_painting (선행도장): 20 time units
   - [ ] erection (탑재): 15 time units

4. **작업장 면적 제약 정의**
   - [ ] junjo: capacity = block 2개(area_per_block = small 4, medium 8, large 12)
   - [ ] pre_outfitting: capacity = medium 1.5개 + large 1개 또는 resource pool = 3 units
   - [ ] daejo: capacity = block 2개
   - [ ] pre_painting: capacity = block 1개(large only)
   - [ ] erection: 제약 없음(출력만)

5. **라우팅 규칙 정의**
   - [ ] 소형 block route: junjo → daejo → erection
   - [ ] 중형 block route: junjo → pre_outfitting → daejo → erection
   - [ ] 대형 block route: junjo → pre_outfitting → daejo → pre_painting → erection
   - [ ] junjo에서 bundle: 소형 3개 → assembled_medium 1개(new prefab)
   - [ ] 조립된 block은 merge 이후 중형 route를 따름

6. **Merge policy 정의**
   - [ ] 사용: `bundle(port="junjo_input", count=3, output_prefab="assembled_medium")`
   - [ ] 전체: 3개가 모두 도착해야 bundle 시작
   - [ ] 조건부 처리: simulation 종료 전 3개 미만 도착 시 queue에 유지(no forced merge)

**산출물:**
- `/d/reference2/ai-control-tower/scenarios/m1-demo.json` (완전하고 유효한 JSON)
- 테스트: `python -c "import json; json.load(open('scenarios/m1-demo.json'))"` 통과

---

### P4: End-to-End 통합 테스트
**의존 관계:** P3 (scenario JSON), P0 (engine ready)
**예상 공수:** 2 days
**담당:** 원민호
**다음 단계:** runtime behavior gap 식별

#### 세부 작업
1. **M1 시나리오를 전체 기간으로 실행**
   ```bash
   cd /work-smc/branch
   python run_simulation.py scenarios/m1-demo.json --output results/m1-demo-run1.json
   ```

2. **모든 entity 생명주기 완료 검증**
   - [ ] 전체: small block이 Sink에 도달
   - [ ] 전체: medium/large block이 Sink에 도달
   - [ ] merge로 assembled block 1개 생성
   - [ ] 없음: 종료 시 queue에 갇힌 entity

3. **KPI 출력 점검**
   - [ ] 전체: throughput(완료된 entity 수)
   - [ ] 평균: process별 wait time
   - [ ] 활용률: process별 busy time 비율
   - [ ] 대기열: depth(queue 동시 최대 수)

4. **M1 인수 기준 대비 검증**
   - [ ] 3종 block이 올바른 경로를 따르는가? → event log 확인
   - [ ] Merge가 새 Entity를 생성하는가? → output의 assembled_block 확인
   - [ ] Lot tracking이 작동하는가? → contents field 확인
   - [ ] 대기열: floor area 초과 시 형성되는가? → junjo queue depth > 0 확인

5. **런타임 오류 문서화**
   - [ ] 조건부 처리: behavior crash 발생 시 work-smc repo에 issue 작성
   - [ ] 조건부 처리: JSON schema mismatch → revise scenario
   - [ ] 조건부 처리: logic gap → add ADR to Phase 2 design doc

**성공 기준:**
- Simulation이 오류 없이 끝까지 실행됨
- 출력 JSON이 유효함
- KPI metrics가 기대 범위와 일치함(M1 demo checklist 참고)

---

## 4주차 (4/15 - 4/21): 데모 준비와 문서화

### P5: M1 데모 시나리오 문서화
**의존 관계:** P4(integration test 완료)
**예상 공수:** 1.5 days
**담당:** 원민호
**다음 단계:** 발표 자료

#### 세부 작업
1. **데모 서사 문서 작성**
   - `/d/reference2/ai-control-tower/research/til/2026-04-15-m1-demo-walkthrough.md`
   - 각 단계 설명: Source → bundle → branch → Sink
   - trial run의 예상 KPI 값 표시
   - 수행한 parameter tuning 문서화

2. **JSON 시나리오 walkthrough 작성**
   - m1-demo.json 주석 버전 작성
   - 각 component 역할 설명
   - 수정 방법 설명: block generation rate, tact times, floor areas

3. **샘플 출력 보고서 생성**
   - simulation 실행 후 KPI output 캡처
   - final demo report용 `.md` 템플릿 생성
   - 형식: Throughput | Avg Wait | Utilization 표

---

### P6: CTO 비교 검증 준비 (Simio/DEVS 준비)
**의존 관계:** P4 (baseline scenario), P2 (CTO agreement)
**예상 공수:** 1.5 days
**담당:** 원민호
**다음 단계:** 외부 검증 활성화

#### 세부 작업
1. **시나리오를 중립 형식으로 export**
   - m1-demo.json에 모든 parameter가 명시됐는지 확인
   - tact times, floor areas, block types의 `.csv` export 생성
   - CTO 팀이 이를 독립적으로 읽을 수 있는지 검증

2. **비교 기준선 문서화**
   - `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/04-comparison-setup.md`
   - "무엇을 비교하는가?" — metrics 목록
   - "CTO 팀은 Simio/DEVS를 어떻게 실행하는가?" — scenario mapping
   - "결과 마감은 언제인가?" — timeline

3. **결과 차이 처리 준비**
   - 결과가 다르면 허용 가능한 tolerance는 얼마인가?
   - behavior mismatch는 누가 조사하는가?
   - findings는 어디에 문서화하는가?

---

## 5주차 (4/22 - 4/30): 최종 테스트와 M1 데모

### P7: M1 데모 실행과 보고
**의존 관계:** 모든 선행 작업
**예상 공수:** 2-3 days
**담당:** 원민호 + team(데모 발표가 필요할 경우)
**다음 단계:** M2 planning

#### 세부 작업
1. **최종 시나리오 검증 실행**
   - [ ] 실행: m1-demo.json 3× with different random seeds
   - [ ] 검증: results consistent within 5% variance
   - [ ] 발표용 screenshot/log 캡처

2. **M1 데모 보고서 작성**
   - `/d/reference2/ai-control-tower/research/til/2026-04-30-m1-demo-report.md`
   - 섹션:
     - Scenario 요약(blocks, processes, constraints)
     - KPI 결과(throughput, wait, utilization)
     - M1 인수 기준 checklist(pass/fail)
     - screenshot/diagram
     - 알려진 한계(구현되지 않은 항목)

3. **이해관계자 발표 준비**
   - [ ] 다음을 보여주는 deck 또는 live demo 준비:
       - Block 생성과 흐름
       - junjo의 Merge event
       - block type별 routing
       - floor area constraint 정의에 따른 queueing
       - 최종 KPI report

4. **피드백 수집**
   - [ ] scenario가 삼성 기대와 맞는가?
   - [ ] M1 acceptance criteria를 충족하는가?
   - [ ] M2에서 무엇을 우선해야 하는가?

---

## 열린 이슈 추적

| 이슈 | 상태 | 담당 | 기한 |
|-------|--------|-------|-----|
| 3/24 삼성중공업 미팅 결과 | PENDING | 원민호 | 3/26 |
| v3 엔진 engine 코드 리뷰 | PENDING | 원민호 | 3/31 |
| Bundle behavior 단위테스트 | PENDING | TBD | 4/3 |
| M1 JSON scenario 완성 | PENDING | 원민호 | 4/7 |
| End-to-end integration test | PENDING | 원민호 | 4/14 |
| Simio/DEVS 비교기준 합의 | PENDING | 서경민 CTO | 4/14 |
| M1 demo 완료 | PENDING | 원민호 | 4/30 |

---

## 추천 팀 작업 분배

**팀원이 가능하다면:**

| 작업 | 담당자 | 기간 | 시작 |
|------|----------|----------|-------|
| P0: Engine code review | 원민호 | 2-3d | 3/25 |
| P1: Bundle 단위 테스트 | Dev(가능한 경우) | 1.5일 | 3/25(병렬) |
| P2: Samsung meeting debrief | 원민호 or PM | 0.5d | 3/25 |
| P3: M1 scenario JSON | 원민호 | 2-3d | 4/1 |
| P4: Integration test | 원민호 | 2d | 4/7 |
| P5: Demo documentation | 원민호 | 1.5d | 4/15 |
| P6: CTO comparison prep | 원민호 | 1.5d | 4/15 |
| P7: M1 demo & report | 원민호 + PM | 2-3d | 4/22 |

**핵심 경로(직렬):** P0 → P3 → P4 → P7 = 약 9일
**병렬 작업 적용 시(P1, P2):** 겹쳐서 약 7일 calendar time으로 압축 가능

---

## M1 인수 기준 체크리스트

M1 demo 검증에 사용한다.

- [ ] 3종 블록이 Prefab별 다른 경로를 정상적으로 따름
- [ ] Entity Merge 후 새 ID 생성 및 이전 Entity Destroy
- [ ] Merge된 Entity에서 원래 부품 Lot 추적 가능
- [ ] 배치 면적 초과 시 대기(Queue) 발생
- [ ] 시뮬레이션 완료 후 KPI 통계 출력
- [ ] Octopus v3 엔진에서 JSON만으로 구현됨 (새 코드 없음)
- [ ] 시나리오 재현 가능(동일 JSON → 동일 결과, ±random variance)

---

## 다음 세션 액션(권장)

1. **M1 deadline이 고정인지 확인** — 4/30은 움직일 수 없는가?
2. **팀원 배정** — P1, P2를 도울 수 있는 사람은 누구인가?
3. **삼성 미팅 debrief 일정 잡기** — 3/24 미팅 노트는 언제 확보되는가?
4. **work-smc branch pull** — 즉시 실행하고 P0 시작
5. **테스트 프레임워크 설정** — unit test는 어디에 둘 것인가? (`tests/` directory?)

---

## 참고 자료

- Requirements: `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/01-requirements.md`
- Design (ADR): `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/02-design.md`
- Verification Plan: `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/03-verification.md`
- v3 Learnings: `/d/reference2/ai-control-tower/research/til/2026-03-25-ouroboros-capacity-planning-v3-behaviors.md`
