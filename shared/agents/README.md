# Shared Agents

여러 프로젝트 팀에서 반복해서 쓰는 공통 에이전트 역할이다. 프로젝트별 `team.md`는
아래 역할을 참조하고, 프로젝트 고유 역할만 자체 팀에 추가한다.

## 공통 역할

- `project-orchestrator`: 요청을 프로젝트, 작업 표면, 검증 경로로 라우팅한다.
- `context-explorer`: 저장소 지침, 관련 코드, 최근 메모리를 읽고 작업 브리프를 만든다.
- `implementation-planner`: 변경 범위, 위험, 검증 계획을 좁힌다.
- `verification-runner`: 변경 표면에 맞는 lint, typecheck, test, runtime 검증을 실행한다.
- `docs-syncer`: 코드, 운영 규칙, 팀 프로필 사이의 stale 문서를 찾고 갱신한다.
- `memory-curator`: 세션에서 반복 가능한 규칙 후보를 `projects/<project>/`나 `shared/`로 분류한다.

## 사용 규칙

공통 역할은 프로젝트 안에 복사하지 않는다. 프로젝트별 팀 문서에서는 이 역할 이름을
그대로 참조하고, 프로젝트 고유 책임과 입력 문서만 덧붙인다.
