# AI Control Tower

AI 도구, 스킬, 에이전트, 문서 워크플로우를 실제 프로젝트에 적용하기 전에
검증하는 개인 작업 공간이다. 루트의 `CLAUDE.md`는 에이전트 실행 지침이고,
이 README는 사람이 저장소를 빠르게 탐색하기 위한 인덱스다.

## 폴더 구조

| 경로 | 역할 |
| --- | --- |
| `.claude/` | Claude Code용 로컬 스킬, 참조 문서, 실행 스크립트. `skills-lock.json`과 함께 설치된 스킬 버전을 추적한다. |
| `.obsidian/` | Obsidian으로 이 저장소를 열 때 쓰는 로컬 vault 설정. 새 로컬 상태 파일은 `.gitignore` 대상이다. |
| `.omc/` | OMC/mission-control 계열의 세션, 체크포인트, 프로젝트 상태 파일. 지속 문서의 원본이 아니라 도구 상태에 가깝다. |
| `agent/` | 재사용 가능한 에이전트 정의. 현재 `atlas.md`가 저장소 맥락 파악용 에이전트 역할을 한다. |
| `decisions/` | 의사결정 기록과 Agent Arena 결과. 날짜 기반 파일명으로 남긴다. |
| `harness/` | 개인 AI 엔지니어링 하네스 원본. core 규칙, 프로젝트별 overlay, 템플릿, git hook, Codex 스킬을 포함한다. |
| `outputs/` | 필요할 때 생성되는 임시 산출물 위치. 장기 원본으로 보지 않고 비어 있으면 제거한다. |
| `presentations/` | 발표용 HTML 슬라이드와 발표 스크립트. `assets/`에는 발표 보조 자산을 둔다. |
| `problem-finding/` | 반복되는 불편을 실행 가능한 문제 후보로 바꾸는 기록 공간. |
| `project/` | `ai-control-tower` 자체 운영 문서. roadmap, inventory, distribution sync, runbook으로 나눈다. |
| `reports/` | 일일 보고서나 목표 기반 결과 보고서. |
| `requirements/` | 기능이나 실험의 요구사항 문서. |
| `research/` | 학습, 리서치, TIL, 도메인 모델, 콘텐츠 digest 자료. |
| `reviews/` | 설계나 문서에 대한 리뷰 결과. |
| `scripts/` | YouTube, 프레젠테이션, 저장소 메타데이터 작업용 유틸리티 스크립트. |
| `sync/` | 팀 채널 요약, 주간 싱크 등 외부 정보 동기화 기록. |
| `templates/` | 발표와 플래너 같은 재사용 템플릿. |

## 주요 문서

| 파일 | 내용 |
| --- | --- |
| `CLAUDE.md` | 저장소 목적, 기본 디렉터리 설명, 발표 제작 규칙, 알려진 이슈. |
| `harness/README.md` | 개인 하네스의 목적, 구조, 승격 규칙, 세션 종료 메모리 원칙. |
| `project/README.md` | `project/` 하위 운영 문서의 분류 기준. |
| `project/runbooks/folder-cleanup-criteria.md` | 폴더 유지, 통합, 아카이브, 삭제 기준. |
| `problem-finding/README.md` | 문제 발견 기록 방식과 평가 기준. |
| `skills-lock.json` | `.claude/skills/`에 들어온 스킬의 source와 hash lock. |

## 도구와 스킬

### Claude Code 스킬

`.claude/skills/` 아래에는 Claude Code에서 직접 호출할 수 있는 스킬들이 있다.

| 스킬 | 용도 |
| --- | --- |
| `compound` | 작업 중 검증된 인사이트를 구조화된 지식 베이스로 축적한다. |
| `content-digest` | YouTube, X/Twitter, 웹페이지, PDF를 quiz-first 방식으로 정리한다. |
| `fetch-tweet` | X/Twitter URL에서 트윗 원문과 작성자, 인게이지먼트 데이터를 가져온다. |
| `history-insight` | Claude Code 세션 히스토리를 추출하고 요약한다. |
| `my-context-sync` | Slack, Notion 등 여러 소스의 컨텍스트를 한 문서로 모은다. |
| `session-analyzer` | 과거 Claude Code 세션이 스킬 명세대로 실행됐는지 후행 분석한다. |
| `session-wrap` | 세션 종료 시 변경사항, 학습, 후속 작업을 정리한다. |
| `team-assemble` | 복잡한 작업을 전문가 역할로 나누고 팀 단위 실행 흐름을 설계한다. |

