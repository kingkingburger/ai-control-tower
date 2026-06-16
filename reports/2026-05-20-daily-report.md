# 일일 작업 보고서 - 2026-05-20

작성 시점: 2026-05-20 14:47 KST 기준

## 1. 요약

- 오늘의 핵심 작업은 `octoto`, `octopus-hub-server`, `octopus/apps/web/hub` 3개 repo에서 Hub 중복 인증 테이블 제거 계획을 실제 구현 단위로 밀어낸 것이다.
- Hub server가 Octoto JWT를 검증하고, 내부 hydrate API/client를 통해 사용자/권한그룹 정보를 서버 간 호출로 가져오는 방향을 확정했다.
- Hub front의 핵심 사용자/권한 신청/권한그룹/고객 현황 경로를 Hub 로컬 user API에서 Octoto API 기준으로 옮겼다.
- Hub server의 중복 인증 테이블 drop은 PG/Oracle 양쪽 migration과 CLI까지 만들었지만, 런타임 참조와 FK가 남아 있어 실제 DB drop은 금지 상태로 유지했다.
- `daily-report` 스킬을 설계해 `plugin-mh` 원본과 로컬 Codex 미러에 적용했다. 단, `plugin-mh` 변경은 아직 커밋되지 않았다.
- 운영 지원으로 Codex under-development warning 원인 확인, Notion MCP 재로그인, Zellij 세션 저장 명령 안내, 과학/문학/엔터테인먼트 Q&A가 있었다.
- 현재 상태: 핵심 구현은 다수 커밋 완료, 일부 변경은 진행 중이다. `octoto`에는 `.env.docker` 로컬 변경, `octopus-hub-server`에는 `octoto-legacy-permission-client.service.ts` 미커밋 변경, `plugin-mh`에는 daily-report 관련 미커밋 변경이 남아 있다.

## 2. 타임라인

| Time | Project | Event | Evidence |
|------|---------|-------|----------|
| 09:27 | `octoto` | Oracle 통합 세션 종료 후속으로 오류 학습, 자동화 후보, 문서 갱신 필요 항목을 정리했다. | Codex logs `019e42c7-*` |
| 10:44 | `octoto` / Hub repos | `hub-remove-duplicate-auth-tables-session-plan.md` 실행을 시작했다. | Codex log `019e430b-*` |
| 10:53 | `octoto` | Hub 연동용 사용자 `companyId` 계약을 추가했다. | commit `7abb3cf` |
| 11:02 | `octopus-hub-server` | Hub server가 Octoto JWT를 검증하도록 전환했다. | commit `a52bdb74` |
| 11:08-11:28 | Hub architecture | Hub server가 Octoto를 부를 때 사용자 토큰 없이 호출해야 하는 문제를 재검토하고, 서버 간 내부 토큰 + hydrate API 방향을 확정했다. | Codex log `019e430b-*` |
| 11:14 | local Codex | Notion MCP `invalid_grant` 계열 문제를 재로그인으로 해결했다. `default_mode_request_user_input` warning은 별도 설정 문제로 남겼다. | Codex log `019e431a-22df-*` |
| 11:44 | `octoto`, `octopus-hub-server` | Octoto 내부 hydrate API와 Hub server hydrate client를 추가했다. | commits `2cfbfa1`, `14e59c2a` |
| 11:59 | `octoto` | 테스트를 PG/Oracle dialect별로 분리하고 기본 테스트 흐름을 정리했다. | commit `22b1f69` |
| 12:14 | `octopus-hub-server`, `octopus` | Hub server current user 조회를 Octoto hydrate로 전환하고, Hub front가 Octoto 권한 정보를 덮어쓰지 않게 수정했다. | commits `72c8ea6f`, `8e587e231` |
| 12:19-12:43 | `octopus-hub-server` | 중복 인증 테이블 drop migration을 PG/Oracle로 분리 검증하고 실행 CLI를 추가했다. | commits `406ada97`, `a9f91682` |
| 12:37-13:56 | `octopus/apps/web/hub` | 현재 사용자 기준, 권한 신청, 사용자 관리, userRole, currentCustomer 경로를 Octoto API 기준으로 전환했다. | commits `8d4645ee2`, `4c6593c5c`, `44d30d744`, `dfdcc277d`, `0e56b73b2` |
| 13:33 | `octoto` | Hub front가 쓸 `loginId` 중복 확인 API를 추가했다. | commit `9c9044c` |
| 13:47-13:50 | Hub server/docs | 별도 `OCTOTO_INTERNAL_BASE_URL` 대신 기존 `OCTOTO_BASE_URL`을 사용하도록 결정하고 코드/문서를 맞췄다. | commits `cee3f6eb`, `807e904` |
| 13:52-14:04 | `plugin-mh`, local Codex | `daily-report` 스킬을 설계하고 plugin-mh 원본 + 로컬 Codex 미러에 적용했다. | Codex log `019e43b9-*`, local files |
| 14:11-14:15 | `octopus-hub-server`, `octoto docs` | Hub server login/logout 호환 API를 Octoto 인증 프록시로 전환하고, 공유 앱 blocker와 startup seed blocker를 문서화했다. | commits `25f2970c`, `fcbe118`, `73d29af` |
| 14:30-14:38 | `octopus-hub-server`, `octoto docs` | `/user/v2/currInfo`를 `CurrentUserModule`로 분리하고 Octoto permission 기반 `menuRoles` 보강을 추가했다. | commits `4c54e1c4`, `aa7274b1`, `c39246c` |
| 14:46 | `octopus-hub-server` | Hub server legacy `role-group` API를 Octoto 권한그룹 API로 전환하는 첫 핵심 단위를 커밋했다. | commit `a3657779` |

