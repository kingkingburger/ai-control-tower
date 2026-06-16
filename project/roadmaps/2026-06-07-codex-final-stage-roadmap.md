# Codex 최종 단계 로드맵

작성일: 2026-06-07

## 현재 위치

현재 상태는 5단계 체계 기준으로 **2.7단계**다.

- 1단계 세팅은 완료됐다. Codex config에는 trusted project, MCP, plugins, hooks,
  memories, goals가 이미 켜져 있다.
- 2단계 워크플로 레이어는 강하다. `ai-control-tower`, `projects/`, `shared/`, `.omc`,
  `closing-lite`, `daily-report`, `review-loop`, `agent-arena`를 실제로 쓴다.
- 3단계 병렬 에이전트 운영은 초입이다. agent/skill 실험 흔적은 있지만, 독립
  worktree, branch, PR, CI 수정을 묶은 운영 루프는 아직 표준화되지 않았다.
- 4단계 다중 모델 교차검증은 아직 ad hoc이다. `agent-arena`와 `review-loop`는
  있지만 Codex, Claude, Gemini 결과를 같은 형식으로 비교하는 파이프라인은 없다.
- 5단계 자산 동기화는 재료가 많지만 미완이다. Codex skills, Claude skills,
  `.omc`, `projects/`, `shared/`, 프로젝트별 문서가 공존하고 있으며 단일 원본과 배포 규칙이
  아직 명확하지 않다.

## 확인된 갭

가장 큰 갭은 "있는 것처럼 보이는 자동화"와 "실제로 실행 가능한 자동화"가 아직
분리되어 있다는 점이다.

- 기존 `shared/git-hooks/octoto/pre-commit`
- 기존 `shared/git-hooks/octoto/commit-msg`

위 hook은 존재하지 않는 `shared/bin/octoto-harness.ps1`를 호출하던 깨진 자산이었다.
프로젝트 중심 구조로 정리하면서 제거했으므로 현재 상태를 "훅 기반 자동화 완료"로
보면 안 된다. 훅 자동화가 필요하면 새 runner와 훅을 같은 변경으로 재도입한다.

또 하나의 갭은 자산 원본의 분산이다.

- Codex 전역 스킬: `C:\Users\dnjsa\.codex\skills`
- 프로젝트별 팀 원본: `projects/`
- 공통 규칙/템플릿/스킬 원본: `shared/`
- Claude 계열 과거 스킬: `.claude/skills`
- OMC 상태와 메모리: `.omc`
- 프로젝트별 공유 문서: 각 저장소의 `AGENTS.md`, `CLAUDE.md`, docs

최종 단계로 가려면 이들을 모두 직접 편집하는 방식이 아니라,
`ai-control-tower`를 원본으로 삼고 각 도구 위치에는 검증된 배포본만 동기화해야
한다.

## 목표 상태

최종 목표는 다음 한 문장으로 정의한다.

> `ai-control-tower`를 모든 AI 코딩 도구의 원본 규칙 저장소로 만들고,
> Codex, Claude, OMC, 프로젝트 문서에는 검증된 배포본만 동기화한다.

이 목표를 달성하면 다음이 가능해야 한다.

- 공통 작업 규칙은 `shared/rules/`에서만 수정한다.
- 프로젝트별 팀 프로필과 운영 메모리는 `projects/<project>/`에서만 수정한다.
- Codex, Claude, 프로젝트 문서 위치의 파일은 원본이 아니라 배포 대상임을 알 수
  있다.
- 동기화 전에 절대경로, 깨진 링크, 위험 명령, 누락된 런타임 파일을 검사한다.
- 고위험 작업은 여러 에이전트나 모델의 결과를 비교한 뒤 사람이 최종 판단한다.

## 실행 계획

### 1주차: 인벤토리와 깨진 자동화 복구

목표는 현재 자산과 자동화 상태를 거짓 없이 파악하는 것이다.

작업:

- `C:\Users\dnjsa\.codex\skills`, `projects/`, `shared/`, `.claude/skills`, `.omc`를 목록화한다.
- 각 자산을 `원본`, `배포본`, `폐기 후보`, `검토 필요`로 분류한다.
- 기존 깨진 hook 제거 상태를 확인하고, 재도입이 필요하면 runner 설계를 새로 잡는다.

완료 기준:

- 깨진 hook 호출이 없다.
- 자산 인벤토리 문서가 존재한다.
- `projects/`와 `shared/` 안의 절대경로 사용처가 의도된 것인지 확인되어 있다.

### 2주차: 단일 원본 구조 확정

목표는 어디를 수정해야 하는지 헷갈리지 않는 구조를 만드는 것이다.

