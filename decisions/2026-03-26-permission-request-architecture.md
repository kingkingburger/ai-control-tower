# Arena 토론 결과: 권한신청 워크플로우 아키텍처 — hub polling vs webhook vs auth-server 올인

**일시**: 2026-03-26
**프리셋**: 8인
**라운드**: 15회

---

## 추천안

**auth-server 올인 (hub는 읽기전용 뷰)**

15라운드에 걸친 격렬한 토론 끝에 전원(7:0)이 auth-server 올인으로 수렴했다. 핵심 근거는 세 가지다. 첫째, 권한 신청/승인/발급의 전체 라이프사이클을 auth-server 단일 서비스가 소유하면 hub-auth 간 분산 트랜잭션이 원천 제거되고 변경 포인트가 1곳으로 수렴한다. 둘째, 이메일 발송을 fire-and-forget 비동기 처리하고 email_logs 테이블로 격리하면 SMTP 장애가 인증 서비스를 죽이는 시나리오를 차단할 수 있다. 셋째, hub는 2개 API 호출(내 권한 목록 + redirect URL)과 인라인 배너만 담당하므로 M1 5주 공수(~5.5일)로 충분히 수용 가능하다.

---

## 옵션 비교

### 옵션 A: hub polling (hub가 주기적으로 auth-server 상태 조회)
- **핵심**: hub가 cron/polling으로 auth-server의 권한 상태를 주기적으로 가져와 UI에 반영
- **장점**:
  - 단방향 의존(hub→auth)으로 구조가 단순
  - hub 기존 BullMQ/Redis 인프라 재사용 가능
  - auth-server 변경 최소화
- **리스크**:
  - polling 간격만큼 UX 지연 (상태 반영 블랙홀)
  - hub가 워크플로우 상태를 이중 관리하게 되어 동기화 실패 가능성
- **적합 조건**: auth-server 변경이 불가능하고 실시간성이 중요하지 않은 내부 관리 도구

### 옵션 B: webhook (auth-server가 hub에 이벤트 푸시)
- **핵심**: auth-server에서 상태 변경 시 webhook으로 hub에 알림, hub가 후속 처리
- **장점**:
  - 실시간 반영 가능 (polling 지연 없음)
  - 이벤트 기반으로 확장성 있음
- **리스크**:
  - webhook 실패 시 reconciliation 로직 필요 (결국 polling도 병행)
  - auth-server→hub 역방향 의존 추가
- **적합 조건**: 멀티서비스가 권한 이벤트를 구독해야 하는 이벤트 드리븐 아키텍처

### 옵션 C: auth-server 올인 (hub는 읽기전용 뷰)
- **핵심**: auth-server가 권한 신청/승인/이메일 발송/상태관리를 전부 소유. hub는 redirect URL로 옥토토(auth-server UI)에 보내고, 읽기전용 권한 뷰만 표시
- **장점**:
  - 변경 포인트 1곳 — 분산 트랜잭션 자체가 없음
  - 권한의 SSoT가 auth-server에 완전히 집중
  - hub-auth 간 연동 코드 제로 (API 2개만 호출)
- **리스크**:
  - auth-server 비대화 가능성 (이메일 인프라까지 포함)
  - SMTP 장애가 auth-server에 영향 줄 수 있음 (fire-and-forget + 비동기 큐로 완화)
- **적합 조건**: 권한 관련 모든 로직을 단일 서비스에서 관리하고, hub 변경을 최소화하려는 현재 상황

---

## 갈등 지도

| 쟁점 | 초기 입장 | 최종 결론 |
|------|----------|----------|
| hub polling vs webhook vs auth-server 올인 | polling(옹호자, 기술설계자) / webhook(비판자, 품질악마) / auth-server(비전가, 현실주의자) / 조건부(UX) | **전원 auth-server 올인 (7:0)** — R4~6에서 대세 전환, R7~9에서 옹호자 마지막 합류 |
| SMTP 장애가 인증 서비스를 죽이는 문제 | 품질악마: auth-server 올인의 치명적 결함 | **fire-and-forget 비동기 처리 + email_logs 테이블 격리로 해결** — 메인 스레드 동기 호출 절대 금지 |
| hub→옥토토 이동 방식 | (미정) | **auth-server가 redirect URL 생성 + 단기 JWT 토큰, hub에 인라인 배너** — returnUrl 화이트리스트 검증 필수 |
| hub의 역할 범위 | 옹호자: hub가 워크플로우 전체 소유 | **hub는 읽기전용 뷰만** — API 2개(내 권한 목록 + redirect URL), 캐시 TTL 5분, circuit breaker |
| service-to-service 인증 | (미정) | **M1은 shared API key, M2에서 HMAC/JWT 업그레이드** |
| feature flag 롤백 가능성 | (미정) | **feature flag로 권한 모듈 롤백 가능 필수** |
| M1 이메일 범위 | 비전가: 풀스펙 이메일 시스템 | **Nodemailer fire-and-forget + 템플릿 2종** — "이메일은 v2" 원칙에서 M1 최소 구현으로 합의 |

