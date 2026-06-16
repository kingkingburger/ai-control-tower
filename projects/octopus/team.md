# Octopus Team

Octopus 팀은 Hub frontend와 공유 web package를 다루는 프로젝트 팀이다. 작업
시작점은 `profile.md`이며, 공통 역할은 `../../shared/agents/README.md`를 참조한다.

## 공통 역할

- `project-orchestrator`
- `context-explorer`
- `implementation-planner`
- `verification-runner`
- `docs-syncer`
- `memory-curator`

## 프로젝트 고유 역할

- `hub-front-lead`: `apps/web/hub` 화면, Nuxt 설정, Hub runtime을 담당한다.
- `shared-web-lead`: `packages/web` 공통 컴포넌트와 shared composable 영향 범위를 추적한다.
- `capture-surface-lead`: report capture의 host, auth, page completion contract를 분리한다.
- `build-memory-lead`: Hub Docker/generate OOM과 번들 설정 변경의 위험을 관리한다.
- `visual-runtime-verifier`: Hub UI 변경을 실제 렌더링 surface에서 확인한다.

## 운영 원칙

사용자가 `hub front`라고 말하면 기본 대상은 `D:\reference2\octopus\apps\web\hub`다.
리포트 캡처 실패는 browser service 탓으로 단정하기 전에 URL, auth, host, capture
contract를 먼저 확인한다.
