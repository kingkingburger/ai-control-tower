# 일일 작업 보고서 - 2026-05-21

작성 시점: 2026-05-22 KST 작성, 기간 2026-05-21 00:00~23:59 KST

## 1. 요약

- 핵심 작업은 `octoto`와 `octopus-hub-server`가 같이 사용하는 DB dialect를 PG와 Oracle 양쪽에서 모두 안정적으로 기동/마이그레이션할 수 있도록 정리한 것이다.
- Hub server가 Oracle을 사용할 때 typeorm sync/migration이 깨지는 원인을 추적하고, 메뉴 seed 누락, JSON 집계 경로 Oracle 비호환, 권한그룹 공유 시 userId 검증 차단 등 후속 회귀를 잡았다.
- DB 보정 수단이 "서버 기동 시에만 실행"되는 구조라 drift가 누적되는 문제를 짚고, DB 준비 경로를 서버 기동과 분리하는 방향으로 커밋했다. 관련 규칙은 octoto agent-memory에 학습 항목으로 저장했다.
- `octopus/apps/web/hub`는 dynamic-api, data-integration-v2, 시스템 설정 탭, 이메일/리포트 모달 등 UI 측 리팩토링 커밋이 다수 일어났다.
- Hub front ↔ Hub server 연동 후 E2E로 자동 테스트할 수 있는지 시도했고, 캡처/리포트 경로(`common-utils/uploads`)를 확인했다. 동시에 레포트 캡처 모듈을 Octoto RS256 토큰 기반으로 전환했다.
- 운영 지원으로 DataGrip Oracle introspection level 조정(테이블만 보이고 컬럼 미노출), Oracle 관리자(system) 계정 비밀번호 초기 설정, SDI 시절 Oracle 사용 이력 비교 같은 디버깅 질의가 있었다.
- 잡담/Q&답변: 오리 요리 갈색 소스(해선장/북경오리장)와 가정 레시피, 대한민국 맹견 분류와 도사견, 동물/식물 개량과 교배 방식.
- 현재 상태: 핵심 회귀 수정은 다수 커밋 완료. `ai-control-tower`, `plugin-mh`, `octopus-simulator-engine`에는 어제 자 커밋이 없다. `octopus`에는 다수 미커밋 변경이 남아 있지만, 이는 다른 워크스트림(agentic-ai 앱 신규 추가 등)으로 보이며 본 보고서 범위 밖이다.

## 2. 타임라인

