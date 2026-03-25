# M1 Prioritized Task Roadmap — Samsung Heavy Industries Shipyard Simulation
## 삼성중공업 거제조선소 Capacity Planning Simulation M1 우선순위

**Deadline:** 2026-04-30 (5 weeks from 2026-03-25)
**Owner:** 원민호
**Document Date:** 2026-03-25

---

## Executive Summary

Ouroboros Phase 1-3 문서 완료. 이제 엔진 검증과 실제 동작 테스트 단계. 5주 내 M1 데모 완성을 위해서는 **병렬 작업** 필요. 다음 세션부터는 팀 내 협력 가능한 작업들이 있으므로 작업 분담 추천.

---

## Week 1 (3/25 - 3/31): Engine Validation & PoC Foundation

### P0: Engine Code Review — v3 Behavior 검증
**Dependency:** Block everyone else until complete
**Effort:** 2-3 days
**Blockers:** None
**Next:** All subsequent work depends on this

#### Subtasks
1. **work-smc 브랜치 pull 및 로컬 실행 검증**
   - [ ] Clone work-smc branch
   - [ ] Run existing example simulations
   - [ ] Confirm v3 engine boots without error
   - [ ] Document Python version, dependencies, installation steps

2. **35개 behavior 목록 확인 및 조선소 매핑**
   - [ ] List all behavior/* files (expected ~35)
   - [ ] Match to requirements: `bundle`, `branch`, `acquire_resource`, `release_resource`
   - [ ] Verify each behavior's JSON schema
   - [ ] Document edge cases (e.g., bundle with count mismatch)

3. **Bundle behavior behavior 상세 검증**
   - [ ] Read `core/behavior/handlers/transform_handlers.py:150` (bundle impl)
   - [ ] Trace `wait_for_items` + `pop` logic for Lot tracking
   - [ ] Test: merge 3 small blocks → confirm `contents` field tracking
   - [ ] Test: incomplete merge → confirm no crash on sim end

4. **Branch behavior for routing**
   - [ ] Confirm `branch(condition=...)` works with prefab checks
   - [ ] Test: route small/medium/large blocks correctly
   - [ ] Edge case: what if condition is always false?

5. **Resource constraint (acquire/release)**
   - [ ] Verify `sim.Resource` capacity model
   - [ ] Test: queue formation when capacity exceeded
   - [ ] Measure: avg_wait_time metric generation

**Verification Plan:**
```python
# test_v3_engine_basics.py
def test_bundle_behavior():
    # 3 small blocks → 1 assembled block
    # Verify: contents tracking, prefab transformation
    pass

def test_branch_routing():
    # 3 block types → 3 paths
    # Verify: small doesn't visit pre_painting, etc.
    pass

def test_resource_capacity():
    # Exceed floor area → queue forms
    # Verify: blocking and release logic
    pass
```

---

### P1: Bundle Behavior Unit Tests (Parallel with P0)
**Dependency:** P0 code review in progress
**Effort:** 1.5 days
**Owner:** Can be delegated if team available
**Next:** Informs Phase 2 design adjustments

#### Subtasks
1. **Create `tests/test_bundle_merge.py`**
   - [ ] Test case 1: 3 small blocks → 1 assembled_block
     - Input: Entity(prefab="small_block") ×3
     - Expected: Entity(prefab="assembled_block"), contents=[id1, id2, id3]

   - [ ] Test case 2: 6 blocks → 2 assemblies (batch processing)
     - Input: 6 small blocks
     - Expected: 2 assembled_blocks created sequentially

   - [ ] Test case 3: Incomplete bundle on sim end
     - Input: 2 blocks, count=3, simulation ends
     - Expected: No crash, graceful shutdown

   - [ ] Test case 4: Merge creates new Lot hierarchy
     - Input: 3 small blocks with tags=[component_id]
     - Expected: new_block.contents contains all tags

2. **Create JSON test scenario `scenarios/test_merge_only.json`**
   - Source generates 3 small blocks (time: 0, 10, 20)
   - Bundle waits for all 3, produces assembled_block
   - Record entity lifecycle

3. **Verify test output structure**
   - [ ] Entity registry format
   - [ ] Event log schema
   - [ ] KPI fields (throughput, wait_time, utilization)

**Success Criteria:**
- All 4 test cases pass
- test_merge_only.json simulation runs to completion
- Lot tracking confirmed in output

---

### P2: Samsung Meeting Debrief — 3/24 결과 확인
**Dependency:** None
**Effort:** 0.5 days
**Owner:** 원민호 (or delegate to team lead)
**Next:** Informs data format and Merge policy

#### Subtasks
1. **Collect meeting notes from 3/24 with CTO 서경민**
   - [ ] Confirm block data format (will they provide CSV, JSON, or raw?)
   - [ ] Clarify Merge policy: "모두 모이고 시작" vs. "첫 N개부터 병렬 시작"?
   - [ ] Ask about tact time data source (공정표, 실제 기록, 추정?)
   - [ ] Confirm floor area metrics (m², relative units, or sim slots?)

2. **Document any new constraints or clarifications**
   - [ ] If data format differs from assumptions → update Phase 2 design doc
   - [ ] If Merge policy changes → update bundle behavior test

3. **Get confirmation on Simio/DEVS comparison scope**
   - [ ] Which metrics will CTO team verify? (throughput, avg_wait, utilization?)
   - [ ] What is "same scenario"? (block mix, tact times, floor areas?)
   - [ ] Timeline for CTO's comparison results?

**Success Criteria:**
- All 3 questions answered in writing
- Any design changes documented
- CTO comparison timeline confirmed

---

## Week 2-3 (4/1 - 4/14): JSON Scenario Construction & Integration Test

### P3: M1 Scenario JSON Writing
**Dependency:** P0 (engine validation), P2 (data format confirmed)
**Effort:** 2-3 days
**Owner:** 원민호
**Next:** M1 demo execution

#### Subtasks
1. **Create `scenarios/m1-demo.json` — Full M1 Scenario**

   Structure:
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

2. **Define block generation timeline**
   - [ ] Small block: 1 every 10 time units (source spawns 30 over 500 units)
   - [ ] Medium block: 1 every 15 time units
   - [ ] Large block: 1 every 20 time units
   - Ensure 3 small blocks align for merge test

3. **Define process tact times**
   - [ ] junjo (중조): 30 time units per block (base)
   - [ ] pre_outfitting (선행의장): 25 time units
   - [ ] daejo (대조): 35 time units
   - [ ] pre_painting (선행도장): 20 time units
   - [ ] erection (탑재): 15 time units

4. **Define floor area constraints**
   - [ ] junjo: capacity = 2 blocks (area_per_block = 4 for small, 8 for medium, 12 for large)
   - [ ] pre_outfitting: capacity = 1.5 medium + 1 large OR resource pool = 3 units
   - [ ] daejo: capacity = 2 blocks
   - [ ] pre_painting: capacity = 1 block (large only)
   - [ ] erection: no constraint (output only)

5. **Define routing rules**
   - [ ] Small block route: junjo → daejo → erection
   - [ ] Medium block route: junjo → pre_outfitting → daejo → erection
   - [ ] Large block route: junjo → pre_outfitting → daejo → pre_painting → erection
   - [ ] Bundle at junjo: 3 small → 1 assembled_medium (new prefab)
   - [ ] Assembled block follows medium route post-merge

6. **Merge policy**
   - [ ] Use `bundle(port="junjo_input", count=3, output_prefab="assembled_medium")`
   - [ ] All 3 must arrive before bundle starts
   - [ ] If < 3 arrive before sim end, stay in queue (no forced merge)

**Deliverable:**
- `/d/reference2/ai-control-tower/scenarios/m1-demo.json` (complete, valid JSON)
- Test: `python -c "import json; json.load(open('scenarios/m1-demo.json'))"` passes

---

### P4: End-to-End Integration Test
**Dependency:** P3 (scenario JSON), P0 (engine ready)
**Effort:** 2 days
**Owner:** 원민호
**Next:** Identifies any runtime behavior gaps

#### Subtasks
1. **Run M1 scenario for full duration**
   ```bash
   cd /work-smc/branch
   python run_simulation.py scenarios/m1-demo.json --output results/m1-demo-run1.json
   ```

2. **Verify all entities complete lifecycle**
   - [ ] All small blocks reach Sink
   - [ ] All medium/large blocks reach Sink
   - [ ] 1 assembled block created from merge
   - [ ] No entities stuck in queue at end

3. **Inspect KPI output**
   - [ ] Total throughput (entities completed)
   - [ ] Average wait time per process
   - [ ] Utilization per process (% time busy)
   - [ ] Queue depths (max simultaneous in queue)

4. **Validate against M1 acceptance criteria**
   - [ ] 3 block types follow correct paths? → Verify event log
   - [ ] Merge creates new Entity? → Confirm assembled_block in output
   - [ ] Lot tracking works? → Check contents field
   - [ ] Queue forms on floor area exceed? → Check junjo queue depth > 0

5. **Document any runtime errors**
   - [ ] If behavior crashes → post issue to work-smc repo
   - [ ] If JSON schema mismatch → revise scenario
   - [ ] If logic gap → add ADR to Phase 2 design doc

**Success Criteria:**
- Simulation runs to completion without errors
- Output JSON valid
- KPI metrics match expected ranges (see M1 demo checklist)

---

## Week 4 (4/15 - 4/21): Demo Preparation & Documentation

### P5: M1 Demo Scenario Documentation
**Dependency:** P4 (integration test complete)
**Effort:** 1.5 days
**Owner:** 원민호
**Next:** Presentation material

#### Subtasks
1. **Create demo narrative document**
   - `/d/reference2/ai-control-tower/research/til/2026-04-15-m1-demo-walkthrough.md`
   - Explain each step: Source → bundle → branch → Sink
   - Show expected KPI values from trial run
   - Document any parameter tuning done

2. **Create JSON scenario walkthrough**
   - Annotated version of m1-demo.json
   - Explain each component's role
   - Show how to modify: block generation rate, tact times, floor areas

3. **Generate sample output report**
   - Run simulation, capture KPI output
   - Create `.md` template for final demo report
   - Format: Throughput | Avg Wait | Utilization table

---

### P6: Prepare for CTO Comparison (Simio/DEVS Readiness)
**Dependency:** P4 (baseline scenario), P2 (CTO agreement)
**Effort:** 1.5 days
**Owner:** 원민호
**Next:** Enable external validation

#### Subtasks
1. **Export scenario to neutral format**
   - Ensure m1-demo.json has all parameters explicitly stated
   - Generate `.csv` export of tact times, floor areas, block types
   - Verify CTO team can read these independently

2. **Document comparison baseline**
   - `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/04-comparison-setup.md`
   - "What are we comparing?" — metrics list
   - "How will CTO team run Simio/DEVS?" — scenario mapping
   - "When are results due?" — timeline

3. **Prepare for discrepancy handling**
   - If results differ, what's acceptable tolerance?
   - Who investigates behavior mismatch?
   - Where will findings be documented?

---

## Week 5 (4/22 - 4/30): Final Testing & M1 Demo

### P7: M1 Demo Execution & Reporting
**Dependency:** All prior tasks
**Effort:** 2-3 days
**Owner:** 원민호 + team (if demo presentation needed)
**Next:** M2 planning

#### Subtasks
1. **Final scenario validation run**
   - [ ] Run m1-demo.json 3× with different random seeds
   - [ ] Verify results consistent within 5% variance
   - [ ] Capture screenshots/logs for presentation

2. **Create M1 Demo Report**
   - `/d/reference2/ai-control-tower/research/til/2026-04-30-m1-demo-report.md`
   - Sections:
     - Scenario summary (blocks, processes, constraints)
     - KPI results (throughput, wait, utilization)
     - M1 acceptance criteria checklist (pass/fail)
     - Screenshots/diagrams
     - Known limitations (anything not implemented)

3. **Prepare presentation for stakeholders**
   - [ ] Deck or live demo showing:
       - Block generation and flow
       - Merge event at junjo
       - Routing by block type
       - Floor area constraint queuing
       - Final KPI report

4. **Gather feedback**
   - [ ] Does scenario match Samsung expectations?
   - [ ] Are M1 acceptance criteria met?
   - [ ] What should M2 prioritize?

---

## Open Issues Tracking

| Issue | Status | Owner | Due |
|-------|--------|-------|-----|
| 3/24 삼성중공업 미팅 결과 | PENDING | 원민호 | 3/26 |
| v3 엔진 engine 코드 리뷰 | PENDING | 원민호 | 3/31 |
| Bundle behavior 단위테스트 | PENDING | TBD | 4/3 |
| M1 JSON scenario 완성 | PENDING | 원민호 | 4/7 |
| End-to-end integration test | PENDING | 원민호 | 4/14 |
| Simio/DEVS 비교기준 합의 | PENDING | 서경민 CTO | 4/14 |
| M1 demo 완료 | PENDING | 원민호 | 4/30 |

---

## Suggested Team Work Distribution

**If team members are available:**

| Task | Assignee | Duration | Start |
|------|----------|----------|-------|
| P0: Engine code review | 원민호 | 2-3d | 3/25 |
| P1: Bundle unit tests | Dev (if available) | 1.5d | 3/25 (parallel) |
| P2: Samsung meeting debrief | 원민호 or PM | 0.5d | 3/25 |
| P3: M1 scenario JSON | 원민호 | 2-3d | 4/1 |
| P4: Integration test | 원민호 | 2d | 4/7 |
| P5: Demo documentation | 원민호 | 1.5d | 4/15 |
| P6: CTO comparison prep | 원민호 | 1.5d | 4/15 |
| P7: M1 demo & report | 원민호 + PM | 2-3d | 4/22 |

**Critical path (serial):** P0 → P3 → P4 → P7 = ~9 days
**With parallel work (P1, P2):** Can overlap to compress to ~7 days calendar time

---

## M1 Acceptance Criteria Checklist

Use this to validate M1 demo:

- [ ] 3종 블록이 Prefab별 다른 경로를 정상적으로 따름
- [ ] Entity Merge 후 새 ID 생성 및 이전 Entity Destroy
- [ ] Merge된 Entity에서 원래 부품 Lot 추적 가능
- [ ] 배치 면적 초과 시 대기(Queue) 발생
- [ ] 시뮬레이션 완료 후 KPI 통계 출력
- [ ] Octopus v3 엔진에서 JSON만으로 구현됨 (새 코드 없음)
- [ ] 시나리오 재현 가능 (동일 JSON → 동일 결과, ±random variance)

---

## Next Session Actions (Recommended)

1. **Confirm M1 deadline is hard** — 4/30 is immovable?
2. **Assign team members** — Who can help with P1, P2?
3. **Schedule Samsung meeting debrief** — When will 3/24 meeting notes be available?
4. **Pull work-smc branch** — Immediate action, start P0
5. **Set up testing framework** — Where will unit tests live? (tests/ directory?)

---

## References

- Requirements: `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/01-requirements.md`
- Design (ADR): `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/02-design.md`
- Verification Plan: `/d/reference2/ai-control-tower/docs/ouroboros/2026-03-25-shipyard-capacity-sim/03-verification.md`
- v3 Learnings: `/d/reference2/ai-control-tower/research/til/2026-03-25-ouroboros-capacity-planning-v3-behaviors.md`
