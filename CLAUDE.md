# AI Control Tower

AI 관련 실험을 위한 작업 공간. 유저 환경에 적용하기 전에 여기서 먼저 테스트한다.

## 용도
- AI 도구/플러그인/스킬 실험
- 새로운 워크플로우 프로토타이핑
- 설정 변경 전 사전 검증
- 의사결정 시뮬레이션 (Agent Arena) 및 decisions/ 기록

## Known Issues
- Notion 플러그인 MCP 충돌: Claude AI 내장 통합과 플러그인이 동일한 "notion" 서버를 등록하여 스킵됨. 플러그인의 `.mcp.json`을 비워서 해결. 업데이트 시 재발 가능.
