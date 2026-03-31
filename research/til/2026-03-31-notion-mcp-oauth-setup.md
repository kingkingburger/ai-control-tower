# Notion MCP OAuth 설정 (Windows / Claude Code)

## 날짜
2026-03-31

## 배경
Notion MCP를 Claude Code에서 사용하려고 했으나, 워크스페이스 관리자 권한이 없어 Internal Integration(API 토큰) 생성 불가. 대안으로 빌트인 OAuth 방식 사용.

## 학습 포인트

### 1. `--transport oauth`는 존재하지 않는다
Claude MCP는 `stdio`, `sse`, `http`만 지원. OAuth 기반 MCP는 Claude AI 플랫폼 설정(Settings > Connected Apps)에서 활성화해야 함.

### 2. OAuth 인증 흐름
- 세션 시작 시 `mcp__notion__authenticate` 도구가 나타남
- 호출하면 브라우저 인증 URL 발급
- 인증 완료 후 `mcp__notion__notion-search`, `notion-fetch` 등 도구 활성화
- `authenticate` 도구는 인증 후 사라짐

### 3. `resource` 파라미터 제거 워크어라운드
OAuth URL에 `resource=https%3A%2F%2Fmcp.notion.com%2Fmcp` 파라미터가 포함되면 `invalid_target` 에러 발생. URL에서 `&resource=...` 부분을 제거하면 정상 작동.

### 4. Built-in 통합 vs 로컬 MCP
- Slack, Google Calendar, Gmail, Drive → `mcp__claude_ai_*` (서버사이드, 플랫폼 관리)
- Notion → `mcp__notion__*` (OAuth 기반, 세션별 인증)
- `~/.claude.json`의 mcpServers로는 OAuth 타입 추가 불가

### 5. OAuth 토큰은 머신별 격리
공유 Claude 구독 환경에서도 OAuth 토큰은 개인 계정/머신 단위. 다른 사람 컴퓨터에 영향 없음.

### 6. Admin 권한 없이도 가능
Internal Integration 생성에는 워크스페이스 관리자 권한 필요. OAuth 방식은 개인 Notion 계정만으로 동작하므로 관리자 권한 불필요.

## 관련
- CLAUDE.md Known Issues에 워크어라운드 기록됨
- Windows에서 URL 클립보드 복사: `echo -n "URL" | clip`
