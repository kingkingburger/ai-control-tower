# Octopus Hub Server Project Profile

대상 저장소: `D:\reference2\octopus-hub-server`

## 분류

회사 주 프로젝트다. 팀 저장소에 남기는 문서와 코드는 team-safe 기준으로 쓴다.
이 저장소는 코드 변경 전 feature branch 원칙을 특별히 강하게 적용한다.

## 역할

NestJS + TypeScript + pnpm workspace + Turbo 기반 Hub backend 모노레포다.
`apps/main-service`가 API gateway와 주요 비즈니스 로직을 담당하고,
MQTT, Influx, worker, capture 관련 서비스가 별도 앱으로 존재한다.

## 시작 순서

1. `D:\reference2\AGENTS.md`와 ownership 원장을 확인한다.
2. 현재 브랜치를 확인한다. `main` 또는 `master`면 코드 변경 전 feature branch를
   만들거나 전환한다. 사용자가 명시적으로 예외를 지시한 경우만 그대로 진행한다.
3. `AGENTS.md`, `CLAUDE.md`, `README.md`, `package.json`을 읽는다.
4. 수정 대상 서비스의 하위 문서와 nearest 지침을 읽는다.
5. Octoto 연동이면 `OCTOTO_*` env, JWKS/RS256, internal token, menu-sync,
   report capture contract를 함께 확인한다.

## 작업 기준

- Octoto JWT 검증은 RS256 JWKS만 사용한다. HS256 fallback을 되살리지 않는다.
- Guard에서 검증한 `tokenUser`를 재사용하고, interceptor나 service에서 JWT를
  다시 파싱하지 않는다.
- 새 Octoto 외부 호출은 injectable `OctotoXxxService` 경계로 둔다.
- inline `console.log`, 빈 catch, 의미 없는 rethrow wrapper를 남기지 않는다.
- Oracle SQL을 다룰 때 실제 identifier casing을 확인한다.

## 자주 쓰는 명령

```bash
pnpm run type-check
pnpm run type-check:main
pnpm run build
pnpm run test
pnpm run test:main
pnpm run format
pnpm --filter ./apps/main-service exec tsgo --noEmit -p tsconfig.build.json
```

## 세션 종료 메모

반복되는 작업 규칙은 `agent-rules-candidates.md`로 올리고, 1회성 관찰은
`session-memory.md`에 둔다. 팀 저장소로 승격할 내용은 로컬 맥락을 제거한 뒤
대상 repo의 지침 문서에 반영한다.