작업:

- 공통 규칙 원본을 `shared/rules/`로 고정한다.
- 프로젝트별 팀 프로필 원본을 `projects/<project>/`로 고정한다.
- Codex용 skill 원본을 `shared/skills/` 또는 별도 `distribution/codex/`
  중 하나로 확정한다.
- Claude, OMC, 프로젝트 문서는 배포 대상이라는 규칙을 문서화한다.

완료 기준:

- `projects/README.md`와 `shared/README.md`만 읽어도 원본과 배포본의 차이를 알 수 있다.
- 새 규칙을 추가할 때 어느 파일을 고쳐야 하는지 결정할 수 있다.
- `.omc/project-memory.json` 같은 도구 종속 상태 파일은 지속 메모리 원본으로 쓰지
  않는다는 정책이 유지된다.

### 3주차: 동기화 스크립트 만들기

목표는 수동 복사를 줄이고, drift를 실행 전에 잡는 것이다.

작업:

- `sync codex`: 원본 스킬과 규칙을 Codex 위치로 동기화한다.
- `sync claude`: Claude 계열 스킬 또는 지침을 동기화한다.
- `sync project <name>`: 프로젝트별 `AGENTS.md`, `CLAUDE.md`, docs 후보를
  동기화하거나 차이를 보고한다.
- 동기화 전에 다음 검사를 실행한다.
  - 깨진 링크
  - 누락된 스크립트
  - 의도되지 않은 절대경로
  - prompt injection 가능성이 큰 문구
  - 파괴적 명령

완료 기준:

- dry-run으로 변경 예정 파일을 볼 수 있다.
- 실제 sync 후 git diff가 예상 범위와 일치한다.
- sync 대상 파일이 원본인지 배포본인지 문서에 표시된다.

### 4주차: 병렬 개발 운영 루프 만들기

목표는 3단계를 실험이 아니라 운영 가능한 루프로 만드는 것이다.

작업:

- 우선 `octoto` 한 저장소에만 적용한다.
- task 하나를 입력하면 다음 흐름이 실행되게 한다.
  - worktree 생성
  - branch 생성
  - agent 실행
  - 테스트 또는 focused verification 실행
  - diff 요약
  - 사람이 merge 여부 판단
- PR, CI 자동수정은 이 루프가 안정된 뒤 붙인다.

완료 기준:

- 독립 worktree에서 최소 1개 작업을 끝까지 완료한다.
- 실패 시 원본 checkout을 오염시키지 않는다.
- 사람의 판단 지점과 자동 실행 지점이 구분되어 있다.

### 5주차 이후: 고위험 작업에 교차검증 붙이기

목표는 모든 작업을 무겁게 만드는 것이 아니라, 위험한 작업만 더 강하게 검증하는
것이다.

적용 대상:

- 보안 리뷰
- 대형 리팩터링
- DB 마이그레이션
- 아키텍처 결정
- 운영 장애 원인 분석

작업:

- Codex, Claude, Gemini 또는 Hive/mco류 오케스트레이터를 같은 입력에 대해 실행한다.
- 결과를 JSON, Markdown table, PR comment 중 하나의 형식으로 정규화한다.
- 합의된 문제, 한 모델만 발견한 문제, 사람이 판단해야 할 문제를 분리한다.

완료 기준:

- 최소 1개 고위험 작업에서 다중 모델 비교 결과를 기록한다.
- 비교 결과가 실제 수정이나 의사결정에 반영된다.
- 비용과 노이즈 때문에 일반 작업까지 무조건 교차검증하지 않는다.

## 운영 원칙

- 새 도구 도입보다 원본 구조 정리가 먼저다.
- hook이나 wrapper는 존재 여부가 아니라 실행 가능성으로 판단한다.
- 대상 프로젝트 문서에는 협업자에게 안전한 규칙만 둔다.
- 프로젝트별 반복 학습은 `projects/<project>/`에 두고, 여러 프로젝트에 반복되는 규칙만 `shared/`로 승격한다.
- 최종 단계의 핵심은 "도구가 많다"가 아니라 "규칙과 스킬의 원본이 하나다"이다.

## 다음 액션

가장 먼저 할 일은 1주차 작업이다.

1. 자산 인벤토리 문서를 만든다.
2. 깨진 hook 자동화 제거 상태를 유지하고, 재도입 시 runner 설계를 먼저 작성한다.
3. `projects/README.md`와 `shared/README.md`에 원본/배포본 경계를 유지한다.
4. 그다음에야 sync 스크립트와 병렬 worktree 운영을 설계한다.
