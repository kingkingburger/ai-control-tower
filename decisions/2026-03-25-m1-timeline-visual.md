# M1 Timeline — Visual Overview
**Samsung Heavy Industries Shipyard Simulation Demo**
**Deadline: 2026-04-30 (5 weeks from 2026-03-25)**

```
WEEK 1 (3/25-3/31): Foundation & Validation
┌─────────────────────────────────────────────────────┐
│ P0: Engine Code Review (BLOCKING)        │ 원민호    │
│ ├─ Pull work-smc branch                  │ 3/25     │
│ ├─ Run basic example                     │ 3/25     │
│ ├─ Verify 35 behaviors list              │ 3/26-27  │
│ ├─ Test bundle/branch/resource           │ 3/28-29  │
│ └─ Write findings TIL                    │ 3/30     │
├─────────────────────────────────────────────────────┤
│ P1: Bundle Unit Tests (PARALLEL)         │ Dev/TBD  │
│ ├─ Create test_bundle_merge.py           │ 3/25-26  │
│ ├─ Create test_merge_only.json           │ 3/26-27  │
│ └─ Run pytest, verify output             │ 3/28-29  │
├─────────────────────────────────────────────────────┤
│ P2: Samsung Meeting Debrief (QUICK)      │ 원민호    │
│ ├─ Collect 3/24 meeting notes            │ 3/25-26  │
│ ├─ Answer 3 key questions                │ 3/27     │
│ └─ Document constraints                  │ 3/30     │
└─────────────────────────────────────────────────────┘
DECISION GATE: P0 must complete successfully before Week 2

WEEK 2-3 (4/1-4/14): Scenario & Integration
┌─────────────────────────────────────────────────────┐
│ P3: M1 Scenario JSON Writing             │ 원민호    │
│ ├─ Define block generation (small/med/lg)│ 4/1-2    │
│ ├─ Define tact times per process         │ 4/2-3    │
│ ├─ Define floor area constraints         │ 4/3-4    │
│ ├─ Define routing rules                  │ 4/4-5    │
│ ├─ Define merge policy (bundle)          │ 4/5-6    │
│ └─ Validate JSON syntax                  │ 4/6-7    │
│ DELIVERABLE: /scenarios/m1-demo.json    │
├─────────────────────────────────────────────────────┤
│ P4: End-to-End Integration Test          │ 원민호    │
│ ├─ Run full M1 scenario (500 sim units)  │ 4/8-9    │
│ ├─ Verify all entities complete          │ 4/9      │
│ ├─ Inspect KPI output                    │ 4/10     │
│ ├─ Validate M1 acceptance criteria       │ 4/10-11  │
│ └─ Document any errors                   │ 4/11-12  │
│ DELIVERABLE: /results/m1-run.json        │
└─────────────────────────────────────────────────────┘
DECISION GATE: P4 must pass all M1 criteria before Week 4

WEEK 4 (4/15-4/21): Demo Prep
┌─────────────────────────────────────────────────────┐
│ P5: M1 Demo Documentation                │ 원민호    │
│ ├─ Create demo walkthrough TIL           │ 4/15-16  │
│ ├─ Annotate JSON scenario                │ 4/16-17  │
│ └─ Generate sample output report         │ 4/17-18  │
├─────────────────────────────────────────────────────┤
│ P6: Prepare for CTO Comparison           │ 원민호    │
│ ├─ Export scenario to neutral format     │ 4/15-16  │
│ ├─ Document comparison baseline          │ 4/16-17  │
│ └─ Plan for discrepancy handling         │ 4/18-19  │
│ DELIVERABLE: 04-comparison-setup.md      │
└─────────────────────────────────────────────────────┘
DECISION GATE: Ready for final demo execution

WEEK 5 (4/22-4/30): M1 Demo & Report
┌─────────────────────────────────────────────────────┐
│ P7: M1 Demo Execution & Reporting        │ 원민호    │
│ ├─ Final scenario validation (3× runs)   │ 4/22-24  │
│ ├─ Create M1 demo report                 │ 4/24-25  │
│ ├─ Prepare presentation slides           │ 4/25-26  │
│ ├─ Gather stakeholder feedback           │ 4/27-29  │
│ └─ FINAL DELIVERY                        │ 4/30     │
│ DELIVERABLE: /research/til/2026-04-30-m1-demo-report.md
└─────────────────────────────────────────────────────┘
```

