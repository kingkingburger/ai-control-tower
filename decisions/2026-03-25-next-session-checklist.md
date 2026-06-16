# 다음 세션 체크리스트 — 삼성 조선소 M1 데모
**목표:** 1주차 engine validation 시작
**준비일:** 2026-03-25

---

## 다음 세션 전: 비동기 준비 작업

### 1. 삼성 3/24 미팅 노트 확인
- [ ] 블록 데이터 형식(CSV/JSON/raw?) debrief 확보
- [ ] 명확화: Merge policy("모두 대기" vs "병렬 batch")
- [ ] 확인: tact time과 floor area data source
- [ ] 문서화: `/decisions/2026-03-25-samsung-meeting-summary.md`로 저장

### 2. work-smc 브랜치 접근 준비
- [ ] 보장: SSH key 설정 완료(`~/.ssh/config` 확인)
- [ ] 테스트: Octopus v3 repo에서 `git clone` 또는 `git fetch`
- [ ] 문서화: clone 위치(예: `/d/octopus-v3-engine/`)

---

## 세션 1 시작 (1주차: 3/25-3/31)

### P0: 엔진 코드 리뷰 (차단 작업)
**예상 공수:** 2-3일 | **담당:** 원민호

즉시 실행:
```bash
# 1. work-smc 브랜치 pull
cd /path/to/octopus-v3-engine
git checkout work-smc
git pull origin work-smc

# 2. dependencies 설치
pip install -r requirements.txt

# 3. 검증용 예시 simulation 실행
python examples/run_basic_sim.py
```

**그다음 탐색:**
- [ ] 목록화: behavior file 전체: `find core/behavior -name "*.py" | wc -l`
- [ ] 검증: bundle impl: `grep -n "def bundle" core/behavior/handlers/transform_handlers.py`
- [ ] 검증: branch impl: `grep -n "def branch" core/behavior/handlers/control_handlers.py`
- [ ] Resource model 확인: `grep -n "class Resource" core/simulation.py`
- [ ] findings를 `/research/til/2026-03-26-engine-review-findings.md`에 작성

### P1: Bundle 단위 테스트 (병렬, 선택)
**예상 공수:** 1.5일 | **담당:** Dev team member(가능한 경우)

생성:
- [ ] 테스트 케이스 4개가 포함된 `/tests/test_bundle_merge.py` 작성
- [ ] 예시 scenario `/scenarios/test_merge_only.json` 작성
- 실행: `pytest tests/test_bundle_merge.py -v`

### P2: 삼성 미팅 debrief
**예상 공수:** 0.5일 | **담당:** 원민호 또는 PM

답변 문서화:
- 데이터 형식은 무엇인가?
- 병합 시점은 언제인가?
- 지표 출처는 무엇인가?
- CTO 비교 검증 일정은 언제인가?

저장 위치: `/decisions/2026-03-25-samsung-meeting-summary.md`

---

## 세션 2 시작 (2주차: 4/1 이후)

P0가 성공적으로 완료된 뒤에만 진행:

### P3: M1 시나리오 JSON
`/scenarios/m1-demo.json`에 다음을 포함:
- block 생성 rate(small 10u, medium 15u, large 20u)
- process별 tact time
- floor area constraint 정의
- routing rules
- Bundle merge policy 정의

### P4: 통합 테스트
```bash
python run_simulation.py scenarios/m1-demo.json --output results/m1-run.json
```

검증:
- 모든 entity가 lifecycle을 완료
- KPI metrics 생성
- M1 acceptance criteria 충족

---

## M1 데모 마감: 2026-04-30

**핵심 경로:**
```
P0 (2-3d) → P3 (2-3d) → P4 (2d) → P7 (2-3d) = 8-11 days
```

**병렬 작업 적용 시(P1, P2):** 겹쳐서 calendar 기준 약 7일로 압축 가능

---

## 이번 세션 성공 지표

- [ ] work-smc 브랜치 pull 및 로컬 실행 완료
- [ ] behavior 35개 목록 확인
- [ ] bundle/branch/acquire_resource/release_resource 검증
- [ ] 삼성 미팅 노트 문서화
- [ ] 단위 테스트 구조 준비
- [ ] 팀과 roadmap 검증

---

## 감시할 위험

| 위험 | 완화책 | 담당 |
|------|-----------|-------|
| v3 engine이 필요한 behavior를 지원하지 않음 | P0 code review로 gap을 조기 발견 | 원민호 |
| Samsung data format이 맞지 않음 | meeting debrief(P2)에서 확인 | 원민호 |
| Merge policy가 불명확함 | P2에서 CTO에게 직접 질문 | 원민호 |
| 단위 테스트가 v3에서 실패함 | 테스트 케이스 조정 또는 이슈 작성 | Dev |
| CTO comparison 일정 지연 | P2에서 일정 합의 후 문서화 | PM |

---

## 이번 세션에서 만든 파일

- `/d/reference2/ai-control-tower/decisions/2026-03-25-m1-priority-roadmap.md` (상세 5주 계획)
- `/d/reference2/ai-control-tower/decisions/2026-03-25-next-session-checklist.md` (현재 파일)

---

## 빠른 링크

- 요구사항: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/01-requirements.md`
- 설계: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/02-design.md`
- 검증: `docs/ouroboros/2026-03-25-shipyard-capacity-sim/03-verification.md`
- v3 학습: `research/til/2026-03-25-ouroboros-capacity-planning-v3-behaviors.md`
