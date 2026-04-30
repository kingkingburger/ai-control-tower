# Octoto Service Scope Cascade Rules

## Trigger

Use this checklist when changing any of these surfaces:

- `services.code`
- `role_groups.service_code`
- `role_group_service_visibility.service_code`
- `user_service_access.service_code`
- `role_group_service_access.service_code`
- `service_menus.service_code`
- service-scoped RoleGroup, department RoleGroup, Knox department sync

## Rules

- Do not rely only on database cascade behavior. Check both `updateService()` and `deleteService()` in `src/domains/service/service.service.ts`.
- For service deletion, explicitly account for service-scoped RoleGroups, `role_group_service_visibility`, `user_role_group_join`, `user_service_access`, `role_group_service_access`, `auth_requests`, `service_menus`, and `actions`.
- For service code changes, ensure FK constraints that should follow `services.code` use `ON UPDATE cascade`. `role_group_service_visibility.service_code` must stay cascade-on-update.
- Service code changes must invalidate users with direct `user_service_access` for the old code and users in affected RoleGroups.
- Add or update regression tests when this area changes:
  - `tests/unit/service.service.test.ts`
  - `tests/unit/service-code-cascade.test.ts`

## Minimum Verification

- `bun test tests/unit/service.service.test.ts tests/unit/service-code-cascade.test.ts`
- `bunx biome check src/domains/service/service.service.ts src/db/schema.ts`
