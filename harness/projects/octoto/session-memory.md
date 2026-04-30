# Octoto 세션 메모리

`closing-lite` 항목을 여기에 누적한다.

## Entries

### 2026-04-30 서비스 삭제 500 회귀

- 완료한 작업: `test2` 서비스 삭제 시 500이 나는 원인을 `role_groups.service_code` FK의 `ON DELETE SET NULL`과 partial unique index 충돌 가능성으로 좁히고, 서비스 삭제 로직에서 서비스 귀속 RoleGroup을 먼저 soft-delete하도록 수정했다.
- 검증: `bun test tests/unit/service.service.test.ts` 통과, `bunx biome check src/domains/service/service.service.ts` 통과. 전체 `bun run lint`는 기존 unrelated 포맷 이슈(`action.routes.ts`, `menu-sync.routes.ts`, `role-group.routes.ts`)로 실패했다.
- 배운 점: 서비스 스코프 테이블이나 `services.code` 참조 FK를 추가한 뒤에는 `deleteService()`/`updateService()` 연쇄 정리 경로를 반드시 재점검해야 한다. 특히 DB cascade에 기대면 실제 FK 옵션, unique index, soft-delete 정책이 엇갈려 500이 날 수 있다.
- 주의할 점: 서비스 삭제는 `role_groups.service_code`, `role_group_service_visibility`, `user_role_group_join`, `user_service_access`, `role_group_service_access`, `auth_requests`, `service_menus`, `actions`를 한 묶음으로 본다.
- 추가 탐색 결과: `role_group_service_visibility.service_code`의 `ON UPDATE no action`도 서비스 코드 변경 500을 만들 수 있는 같은 계열 위험이었다. FK를 `ON UPDATE cascade`로 보강하고 코드 변경 시 캐시 무효화 대상을 넓혔다.
- 하네스 증강: `projects/octoto/service-scope-cascade-rules.md`에 서비스 스코프 cascade 점검 규칙을 추가했다.

### 2026-04-29

- 맥락: 사용자는 세션 종료를 커밋과 `closing-lite` 누적으로 정의했다.
- 정정된 선호: 프로젝트별 히스토리와 학습은 Octoto의 `docs/agent-memory.md`에
  둔다. 반복 운영 규칙만 `ai-control-tower`로 승격한다.
- 후보 규칙: 세션 종료 워크플로는 대상 저장소 커밋과 private memory 업데이트를
  분리해야 한다.
- 배운 점: 하네스에는 명시적인 사용자 질문 정책이 필요하다. 사용자는 Claude
  Code처럼 빠른 구조화 질문 흐름을 기대한다.
- 증강할 점: 매 세션 종료 때 배운 점과 하네스 개선 후보를 private project
  overlay에 추가한다.
- 배운 점: 사용자는 하네스 문서와 세션 메모리가 기본적으로 한국어로 작성되기를
  원한다.
- 증강할 점: 문서 언어 정책을 공통 규칙에 추가하고, 예외는 코드/명령어/경로/API
  이름으로 제한한다.

### 2026-04-29 메모리 위치 정정

- 정정: 프로젝트별 히스토리와 세션 메모리는 프로젝트에 누적한다. Octoto에서는
  `docs/agent-memory.md`를 사용한다.
- 정정: `ai-control-tower`는 프로젝트별 원시 히스토리를 대신 보관하는 곳이 아니라,
  반복되는 운영 규칙을 core 규칙, 템플릿, 스킬로 승격하는 곳이다.
- 정정: `.omc/project-memory.json`은 지속 메모리 원본으로 쓰지 않는다. 유효한
  내용은 프로젝트 메모리로 이관하고 `.omc`는 제거한다.

### 2026-04-29 세션 종료 컴파운딩 정정

- 정정: 사용자는 세션 종료 시 에이전트가 배운 점을 물어볼 때까지 기다리지 않고,
  변경 파일, 사용자 정정, 검증 실패, 반복 선호를 자동으로 탐색해 메모리로
  컴파운드하기를 기대한다.
- 이번 사례: 사용자 목록 전화번호 칼럼은 처음에는 상태 옆 이동 요청이었지만,
  곧 "아예 빼버려"로 바뀌었다. 최신 요청이 통제 지시이며, 이전 방향은 즉시
  폐기해야 한다.
- 검증 메모: `bunx vue-tsc --noEmit`와 `bun run test src/test/pages/UsersPage.test.ts`
  는 통과했다. 전체 `bun run test`는 `LoginPage.test.ts` Knox 관련 기존 실패 5건으로
  실패했다.
- 하네스 증강: `core/session-close.md`에 세션 종료 시 자동 탐색과 컴파운딩 절차를
  명시했다.
