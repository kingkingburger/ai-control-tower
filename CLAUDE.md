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
  - `youtube-slides/` — 유튜브 영상 프레임 추출 (`{VIDEO_ID}/slides.html`, `slides.md`, `images/`)
  - `domain-model/` — 도메인 모델 문서 (원본 + readable 버전)
  - `til/` — Today I Learned 기록 (`YYYY-MM-DD-주제.md`)
- `docs/` — 프로젝트별 상세 문서
  - `ouroboros/{YYYY-MM-DD}-{project}/` — Ouroboros 3단계 산출물 (`01-requirements.md`, `02-design.md`, `03-verification.md`)
- `scripts/` — 유틸리티 스크립트 (`gen_html.py`: YouTube 트랜스크립트 HTML 생성, `capture_frames.py`: 영상 프레임 추출, `generate_output.py`: 슬라이드 HTML/MD 변환)
- `sync/` — 팀 채널 위클리 요약 등 외부 정보 싱크

## Presentation 제작
- 템플릿: `templates/slide-deck.html` 기반
- 슬라이드 마크업: HTML `<section>` 태그, 화살표 키 네비게이션
- CSS 변수로 컬러 스킴 조정 (`--day1-color`, `--day2-color` 등)
- 발표 시: F11 전체화면 + 화살표 키

## Known Issues
- ~~Notion 플러그인 MCP 충돌: Claude AI 내장 통합과 플러그인이 동일한 "notion" 서버를 등록하여 스킵됨.~~ → **해결됨 (2026-03-31)**: 빌트인 OAuth로 Notion MCP 연결. 플러그인 방식 폐기.
- Notion OAuth `resource` 파라미터 오류: OAuth URL에 `resource` 파라미터가 포함되면 `invalid_target` 에러 발생. URL에서 `resource` 파라미터를 제거하면 해결. (Admin 권한 없이 Integration 생성 불가 → OAuth 방식 사용)