## 3. 프로젝트별 작업

### `D:\reference2\octoto`

- 목표: Hub가 자체 사용자/권한 테이블에 덜 의존하도록 Octoto 쪽 인증/사용자/권한 계약을 보강한다.
- 수행 작업:
  - `/api/auth/me`, 사용자 조회, 로그인 JWT, Postgres/Oracle repository에 `companyId`를 포함했다.
  - Hub server 전용 내부 hydrate API를 추가했다. 공유 내부 토큰이 없거나 틀리면 실패하도록 했다.
  - `loginId` 중복 확인 API를 추가했다.
  - PG/Oracle 테스트 분리 기준을 `test:pg`, `test:oracle`, 기본 test 흐름으로 정리했다.
  - Hub 중복 인증 테이블 제거 세션 계획, inventory, 운영 문서를 여러 차례 갱신했다.
- 변경 파일/산출물:
  - 코드: `src/domains/internal-hub/*`, `src/domains/user/user.routes.ts`, auth/user repository 계약, Oracle/Postgres repository.
  - 문서: `docs/hub-integration/OPERATIONS.md`, `docs/hub-integration/hub-remove-duplicate-auth-tables-session-plan.md`, `docs/hub-integration/hub-remove-duplicate-auth-tables-inventory-2026-05-20.md`, `docs/agent-memory.md`.
- 현재 상태:
  - 오늘 확인된 관련 커밋 다수 완료.
  - `D:\reference2\octoto\.env.docker`는 로컬 내부 토큰/env 변경 때문에 미커밋 상태로 남아 있다. 값은 보고서에 기록하지 않았다.

### `D:\reference2\octopus-hub-server`

