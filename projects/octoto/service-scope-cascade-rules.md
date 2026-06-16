# Octoto 서비스 범위 cascade 규칙

## 트리거

다음 표면을 변경할 때 이 checklist를 사용한다.

- `services.code`
- `role_groups.service_code`
- `role_group_service_visibility.service_code`
- `user_service_access.service_code`
- `role_group_service_access.service_code`
- `service_menus.service_code`
- service-scoped RoleGroup, department RoleGroup, Knox department sync 확인

## 규칙

- database cascade 동작에만 의존하지 않는다. `src/domains/service/service.service.ts`의 `updateService()`와 `deleteService()`를 모두 확인한다.
- service 삭제 시 service-scoped RoleGroups, `role_group_service_visibility`, `user_role_group_join`, `user_service_access`, `role_group_service_access`, `auth_requests`, `service_menus`, `actions`를 명시적으로 고려한다.
- service code 변경 시 `services.code`를 따라가야 하는 FK constraint가 `ON UPDATE cascade`를 쓰는지 확인한다. `role_group_service_visibility.service_code`는 cascade-on-update 상태를 유지해야 한다.
- service code 변경은 예전 code의 직접 `user_service_access`를 가진 사용자와 영향받은 RoleGroups의 사용자를 invalidation해야 한다.
- 이 영역이 바뀌면 regression test를 추가하거나 갱신한다.
  - `tests/unit/service.service.test.ts`
  - `tests/unit/service-code-cascade.test.ts`

## 최소 검증

- `bun test tests/unit/service.service.test.ts tests/unit/service-code-cascade.test.ts`
- `bunx biome check src/domains/service/service.service.ts src/db/schema.ts`
