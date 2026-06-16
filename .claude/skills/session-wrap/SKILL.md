---
name: session-wrap
description: 사용자가 "세션 마무리", "세션 종료", "/wrap", "학습 내용 문서화", "무엇을 커밋해야 하지"를 요청하거나, 코딩 세션 종료 전 완료한 작업을 분석하려 할 때 사용한다.
version: 2.0.0
---

# Session Wrap 스킬

멀티 에이전트 분석을 포함한 종합 세션 마무리 워크플로우.

## 실행 흐름

```
┌─────────────────────────────────────────────────────┐
│  1. Git 상태 확인                                   │
├─────────────────────────────────────────────────────┤
│  2. Phase 1: 분석 에이전트 4개(병렬)                │
│     ┌─────────────────┬─────────────────┐           │
│     │  doc-updater    │  automation-    │           │
│     │  (문서 갱신)    │  scout          │           │
│     ├─────────────────┼─────────────────┤           │
│     │  learning-      │  followup-      │           │
│     │  extractor      │  suggester      │           │
│     └─────────────────┴─────────────────┘           │
├─────────────────────────────────────────────────────┤
│  3. Phase 2: 검증 에이전트(순차)                    │
│     ┌───────────────────────────────────┐           │
│     │       duplicate-checker           │           │
│     │  (Phase 1 제안 검증)              │           │
│     └───────────────────────────────────┘           │
├─────────────────────────────────────────────────────┤
│  4. 결과 통합 및 AskUserQuestion                    │
├─────────────────────────────────────────────────────┤
│  5. 선택된 액션 실행                                │
└─────────────────────────────────────────────────────┘
```

## 1단계: Git 상태 확인

```bash
git status --short
git diff --stat HEAD~3 2>/dev/null || git diff --stat
```

## 2단계: Phase 1 - 분석 에이전트(병렬)

에이전트 4개를 병렬 실행한다(한 메시지에 Task 호출 4개).

### 세션 요약(모든 에이전트에 제공)

```
세션 요약:
- 작업: [세션에서 수행한 주요 작업]
- 파일: [생성/수정한 파일]
- 결정: [내린 핵심 결정]
```

### 병렬 실행

```
Task(
    subagent_type="doc-updater",
    description="문서 업데이트 분석",
    prompt="[세션 요약]\n\nCLAUDE.md, context.md 업데이트가 필요한지 분석한다."
)

Task(
    subagent_type="automation-scout",
    description="자동화 패턴 분석",
    prompt="[세션 요약]\n\n반복 패턴이나 자동화 기회를 분석한다."
)

Task(
    subagent_type="learning-extractor",
    description="학습 지점 추출",
    prompt="[세션 요약]\n\n학습 내용, 실수, 새 발견을 추출한다."
)

Task(
    subagent_type="followup-suggester",
    description="후속 작업 제안",
    prompt="[세션 요약]\n\n미완료 작업과 다음 세션 우선순위를 제안한다."
)
```

### 에이전트 역할

| 에이전트 | 역할 | 출력 |
|----------|------|------|
| **doc-updater** | CLAUDE.md/context.md 갱신 필요성 분석 | 추가할 구체적 내용 |
| **automation-scout** | 자동화 패턴 탐지 | skill/command/agent 제안 |
| **learning-extractor** | 학습 지점 추출 | TIL 형식 요약 |
| **followup-suggester** | 후속 작업 제안 | 우선순위가 있는 작업 목록 |

## 3단계: Phase 2 - 검증 에이전트(순차)

Phase 1 완료 후 실행한다(Phase 1 결과에 의존).

```
Task(
    subagent_type="duplicate-checker",
    description="Phase 1 제안 검증",
    prompt="""
Phase 1 분석 결과를 검증한다.

## doc-updater 제안:
[doc-updater results]

## automation-scout 제안:
[automation-scout results]

제안이 기존 docs/automation과 중복되는지 확인한다.
1. 완전 중복: 생략 권장
2. 부분 중복: 병합 방식 제안
3. 중복 없음: 추가 승인
"""
)
```

## 4단계: 결과 통합

```markdown
## 마무리 분석 결과

### 문서 업데이트
[doc-updater summary]
- 중복 확인: [duplicate-checker feedback]

### 자동화 제안
[automation-scout summary]
- 중복 확인: [duplicate-checker feedback]

### 학습 지점
[learning-extractor summary]

### 후속 작업
[followup-suggester summary]
```

## 5단계: 액션 선택

```
AskUserQuestion(
    questions=[{
        "question": "어떤 액션을 수행할까요?",
        "header": "마무리 옵션",
        "multiSelect": true,
        "options": [
            {"label": "커밋 생성(권장)", "description": "변경 사항 커밋"},
            {"label": "CLAUDE.md 업데이트", "description": "새 지식/워크플로우 문서화"},
            {"label": "자동화 생성", "description": "skill/command/agent 생성"},
            {"label": "건너뛰기", "description": "액션 없이 종료"}
        ]
    }]
)
```

## 6단계: 선택된 액션 실행

사용자가 선택한 액션만 실행한다.

---

## 빠른 참조

### 사용할 때

- 의미 있는 작업 세션 종료 시
- 다른 프로젝트로 전환하기 전
- 기능 구현 또는 버그 수정 완료 후

### 생략할 때

- 사소한 변경만 있는 아주 짧은 세션
- 코드 읽기/탐색만 한 경우
- 단발성 질문에 답한 경우

### 인자

- 비어 있음: 상호작용 방식으로 진행(전체 워크플로우)
- 메시지 제공됨: 커밋 메시지로 사용하고 바로 커밋

## 추가 리소스

상세 오케스트레이션 패턴은 `references/multi-agent-patterns.md`를 참고한다.