| Time | Project | Event | Evidence |
|------|---------|-------|----------|
| 09:23-09:29 | `octoto` 등 | hub main-server env를 Postgres → Oracle 기준으로 바꾸기 시작했다. 초기 sync, 관리자 계정 비밀번호, system 권한 등을 질문하며 환경을 정비했다. | Codex log `019e47ea-*`, `019e47ef-bc84-*` |
| 09:48 | `octoto` | 인증 없이 처리 가능한 값들을 env에 옮겼다. | commit `492ff07` |
| 09:49 | `octoto` | 주간 실적 보고 완료 기록을 todos에 남겼다. | commit `7427410` |
| 10:07 | `octoto`/Hub | Hub Oracle migration이 깨진 이유를 SDI 프로젝트 이력과 비교하며 추적했다. typeorm entity 추가와 oracledb 클라이언트 동작이 원인 후보였다. | Codex log `019e4812-*` |
| 10:33 | `octopus-hub-server` | main-service의 Oracle 부팅 설정을 PG형 env와 동일한 구조로 맞췄다. | commit `c71bca97` |
| 10:42-13:42 | `octopus-hub-server`/`octoto` | Oracle 초기 seed가 없어 사이드바 메뉴가 비는 문제, datagrip introspection level/스키마 중복 표시 문제, 수동 seed/insert-or-pass SQL 생성, app vs octoto 스키마 권한 등을 같이 디버깅했다. | Codex log `019e4832-*`, `019e48cc-*` |
| 12:20 | `octoto` | Hub Oracle 테이블명과 메뉴 seed 기준을 문서로 보정했다. | commit `09bcf6c` |
| 13:41 | `octopus-hub-server` | 기본 사이드바 메뉴 구조 seed를 보정했다. | commit `2745f409` |
| 13:42-14:50 | Hub server | "서버 기동 시에만 DB 보정이 실행되는" 구조에 따른 drift를 짚고, DB 준비를 서버 기동과 분리하는 방향으로 정리했다. | Codex log `019e48d8-*`, `019e4915-*` |
| 14:33 | `octopus-hub-server` | 대시보드 생성과 JSON 집계 경로를 Oracle 호환으로 수정했다. SQL 식별자 사용 규칙을 메모리/문서로 남겼다. | commit `7e5541d2` |
| 14:56 | `octoto` | DB 준비 경로를 서버 기동과 분리했다. | commit `d6026d8` |
| 15:09 | `octopus-hub-server` | 권한그룹 공유가 userId 검증에 막히지 않게 수정했다. | commit `51b1d302` |
| 15:53 | `octopus-hub-server` | 중복 auth 테이블 제거 대상을 Hub 단수 user 기준으로 보정했다. | commit `c16e0c83` |
| 16:43 | `octopus-hub-server` | Hub 서버 pnpm dev 기동 실패를 수정했다. | commit `87495b15` |
| 16:43-17:58 | `octopus-hub-server`/Hub front | 리포트 캡처 모듈 작업. 저장 위치가 `common-utils/uploads`인 이유 확인. | Codex log `019e497d-*` |
| 16:57 | `octopus-hub-server` | 레포트 캡처가 Octoto RS256 토큰을 사용하도록 수정했다. | commit `9d6be5d6` |
| 18:17 | `octopus/apps/web/hub` 등 | Hub front UI 정리 작업이 종료됐다. 자세한 커밋은 §3 참고. | Hub front commits 09:39~18:16 |
| 17:58-18:17 | Hub 통합 | Hub front ↔ Hub server 연동 후 E2E 자동 테스트 가능 여부를 확인했다. 캡처/리포트 경로를 점검했다. | Codex log `019e498a-*` |

## 3. 프로젝트별 작업

### `D:\reference2\octoto`

- 목표: Hub가 PG와 Oracle 양쪽에서 정상 부팅/마이그레이션 되도록 octoto 측 환경/문서/계약을 보강한다.
- 수행 작업:
  - 인증 없이 처리할 수 있는 값들을 env로 분리했다.
  - 주간 실적 보고 완료 기록을 todos에 남겼다.
  - Hub Oracle 테이블명과 메뉴 seed 기준을 hub-integration 문서에 반영했다.
  - DB 준비 경로를 서버 기동과 분리해, 서버를 띄우지 않고도 마이그레이션/시드를 돌릴 수 있게 했다.
  - DB가 수정되면 migration/문서 처리를 함께 하도록 agent-memory에 규칙을 남겼다.
- 변경 파일/산출물:
  - 커밋: `492ff07`, `7427410`, `09bcf6c`, `d6026d8`
  - 문서: `docs/hub-integration/*`, `docs/agent-memory.md` 영역
- 현재 상태:
  - 관련 커밋 완료, 워킹 트리는 깨끗하다.

### `D:\reference2\octopus-hub-server`

- 목표: Hub server가 Oracle dialect에서도 안정적으로 부팅/마이그레이션/조회 가능하게 한다. 동시에 Hub 통합 흐름(리포트 캡처, 권한그룹 공유, 중복 인증 테이블 정리)을 진행한다.
- 수행 작업:
  - main-service의 Oracle 부팅 설정을 PG와 같은 env 구조로 맞췄다.
  - 기본 사이드바 메뉴 구조 seed를 보정해, 첫 로그인 시 메뉴가 빈 화면이 되지 않도록 했다.
  - 대시보드 생성과 JSON 집계 SQL을 Oracle 호환 식별자/구문으로 수정했다.
  - 권한그룹 공유에서 userId 검증에 막히던 문제를 해소했다.
  - 중복 인증 테이블 제거 대상을 Hub 단수 user 기준으로 다시 정렬했다.
  - Hub 서버 `pnpm dev` 기동 실패를 수정했다.
  - 레포트 캡처가 Octoto RS256 토큰을 사용하도록 인증 흐름을 전환했다.