- 목표: Hub server의 인증/사용자/권한 런타임을 Hub 로컬 인증 테이블에서 Octoto 계약으로 옮긴다.
- 수행 작업:
  - Hub server `AuthGuard`가 Octoto JWKS 기반 RS256 access token을 검증하도록 전환했다.
  - Octoto internal hydrate client를 추가하고 `OCTOTO_BASE_URL` 기준으로 통합했다.
  - `/user/v2/currInfo`를 Octoto hydrate 기반으로 전환하고, 이후 `CurrentUserModule`로 분리했다.
  - current-user 응답에 필요한 `menuRoles`를 Octoto permission API에서 보강했다.
  - Hub server 로그인 호환 API를 Octoto 인증 프록시로 전환했다.
  - 구형 Knox login endpoint, auth-request runtime module을 제거하거나 제외했다.
  - 중복 인증 테이블 drop migration을 PG/Oracle 양쪽으로 구현하고, 안전 플래그가 필요한 CLI를 추가했다.
  - legacy `role-group` API를 Octoto `/api/role-groups` 호출로 바꾸는 첫 단위를 커밋했다.
- 변경 파일/산출물:
  - `apps/main-service/src/common/jwt-core/octoto-jwt-verifier.service.ts`
  - `apps/main-service/src/common/octoto/octoto-hydrate-client.service.ts`
  - `apps/main-service/src/common/octoto/octoto-auth-client.service.ts`
  - `apps/main-service/src/common/octoto/octoto-permission-client.service.ts`
  - `apps/main-service/src/common/octoto/octoto-legacy-permission-client.service.ts`
  - `apps/main-service/src/api/current-user/*`
  - `apps/main-service/src/migration/cli/remove-duplicate-auth-tables.ts`
- 현재 상태:
  - 주요 전환 커밋 완료.
  - `apps/main-service/src/common/octoto/octoto-legacy-permission-client.service.ts`에 미커밋 변경이 남아 있다. 로그상 다음 작업인 `menu-role` 변환 준비/진행분으로 보이며, 보고서 작성 시점에는 완료로 단정하지 않는다.

### `D:\reference2\octopus\apps\web\hub`

- 목표: Hub front가 Hub server의 로컬 user/auth request projection 대신 Octoto API를 직접 기준으로 삼게 한다.
- 수행 작업:
  - `userCurrent` store에서 Hub currInfo 재조회와 `hubServerUserId` 상태 의존을 줄였다.
  - 권한 신청 store와 KnoxAuthModal을 Octoto available groups/auth request API 전용으로 전환했다.
  - 사용자 관리 store를 Octoto 사용자 목록/상세/생성/수정/삭제/비밀번호 변경/loginId 중복 확인 기준으로 전환했다.
  - `userRole` store를 Octoto membership API로 전환했다.
  - `currentCustomer` store에서 Hub user API 의존을 제거했다.
- 현재 상태:
  - 관련 커밋 완료.
  - `git diff` 기준 미커밋 변경은 없다.
  - `git log --all`에는 같은 날짜의 custom-alarm 계열 타 브랜치 커밋도 보였지만, 이번 보고서는 Codex 세션 로그와 현재 branch의 Hub 중복 제거 작업에 매핑되는 커밋만 핵심 작업으로 분류했다.

### `D:\reference2\plugin-mh` / 로컬 Codex config

- 목표: Codex 전체 대화를 하루 작업 보고서로 정리하는 도구 비종속 `daily-report` 스킬을 만든다.
- 수행 작업:
  - 새 skill `skills/daily-report/SKILL.md`를 추가했다.
  - 새 Codex slash prompt `codex/prompts/daily-report.md`를 추가했다.
  - README/GUIDE/AGENTS/CLAUDE/marketplace/plugin metadata와 `closing-lite` 관련 링크를 동기화했다.
  - 로컬 Codex 미러에 `C:\Users\dnjsa\.codex\skills\daily-report\SKILL.md`와 `C:\Users\dnjsa\.codex\prompts\daily-report.md`를 설치했다.