### 에이전트와 하네스

| 도구 | 위치 | 용도 |
| --- | --- | --- |
| Atlas agent | `agent/atlas.md` | 저장소 구조, 관련 파일, 검증 경로를 짧은 실행 브리프로 정리한다. |
| My Harness skill | `harness/skills/my-harness/SKILL.md` | 개인 하네스를 다른 저장소에 overlay처럼 적용하고 세션 종료 메모리를 관리한다. |
| Harness core rules | `harness/core/` | 작업 스타일, git, 검증, 언어, 메모리 승격 같은 반복 규칙을 보관한다. |
| Harness templates | `harness/templates/` | `AGENTS.md`, `CLAUDE.md`, 아키텍처/보안/신뢰성 문서 템플릿. |

### 스크립트

루트에 별도 `package.json`이나 Python 의존성 매니페스트는 없다. 필요한 런타임은
스크립트별로 준비해서 실행한다.

| 스크립트 | 사용처 |
| --- | --- |
| `scripts/extract_metadata.sh` | `python -m yt_dlp`로 YouTube 제목, 채널, 업로드일, 길이, 영상 ID를 추출한다. |
| `scripts/extract_transcript.sh` | YouTube 자막을 JSON3 형식으로 `output_dir/source/`에 저장한다. |
| `scripts/download_video.sh` | YouTube 영상을 720p 이하 mp4로 `output_dir/source/`에 저장한다. |
| `scripts/capture_frames.py` | 영상과 JSON3 자막을 받아 프레임 이미지와 `segments.json`을 만든다. `ffmpeg`가 필요하다. |
| `scripts/generate_output.py` | `segments.json`을 `slides.md`와 `slides.html`로 변환한다. |
| `scripts/gen_html.py` | 기존 YouTube digest 데이터를 특정 HTML 문서로 변환하는 하드코딩된 레거시 스크립트다. |
| `scripts/pptx_to_html.py` | PPTX를 레이아웃 보존 HTML로 변환한다. `python-pptx`가 필요하다. |
| `scripts/update_repos.sh` | GitHub CLI로 `kingkingburger/*` 저장소 description과 topics를 일괄 업데이트한다. |

## 자주 쓰는 흐름

### YouTube 슬라이드 추출

```bash
scripts/extract_metadata.sh "<YouTube URL>"
scripts/extract_transcript.sh "<YouTube URL>" "<output_dir>"
scripts/download_video.sh "<YouTube URL>" "<output_dir>"
python scripts/capture_frames.py "<video.mp4>" "<subtitle.json3>" "<output_dir>" --min-interval 3
python scripts/generate_output.py "<output_dir>" --title "<title>" --url "<url>" --channel "<channel>" --date "<date>" --duration "<duration>"
```

결과는 보통 `<output_dir>/images/`, `<output_dir>/segments.json`,
`<output_dir>/slides.md`, `<output_dir>/slides.html`로 나뉜다.

### 발표 HTML 작성

`templates/slide-deck.html`을 기반으로 `presentations/`에 날짜 기반 HTML 파일을
만든다. 발표 원고가 필요하면 같은 날짜와 제목으로 `*-speaker-script.md` 또는
`*-script.md`를 둔다.

### 하네스 작업

`harness/`는 공유 프로젝트 문서가 아니라 개인 운영 규칙을 모으는 곳이다.
프로젝트에 반복 적용할 만큼 안정된 내용만 대상 저장소의 `AGENTS.md`나 문서로
승격하고, 개인 선호나 임시 관찰은 `harness/projects/<project>/`에 남긴다.

## 기록 규칙

- 날짜가 중요한 문서는 `YYYY-MM-DD-주제.md` 형식을 우선 사용한다.
- README나 history 항목은 나중에 읽는 사람이 맥락을 이해하도록 짧은 배경과
  구체적 변경만 남긴다.
- 터미널 조사 과정, 일회성 디버깅 로그, 도구의 임시 상태는 장기 문서에 그대로
  옮기지 않는다.
- 새로 생성되는 대용량 미디어, 빌드 산출물, 로컬 도구 상태는 `.gitignore`에
  맞춰 저장소 원본과 분리한다.