- 변경 파일/산출물:
  - 커밋: `c71bca97`, `2745f409`, `7e5541d2`, `51b1d302`, `c16e0c83`, `87495b15`, `9d6be5d6`
  - 영향 영역: main-service 부팅 설정/env, 메뉴 seed, 대시보드 생성/집계, 권한그룹 공유, auth 마이그레이션 대상, 리포트 캡처 인증
- 현재 상태:
  - 워킹 트리는 깨끗하다.
  - Hub 통합 후 E2E 자동 테스트 도입은 시도 단계이고, 자동 실행 가능 여부와 캡처/리포트 산출 경로(`common-utils/uploads`)를 확인했다.

### `D:\reference2\octopus` (Hub front 영역)

- 목표: dynamic-api/data-integration v2 페이지 분할, 시스템 설정 탭 분리, 이메일/리포트 관련 모달과 톤다운, AI 모델 컴포넌트 품질 등을 다듬는다.
- 어제 자 주요 커밋(시간순):
  - `e34807de5` 09:39 `[Add](sdi)`: ai-data-analyze 페이지 일괄 복제(ai-model-create, ai-real-time-anomaly-detection, data-analysis)
  - `91a5d9187` 09:48 `[feat]` 레포트 관리 수정모달 이메일 내용 입력 폼 개선
  - `6ec65c8c2` 10:04, `ba86e75fe` 10:21 `[docs]` README update
  - `330f3da6a` 14:29 `[Update](app)` hub: 이메일 컨텐츠/템플릿 모달 미리보기 카드 제거, el-scrollbar 톤 통일
  - `be62b0ae4` 14:37 `[Update](app)` hub: 시스템 설정 좌측 탭/이메일 템플릿 아이콘 톤다운
  - `6d228d3da` 15:15 `[Refactor](app)` hub: system/setting 탭(StyleTab/LocaleTab) 분리, primary-alpha 톤다운, 모달 prefix 제거
  - `ad77ee1d6` 15:22 `[Docs]` package version update
  - `3a7e30391` 16:00 `[refactor]` AI 모델 관련 컴포넌트 코드 품질 개선
  - `1a89c50da` 16:00 Merge PR #1032 from uvcdev/hub-dev-jj
  - `f5b22206d` 16:11 Merge develop into hub-dashboard-jj
  - `5a249dc70` 16:50 `[Refactor](app)` hub: system/setting 세션·즐겨찾기 탭 분리(SessionFavoriteTab), 스타일 탭 색 선택기를 Vue3ColorPicker로 교체
  - `dd413f6e6` 17:03 `[Docs]` README update
  - `272f91782` 17:37 `[Feat](app)` hub: data-integration-v2 페이지 추가(Recipe/Template/API 에디터)
  - `3304b1ad1` 17:39 `[Update](app)` hub: dynamic-api 페이지 분할 패널 레이아웃 개편
  - `36457e336` 17:41 `[Feat](app)` hub: 게이트웨이 Hook Input Mapping/Middleware Interface 에디터 추가
  - `59de7330b` 17:43 `[Update](app)` gw: 자산 store bulkInsert 추가
  - `84b3e12e3` 18:16 `[Fix](app)` hub: 이메일 템플릿 모달 미리보기 호출명 오타 수정(EmailTemplatePreviewModal → PreviewModal)
- 현재 상태:
  - 위 커밋은 모두 어제 자에 반영됐다.
  - 별도로 `agentic-ai`, `Dockerfile.web*`, `.gitignore` 등에 다수 미커밋 변경이 남아 있으나, Codex 어제 세션과는 무관한 다른 워크스트림(agentic-ai 앱 신규)으로 보인다. 본 보고서는 어제 자 Hub/Oracle 통합 흐름에 집중했고, 미커밋 변경은 §7에 follow-up으로 남긴다.

