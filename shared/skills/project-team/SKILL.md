---
name: project-team
description: 저장소별 프로젝트 팀을 초기화, 점검, 운영, 마무리하는 프로젝트 중심 에이전트 워크플로우. 사용자가 프로젝트 팀, 프로젝트 하네스, 팀 프로필, shared rules, session close/wrap-up, closing-lite식 메모리 누적, 프로젝트별 에이전트 맥락을 요청할 때 사용한다.
---

# 프로젝트 팀

`ai-control-tower`의 프로젝트별 팀 프로필을 대상 저장소 위에 적용한다. 프로젝트
맥락은 `projects/<project>/`에서 시작하고, 여러 프로젝트에 반복되는 규칙과
템플릿은 `shared/`에서 가져온다.

## 우선순위

1. 사용자의 최신 요청을 따른다.
2. 대상 저장소의 자체 지침을 먼저 읽는다.
3. 존재하면 `projects/<project>/profile.md`를 적용한다.
4. 대상 저장소 규칙과 충돌하지 않는 범위에서 `shared/rules/` 규칙을 적용한다.

프로젝트 팀 선호를 이유로 대상 저장소의 안전, 검증, 커밋 규칙을 약화하지 않는다.

사용자 입력이 필요한 결정은 `shared/rules/ask-user-question.md`를 따른다.
런타임이 구조화 질문을 지원하면 그것을 우선 사용하고, 지원하지 않으면 짧은
일반 질문 하나로 대체한다.

프로젝트 팀 문서, 세션 메모리, 증강 후보는 기본적으로 한국어로
작성한다. 코드, 명령어, 경로, 환경 변수, API 이름, 외부 고유명사는 원문을
유지한다.

## 명령 흐름

### 초기화

새 프로젝트 팀을 적용할 때 사용한다.

1. 대상 저장소를 검사한다.
2. `projects/<project>/profile.md`를 읽거나 만든다.
3. 프로젝트별 메모리는 `projects/<project>/`에 두고 대상 저장소에는 안정된
   협업 규칙만 승격한다.
4. 사용자가 명시적으로 원하거나 프로젝트에 필수 에이전트 지침이 없을 때만 대상
   저장소 문서를 추가한다.

### 감사

프로젝트에 충분한 에이전트 맥락이 있는지 점검할 때 사용한다.

1. 대상 저장소 지침과 문서를 검토한다.
2. `shared/templates/`와 비교한다.
3. 부족한 부분을 프로젝트 프로필 후보, shared 후보, 대상 저장소 문서 후보로
   나누어 보고한다.

### Update

세션에서 배운 점을 반영할 때 사용한다.

1. 1회성 관찰은 `session-memory.md`에 넣는다.
2. 반복되거나 영향이 큰 패턴은 `agent-rules-candidates.md`에 넣는다.
3. 여러 프로젝트에 반복되는 규칙은 `shared/`로, 해당 프로젝트에만 필요한
   규칙은 `projects/<project>/`로 정리한다.

### 종료

사용자가 세션 종료, 마무리, wrap-up을 요청할 때 사용한다.

1. 대상 저장소 상태를 확인한다.
2. 변경 파일을 검토하고 무관한 사용자 변경은 제외한다.
3. 집중 검증을 실행한다.
4. 세션 종료에 커밋이 포함된다는 기대가 있으면 관련 대상 저장소 변경을 커밋한다.
5. 명시적으로 요청하지 않으면 push하지 않는다.
6. `closing-lite`를 실행하거나 동일한 경량 메모리 축적을 수행한다.
7. `projects/<project>/session-memory.md`에 짧은 메모리를 추가한다.
8. 그 메모리에 배운 점과 하네스 증강 아이디어를 포함한다.

## 참고 문서

- `../../rules/principles.md`
- `../../rules/work-style.md`
- `../../rules/git.md`
- `../../rules/ask-user-question.md`
- `../../rules/language.md`
- `../../rules/verification.md`
- `../../rules/session-close.md`
- `../../rules/memory-promotion.md`
- `../../../projects/<project>/profile.md`
