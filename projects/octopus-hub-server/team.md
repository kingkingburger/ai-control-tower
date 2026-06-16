# Octopus Hub Server Team

Octopus Hub Server 팀은 NestJS/Turbo 기반 Hub backend와 Octoto 연동을 다루는
프로젝트 팀이다. 작업 시작점은 `profile.md`이며, 공통 역할은
`../../shared/agents/README.md`를 참조한다.

## 공통 역할

- `project-orchestrator`
- `context-explorer`
- `implementation-planner`
- `verification-runner`
- `docs-syncer`
- `memory-curator`

## 프로젝트 고유 역할

- `main-service-lead`: `apps/main-service` API, guard, interceptor, service graph를 담당한다.
- `octoto-auth-lead`: RS256 JWKS, issuer/audience, `OCTOTO_*` env, tokenUser 재사용 경계를 지킨다.
- `capture-worker-lead`: worker-service report capture, login token, page completion signal을 추적한다.
- `oracle-sql-lead`: TypeORM/Oracle identifier casing과 executable SQL 위험을 확인한다.
- `branch-guard`: 코드 변경 전 feature branch 규칙을 확인한다.

## 운영 원칙

`main` 또는 `master`에서 바로 코드 변경하지 않는다. Octoto JWT 검증은 RS256 JWKS만
사용하고, HS256 fallback이나 Guard 이후 JWT 재파싱을 되살리지 않는다.
