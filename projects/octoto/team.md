# Octoto 팀

Octoto 팀은 중앙 인증, 권한, 서비스 메뉴, 감사 로그, PostgreSQL/Oracle parity를
다루는 프로젝트 팀이다. 작업 시작점은 `profile.md`이며, 공통 역할은
`../../shared/agents/README.md`를 참조한다.

## 공통 역할

- `project-orchestrator`
- `context-explorer`
- `implementation-planner`
- `verification-runner`
- `docs-syncer`
- `memory-curator`

## 프로젝트 고유 역할

- `auth-boundary-lead`: Knox, JWT, 세션, `/api/auth/me`, permission source 경계를 추적한다.
- `permission-policy-lead`: role group, service access, menu/action visibility 정책을 검증한다.
- `oracle-parity-lead`: PostgreSQL과 Oracle read/write/bulk/cleanup parity를 확인한다.
- `hub-integration-lead`: Hub front/server와 Octoto API 사이의 ID, auth, permission 계약을 조율한다.
- `ci-cd-operator`: Jenkins, Argo CD, GitOps push 실패처럼 저장소 밖 운영 truth가 필요한 이슈를 분리한다.

## 운영 원칙

권한/인증 문제는 UI-only 보정으로 끝내지 않는다. 서버/API/domain 경계의 불변식을
먼저 고정하고, UI는 그 정책을 사용자에게 드러내는 보조 표면으로 다룬다.