### `D:\reference2\ai-control-tower`

- 목표: 어제 작업을 증거 기반으로 정리한다.
- 수행 작업:
  - Codex 세션 로그(19개), 관련 repo git log/status, 전일 보고서 형식을 확인했다.
  - 본 보고서를 `reports/2026-05-21-daily-report.md`로 생성했다.
- 현재 상태:
  - 어제 자 커밋은 없다. 본 보고서 파일 생성으로 변경이 생긴다.
  - 전일 작성한 `reports/2026-05-20-daily-report.md`도 함께 워킹 트리에 untracked 상태였다.

### `D:\reference2\plugin-mh`, `octopus-simulator-engine`

- 어제 자 커밋 없음, 워킹 트리 깨끗.
- daily-report 스킬 자체는 5/20에 적용된 상태이며 추가 변경 없음.

### 일반 질의응답 / 운영 지원

- DB/도구:
  - DataGrip에서 Oracle 접속 시 테이블은 보이는데 컬럼 상세가 안 나오는 문제를 introspection level과 스키마 노출 옵션으로 해결했다. 동일 서비스 이름에서 테이블이 중복 표시되는 부분도 정리했다.
  - Oracle `system` 계정 초기 비밀번호 설정, app 스키마 접근 권한 차이를 확인했다.
  - SDI 프로젝트가 Oracle을 사용했던 과거 이력을 git log로 비교해, Hub의 현재 Oracle migration이 왜 깨지는지 원인 후보를 추렸다.
- 잡학:
  - 오리 요리에 곁들이는 갈색 소스가 해선장(Hoisin sauce)이고, 북경오리 소스와의 차이, 가정에서 만드는 레시피를 정리했다.
  - 대한민국 맹견 분류(도사견 포함), "개량"이 동물·식물에서 어떻게 이뤄지는지, 동물 교배 방식을 설명했다.

## 4. 결정 사항

| Decision | Reason | Impact | Evidence |
|----------|--------|--------|----------|
| Hub의 DB 준비(마이그레이션/seed)는 서버 기동과 분리한다. | 보정 로직이 서버 기동 시에만 실행되면 drift가 누적되고 운영 측 보정이 불투명해진다. | `octoto`와 hub server에서 DB 준비 경로를 별도 명령/스크립트로 분리하기 시작했다. | Codex `019e48cc-*`, commit `d6026d8` |
| Hub의 1차 dialect 목표는 PG와 Oracle을 "동시에" 만족시키는 것이다. | 한쪽 dialect만 우선하면 다른 쪽에서 즉시 회귀가 난다(JSON 집계, 식별자 처리 등). | 대시보드/집계 SQL을 Oracle 호환 식별자 기준으로 다시 작성, 메뉴 seed/마이그레이션 대상 보정. | commits `7e5541d2`, `2745f409`, `c16e0c83` |
| 중복 인증 테이블 정리 대상은 Hub의 "단수 user" 기준으로 한다. | 다중 user 가정으로 짜둔 이전 계획이 실제 Hub 단수 user 구조와 어긋났다. | 마이그레이션 타겟 좁힘. drop 자체는 여전히 운영 blocker 확인 후 진행. | commit `c16e0c83` |
| 레포트 캡처는 Octoto RS256 토큰을 사용한다. | 캡처 모듈이 기존 인증 방식으로 호출하면 Octoto 통합 인증 정책과 어긋난다. | hub server의 캡처 클라이언트가 Octoto JWT 기반으로 호출. | commit `9d6be5d6` |
| 권한그룹 공유에서는 userId 검증을 통과시킨다. | "공유" 동작 자체는 다른 사용자에게 권한을 부여하는 절차이므로 본인 userId 검증으로 막히면 안 된다. | v2 대시보드 권한그룹 공유 경로 정상화. | commit `51b1d302` |
| SQL을 직접 쓸 때는 식별자(스키마/테이블/컬럼) 처리를 명시적으로 한다. | "내가 바로 갖다 썼다가" Oracle 식별자 대소문자/따옴표 처리에서 깨지는 일이 발생했다. | 메모리/문서에 규칙으로 저장. 이후 SQL 작성 시 따옴표/스키마 명시. | Codex `019e4915-*` |

