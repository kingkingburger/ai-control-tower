# TIL: Slack API 한글 이름 검색 실패

**날짜**: 2026-03-26

## 문제

Slack MCP의 `slack_search_public_and_private`에서 `from:정현석` 같은 한글 display name 기반 검색이 동작하지 않음. 결과가 0건으로 나옴.

## 해결

1. `slack_search_users`로 한글 이름 → user ID 조회 (정현석 → `U0A78E0QBFU`)
2. `from:<@U0A78E0QBFU>` 형태로 user ID 기반 검색

## 검색 전략 패턴

```
한글 이름 검색 시도 → 실패
  ↓
slack_search_users로 user ID 조회
  ↓
from:<@USER_ID>로 재검색 → 성공
```

## 추가 학습

- 키워드 검색도 한글/영어 혼용 시 AND 조건으로 동작하므로, 너무 많은 키워드를 넣으면 결과가 줄어듦
- 검색 실패 시 같은 방법을 반복하지 말고 검색 축을 전환하는 것이 핵심 (이름 → ID, 키워드 변경, 채널 필터 추가/제거 등)