---

## 합의 사항

1. **auth-server가 권한 신청/승인/이메일 발송/상태관리를 전부 소유한다** — 전원 동의(7:0). hub는 읽기전용 뷰.
2. **hub는 API 2개만 호출한다** — 내 권한 목록 조회 + redirect URL 생성. 캐시 TTL 5분 + circuit breaker + shared API key 인증.
3. **이메일 발송은 메인 스레드에서 절대 동기 호출하지 않는다** — fire-and-forget 비동기 처리.
4. **email_logs 테이블 + status 컬럼 필수** — pending/sent/failed 상태 추적.
5. **Slack 실패 알림** — 이메일 발송 실패 시 즉시 Slack 채널에 알림.
6. **circuit breaker on hub→auth-server 호출** — auth-server 장애 시 hub가 연쇄 장애되지 않도록.
7. **returnUrl 화이트리스트 검증** — 오픈 리다이렉트 공격 차단.
8. **service-to-service 인증** — M1은 shared API key, M2에서 HMAC/JWT로 업그레이드.
9. **feature flag로 권한 모듈 롤백 가능** — 장애 시 즉시 비활성화.
10. **E2E 테스트 4종 필수** — 신청→승인→발급, webhook실패 재시도, TTL만료, 동시신청 race condition.

---

## M1 구현 명세

### DB 스키마 (auth-server)

```sql
-- 권한 신청 테이블
CREATE TABLE permission_requests (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_id  UUID NOT NULL,
  approver_id   UUID,
  resource_type VARCHAR(100) NOT NULL,
  resource_id   UUID NOT NULL,
  status        VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | approved | rejected | expired
  reason        TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at    TIMESTAMPTZ,
  CONSTRAINT uq_active_request UNIQUE (requester_id, resource_type, resource_id)
    WHERE status = 'pending'  -- partial unique index: 중복 신청 방지
);

-- 이메일 발송 로그
CREATE TABLE email_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id      UUID REFERENCES permission_requests(id),
  template_type   VARCHAR(50) NOT NULL,  -- approval_request | approval_complete
  recipient_email VARCHAR(255) NOT NULL,
  status          VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | sent | failed
  error_message   TEXT,
  retry_count     INT DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at         TIMESTAMPTZ
);
```

### API 엔드포인트 (auth-server)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/permissions/request` | 권한 신청 생성 | Bearer JWT (사용자) |
| POST | `/api/permissions/:id/approve` | 권한 승인 (원클릭 URL) | 단기 JWT 토큰 |
| POST | `/api/permissions/:id/reject` | 권한 거절 | 단기 JWT 토큰 |
| GET | `/api/permissions/my` | 내 권한 목록 조회 | Bearer JWT (사용자) |
| GET | `/api/permissions/pending` | 승인 대기 목록 (관리자) | Bearer JWT (관리자) |
| GET | `/api/service/redirect-url` | hub→옥토토 redirect URL 생성 | shared API key |

### hub 변경사항

hub 변경은 최소화한다. 구체적으로:

1. **인라인 배너 컴포넌트** — "권한 신청/관리는 옥토토에서" 배너 + redirect 버튼
2. **읽기전용 권한 뷰** — auth-server `/api/permissions/my` 호출 결과를 캐싱(TTL 5분)하여 표시
3. **API 호출 레이어** — 2개 API만 호출하는 얇은 클라이언트
   - circuit breaker: 5회 연속 실패 시 30초 open
   - shared API key: `X-Service-Key` 헤더
4. **feature flag** — `PERMISSION_MODULE_ENABLED` 환경변수로 전체 모듈 on/off

### 이메일 인프라 (auth-server)

1. **EmailService 클래스** — Nodemailer 래핑, auth-server 내부에 격리
2. **fire-and-forget 패턴** — 승인/거절 API 응답 후 비동기로 이메일 발송. 메인 스레드 블로킹 없음
3. **email_logs 테이블** — 모든 발송 시도를 pending/sent/failed로 기록
4. **Slack 실패 알림** — status=failed 시 Slack webhook으로 즉시 알림
5. **템플릿 2종**:
   - `approval_request`: 승인자에게 보내는 신청 알림 (원클릭 승인 URL 포함)
   - `approval_complete`: 신청자에게 보내는 승인/거절 결과 알림
6. **재시도**: 최대 3회, 지수 백오프 (1s → 2s → 4s)

