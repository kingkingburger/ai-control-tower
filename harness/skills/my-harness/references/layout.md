# 개인 하네스 구조

하네스 파일 시스템 계약이 필요한 작업에서 이 파일을 참고한다.

```text
harness/
  core/
    principles.md
    git.md
    ask-user-question.md
    language.md
    verification.md
    session-close.md
    memory-promotion.md
  templates/
    AGENTS.template.md
    CLAUDE.template.md
    ARCHITECTURE.template.md
    docs/
      DESIGN.template.md
      SECURITY.template.md
      RELIABILITY.template.md
  projects/
    default/
      profile.md
    <project>/
      profile.md
      private-notes.md
      session-memory.md
      agent-rules-candidates.md
  skills/
    my-harness/
      SKILL.md
```

대상 저장소는 코드와 공유 문서를 소유한다. control tower는 private memory와 개인
운영 규칙을 소유한다.
