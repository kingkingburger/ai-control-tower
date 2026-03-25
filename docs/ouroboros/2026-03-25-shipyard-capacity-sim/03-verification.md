# 삼성중공업 거제조선소 Capacity Planning Simulation
## 03 — 검증 계획

> Ouroboros Phase 3 산출물 | 2026-03-25

---

## 검증 전략 개요

3단계 검증으로 구성한다:
1. **단위 검증** — 각 behavior가 조선소 시나리오에서 정상 동작하는지
2. **통합 검증** — 5공정 파이프라인이 end-to-end로 동작하는지
3. **비교 검증** — Simio/DEVS 결과와 Octopus 결과가 일치하는지

---

## 1. 단위 검증 시나리오

### 1.1 Entity Merge (bundle)

**시나리오: 소형 블록 3개 → assembled_block 1개**

| 스텝 | 행동 | 기대 결과 |
|------|------|----------|
| 1 | Source에서 small_block 3개 생성 | EntityRegistry에 3개 등록 |
| 2 | 3개가 중조 input 포트에 도착 | port.length == 3 |
| 3 | bundle(count=3, output_prefab="assembled_block") 실행 | 새 Entity 생성, prefab=="assembled_block" |
| 4 | Lot 추적 확인 | new_entity.contents에 원래 3개 entity ID 포함 |
| 5 | 원본 entity 상태 확인 | registry에서 contained 상태 |

**검증 코드:**
```python
def test_bundle_creates_assembled_block():
    result = run_simulation("test_merge_only.json", duration=100)
    assembled = [e for e in result.entities if e.prefab == "assembled_block"]
    assert len(assembled) >= 1
    assert len(assembled[0].contents) == 3
```

**엣지케이스:**
- 소형 블록이 2개만 도착하고 시뮬레이션 종료 → bundle이 대기 중 종료, 에러 없이 완료
- 소형 블록 6개 도착 → 2번 bundle 실행, assembled_block 2개 생성

### 1.2 공정 라우팅 분기

**시나리오: 3종 블록이 각각 다른 경로로 분배**

| 블록 종류 | 경로 | 거쳐야 할 공정 |
|-----------|------|---------------|
| small (route=short) | 중조 → 대조 → 탑재 | 3개 |
| medium (route=medium) | 중조 → 선행의장 → 대조 → 탑재 | 4개 |
| large (route=full) | 중조 → 선행의장 → 대조 → 선행도장 → 탑재 | 5개 |

**검증 방법:**
```python
def test_routing_by_block_type():
    result = run_simulation("test_routing.json", duration=500)
    events = result.event_log

    # large 블록은 반드시 pre_painting을 거침
    large_events = [e for e in events if e.prefab == "large_block"]
    assert any(e.component == "pre_painting" for e in large_events)

    # small 블록은 pre_outfitting을 거치지 않음
    small_events = [e for e in events if e.prefab == "small_block"]
    assert not any(e.component == "pre_outfitting" for e in small_events)
```

### 1.3 배치 면적 제약

**시나리오: 면적 capacity=9, 블록 area=3인 경우 동시 3개까지만 작업**

| 스텝 | 행동 | 기대 결과 |
|------|------|----------|
| 1 | 블록 4개가 동시에 중조에 도착 | 3개 acquire 성공, 1개 대기 |
| 2 | 첫 번째 블록 처리 완료 → release | 대기 중인 4번째 블록 acquire 성공 |
| 3 | KPI 확인 | junjo_queue.avg_wait_time > 0 |

**검증 방법:**
```python
def test_floor_area_constraint():
    result = run_simulation("test_floor_area.json", duration=300)
    queue_kpi = result.kpi["junjo_queue"]
    assert queue_kpi["max_length"] > 0  # 대기 발생 확인
    floor_kpi = result.kpi["junjo_floor"]
    assert floor_kpi["utilization"] > 0.5  # 면적 활용률 50% 이상
```

### 1.4 택트타임 (확률 분포)