### 비타협 조건 (전원 합의, 위반 시 릴리즈 블로커)

1. 이메일 발송은 메인 스레드에서 절대 동기 호출 금지 (fire-and-forget)
2. email_logs 테이블 + status 컬럼 필수
3. Slack 실패 알림
4. circuit breaker on hub→auth-server 호출
5. returnUrl 화이트리스트 검증
6. service-to-service 인증 (M1: shared API key)
7. feature flag로 권한 모듈 롤백 가능
8. E2E 테스트 4종: 신청→승인→발급 / webhook실패 재시도 / TTL만료 / 동시신청 race condition

### M1 공수 추정

| 작업 | 일수 |
|------|------|
| DB 스키마 + 마이그레이션 | 0.5일 |
| API 엔드포인트 6개 | 1.5일 |
| EmailService + 템플릿 2종 | 1일 |
| hub 인라인 배너 + 읽기전용 뷰 | 1일 |
| circuit breaker + shared API key | 0.5일 |
| E2E 테스트 4종 | 1일 |
| **합계** | **~5.5일** |

---

## 토론 요약 (라운드별 주요 전환점)

### Phase 1 — R0: 초기 입장 (3파전)
세 옵션이 격돌했다. 옹호자와 기술설계자는 hub polling(단방향, 심플)을, 비판자와 품질악마는 webhook(양방향이 아님, 실시간)을, 비전가와 현실주의자는 auth-server 올인(연동 코드 제로, 변경 포인트 1곳)을 주장. UX대변인은 auth-server 중심이되 조건부 입장.

### R1~3: 핵심 갈등 — 세 옵션 격돌
옹호자가 "polling은 단방향이라 심플"로 방어했으나, 비판자가 "polling은 UX 블랙홀"로 정면 반박. 비전가는 "auth-server에 다 넣으면 polling 자체가 불필요"로 근본 해법 제시. 품질악마가 최대 쟁점을 던짐: "auth-server 올인은 SMTP가 인증을 죽인다."

### R4~6: 대세 전환 — auth-server 올인으로 수렴
결정적 전환점. 비판자가 webhook을 철회하고 조건부 auth-server 올인으로 전향(조건: 장애격리, 스코프경계, 이메일v2 데드라인). 현실주의자가 "이메일은 v2, 비동기 fire-and-forget"으로 SMTP 문제의 현실적 해법 제시. 품질악마가 비동기 큐 해법을 수용하며 조건 3개 제시. 비전가+품질악마+현실주의자 3인 합의 도출.

### R7~9: 전원 수렴 (7:0)
옹호자가 마지막 반격: "6:1이라고 틀린 게 아니다." 그러나 결국 조건부 전향. 옹호자의 조건: circuit breaker, health check polling 레이어, M1 스코프 잠금. 이로써 전원 auth-server 올인 합의 완성.

### R10~12: 세부 아키텍처 확정
구체적 구현 명세 합의. hub→옥토토 이동(redirect URL + 단기 JWT), M1 이메일(Nodemailer fire-and-forget + EmailService 격리 + email_logs + Slack 알림 + 템플릿 2종), hub 최소 역할(API 2개 + 캐시 TTL 5분 + circuit breaker + shared API key), M1 공수(~5.5일).

### R13~15: 비타협 조건 확정 및 최종 정리
8개 비타협 조건 전원 합의. E2E 테스트 4종 확정. M1→M2→M3 로드맵 정리.

---

## 다음 단계 (M1 → M2 → M3)

### M1 (5주 내): 최소 동작 구현
1. auth-server에 permission_requests + email_logs 테이블 생성
2. API 6개 구현 (신청/승인/거절/내 목록/대기 목록/redirect URL)
3. EmailService 클래스 + Nodemailer fire-and-forget + 템플릿 2종
4. hub 인라인 배너 + 읽기전용 권한 뷰 (API 2개 호출)
5. circuit breaker + shared API key + feature flag 조합
6. E2E 테스트 4종
7. Slack 실패 알림 연동

### M2: 안정화 및 고도화
1. shared API key → HMAC/JWT service-to-service 인증 업그레이드
2. 이메일 템플릿 확장 (다국어, 커스텀 브랜딩)
3. email_logs 데이터 기반 outbox 패턴 도입 여부 판단
4. 인앱 노티피케이션 추가 (이메일 보완)
5. 권한 신청 대시보드 (관리자용 통계)

### M3: 멀티서비스 확장
1. auth-server 권한 API를 다른 서비스에서도 호출 가능하도록 공개
2. 이벤트 기반 구독 모델 검토 (webhook/SSE)
3. 감사 로그(audit trail) 정식 도입
4. RBAC → ABAC 확장 검토
