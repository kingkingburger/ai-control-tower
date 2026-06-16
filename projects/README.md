# 프로젝트 팀

`projects/`는 저장소나 작업 표면별 에이전트 팀을 관리하는 최상위 공간이다.
각 프로젝트는 자체 프로필, 팀 구성, 세션 메모리, 워크플로우를 가진다.

## 구조

```text
projects/
  <project>/
    profile.md
    team.md              # 필요할 때 생성
    agents/              # 프로젝트 전용 에이전트 정의
    workflows/           # 프로젝트 전용 실행 흐름
    session-memory.md    # 반복 실행에서 얻은 관찰
    agent-rules-candidates.md
```

`profile.md`는 항상 그 프로젝트의 시작점이다. 중복되는 규칙이나 에이전트는
프로젝트 안에 복사하지 말고 `shared/`의 자산을 참조한다.

## Shared 사용 규칙

- 반복되는 작업 스타일, 검증, git, 메모리 승격 규칙은 `shared/rules/`를 참조한다.
- 여러 프로젝트에서 재사용하는 스킬은 `shared/skills/`에 둔다.
- 문서 템플릿은 `shared/templates/`를 기준으로 삼는다.
- 프로젝트에만 해당하는 운영 메모리와 팀 구성은 해당 `projects/<project>/`에 둔다.

## 승격 기준

프로젝트 안에서 두 번 이상 반복되거나 여러 프로젝트에 적용할 수 있는 규칙만
`shared/`로 올린다. 대상 저장소의 협업 문서로 남길 내용은 비밀값과 로컬 도구
상태를 제거한 뒤 해당 저장소의 문서 규칙에 맞게 반영한다.
