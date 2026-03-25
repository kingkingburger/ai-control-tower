# Next Session Checklist — Samsung Shipyard M1 Demo
**Target:** Start Week 1 engine validation
**Prepared:** 2026-03-25

---

## BEFORE NEXT SESSION: Async Prep Tasks

### 1. Confirm Samsung 3/24 Meeting Notes
- [ ] Get debrief on block data format (CSV/JSON/raw?)
- [ ] Clarify Merge policy ("wait all" vs "parallel batch")
- [ ] Confirm tact time and floor area data sources
- [ ] Document in `/decisions/` as `2026-03-25-samsung-meeting-summary.md`

### 2. Prepare work-smc Branch Access
- [ ] Ensure SSH key configured (check `~/.ssh/config`)
- [ ] Test: `git clone` or `git fetch` Octopus v3 repo
- [ ] Document clone location (e.g., `/d/octopus-v3-engine/`)

---

## SESSION 1 START (Week 1: 3/25-3/31)

### P0: Engine Code Review (BLOCKING)
**Effort:** 2-3 days | **Owner:** 원민호

Run this immediately:
```bash
# 1. Pull work-smc branch
cd /path/to/octopus-v3-engine
git checkout work-smc
git pull origin work-smc

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example simulation to verify
python examples/run_basic_sim.py
```

**Then explore:**
- [ ] List all behavior files: `find core/behavior -name "*.py" | wc -l`
- [ ] Verify bundle impl: `grep -n "def bundle" core/behavior/handlers/transform_handlers.py`
- [ ] Verify branch impl: `grep -n "def branch" core/behavior/handlers/control_handlers.py`
- [ ] Check Resource model: `grep -n "class Resource" core/simulation.py`
- [ ] Write findings in `/research/til/2026-03-26-engine-review-findings.md`

### P1: Bundle Unit Tests (Parallel, Opt)
**Effort:** 1.5 days | **Owner:** Dev team member (if available)

Create:
- [ ] `/tests/test_bundle_merge.py` with 4 test cases
- [ ] `/scenarios/test_merge_only.json` example scenario
- Run: `pytest tests/test_bundle_merge.py -v`

### P2: Samsung Meeting Debrief
**Effort:** 0.5 days | **Owner:** 원민호 or PM

Document answers:
- Data format?
- Merge timing?
- Metric sources?
- CTO comparison timeline?

Save to: `/decisions/2026-03-25-samsung-meeting-summary.md`

---

## SESSION 2 START (Week 2: 4/1+)

Only after P0 completes successfully:

### P3: M1 Scenario JSON
Create `/scenarios/m1-demo.json` with:
- Block generation rates (small 10u, medium 15u, large 20u)
- Tact times per process
- Floor area constraints
- Routing rules
- Bundle merge policy

### P4: Integration Test
```bash
python run_simulation.py scenarios/m1-demo.json --output results/m1-run.json
```

Verify:
- All entities complete lifecycle
- KPI metrics generated
- M1 acceptance criteria met

---

## M1 Demo Deadline: 4/30/2026

**Critical Path:**
```
P0 (2-3d) → P3 (2-3d) → P4 (2d) → P7 (2-3d) = 8-11 days
```

**With parallel work (P1, P2):** Can overlap to ~7 days calendar

---

## Success Metrics for This Session

- [ ] work-smc branch pulled and running locally
- [ ] 35 behaviors list confirmed
- [ ] bundle/branch/acquire_resource/release_resource verified
- [ ] Samsung meeting notes documented
- [ ] Unit test structure ready
- [ ] Roadmap validated with team

---

## Risks to Monitor

| Risk | Mitigation | Owner |
|------|-----------|-------|
| v3 engine doesn't support needed behaviors | P0 code review will reveal gaps early | 원민호 |
| Samsung data format incompatible | Confirm in meeting debrief (P2) | 원민호 |
| Merge policy unclear | Ask CTO directly in P2 | 원민호 |
| Unit tests fail on v3 | Adjust test cases or file issue | Dev |
| CTO comparison timeline slips | Agree on timeline in P2, document | PM |

---

## Files Created This Session

- `/d/reference2/ai-control-tower/decisions/2026-03-25-m1-priority-roadmap.md` (detailed 5-week plan)
- `/d/reference2/ai-control-tower/decisions/2026-03-25-next-session-checklist.md` (this file)

---

## Quick Links

- Requirements: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/01-requirements.md`
- Design: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/02-design.md`
- Verification: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/03-verification.md`
- v3 Learnings: `research/til/2026-03-25-ouroboros-capacity-planning-v3-behaviors.md`
