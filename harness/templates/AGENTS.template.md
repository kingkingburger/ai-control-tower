# [PROJECT_NAME] 에이전트 지침

이 파일은 이 저장소에서 작업하는 AI 코딩 에이전트의 공유 진입점이다. 팀에
안전하고 프로젝트에 특화된 내용만 둔다.

## 먼저 읽을 문서

- [CLAUDE.md](CLAUDE.md): 프로젝트 맥락, 명령어, 제약.
- [ARCHITECTURE.md](ARCHITECTURE.md): 아키텍처와 의존 방향.
- 하위 디렉터리를 편집하기 전에는 관련 중첩 지침 파일.

## 언어

- 응답 언어: [LANGUAGE]
- 커밋 메시지 언어: [COMMIT_LANGUAGE]
- 커밋 형식: `{type}: {description}`

## 명령어

- 설치: `[INSTALL_COMMAND]`
- lint: `[LINT_COMMAND]`
- 테스트: `[TEST_COMMAND]`
- typecheck: `[TYPECHECK_COMMAND]`

## 안전

- 비밀 파일을 읽거나 출력하지 않는다.
- 명시적 요청 없이 파괴적인 git 명령을 실행하지 않는다.
- 사용자 변경을 되돌리지 않는다.
- 명시적 요청 없이 push하지 않는다.

## 검증

모든 변경에 맞는 집중 검증을 실행하고, 무엇을 실행했는지 보고한다.

## 아키텍처

[ARCHITECTURE.md](ARCHITECTURE.md)를 따른다. 현재 사용처가 없는 추상화를
추가하지 않는다.
