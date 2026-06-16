# Octoto Project Profile

대상 저장소: Octoto checkout (`<octoto-repo>`)

## 경계

`octoto`는 회사 주 프로젝트다. 다른 사람과 함께 보는 저장소이므로 프로젝트별
에이전트 학습과 세션 메모리는 Octoto 안의 명시된 메모리 문서에 저장한다. 여러
프로젝트에 반복 적용할 운영 규칙만 `ai-control-tower`로 승격한다.

팀이 보는 프로젝트 파일에 섞이면 안 되는 로컬 운영 맥락은 이 프로필에 둔다.

## 시작 순서

1. `<octoto-repo>/AGENTS.md`를 읽는다.
2. `CLAUDE.md`, `frontend/CLAUDE.md`, `src/CLAUDE.md`, 관련
   `.claude/rules/*`처럼 참조된 프로젝트 지침을 읽는다.
3. 이 프로젝트 프로필을 읽는다.
4. 과거 운영 맥락이 도움이 될 때만 `session-memory.md`를 읽는다.

## 핵심 역할

Octoto는 Hub/Octopus 등 여러 서비스가 공유하는 중앙 인증 서버다. 유저 데이터,
JWT, 세션, 권한, 서비스 메뉴, 감사 로그의 핵심 계약을 책임진다. Hub 연동 작업은
Octoto server/API/domain 경계와 Hub front/server의 소비 경계를 함께 확인한다.

## 자주 쓰는 명령

```bash
bun run lint
bun test
bun run test:pg
bun run test:oracle
bun run test:e2e
cd frontend && bun run test --run ...
cd frontend && bun run build
```

## 반복 주의점

- 권한/인증 문제는 UI-only 패치로 끝내지 말고 서버/API/domain 경계에서 불변식을
  먼저 고정한다.
- Oracle parity는 GET smoke만으로 충분하지 않다. writes, bulk, cleanup,
  dialect-unsafe path를 함께 확인한다.
- 배포 실패는 Jenkins/Argo CD UI 상태가 운영 truth일 수 있다.
- generic push 요청은 현재 branch를 `origin`과 `uvcdev` 모두에 push하는 뜻이다.

## 세션 종료 기대값

Octoto 작업 중 사용자가 세션 종료나 마무리를 요청하면 다음을 수행한다.

1. Octoto 상태를 확인한다.
2. 관련 변경을 검증한다.
3. 관련 Octoto 변경을 한국어 커밋 메시지로 커밋한다.
4. 명시적으로 요청하지 않으면 push하지 않는다.
5. 이 프로젝트 프로필에 `closing-lite` 메모리를 추가한다.

## 응답/운영 선호

- 사용자가 다른 언어를 요청하지 않으면 한국어로 응답한다.
- 프로젝트 팀 문서, 운영 메모, 세션 메모리, 증강 후보는 기본적으로 한국어로 쓴다.
- 세션 종료는 커밋과 프로젝트 메모리 축적을 포함한다.
- Octoto 공유 문서에는 프로젝트별 학습을 누적하고, 반복 규칙만 `ai-control-tower`
  `shared/`로 승격한다.
