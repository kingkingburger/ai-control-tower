# 삼성중공업 거제조선소 Capacity Planning Simulation
## 02 — 설계 문서

> Ouroboros Phase 2 산출물 | 모호성: 13% | 2026-03-25

---

## 핵심 설계 결정: v3 엔진을 그대로 활용한다

v3 엔진(work-smc 브랜치)을 탐색한 결과, 삼성중공업 요구사항의 **90% 이상이 이미 구현되어 있다.**
새로운 컴포넌트나 behavior를 만들 필요 없이, **JSON 시나리오 구성만으로 M1 데모가 가능하다.**

---

## ADR (Architecture Decision Records)

### ADR-1: Entity Merge에 `bundle` behavior 사용

**결정:** 중조 공정에서 소형 블록 3개를 합치는 데 `bundle` behavior를 사용한다.

**대안 비교:**

| 대안 | 장점 | 단점 | 판정 |
|------|------|------|------|
| `bundle(port, count=3, output_prefab)` | 같은 포트에서 N개 수집, 단순명확 | 다른 포트 조합 불가 | **M1 채택** |
| `assemble(consume=[ConsumeSpec])` | 다른 포트에서 각각 수집 가능, 유연 | JSON이 복잡 | M2에서 필요시 |
| `transform(new_prefab)` | 기존 entity prefab만 변경 | 여러 entity를 하나로 못 합침 | 부적합 |

**근거 (코드 기반):**
- `bundle`은 `core/behavior/handlers/transform_handlers.py:150`에서 구현
- 같은 포트에서 `count`개 entity를 `wait_for_items` + `pop`으로 수집
- `output_prefab`으로 새 Entity 생성, `registry.contain(child, new_entity)`로 Lot 추적
- 삼성중공업 시나리오에서 소형 블록은 모두 같은 경로(중조)로 오므로 단일 포트 수집으로 충분

### ADR-2: 공정 라우팅에 `branch` behavior 사용

**결정:** Prefab 종류에 따른 공정 경로 분기를 `branch` behavior로 처리한다.

**대안 비교:**

| 대안 | 장점 | 단점 | 판정 |
|------|------|------|------|
| `branch` behavior (Tier 2) | 조건별 다른 behavior 파이프라인 실행, 유연 | 컴포넌트 내부 로직 | **M1 채택** |
| `switch` behavior | 다중 분기에 적합 | branch보다 복잡 | 3종 이상이면 M2 |
| Conveyor RoutingNode | 인프라 수준 라우팅, 검증됨 | 컨베이어 구조 필요 | 물리 이동 필요시 |
| Dispatcher Rules | 규칙 기반 분배 | 오버킬 | 불필요 |

**근거:** 조선소 공정은 블록 종류에 따라 **일부 공정을 건너뛰는** 패턴. 각 공정 컴포넌트 내부에서 `branch(condition="entity.prefab == 'large_block'")`으로 다음 output 포트를 선택하면 된다.

### ADR-3: 배치 면적 제약에 `acquire_resource` / `release_resource` 사용

**결정:** 공정별 배치 면적을 `Resource` 컴포넌트(capacity=N)로 모델링한다.

**근거:**
- v3의 `acquire_resource` behavior가 `sim.Resource`를 사용하여 capacity 기반 블로킹을 지원
- 블록 크기별 면적 소비: 소형=1, 중형=2, 대형=4 (단위: 면적 슬롯)
- 면적 가득 참 → `acquire_resource`가 블록 → Queue에서 대기 발생
- 이 패턴은 DES에서 표준적인 Resource Constraint 모델링 방식

### ADR-4: Merge 정책은 "모두 모이고 시작"

**결정:** 중조에서 소형 블록 3개가 모두 도착한 후 assemble을 시작한다.

**근거:** `bundle` behavior가 `port.wait_for_items`를 count회 호출하므로, 자연스럽게 N개가 모일 때까지 대기한다. 실제 조선소에서도 부품이 모두 준비된 후 조립을 시작한다.

---

## 시스템 아키텍처: v3 컴포넌트 매핑

```
[Source: block_generator]
  │ create_entity(prefab=small/medium/large)
  │ set_tag(route_type=...)
  ▼
[Dispatcher: route_by_type]
  │ prefab별 다른 output 포트로 분배
  ├──→ [중조: junjo]          ←── 모든 블록
  │      bundle(3) → assembled_block
  │      hold(tact_time)
  │      branch(prefab) → 포트 선택
  │
  ├──→ [선행의장: pre_outfitting]  ←── medium, large만
  │      hold(tact_time)
  │
  ├──→ [대조: daejo]          ←── 모든 블록
  │      hold(tact_time)
  │
  ├──→ [선행도장: pre_painting]  ←── large만
  │      hold(tact_time)
  │
  └──→ [탑재: erection]       ←── 모든 블록
         destroy_entity → KPI 집계

[Resource: floor_area_*]  ←── 각 공정별 배치면적 제약
  acquire_resource → hold → release_resource
```

---

## Prefab 정의