## 5. 문제와 해결

| 문제 | 원인 | 해결 | 남은 위험 |
|---------|-------|------------|----------------|
| Hub Oracle에서 typeorm migration이 동작하지 않는다. | entity 추가, oracledb 드라이버 동작, 이전 dialect 시드 부재 등 다층 원인. | 부팅 설정을 PG와 동일 구조로 맞추고, seed/migration 경로를 분리. SDI 이력과 비교해 누락된 보정 포인트 식별. | 일부 entity의 Oracle 전용 type cast가 여전히 필요할 수 있음 |
| 첫 로그인 시 사이드바 메뉴가 비어 있다. | Oracle dialect에서 기본 메뉴 seed가 누락. | 기본 사이드바 메뉴 seed 보정 커밋. | seed 수정 SQL의 멱등성(없으면 insert, 있으면 pass) 검증 지속 필요 |
| 대시보드 생성/JSON 집계가 Oracle에서 실패. | PG 전용 식별자/JSON 함수 사용. | Oracle 호환 식별자/구문으로 SQL 재작성. | 향후 dialect별 추상화 일관성 점검 필요 |
| 권한그룹 공유 시 userId 검증에 막힘. | 공유 대상 검증 로직이 공유 행위 자체를 사용자 본인 한정으로 좁혀버림. | userId 검증 우회 + 공유 가능 조건으로 보정. | 공유 가능 사용자 범위 추가 권한 체크가 필요할 수 있음 |
| 중복 auth 테이블 제거 마이그레이션 타겟이 어긋남. | Hub의 user가 단수 구조인데, 마이그레이션이 복수 user 가정으로 작성. | 단수 user 기준으로 마이그레이션 대상 재정의. | 실제 drop 실행은 운영 blocker(런타임 참조, FK, seed) 해제 후 |
| Hub server `pnpm dev` 기동 실패. | dev 흐름에서 env/module 의존이 어긋남(상세는 commit 메시지 참조). | 기동 실패 수정 커밋. | dev/prod 경로 차이가 추가 회귀로 이어질 수 있음 |
| DataGrip에서 Oracle 테이블 컬럼 상세 미노출/중복 스키마 표시. | introspection level이 얕고, system 권한으로 본인 외 스키마를 포함해 두 번 노출됨. | introspection 상향 + 스키마 노출 옵션 조정. | DataGrip 설정 의존이라 팀 공유 시 별도 안내 필요 |
| 레포트 캡처 캡처물/리포트가 생성되지 않음. | 인증 방식과 저장 경로(`common-utils/uploads`) 미스매치. | RS256 토큰 기반으로 전환, 저장 경로 확인. | 캡처 산출물 retention/정리 정책 부재 |

## 6. 파일과 산출물

- 생성: `D:\reference2\ai-control-tower\reports\2026-05-21-daily-report.md`
- 주요 커밋(요약):
  - octoto: `492ff07`, `7427410`, `09bcf6c`, `d6026d8`
  - octopus-hub-server: `c71bca97`, `2745f409`, `7e5541d2`, `51b1d302`, `c16e0c83`, `87495b15`, `9d6be5d6`
  - octopus(Hub front 주요): `e34807de5`, `91a5d9187`, `330f3da6a`, `be62b0ae4`, `6d228d3da`, `3a7e30391`, `5a249dc70`, `272f91782`, `3304b1ad1`, `36457e336`, `59de7330b`, `84b3e12e3`, (Merge `1a89c50da`, `f5b22206d`)
- 주요 영향 영역:
  - Hub server: main-service Oracle 부팅 설정, 메뉴 seed, 대시보드/집계 SQL, 권한그룹 공유, auth 마이그레이션 타겟, 레포트 캡처 인증
  - Hub front: dynamic-api/data-integration-v2 페이지, 시스템 설정 탭 분리, 이메일/리포트 모달 톤다운, 게이트웨이 Hook/Middleware 에디터

