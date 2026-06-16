# 프로젝트 팀 구조

프로젝트 팀 파일 시스템 계약이 필요한 작업에서 이 파일을 참고한다.

```text
projects/
  default/
    profile.md
  <project>/
    profile.md
    notes.md
    team.md
    agents/
    workflows/
    session-memory.md
    agent-rules-candidates.md

shared/
  rules/
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
  skills/
    project-team/
      SKILL.md
```

대상 저장소는 코드와 협업 문서를 소유한다. `projects/`는 프로젝트 팀 맥락을
소유하고, `shared/`는 여러 프로젝트가 함께 쓰는 규칙과 템플릿을 소유한다.
