# Octoto 에이전트 규칙 후보

여기의 규칙은 후보일 뿐이다. 반복되고, 팀에 안전하며, 협업자에게 분명히
유익할 때만 Octoto 공유 문서로 승격한다.

## Candidates

- 프로젝트별 세션 메모리는 Octoto 안의 명시된 메모리 문서에 둔다.
- 세션 종료 때 대상 저장소 작업을 먼저 정리한 뒤, 프로젝트 메모리를 갱신한다.
- 위험하거나 선호가 중요한 결정에는 가능한 경우 구조화 질문을 사용한다. 사용할
  수 없으면 짧은 일반 질문 하나로 대체한다.
- 모든 세션 종료를 메모리 복리 단계로 취급한다. 배운 점과 하네스 증강 후보를
  기록한다.
- 하네스가 작성하는 문서, 개인 메모, 세션 종료 기록은 기본 한국어로 작성한다.
- 여러 프로젝트에 반복 적용할 수 있는 운영 규칙만 `ai-control-tower/harness/core`
  로 승격한다.
- 세션 종료 요청을 받으면 사용자가 따로 묻지 않아도 배운 점, 사용자 정정, 실패한
  가정, 검증 결과, 하네스 증강 후보를 자동으로 탐색해 프로젝트 메모리와 개인
  하네스 후보에 누적한다.
- 코드를 분리하거나 새 helper/reducer를 만들 때는 "무엇을 하는지"뿐 아니라
  "왜 이 경계로 뺐는지"와 "어떤 회귀를 막는지"를 코드 가까운 주석이나 문서에
  남긴다. 단순 구현 설명은 피하고, 정책 경계·race 방지·저장 payload와 화면 상태
  불일치처럼 다음 작업자가 배워야 하는 이유를 우선 기록한다.
- `user_role_group_join` 또는 `user_service_access`처럼 권한 membership을 바꾸는
  프론트엔드 mutation을 수정할 때는 API별로 보지 말고 같은 DB source를 읽는 Query
  cache fan-out을 먼저 확인한다. Octoto의 대표 대상은 `user-role-matrix`,
  `user-role-groups/matrix`, `user-roles`, `role-group-users`, `role-groups`,
  `role-group`, `service-members`이다.
- bulk 권한 mutation이 200을 반환해도 `summary.assigned`/`summary.unassigned`가
  0이면 성공으로 안내하지 않는다. 실제 변경 0건은 선택 service나 대상 조인 불일치
  가능성이 있으므로 경고 또는 변경 없음으로 드러내고 회귀 테스트에 포함한다.