## 7. 후속 조치

- octoto/Hub server 마이그레이션 흐름을 "서버 기동 없이 단독 실행"으로 정착시키고, 운영 매뉴얼에 표준 명령을 명시한다.
- Hub server seed의 멱등성(없으면 insert, 있으면 pass)을 PG/Oracle 양쪽에서 회귀 테스트로 보장한다.
- Hub server typeorm + Oracle entity 추가 시 발생하는 sync/migration 회귀의 근본 원인을 SDI 이력과 비교해 한 번 더 문서화한다.
- 중복 인증 테이블 실제 drop은 런타임 참조/FK/seed/외부 앱 의존 blocker가 0이 될 때까지 금지 상태를 유지한다.
- Hub 통합 후 E2E 자동 테스트(어제 시도)는 캡처/리포트 산출 경로를 표준화한 뒤 본격적으로 정착시킨다.
- `D:\reference2\octopus` 워킹 트리의 `agentic-ai` 신규 앱 및 Dockerfile 변경은 다른 워크스트림이므로 커밋 단위와 담당자를 별도로 정리한다.
- SQL 직접 작성 시 식별자/대소문자/스키마를 명시하는 규칙을 octoto agent-memory에 더해, hub server 쪽 메모리에도 함께 동기화한다.

## 8. 증거 출처

### 읽은 출처

- Codex session logs under `C:\Users\dnjsa\.codex\sessions\2026\05\21\*.jsonl` (총 19개)
  - 09-23-48-019e47ea, 09-27-48-019e47ee, 09-29-11-019e47ef-afe9, 09-29-14-019e47ef-bc84, 09-29-16-019e47ef-c723, 09-29-31-019e47ef-fff8, 09-56-47-019e4808, 10-07-36-019e4812, 10-25-33-019e4823, 10-42-32-019e4832, 10-47-28-019e4837, 13-30-14-019e48cc, 13-42-57-019e48d8, 14-50-12-019e4915, 15-41-35-019e4944, 15-50-48-019e494d, 15-54-26-019e4950, 16-43-44-019e497d, 16-58-12-019e498a
- Git log/status for repos in `D:\reference2\` (since 2026-05-21 00:00, until 2026-05-22 00:00):
  - `octoto`, `octopus-hub-server`, `octopus`, `plugin-mh`, `octopus-simulator-engine`, `ai-control-tower`
- 작성 참고 파일:
  - `D:\reference2\ai-control-tower\CLAUDE.md`
  - `D:\reference2\ai-control-tower\reports\2026-05-20-daily-report.md`
  - `C:\Users\dnjsa\.claude\projects\D--reference2-ai-control-tower\memory\MEMORY.md`

### 읽지 않았거나 제한된 출처

- Codex 세션 본문(메시지/도구 출력): 각 파일이 100KB+로 커서 `role:user` 인풋만 그렙으로 추출했다. assistant 응답과 tool 호출 본문은 부분만 확인했고, 보고서의 상세 묘사는 Codex 사용자 발화 + 같은 시간대 git 커밋 메시지를 교차 검증한 결과다.
- Claude Code projects 로그(`C:\Users\dnjsa\.claude\projects\...`): 어제 자 transcript는 본 보고서 작성 시점까지 별도로 읽지 않았다(파일이 매우 많고, 어제 자 활동의 대부분이 Codex CLI 쪽 세션이었다).
- Notion/Slack/Gmail/외부 트래커: 사용자가 어제 일정 확인 요청을 별도로 하지 않아 검색 범위에 포함하지 않았다.
- 민감 값(.env, 비밀번호, 토큰, 내부 URL): 보고서에 노출하지 않고 일반화해 기록했다.
- `D:\reference2\octopus`의 미커밋 변경(`agentic-ai/` 신규 앱 등): Codex 어제 세션 범위와 분리되어 보여 본문에는 포함하지 않고 follow-up 항목으로 표시했다.
