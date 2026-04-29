---
name: my-harness
description: Personal harness workflow for initializing, auditing, operating, and closing AI-assisted coding sessions across repositories. Use when the user asks for a personal harness, harness application, session close or wrap-up, closing-lite style memory accumulation, private project overlays, or separating personal agent context from shared repositories.
---

# My Harness

개인 control tower 하네스를 대상 저장소 위에 overlay처럼 적용한다. 공유 프로젝트
문서는 깨끗하게 유지하고, 개인 메모리는
`D:\reference2\ai-control-tower\harness`에 둔다.

## 우선순위

1. 사용자의 최신 요청을 따른다.
2. 대상 저장소의 자체 지침을 먼저 읽는다.
3. 존재하면 `harness/projects/<project>/profile.md`를 적용한다.
4. 대상 저장소 규칙과 충돌하지 않는 범위에서 `harness/core/` 규칙을 적용한다.

개인 하네스 선호를 이유로 대상 저장소의 안전, 검증, 커밋 규칙을 약화하지 않는다.

사용자 입력이 필요한 결정은 `harness/core/ask-user-question.md`를 따른다.
런타임이 구조화 질문을 지원하면 그것을 우선 사용하고, 지원하지 않으면 짧은
일반 질문 하나로 대체한다.

하네스 문서, private overlay, 세션 메모리, 증강 후보는 기본적으로 한국어로
작성한다. 코드, 명령어, 경로, 환경 변수, API 이름, 외부 고유명사는 원문을
유지한다.

## 명령 흐름

### Init

새 프로젝트에 하네스를 적용할 때 사용한다.

1. 대상 저장소를 검사한다.
2. `harness/projects/<project>/profile.md`를 읽거나 만든다.
3. 개인 메모는 control tower에 두고 대상 저장소에 쓰지 않는다.
4. 사용자가 명시적으로 원하거나 프로젝트에 필수 에이전트 지침이 없을 때만 공유
   문서를 대상 저장소에 추가한다.

### Audit

프로젝트에 충분한 에이전트 맥락이 있는지 점검할 때 사용한다.

1. 대상 저장소 지침과 문서를 검토한다.
2. `harness/templates/`와 비교한다.
3. 부족한 부분을 공유 문서 후보 또는 private overlay 후보로 나누어 보고한다.

### Update

세션에서 배운 점을 반영할 때 사용한다.

1. 1회성 관찰은 `session-memory.md`에 넣는다.
2. 반복되거나 영향이 큰 패턴은 `agent-rules-candidates.md`에 넣는다.
3. 팀에 안전하고 안정적인 규칙만 대상 저장소 문서로 승격한다.

### Close

사용자가 세션 종료, 마무리, wrap-up을 요청할 때 사용한다.

1. 대상 저장소 상태를 확인한다.
2. 변경 파일을 검토하고 무관한 사용자 변경은 제외한다.
3. 집중 검증을 실행한다.
4. 세션 종료에 커밋이 포함된다는 기대가 있으면 관련 대상 저장소 변경을 커밋한다.
5. 명시적으로 요청하지 않으면 push하지 않는다.
6. `closing-lite`를 실행하거나 동일한 경량 메모리 축적을 수행한다.
7. `harness/projects/<project>/session-memory.md`에 짧은 메모리를 추가한다.
8. 그 메모리에 배운 점과 하네스 증강 아이디어를 포함한다.

## 참고 문서

- `../../core/principles.md`
- `../../core/git.md`
- `../../core/ask-user-question.md`
- `../../core/language.md`
- `../../core/verification.md`
- `../../core/session-close.md`
- `../../core/memory-promotion.md`
- `../../projects/<project>/profile.md`