**시나리오: triangular(20, 30, 45) 분포로 택트타임 적용**

**검증 방법:**
```python
def test_tact_time_distribution():
    result = run_simulation("test_tact_time.json", duration=10000)
    hold_durations = [e.duration for e in result.events if e.type == "hold_completed"]
    assert min(hold_durations) >= 20
    assert max(hold_durations) <= 45
    assert 25 < statistics.mean(hold_durations) < 35  # 평균은 mode 근처
```

---

## 2. 통합 검증 시나리오 (E2E)

### 2.1 M1 데모 시나리오 전체 흐름

**전제 조건:**
- 시뮬레이션 시간: 480분 (8시간 1교대)
- Source: 소형 블록 평균 10분 간격 생성 (exponential)
- 중조: bundle(3) + hold(triangular 20,30,45)
- 대조: hold(triangular 15,25,35)
- 탑재: hold(40) + destroy
- 면적: 중조 9슬롯, 대조 6슬롯

**E2E 스텝:**

| # | 행동 | 기대 결과 | 검증 방법 |
|---|------|----------|----------|
| 1 | 시뮬레이션 시작 | Source 생성 시작 | event_log에 entity_created 이벤트 |
| 2 | 소형 블록 3개 중조 도착 | bundle 실행 | entity_bundled 이벤트, consumed=[3 IDs] |
| 3 | assembled_block 중조에서 처리 | hold 완료 | hold_completed, duration ∈ [20,45] |
| 4 | 라우팅 분기 | route 태그 기반 분배 | entity가 올바른 공정에 도착 |
| 5 | 대조 처리 | hold 완료 | hold_completed |
| 6 | 탑재 → destroy | Entity 소멸 | entity_destroyed 이벤트 |
| 7 | KPI 리포트 | 처리량, 대기시간, 활용률 | kpi_results 객체 검증 |

**성공 판정 기준:**
- [ ] 480분 시뮬레이션이 에러 없이 완료
- [ ] throughput ≥ 10 (8시간에 최소 10블록 완성)
- [ ] 모든 공정의 utilization > 0 (유휴 공정 없음)
- [ ] queue 대기 발생 (면적 제약이 실제로 작동)
- [ ] Lot 추적: 완성 블록에서 원래 소형 블록 ID 역추적 가능

### 2.2 다종 블록 혼합 시나리오

**전제 조건:**
- 3종 Source: small(60%), medium(30%), large(10%) 비율 생성
- 각각 다른 공정 경로
- 시뮬레이션 시간: 2400분 (5일)

**성공 판정 기준:**
- [ ] 3종 블록이 각각 올바른 경로를 따름
- [ ] large 블록만 pre_painting 통과
- [ ] small 블록은 pre_outfitting/pre_painting 미통과
- [ ] 각 공정 throughput이 비율에 맞게 분포

---

## 3. 비교 검증 (M3)

### 3.1 Simio 비교 검증

**주체:** 서경민 CTO NSL 연구실 학부생 2명
**방법:** 동일 시나리오를 Simio로 구현하여 결과 비교

**비교 지표:**

| 지표 | 단위 | 허용 오차 |
|------|------|----------|
| Throughput (처리량) | blocks/day | ±3% |
| Average Wait Time | minutes | ±5% |
| Resource Utilization | % | ±3% |
| WIP (재공품) | blocks | ±2개 |

**비교 프로토콜:**
1. 동일 입력 JSON (블록 수, 택트타임, 면적)으로 양쪽 실행
2. 난수 시드 고정 (또는 100회 배치 실행 평균)
3. 지표별 차이를 표로 정리
4. 3% 초과 항목에 대해 원인 분석

### 3.2 DEVS 비교 검증

**주체:** 서경민 CTO NSL 연구실 석사 3명
**방법:** DEVS 형식론으로 동일 시스템 모델링, 결과 비교

**DEVS 모델 구조:**
- Atomic Model: 각 공정 (중조, 대조 등)
- Coupled Model: 공정 간 연결 (라우팅 포함)
- 입력: 동일 블록 데이터