---

## Critical Path Visualization

```
SERIAL DEPENDENCIES (blocking chain):
P0 (Engine Review)
    ↓
P3 (M1 Scenario JSON) + P2 (Samsung Debrief)
    ↓
P4 (Integration Test)
    ↓
P5 + P6 (Demo Prep)
    ↓
P7 (Final Demo)

PARALLEL OPPORTUNITIES:
┌─ P0 (2-3d) ──────────────────┐
│  P1 (1.5d) PARALLEL ──┐      │
│  P2 (0.5d) PARALLEL ─┤      │
└─────────────────────→ P3 (2-3d) → P4 (2d) → P5/P6 → P7 (2-3d)

Critical Path (Serial): 8-11 days
With Parallel Work: ~7 days calendar (P1 + P2 overlap with P0)
```

---

## Weekly Milestones & Gates

| Week | Due Date | Milestones | Gate? |
|------|----------|----------|-------|
| **1** | 3/31 | P0 engine review complete, P1/P2 started | YES: P0 must pass |
| **2-3** | 4/14 | P3 JSON complete, P4 integration test passing | YES: P4 criteria met |
| **4** | 4/21 | P5/P6 documentation ready, demo prep complete | YES: Ready to demo |
| **5** | 4/30 | P7 M1 demo delivered, report published | FINAL: M1 Success |

---

## Task Dependencies Map

```
ASYNC (Pre-session):
  Samsung 3/24 Meeting Notes ──→ P2 (Meeting Debrief)

SESSION 1 (Week 1):
  P0 (Engine Review) ────┬→ GATE ──→ PROCEED TO SESSION 2
  P1 (Bundle Tests) ─────┴─→ VALIDATE
  P2 (Meeting Debrief) ──────→ CONFIRM

SESSION 2+ (Week 2-3):
  P0 Results + P2 Results ──→ P3 (JSON Scenario)
                              ↓
                          P4 (Integration Test)
                              ↓
                          GATE: Criteria Met? ──→ SESSION 3

SESSION 3 (Week 4):
  P4 Results ──→ P5 (Demo Documentation)
                P6 (CTO Comparison Setup)

SESSION 4 (Week 5):
  P5/P6 Results ──→ P7 (Final Demo & Report)
                      ↓
                   M1 DELIVERY (4/30)
```

---

## Resource Allocation Model

### Solo Mode (원민호 only)
```
Week 1:  P0 (blocking) + P2 (quick) = 2.5 days → P1 skipped
Week 2-3: P3 (2-3d) + P4 (2d) = 4-5 days
Week 4:  P5 (1.5d) + P6 (1.5d) = 3 days
Week 5:  P7 (2-3d) = demo

Total: ~11-13 days spread over 5 weeks (fits deadline)
Risk: Zero parallelism, no backup
```

### Team Mode (원민호 + Dev team)
```
Week 1:  P0 (원민호) || P1 (Dev team) || P2 (원민호) = 2.5 days parallel
Week 2-3: P3 (원민호) + P4 (원민호) = 4-5 days (P1 results available)
Week 4:  P5 (원민호) + P6 (원민호) = 3 days
Week 5:  P7 (원민호 + PM) = demo + stakeholder feedback

Total: ~7 days actual work, ~5 weeks calendar (safe buffer)
Risk: Distributed, P1 results accelerate P3/P4
```

---

## M1 Acceptance Criteria (Final Checklist)

Use this to validate successful M1 demo:

