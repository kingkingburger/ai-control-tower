# Deep Goal Council Harness

Deep Goal Council은 목표를 작게 잡는 습관을 보정하기 위한 범용 에이전트 팀 하네스다. 상담, 공부, 개발, 디자인, 운영, 커리어/인생 방향처럼 작업 표면이 달라도 같은 구조를 사용한다.

## 하네스 구성

| 구성요소 | 위치 | 역할 |
| --- | --- | --- |
| Harness manifest | `shared/harnesses/deep-goal-council/README.md` | 하네스의 목적, 구성, 운영 원칙을 정의한다. |
| Execution adapter | `shared/skills/deep-goal-council/SKILL.md` | Codex/Claude가 이 하네스를 자동으로 호출하고 실행하게 하는 진입점이다. |
| Team blueprints | `shared/skills/deep-goal-council/references/team-blueprints.md` | 계층 구조, 경쟁 팀, 내부/교차 비판 규칙을 정의한다. |
| Output contract | `shared/skills/deep-goal-council/references/output-contract.md` | Situation Brief, Team Proposal, Cross-Critique, Judge Packet 형식을 고정한다. |
| Surface adapters | `shared/skills/deep-goal-council/references/surface-adapters.md` | 상담, 공부, 개발, 디자인, 운영, 커리어/인생 표면별 변환 규칙을 둔다. |
| Runbook | `project/runbooks/deep-goal-council-harness.md` | `ai-control-tower` 안에서 이 하네스를 운영하고 갱신하는 절차를 둔다. |

## 핵심 구조

```text
사용자 현재 상태
  -> Situation Brief
  -> 3-5개 경쟁 팀
      -> Team Chief
      -> Team Manager
      -> Architect
      -> Operator
      -> Sentinel
      -> Synthesizer
  -> Cross-Critique
  -> Judge Packet
  -> 사용자가 최종 선택
```

## 기본 경쟁 팀

- `moonshot-team`: 목표를 의도적으로 크게 잡고 10배 방향을 제안한다.
- `compound-team`: 누적 가능한 루틴과 시스템을 설계한다.
- `constraint-breaker-team`: 병목과 작업 형식을 바꾼다.
- `craft-team`: 실력, 품질, 정체성 변화를 중심에 둔다.
- `operator-team`: 이번 7일 안에 관찰 가능한 증거를 만든다.

## 실행 원칙

1. 사용자가 최종 심사자다. 하네스는 선택지를 만들고 비교 가능하게 할 뿐, 선택을 대체하지 않는다.
2. 큰 목표는 반드시 12주 캠페인과 7일 첫 증거로 내려온다.
3. 현실적인 실행안은 반드시 1년 이상 방향과 연결된다.
4. 모든 팀은 내부 Sentinel 비판을 거친 뒤 제안서를 낸다.
5. 팀 간 경쟁은 승부가 아니라 판단 품질을 높이는 교차 비판이다.

## 스킬과의 관계

이 하네스의 본체는 역할 구조, 출력 계약, 표면별 어댑터, 운영 런북이다. `shared/skills/deep-goal-council/SKILL.md`는 본체가 아니라 실행 어댑터다. 에이전트 런타임이 자연어 요청에서 이 하네스를 찾고, 필요한 reference를 순서대로 읽고, 결과를 같은 형식으로 내도록 만든다.

## 사용 예시

```text
Deep Goal Council로 현재 상태를 분석해줘.
내 목표가 너무 작고 단기적으로 잡히는 패턴을 보정하고 싶어.
상담/공부/개발/디자인에도 재사용 가능한 경쟁 팀 하네스로 제안서를 만들고,
내가 심사할 수 있는 Judge Packet으로 정리해줘.
```

## 하네스 갱신 기준

다음 문제가 2회 이상 반복되면 하네스를 갱신한다.

- 팀 제안이 서로 비슷해진다.
- Sentinel 비판이 형식적이다.
- Judge Packet이 사용자의 선택을 돕지 못한다.
- 7일 실험이 장기 방향과 연결되지 않는다.
- 특정 작업 표면에서 산출물 계약이 부족하다.
