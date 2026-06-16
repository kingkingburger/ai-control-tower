# AI Control Tower

AI 관련 실험을 위한 작업 공간. 유저 환경에 적용하기 전에 여기서 먼저 테스트한다.

## 용도
- AI 도구/플러그인/스킬 실험
- 새로운 워크플로우 프로토타이핑
- 설정 변경 전 사전 검증
- 의사결정 시뮬레이션 (Agent Arena) 및 decisions/ 기록

## 디렉토리 구조
- `decisions/` — Agent Arena 토론 결과 및 의사결정 기록 (`YYYY-MM-DD-주제.md`)
- `presentations/` — 발표 슬라이드(HTML) + 스크립트(MD) (`YYYY-MM-DD-제목.html`, `-script.md`)
- `templates/` — 재사용 템플릿 (`slide-deck.html`: `{{TITLE}}` 플레이스홀더 치환하여 사용)
- `requirements/` — 요구사항 문서 (`YYYY-MM-DD-주제.md`)
- `research/` — 리서치 자료
  - `readings/youtube/` — 유튜브 강의 자료 정리
  - `digests/` — 콘텐츠 digest와 학습 자료
  - `domain-model/` — 도메인 모델 문서 (원본 + readable 버전)
  - `til/` — Today I Learned 기록 (`YYYY-MM-DD-주제.md`)
- `project/` — 이 저장소 자체의 운영 문서
  - `roadmaps/` — 단계별 목표와 최종 상태
  - `inventories/` — 스킬, 훅, 배포 대상 같은 자산 목록
  - `distribution-sync/` — 원본/배포본 동기화 정책과 drift 처리
  - `runbooks/` — 반복 운영 절차와 정리 기준
- `projects/` — 프로젝트별 에이전트 팀, 프로필, 메모리, 워크플로우
- `shared/` — 여러 프로젝트 팀이 공유하는 규칙, 템플릿, 스킬
- `agent/` — 재사용 가능한 에이전트 정의
- `problem-finding/` — 반복되는 불편을 실행 가능한 문제 후보로 바꾸는 기록
- `reports/` — 일일 보고서와 목표 기반 결과 보고서
- `reviews/` — 설계나 문서 리뷰
- `scripts/` — 유틸리티 스크립트 (`gen_html.py`: YouTube 트랜스크립트 HTML 생성, `capture_frames.py`: 영상 프레임 추출, `generate_output.py`: 슬라이드 HTML/MD 변환)
- `sync/` — 팀 채널 위클리 요약 등 외부 정보 싱크

## 폴더 정리 기준
- 유지, 통합, 아카이브, 삭제 기준은 `project/runbooks/folder-cleanup-criteria.md`를 따른다.
- 추적 파일, 문서 참조, 도구 상태 여부, 원본/배포본 구분, 재생성 경로를 확인하지 않은 폴더는 `unused`가 아니라 `검토 필요`로 둔다.
- 비어 있는 임시 산출물 폴더는 제거해도 되지만, 날짜 기반 기록과 스킬 원본은 별도 인벤토리 없이 삭제하지 않는다.

## Presentation 제작
- 템플릿: `templates/slide-deck.html` 기반
- 슬라이드 마크업: HTML `<section>` 태그, 화살표 키 네비게이션
- CSS 변수로 컬러 스킴 조정 (`--day1-color`, `--day2-color` 등)
- 발표 시: F11 전체화면 + 화살표 키

## Known Issues
- ~~Notion 플러그인 MCP 충돌: Claude AI 내장 통합과 플러그인이 동일한 "notion" 서버를 등록하여 스킵됨.~~ → **해결됨 (2026-03-31)**: 빌트인 OAuth로 Notion MCP 연결. 플러그인 방식 폐기.
- Notion OAuth `resource` 파라미터 오류: OAuth URL에 `resource` 파라미터가 포함되면 `invalid_target` 에러 발생. URL에서 `resource` 파라미터를 제거하면 해결. (Admin 권한 없이 Integration 생성 불가 → OAuth 방식 사용)