```
FUNCTIONAL REQUIREMENTS:
[ ] 3 block types (small/medium/large) created from Source
[ ] Each block type follows correct process route:
    [ ] Small: junjo → daejo → erection
    [ ] Medium: junjo → pre_outfitting → daejo → erection
    [ ] Large: junjo → pre_outfitting → daejo → pre_painting → erection
[ ] Merge occurs: 3 small blocks → 1 assembled_medium
[ ] Entity lifecycle: Source → Processes → Merge → Sink (no stuck entities)
[ ] Lot tracking: assembled_medium.contents shows original 3 block IDs

CONSTRAINT REQUIREMENTS:
[ ] Floor area capacity enforced (blocks queue when full)
[ ] Resource allocation working (block assignment to junjo/daejo/etc.)
[ ] Tact time applied correctly per process
[ ] No deadlocks (all entities eventually reach Sink)

KPI REPORTING:
[ ] Total throughput: N entities completed
[ ] Average wait time per process: table format
[ ] Utilization per process: % busy time
[ ] Queue statistics: max depth, avg length per process

IMPLEMENTATION REQUIREMENTS:
[ ] ZERO new custom Python code (JSON + v3 behaviors only)
[ ] Scenario reproducible (same JSON → ±5% variance across 3 runs)
[ ] Output format valid JSON
[ ] Simulation runs to completion without errors

DOCUMENTATION REQUIREMENTS:
[ ] M1 demo report published
[ ] Scenario walkthrough documented
[ ] KPI output explained
[ ] Known limitations stated
[ ] M2 recommendations included
```

---

## One-Page Summary for Standup

**Q: What's the plan?**
A: 5-week sprint to deliver M1 demo using Octopus v3 engine + JSON scenario.

**Q: What's first?**
A: Engine code review (P0) — must validate v3 has bundle/branch/resource behaviors.

**Q: When's it due?**
A: 2026-04-30 (5 weeks, ~35 days).

**Q: Can we parallelize?**
A: Yes — P1 (unit tests) and P2 (meeting debrief) can run while P0 executes.

**Q: What if P0 fails?**
A: v3 engine is missing critical features → redesign needed. Gate at week 1.

**Q: Who does what?**
A: 원민호 leads P0/P3/P4/P7 (serial). Dev team does P1 (parallel). Both prepare P5/P6.

**Q: Biggest risk?**
A: v3 engine doesn't support Merge or routing. Mitigated by early code review (P0).

---

## Quick Start Commands (Week 1)

```bash
# SESSION 1, DAY 1: Start P0 (Engine Review)
cd /octopus-v3-engine
git checkout work-smc
git pull origin work-smc
pip install -r requirements.txt
python examples/run_basic_sim.py   # Verify engine boots

# Count behaviors
find core/behavior -name "*.py" | wc -l

# Search for critical behaviors
grep -n "def bundle" core/behavior/handlers/transform_handlers.py
grep -n "def branch" core/behavior/handlers/control_handlers.py
grep -n "def acquire_resource" core/behavior/handlers/resource_handlers.py

# Create findings doc
cat > /d/reference2/ai-control-tower/research/til/2026-03-26-engine-review-findings.md << 'EOF'
# Engine Review Findings — 2026-03-26

## Behavior Verification
- [ ] bundle: ✓ found at core/behavior/handlers/transform_handlers.py:150
- [ ] branch: ✓ found at core/behavior/handlers/control_handlers.py:XXX
- [ ] acquire_resource: ✓ found at core/behavior/handlers/resource_handlers.py:XXX
- [ ] release_resource: ✓ found

## Behavior Test Results
- [ ] bundle creates new Entity with correct prefab
- [ ] bundle tracks Lot (contents field)
- [ ] branch routes based on entity.prefab condition
- [ ] acquire_resource blocks when capacity exceeded
- [ ] release_resource unblocks queue

## Issues Found (if any)
- None expected, but document any errors here

## Recommendation
✓ READY to proceed to P3 (JSON scenario)
EOF
```

---

## Next Steps

1. **Print this page** — paste in standup or team chat
2. **Confirm deadlines** — is 4/30 truly hard?
3. **Assign resources** — who handles P1?
4. **Get Samsung notes** — async before Week 1 starts
5. **Pull work-smc** — first command on Day 1
6. **Book decision gates** — P0→P3 (week 1), P4→P5 (week 4)
