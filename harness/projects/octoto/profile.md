# Octoto Private Overlay

대상 저장소: `D:\reference2\octoto`

## 경계

`octoto`는 다른 사람과 함께 보는 저장소다. 프로젝트별 에이전트 학습과 세션
메모리는 Octoto 안의 명시된 메모리 문서에 저장한다. 여러 프로젝트에 반복 적용할
운영 규칙만 `ai-control-tower`로 승격한다.

팀이 보는 프로젝트 파일에 섞이면 안 되는 개인 운영 맥락은 이 overlay에 둔다.

## 시작 순서

1. `D:\reference2\octoto\AGENTS.md`를 읽는다.
2. `CLAUDE.md`, `frontend/CLAUDE.md`, `src/CLAUDE.md`, 관련
   `.claude/rules/*`처럼 참조된 프로젝트 지침을 읽는다.
3. 이 private overlay를 읽는다.
4. 과거 개인 맥락이 도움이 될 때만 `session-memory.md`를 읽는다.

## 세션 종료 기대값

Octoto 작업 중 사용자가 세션 종료나 마무리를 요청하면 다음을 수행한다.

1. Octoto 상태를 확인한다.
2. 관련 변경을 검증한다.
3. 관련 Octoto 변경을 한국어 커밋 메시지로 커밋한다.
4. 명시적으로 요청하지 않으면 push하지 않는다.
5. 이 overlay에 `closing-lite` 메모리를 추가한다.

## 개인 선호

- 사용자가 다른 언어를 요청하지 않으면 한국어로 응답한다.
- 하네스 문서, 개인 메모, 세션 메모리, 증강 후보는 기본적으로 한국어로 쓴다.
- 세션 종료는 커밋과 프로젝트 메모리 축적을 포함한다.
- Octoto 공유 문서에는 프로젝트별 학습을 누적하고, 반복 규칙만 `ai-control-tower`
  core로 승격한다.