- 검증:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin.ps1`
  - 결과: `plugin-mh validation passed. Skills: 23 | Agents: 1 | Codex prompts: 24 | Guardrails: 8`
- 현재 상태:
  - plugin-mh 변경은 아직 커밋되지 않았다.
  - 로컬 Codex 미러 파일은 2026-05-20 14:01 KST에 생성/수정된 것으로 확인했다.

### `D:\reference2\ai-control-tower`

- 목표: 오늘 Codex 작업을 증거 기반 일일 보고서로 남긴다.
- 수행 작업:
  - 현재 repo git 상태, 오늘 Codex session logs, Claude logs, 관련 repo git history/status를 확인했다.
  - 이 보고서를 `reports/2026-05-20-daily-report.md`로 생성했다.
- 현재 상태:
  - `ai-control-tower` 자체에는 오늘 커밋이 없었다.
  - 이 보고서 파일 생성으로 작업공간에 새 변경이 생겼다.

### 일반 질의응답 / 운영 지원

- Codex 시작 시 `default_mode_request_user_input` under-development warning이 뜨는 이유를 확인했다. Notion MCP refresh token 문제와 별개이며, 경고 suppress 설정이 필요하다고 정리했다.
- `mcp login notion`을 실행해 Notion MCP 재로그인을 완료했다.
- Zellij 세션 저장 명령을 확인해 `zellij action save-session`, 레이아웃 저장은 `zellij action dump-layout > layout.kdl`이라고 안내했다.
- 과학/일상 Q&답변:
  - 칼로리는 음식의 에너지량을 `kcal`로 표현한 값이며, 영양소별 계산 기준을 설명했다.
  - 열, 에너지, 물 온도 상승, 분자 운동의 관계를 설명했다.
  - 붓기는 칼로리보다 염분/수분 균형 영향이 크다고 정리했다.
- 문화/엔터테인먼트 Q&답변:
  - 리센느 멤버/특징/곡 분류 관련 질문에 답했다.
  - 일본 문학상, 아쿠타가와상, 아쿠타가와 류노스케와 「라쇼몽」을 설명했다.

## 4. 결정 사항

| Decision | Reason | Impact | Evidence |
|----------|--------|--------|----------|
| Hub server가 Octoto 호출에 사용자 access token만 의존하지 않고, 서버 간 internal token + hydrate API를 쓴다. | Hub server에서 user/profile/role group 정보가 필요하지만 Hub local user table을 없애는 방향이므로, 사용자 JWT에 모든 데이터를 넣거나 무인증 API를 열면 위험하다. | Octoto 내부 hydrate API와 Hub server hydrate client가 추가됐다. | Codex log `019e430b-*`, commits `2cfbfa1`, `14e59c2a` |
| internal hydrate URL은 별도 `OCTOTO_INTERNAL_BASE_URL`이 아니라 기존 `OCTOTO_BASE_URL`을 사용한다. | 같은 Octoto server base URL을 두 env로 나누면 운영 설정이 갈라진다. | Hub server 코드/문서에서 URL 기준을 하나로 통합했다. | commits `cee3f6eb`, `807e904` |
| 중복 인증 테이블 drop은 PG와 Oracle 양쪽을 동시에 만족해야 한다. | Hub/Octoto 통합은 DB dialect가 둘 다 살아 있어야 하며 PG-only migration은 회귀 위험이 크다. | drop migration 테스트가 `test:hub-remove-migration:pg`, `:oracle`로 분리됐다. | commits `406ada97`, `a9f91682`, `a5d7dc3` |
| 실제 DB drop은 아직 금지한다. | `UserModule`, 권한 모듈, startup seed, entity registry, 도메인 FK, 외부 앱 user/role/menu store가 남아 있다. | migration/CLI는 준비됐지만 실행 조건은 inventory 문서에 blocker로 남겼다. | commits `c39246c`, `73d29af`, current docs |
| `daily-report`는 Codex 전용 session closing이 아니라 도구 비종속 증거 수집 스킬로 만든다. | 사용자는 Codex 로그뿐 아니라 Claude/기타 로그, git, 노트까지 소스로 삼는 보고서를 원했다. | plugin-mh와 local Codex에 skill/prompt가 추가됐다. | Codex log `019e43b9-*`, local files |

## 5. 문제와 해결

| 문제 | 원인 | 해결 | 남은 위험 |
|---------|-------|------------|----------------|
| Hub server가 Octoto를 부를 때 사용자 token이 필요한 문제 | Hub local user table을 없애려면 Hub server가 필요한 사용자/권한 정보를 다른 방식으로 얻어야 한다. | 내부 공유 토큰 기반 hydrate API/client를 추가했다. | internal token 운영 주입과 로테이션 정책은 별도 관리 필요 |
| 사용자가 “무인증 API면 안 되나”라고 물을 정도로 구조 설명이 복잡해짐 | JWT, hydrate, projection, DB table 제거 범위가 한 흐름에 섞였다. | “Hub server 전용 internal API + 양쪽 env secret” 구조로 재설명하고 진행했다. | 후속 문서에서 더 짧은 아키텍처 다이어그램이 필요할 수 있음 |
| Hub 중복 인증 테이블 drop을 실행할 수 없음 | 런타임 컨트롤러, entity/FK, startup seed, 외부 앱 의존이 아직 남아 있다. | drop migration과 CLI는 안전 가드를 두고 준비하되 실제 drop 금지 상태를 문서화했다. | blocker 제거 전 실행하면 런타임 장애 가능 |
| Hub server typecheck 실패 | 기존 `alarm-management`, `microservice-shared`, `bull-board`, `nodemailer/mqtt/mathjs` 등 baseline 타입 오류가 섞여 있었다. | 변경 단위별 focused test를 통과시키고 typecheck 실패는 baseline으로 구분해 커밋 메시지에 남겼다. | baseline typecheck debt는 별도 정리 필요 |
| Hub front 전체 lint/typecheck가 깨짐 | 기존 `AiChat`, `chat-bot`, `custom-menu`, `vue-tsc@1.8.27` crash 등 unrelated debt가 있었다. | 변경 파일 중심 eslint로 검증했다. | 전체 front 품질 게이트 복구 필요 |
| plugin-mh daily-report 작업이 적용됐지만 미커밋 | 사용자는 적용을 요청했으나 커밋 요청은 하지 않았다. | validation은 통과했고, uncommitted 상태를 보고서에 명시했다. | 후속 커밋/배포 필요 |

## 6. 파일과 산출물

- 생성: `D:\reference2\plugin-mh\skills\daily-report\SKILL.md`
- 생성: `D:\reference2\plugin-mh\codex\prompts\daily-report.md`
- 생성/설치: `C:\Users\dnjsa\.codex\skills\daily-report\SKILL.md`
- 생성/설치: `C:\Users\dnjsa\.codex\prompts\daily-report.md`
- 생성: `D:\reference2\ai-control-tower\reports\2026-05-20-daily-report.md`
- 주요 Octoto docs: `docs/hub-integration/hub-remove-duplicate-auth-tables-session-plan.md`, `docs/hub-integration/hub-remove-duplicate-auth-tables-inventory-2026-05-20.md`, `docs/hub-integration/OPERATIONS.md`, `docs/agent-memory.md`
- 주요 Hub server modules: `octoto-jwt-verifier`, `octoto-hydrate-client`, `octoto-auth-client`, `octoto-permission-client`, `octoto-legacy-permission-client`, `current-user`
- 주요 Hub front stores: `userCurrent.ts`, `authRequestManage.ts`, `user.ts`, `userRole.ts`, `currentCustomer.ts`

## 7. 후속 조치

- `plugin-mh`의 daily-report 변경을 리뷰 후 커밋할지 결정한다.
- `octoto`의 `.env.docker` 로컬 변경은 민감값/운영값 여부를 확인하고 커밋 제외 또는 안전한 example 문서 반영을 분리한다.
- `octopus-hub-server`의 미커밋 `octoto-legacy-permission-client.service.ts` 변경이 `menu-role` 전환 작업인지 확인하고, 테스트 통과 후 별도 커밋한다.
- Hub server `menu-role`, `user-role-group-join`, 남은 `user`/계정 복구/고객 파일 경로를 Octoto API 기준으로 계속 전환한다.
- Hub 중복 인증 테이블 실제 drop은 blocker 목록이 0이 될 때까지 금지한다.
- typecheck/lint baseline debt를 별도 작업으로 정리하면 향후 focused validation 의존을 줄일 수 있다.
- Oracle 통합 후속으로 `/api/permissions`, audit-log aggregate, mutation parity smoke를 넓히는 회귀 하네스가 필요하다.

## 8. 증거 출처

### 읽은 출처

- Codex session logs under `C:\Users\dnjsa\.codex\sessions\2026\05\20\*.jsonl`
  - `rollout-2026-05-20T09-27-08-019e42c7-762c-7380-bde4-35845f060b13.jsonl`
  - `rollout-2026-05-20T09-27-08-019e42c7-76c5-7170-9776-93377ceab6b8.jsonl`
  - `rollout-2026-05-20T09-27-09-019e42c7-7763-7943-8d75-a42c07ffec3b.jsonl`
  - `rollout-2026-05-20T09-27-09-019e42c7-780b-7f72-b91e-841e1e61278a.jsonl`
  - `rollout-2026-05-20T10-41-04-019e430b-2542-7451-abf3-2c24d83ce240.jsonl`
  - `rollout-2026-05-20T10-57-26-019e431a-22df-71c0-b897-07e40e733884.jsonl`
  - `rollout-2026-05-20T10-57-28-019e431a-27c1-78d3-90bc-e12678e1be86.jsonl`
  - `rollout-2026-05-20T11-04-06-019e4320-3dad-7cb1-99d1-4651f7285076.jsonl`
  - `rollout-2026-05-20T11-54-27-019e434e-52c4-7862-9f8a-fffdb12848e0.jsonl`
  - `rollout-2026-05-20T13-51-48-019e43b9-c3f7-7f81-94cc-9febf1255d60.jsonl`
  - `rollout-2026-05-20T14-26-44-019e43d9-c0cd-7ef1-b80d-467eef0b07e9.jsonl`
  - `rollout-2026-05-20T14-44-33-019e43ea-0edf-7603-9a64-060b24879c06.jsonl`
- 다음 대상의 Git status/log/diff:
  - `D:\reference2\ai-control-tower`
  - `D:\reference2\octoto`
  - `D:\reference2\octopus-hub-server`
  - `D:\reference2\octopus`
  - `D:\reference2\plugin-mh`
- Repo/local files:
  - `D:\reference2\ai-control-tower\CLAUDE.md`
  - `D:\reference2\ai-control-tower\decisions\2026-05-19-증거-남기기-실행-규칙.md`
  - `C:\Users\dnjsa\.codex\skills\daily-report\SKILL.md`
  - `C:\Users\dnjsa\.codex\prompts\daily-report.md`
  - `C:\Users\dnjsa\.codex\memories\MEMORY.md` quick search results
- 보고서 생성 중 실행한 검증:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin.ps1` in `D:\reference2\plugin-mh`

### 읽지 않았거나 제한된 출처

- Claude Code logs: searched `C:\Users\dnjsa\.claude\projects` for files modified on 2026-05-20, but no matching files were found.
- Notion/Gmail/remote issue tracker: 사용자가 local daily-report를 요청했고 외부 출처를 지정하지 않아 검색하지 않았다.
- Sensitive env contents: `.env.docker` changes were detected but values were intentionally not printed or copied into this report.
- 동시 작업 주의: 보고서 마감 시점 근처에 Hub duplicate-auth 세션이 활성 상태로 보였다. 이 보고서는 2026-05-20 14:47 KST에 관찰한 snapshot을 반영한다.