**비교 포인트:**
- DES(salabim) vs DEVS의 이벤트 처리 순서 차이
- 동시 이벤트(tie-breaking) 처리 방식 차이
- 결과 수렴성 (배치 100회 평균)

### 3.3 AnyLogic 대체 검증

**주체:** 삼성중공업 내부
**방법:** 현재 AnyLogic+JS+Excel+Python으로 처리하는 결과와 Octopus 결과 비교

**확인 항목:**
- 동일 블록 데이터 입력 시 유사한 capacity 결과 도출
- Octopus가 AnyLogic 대비 설정 편의성 우위 확인
- 디지털트윈 연동 가능성 확인

---

## 4. 성능 기준

| 기준 | 목표 | 측정 방법 |
|------|------|----------|
| 시뮬레이션 실행 시간 (480분 모델) | < 5초 | time.time() 측정 |
| 시뮬레이션 실행 시간 (30일 모델) | < 30초 | batch runner 측정 |
| 메모리 사용량 (1000 블록) | < 500MB | tracemalloc |
| 동시 시뮬레이션 (멀티프로세스) | 5개 이상 | concurrent.futures |
| EventLog 파일 크기 (480분) | < 10MB | msgpack.zst 압축 |

---

## 5. 자동화 실행 계획

### 테스트 구조

```
test/
├── shipyard/
│   ├── test_merge.py          # 1.1 bundle 검증
│   ├── test_routing.py        # 1.2 라우팅 검증
│   ├── test_floor_area.py     # 1.3 면적 제약 검증
│   ├── test_tact_time.py      # 1.4 택트타임 검증
│   ├── test_e2e_single.py     # 2.1 단일 종류 E2E
│   ├── test_e2e_mixed.py      # 2.2 혼합 E2E
│   └── test_performance.py    # 4. 성능 기준
├── shipyard/fixtures/
│   ├── test_merge_only.json
│   ├── test_routing.json
│   ├── test_floor_area.json
│   ├── test_e2e_single.json
│   └── test_e2e_mixed.json
```

### 실행 방법

```bash
# 전체 조선소 테스트
uv run pytest test/shipyard/ -v

# 단위만
uv run pytest test/shipyard/test_merge.py -v

# 성능 벤치마크
uv run pytest test/shipyard/test_performance.py -v --benchmark
```

---

## 6. 성공/실패 판정 매트릭스

| 카테고리 | 전체 통과 | 부분 통과 | 실패 |
|---------|-----------|-----------|------|
| 단위 (4종) | 4/4 pass | 3/4 pass (면적 제약 미달 허용) | Merge 또는 라우팅 fail |
| E2E (2종) | 2/2 pass | 1/2 pass (혼합은 M2로) | 단일종류 E2E fail |
| 비교 검증 | 모든 지표 3% 이내 | 일부 5% 이내 | 주요 지표 10%+ 차이 |
| 성능 | 모든 기준 충족 | 30일 모델만 미달 | 480분 모델 30초+ |

### M1 데모 최소 통과 기준

- [ ] 단위 검증 4종 모두 pass
- [ ] E2E 단일종류 시나리오 pass
- [ ] 시뮬레이션 480분 모델 < 10초
- [ ] KPI 리포트 출력 (throughput, utilization, wait_time)
- [ ] Lot 추적 가능 (assembled_block → 원래 small_block IDs)

---

## 검증 타임라인

| 주차 | 검증 활동 |
|------|----------|
| Week 1 | test_merge.py, test_routing.py 작성 + 통과 |
| Week 2 | test_floor_area.py, test_tact_time.py 작성 + 통과 |
| Week 3 | test_e2e_single.py 작성 + 통과, Lot 추적 검증 |
| Week 4 | test_e2e_mixed.py, test_performance.py + 데모 리허설 |
| Week 5 | M1 데모 실행 + 삼성중공업 피드백 수렴 |
| M2 이후 | Simio/DEVS 비교 검증 (서경민 CTO 팀 협업) |
