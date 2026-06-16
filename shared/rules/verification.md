# 검증 정책

## 기준

파일이 존재한다는 이유만으로 완료를 보고하지 않는다. 변경 위험도와 표면적에
맞는 집중 검증을 실행한다.

## 선택 기준

- 문서만 변경: 생성 파일을 직접 확인하고, 가능한 markdown 또는 저장소 검사를
  실행한다.
- 백엔드 변경: lint와 관련 테스트를 실행한다.
- 프론트엔드 변경: 단위 테스트, typecheck, 레이아웃/모달/overlay/라우팅/z-index
  변경 시 브라우저 검증을 실행한다.
- 프론트엔드 mutation이 서버 상태를 바꾸면 같은 도메인 데이터를 읽는 모든 Query
  cache key를 찾는다. 화면이나 API가 달라도 같은 DB row, 같은 membership, 같은
  permission state를 바라보면 mutation 성공 처리에서 함께 invalidate한다.
- bulk mutation이 `assigned`, `unassigned`, `skipped` 같은 summary를 반환하면 HTTP
  200만 성공으로 보지 않는다. 실제 변경 건수가 0이면 성공 안내 대신 변경 없음이나
  대상 불일치를 드러내고, 이 케이스를 테스트로 고정한다.
- 스크립트 변경: 스크립트 또는 대표 dry-run 경로를 실행한다.
- 스킬 변경: 생성하거나 크게 수정한 경우 스킬 validator를 실행한다.

## 보고

무엇을 실행했는지 정확히 적는다. 검증하지 못했다면 이유와 남은 위험을 적는다.