```json
{
  "prefabs": [
    {
      "name": "small_block",
      "tags": { "size": "small", "route": "short" },
      "properties": { "weight": 50, "area": 1 }
    },
    {
      "name": "medium_block",
      "tags": { "size": "medium", "route": "medium" },
      "properties": { "weight": 150, "area": 2 }
    },
    {
      "name": "large_block",
      "tags": { "size": "large", "route": "full" },
      "properties": { "weight": 300, "area": 4 }
    },
    {
      "name": "assembled_block",
      "tags": { "size": "assembled", "route": "medium" },
      "properties": { "weight": 200, "area": 3 }
    }
  ]
}
```

---

## 핵심 컴포넌트별 Behavior Pipeline

### 1. Source — block_generator

```json
{
  "name": "block_generator",
  "type": "user",
  "behaviors": [
    { "type": "loop", "count": -1, "body": [
      { "type": "create_entity", "prefab": "small_block",
        "set_tags": { "batch_id": "'B-' + str(int(env.now()))" }},
      { "type": "push_output", "port": "out" },
      { "type": "hold", "duration": { "policy": { "distribution": "exponential", "mean": 10 }}}
    ]}
  ],
  "ports": [
    { "name": "out", "direction": "out" }
  ]
}
```

> 참고: M1에서는 단순화를 위해 소형만 생성. 중형/대형은 별도 Source 또는 확률 분포로 생성.

### 2. 중조 — junjo_assembly (Merge 핵심)

```json
{
  "name": "junjo_assembly",
  "type": "user",
  "behaviors": [
    { "type": "loop", "count": -1, "body": [
      { "type": "acquire_resource", "resource": "junjo_floor", "amount": 3 },
      { "type": "bundle", "port": "in", "count": 3, "output_prefab": "assembled_block" },
      { "type": "hold", "duration": { "policy": { "distribution": "triangular", "low": 20, "mode": 30, "high": 45 }}},
      { "type": "release_resource", "resource": "junjo_floor", "amount": 3 },
      { "type": "push_output", "port": "out" }
    ]}
  ],
  "ports": [
    { "name": "in", "direction": "in", "capacity": 10 },
    { "name": "out", "direction": "out" }
  ]
}
```

**동작 흐름:**
1. `acquire_resource(junjo_floor, 3)` — 면적 3슬롯 확보 (없으면 대기)
2. `bundle(in, 3, assembled_block)` — 소형 3개 대기 후 assembled_block 생성
3. `hold(triangular 20-30-45)` — 택트타임 (확률 분포)
4. `release_resource(junjo_floor, 3)` — 면적 반환
5. `push_output(out)` — 다음 공정으로

### 3. 일반 공정 — pre_outfitting / daejo / pre_painting

```json
{
  "name": "daejo",
  "type": "user",
  "behaviors": [
    { "type": "loop", "count": -1, "body": [
      { "type": "wait_for_input", "port": "in" },
      { "type": "acquire_resource", "resource": "daejo_floor", "amount": "entity.properties.area" },
      { "type": "hold", "duration": { "policy": { "distribution": "triangular", "low": 15, "mode": 25, "high": 35 }}},
      { "type": "release_resource", "resource": "daejo_floor", "amount": "entity.properties.area" },
      { "type": "push_output", "port": "out" }
    ]}
  ]
}
```

**핵심:** `amount`에 expression(`entity.properties.area`)을 사용하여 블록 크기별 면적 소비량을 동적으로 결정.

### 4. 탑재 — erection (Sink)

```json
{
  "name": "erection",
  "type": "user",
  "behaviors": [
    { "type": "loop", "count": -1, "body": [
      { "type": "wait_for_input", "port": "in" },
      { "type": "hold", "duration": 40 },
      { "type": "destroy_entity" }
    ]}
  ]
}
```

### 5. 라우팅 — Dispatcher 활용

```json
{
  "name": "route_after_junjo",
  "type": "dispatcher",
  "properties": {
    "strategy": "condition",
    "rules": [
      {
        "condition": "entity.tags.route == 'short'",
        "target": "daejo"
      },
      {
        "condition": "entity.tags.route in ('medium', 'full')",
        "target": "pre_outfitting"
      }
    ],
    "default": "daejo"
  }
}
```

### 6. Resource — 배치 면적

```json
{
  "name": "junjo_floor",
  "type": "resource",
  "properties": {
    "capacity": 9
  }
}
```

> 9슬롯 = 소형 블록 9개 동시 작업 가능, 또는 조립 3세트(3×3) 동시 가능

---

## Connection 구조

```
block_generator.out → junjo_queue.in
junjo_queue.out → junjo_assembly.in
junjo_assembly.out → route_after_junjo.in
route_after_junjo.out_short → daejo_queue.in
route_after_junjo.out_medium → pre_outfitting_queue.in
pre_outfitting.out → route_after_outfitting.in
route_after_outfitting.out_full → pre_painting_queue.in
route_after_outfitting.out_medium → daejo_queue.in
daejo.out → route_after_daejo.in
route_after_daejo.out_full → pre_painting_queue.in
route_after_daejo.out_other → erection_queue.in
pre_painting.out → erection_queue.in
erection_queue.out → erection.in
```

