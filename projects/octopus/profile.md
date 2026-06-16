# Octopus 프로젝트 프로필

대상 저장소: `D:\reference2\octopus`

## 분류

회사 주 프로젝트다. 팀 저장소에 남기는 문서와 코드는 team-safe 기준으로 쓴다.
반복 실수와 임시 운영 메모는 이 프로젝트 프로필에 둔다.

## 역할

Octopus 웹 모노레포다. Hub 프론트엔드는 `apps/web/hub`, 공통 웹 컴포넌트와
유틸리티는 `packages/web` 아래에 있다. 사용자가 `hub front`라고 말하면 기본
대상은 `D:\reference2\octopus\apps\web\hub`다.

## 시작 순서

1. `D:\reference2\AGENTS.md`와 ownership 원장을 확인한다.
2. `README.md`, `package.json`을 읽는다.
3. Hub 작업이면 `apps/web/hub/package.json`, `apps/web/hub/README.md`를 읽는다.
4. 수정 영역에 `AGENTS.md`나 `CLAUDE.md`가 있으면 그 지침을 우선한다.
5. 과거 Hub integration, capture, Docker build 이슈가 반복될 때만 memory를 검색한다.

## 작업 기준

- Hub UI 작업은 실제 렌더링 표면으로 검증한다.
- 리포트 캡처 실패는 먼저 URL, auth, host, capture contract를 확인한다.
- Docker build/generate는 비용이 크므로 사용자가 직접 재실행한다고 했으면 대신
  설정과 재현 조건만 정리한다.
- Octoto 권한/메뉴와 이어지는 변경은 Octoto와 Hub server 경계를 함께 확인한다.

## 자주 쓰는 명령

```bash
pnpm install
pnpm dev:web-hub
pnpm build:web-hub
pnpm generate:web-hub
pnpm --filter @octopus/web-hub typecheck
pnpm --filter @octopus/web-hub lint
```

## 세션 종료 메모

반복되는 작업 규칙은 `agent-rules-candidates.md`로 올리고, 1회성 관찰은
`session-memory.md`에 둔다. 팀 저장소로 승격할 내용은 로컬 맥락을 제거한 뒤
대상 repo의 지침 문서에 반영한다.
