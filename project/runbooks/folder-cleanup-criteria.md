# Folder Cleanup Criteria

작성일: 2026-06-13

이 문서는 `ai-control-tower`의 폴더를 정리할 때 쓰는 기준이다. 목적은 폴더 수를
줄이는 것이 아니라, 원본 위치와 임시 산출물, 도구 상태, 장기 지식 자산을 헷갈리지
않게 만드는 것이다.

## 판단 기준

폴더를 정리하기 전에는 아래 5가지를 먼저 확인한다.

1. `git ls-files <folder>`에 추적 파일이 있는가.
2. `README.md`, `CLAUDE.md`, `project/`, `harness/` 문서에서 참조되는가.
3. 특정 도구가 런타임에 자동 생성하거나 갱신하는 상태 폴더인가.
4. 장기 원본인지, 배포본인지, 임시 산출물인지 구분되는가.
5. 삭제해도 재생성 경로나 복구 경로가 명확한가.

위 조건을 확인하지 않은 폴더는 `unused`가 아니라 `검토 필요`로 둔다.

## 분류 규칙

### 유지

다음 중 하나라도 해당하면 유지한다.

- 현재 roadmap, README, 하네스 문서에서 원본 위치로 정의되어 있다.
- 날짜 기반 문서, 발표 자료, 리서치처럼 장기 기록의 원본이다.
- 실행 가능한 스킬, 에이전트, 템플릿, 스크립트를 담고 있다.
- 삭제하면 기존 문서 링크나 사용 흐름이 깨진다.

현재 유지 대상:

- `harness/`: 개인 하네스 원본.
- `project/`: 이 저장소 운영 문서.
- `agent/`: repo map과 실행 브리프용 에이전트 정의.
- `.claude/`: Claude 계열 스킬 자산. 단, 장기적으로는 원본/배포본 여부를 다시
  확정해야 한다.
- `decisions/`, `problem-finding/`, `reports/`, `requirements/`, `research/`,
  `reviews/`, `sync/`: 날짜 기반 기록과 리서치 원본.
- `presentations/`, `templates/`, `scripts/`: 발표와 변환 워크플로우의 원본.

### 통합

역할이 겹치지만 즉시 삭제하면 정보 손실이 생기는 폴더는 먼저 통합한다.

- `.claude/skills/`와 `harness/skills/`: 스킬 원본이 둘로 보인다. 기준은
  `harness/skills/`를 원본 후보로 두고, `.claude/skills/`는 Claude 배포본인지
  레거시 원본인지 인벤토리에서 확정한다.
- `CLAUDE.md`와 `README.md`: `CLAUDE.md`는 에이전트 실행 지침, `README.md`는
  사람용 탐색 인덱스로 유지한다. 오래된 폴더 설명은 `README.md` 기준으로
  맞춘다.
- `reports/`, `sync/`, `research/digests/`: 외부 정보 요약이라는 공통점이 있지만
  목적이 다르다. 보고서는 `reports/`, 팀/채널 싱크는 `sync/`, 콘텐츠 학습물은
  `research/digests/`에 둔다.

### 아카이브

장기 기록이지만 현재 실행 흐름에서 사용하지 않는 문서는 삭제하지 않고 아카이브한다.

- 날짜 기반 의사결정과 리서치 문서는 기본적으로 삭제하지 않는다.
- 오래된 발표 자료는 `presentations/archive/`를 만들 때만 이동한다.
- 특정 실험이 종료된 요구사항이나 리뷰는 `requirements/archive/` 또는
  `reviews/archive/`가 필요해질 때 이동한다.

아카이브 이동은 링크 깨짐 확인 후 별도 커밋으로 처리한다.

### 삭제

다음 조건을 모두 만족할 때만 삭제한다.

- 추적 파일이 없다.
- 문서 원본이 아니다.
- 현재 도구가 실행 중에 필요로 하지 않는다.
- 내부 파일이 없거나, 재생성 가능한 산출물뿐이다.
- 삭제 후 `git status --short`와 관련 경로 존재 확인으로 영향이 설명된다.

현재 삭제 가능 후보:

- `outputs/`: 추적 파일 0개, 현재 내부 파일 0개인 임시 산출물 트리다. 필요하면
  워크플로우 실행 시 다시 만든다.
- `.omc/skills/`: 빈 ignored 도구 상태 폴더다. `.omc` 전체는 도구가 다시 만들 수
  있으므로 git 원본으로 승격하지 않는다.
- `.omc/state/sessions/*`: 빈 ignored 도구 상태 폴더다.

## 오늘 확인된 정리 포인트

- `outputs/`는 현재 비어 있고 git에 추적되지 않는다. 삭제해도 커밋 diff는 생기지
  않는다.
- `.obsidian/`과 `.omc/`는 `.gitignore` 대상이다. 저장소 원본 정리 대상이 아니라
  로컬 도구 상태로 취급한다.
- `harness/bin/`은 비어 있지만 roadmap에서 `harness/bin/octoto-harness.ps1`
  누락을 명시하고 있다. 삭제 후보가 아니라 "복구 또는 hook 제거 결정" 후보로
  둔다.
- `CLAUDE.md`에는 현재 존재하지 않는 `docs/`와 과거 구조인
  `research/youtube-slides/` 설명이 남아 있다. 폴더 삭제보다 문서 경계 교정이
  먼저다.
- `.claude/skills/`와 `harness/skills/`는 둘 다 스킬을 담고 있어 단일 원본 결정이
  필요하다.

## 실행 순서

1. 빈 임시 산출물 폴더를 삭제한다.
2. `CLAUDE.md`의 오래된 폴더 설명을 현재 구조에 맞춘다.
3. `.claude/skills/`와 `harness/skills/`를 인벤토리 문서에서 `원본`, `배포본`,
   `폐기 후보`, `검토 필요`로 분류한다.
4. `harness/bin/octoto-harness.ps1`는 복구할지, `harness/git-hooks/octoto/*`에서
   호출을 제거할지 결정한다.
5. 이동이나 삭제가 필요한 추적 파일은 한 번에 많이 묶지 말고 분류별로 작은
   커밋을 만든다.

## 금지 사항

- `rg` 참조가 적다는 이유만으로 문서를 삭제하지 않는다.
- 날짜 기반 기록을 임시 산출물처럼 지우지 않는다.
- `.omc/project-memory.json` 같은 도구 상태 파일을 지속 메모리 원본으로 승격하지
  않는다.
- 원본/배포본 경계가 확정되지 않은 스킬 폴더를 바로 합치지 않는다.