---

## KPI 정의

```json
{
  "kpi": [
    { "name": "throughput", "component": "erection", "metric": "entity_count", "unit": "blocks" },
    { "name": "junjo_utilization", "component": "junjo_floor", "metric": "utilization", "unit": "%" },
    { "name": "daejo_utilization", "component": "daejo_floor", "metric": "utilization", "unit": "%" },
    { "name": "avg_wait_time", "component": "junjo_queue", "metric": "avg_length_of_stay", "unit": "minutes" },
    { "name": "wip_count", "metric": "global", "formula": "junjo_queue.length + daejo_queue.length + erection_queue.length" }
  ]
}
```

---

## 구현 계획 (5주)

### Week 1 (3/25~3/31): 엔진 리뷰 + 기본 시나리오
- [ ] work-smc 브랜치 코드 리뷰 (behavior handlers, types)
- [ ] `bundle` behavior로 Merge PoC (단위 테스트)
- [ ] 최소 시나리오 JSON 작성 (Source → 중조 → Sink)

### Week 2 (4/1~4/7): 라우팅 + 5공정 파이프라인
- [ ] Dispatcher로 3종 블록 라우팅 구현
- [ ] 5공정 전체 파이프라인 JSON 완성
- [ ] Resource로 배치 면적 제약 추가

### Week 3 (4/8~4/14): Merge + Lot 추적
- [ ] bundle → assembled_block 변환 검증
- [ ] Entity.contents로 Lot 추적 확인
- [ ] KPI 수집 설정 및 리포트 생성

### Week 4 (4/15~4/21): 통합 + 데모 준비
- [ ] 전체 시나리오 통합 테스트
- [ ] 삼성중공업 블록 데이터 반영 (가능 시)
- [ ] 데모 시나리오 튜닝 (택트타임, 면적, 분포)

### Week 5 (4/22~4/28): 데모 + 문서화
- [ ] M1 데모 실행 및 KPI 리포트
- [ ] 데모 발표 자료 준비
- [ ] 삼성중공업 피드백 수렴

---

## 엣지케이스 및 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| `bundle`의 `amount` expression 미지원 | 블록 크기별 면적 차등 적용 불가 | `acquire_resource`에서 expression 사용 가능 여부 PoC로 선 검증 |
| 삼성중공업 데이터 미제공 | 실제 택트타임/블록 종류 없이 데모 | 가상 데이터로 M1 진행, M2에서 실데이터 적용 |
| Dispatcher condition expression 오류 | 라우팅 실패 → 블록 유실 | default 경로 설정 + 단위 테스트 |
| 동시 Merge 경합 | 블록 순서 꼬임 | bundle이 port.wait_for_items로 순차 처리하므로 안전 |
| Simio/DEVS 비교 검증 기준 미합의 | M3 지연 | 서경민 CTO 팀과 조기 협의 (택트타임/처리량 기준) |

---

## 시뮬레이션 기본 개념 — 설계 관점

### Capacity Planning의 핵심 질문
> "이 공장 레이아웃과 자원으로, 월 몇 개 블록을 완성할 수 있는가?"

이 질문에 답하려면:
1. **Entity 흐름**: 블록이 공정을 통과하는 속도 (택트타임 × 라우팅)
2. **Resource 병목**: 어디서 대기가 가장 많이 발생하는가 (면적, 장비, 인력)
3. **WIP(Work In Progress)**: 동시에 처리 중인 블록 수
4. **Throughput**: 단위 시간당 완성 블록 수

v3 엔진의 KPI 시스템이 이 4가지를 모두 자동 수집한다.

### Entity Merge가 조선소에서 특별한 이유
일반 제조(자동차, 반도체)에서는 Entity가 변형(transform)되지만 **합쳐지지 않는다.**
조선소에서는 소형 부재 → 소조립 → 중조립 → 대조립 → 탑재로 **점점 커지면서 합쳐진다.**
이 과정에서:
- Entity ID가 바뀜 (A+B+C → D)
- 새 Prefab의 속성(택트타임, 면적)이 적용됨
- 원래 부품의 이력(Lot)이 추적되어야 함

v3의 `bundle` + `EntityRegistry.contain()`이 이 패턴을 정확히 지원한다.

---

## 명확도 추이

| Round | 타겟 | Arch | Rationale | Detail | Risk | 모호성 |
|-------|------|------|-----------|--------|------|--------|
| 0 | 초기 | 0.7 | 0.5 | 0.5 | 0.3 | 47% |
| 1 | 코드검증 | 0.9 | 0.9 | 0.7 | 0.5 | 20% |
| 2 | Merge정책 | 0.9 | 0.9 | 0.9 | 0.5 | 16% |
| 3 | 엣지케이스 | 0.9 | 0.9 | 0.9 | 0.7 | 13% |
