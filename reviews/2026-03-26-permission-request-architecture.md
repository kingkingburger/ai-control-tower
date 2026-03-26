# Expert Review 결과: 권한신청 워크플로우 아키텍처

**일시**: 2026-03-26
**리뷰어**: 5명 (시니어 아키텍트, 보안 엔지니어, DevOps/SRE, 시니어 PM, 테크 리드)
**대상 파일**: `decisions/2026-03-26-permission-request-architecture.md`

---

## 종합 등급

| 리뷰어 | 등급 | 한 줄 평가 |
|---------|------|------------|
| 시니어 아키텍트 | B+ | SSoT와 장애 격리 설계는 우수하나 DDL 문법 오류와 도메인 분리 기준 부재 |
| 보안 엔지니어 | C | 인증/인가 구조에 심각한 취약점 다수, shared API key와 JWT 설계 재작업 필요 |
| DevOps/SRE | B | 격리 설계와 feature flag 조합은 좋으나 폐쇄망 시나리오와 운영 관측성 부재 |
| 시니어 PM | B | 스코프 통제력은 있으나 성공 지표와 핵심 유저 시나리오 누락 |
| 테크 리드 | B | 분산 트랜잭션 제거 판단은 적절하나 일정 과소 산정과 기술 PoC 미검증 |

**평균 등급**: B (보안 영역의 C 등급이 전체를 끌어내림 — 보안 이슈 해결 전 착수 불가)

---

## 공통 평가

### 강점
1. **SSoT(Single Source of Truth) 원칙 일관 적용** — 아키텍트·보안 모두 권한 상승 경로 차단과 데이터 정합성 측면에서 긍정 평가
2. **장애 격리 설계(fire-and-forget)** — 알림 실패가 핵심 워크플로우에 영향 없음. 아키텍트·DevOps·테크 리드 3명 공통 인정
3. **분산 트랜잭션 제거** — 테크 리드·아키텍트 모두 복잡도 감소 판단에 동의
4. **hub 변경 최소화** — 기존 시스템 안정성 보존. 아키텍트·PM 긍정 평가
5. **feature flag + circuit breaker 조합** — 점진적 롤아웃과 장애 대응의 이중 안전장치. DevOps·테크 리드 인정

### 문제점
1. **보안 설계 근본적 결함** — shared API key 평문 전송, JWT 1회 사용 제한 없음 (보안·아키텍트)
2. **일정 과소 산정** — 5.5일 추정에 QA·배포·코드리뷰·E2E 인프라 미포함. 실제 7~9일 (PM·테크 리드)
3. **운영 관측성 부재** — circuit breaker 설정 근거 없음, 모니터링/알람 임계치 없음, 감사 로그 불충분 (DevOps·아키텍트·보안)
4. **expires_at 만료 처리 메커니즘 없음** — 만료된 신청 건의 상태 전이 방식 미정의 (아키텍트·테크 리드)
5. **폐쇄망/SMTP 불가 시나리오 대응 없음** — 고객사 환경 다양성 미고려 (DevOps)
6. **성공 지표(KPI) 전무** — 무엇을 기준으로 성공/실패를 판단하는지 없음 (PM)

---

## 우선순위 개선 목록

### 즉시 수정 (Critical)

| # | 개선 사항 | 제안자 | 구체적 수정안 |
|---|----------|--------|-------------|
| C1 | shared API key 평문 전송 → 인증 강화 | 보안 엔지니어 | HMAC 서명 방식으로 전환. `timestamp + nonce + HMAC-SHA256(secret, payload)` 헤더 구성. 키는 환경변수로 주입하고 Vault 연동 권장 |
| C2 | 원클릭 승인 JWT 탈취 가능 | 보안 엔지니어 | ① 승인자 이메일을 JWT claim에 바인딩 ② `jti` claim으로 1회 사용 보장 (사용된 jti는 Redis/DB에 기록) ③ TTL 15분으로 단축 ④ 승인 시 로그인 세션 검증 추가 |
| C3 | 폐쇄망 SMTP 불가 시나리오 | DevOps/SRE | ① 1차: 내부 SMTP 릴레이 서버 경유 옵션 추가 ② 2차: 인앱 알림 stub을 M1에 포함하여 이메일 불가 시 폴백 경로 확보 ③ notification 채널을 인터페이스로 추상화 |
| C4 | 성공 지표(KPI) 전무 | 시니어 PM | M1 KPI 정의: ① 신청→승인 평균 리드타임 ② 이메일 도달률(≥95%) ③ 승인자 응답률 ④ 시스템 에러율(<1%) |
| C5 | partial unique index DDL 문법 오류 | 시니어 아키텍트 | Drizzle ORM의 partial index 지원 여부 확인 후, 미지원 시 raw SQL 마이그레이션으로 `CREATE UNIQUE INDEX ... WHERE status = 'pending'` 작성 |

### 권장 수정 (Important)

| # | 개선 사항 | 제안자 | 구체적 수정안 |
|---|----------|--------|-------------|
| I1 | 일정 재산정 (5.5일 → 8일) | PM, 테크 리드 | 핵심 구현 5.5일 + QA 1일 + 코드리뷰/수정 0.5일 + 배포/검증 0.5일 + E2E 인프라 셋업 0.5일 = **최소 8일**. PoC 실패 시 9일 |
| I2 | Nodemailer + Bun PoC | 테크 리드 | 착수 전 1일 내 PoC: Bun에서 Nodemailer SMTP 송신 + 한글 인코딩. 실패 시 Resend API 전환 |
| I3 | circuit breaker 설정값 근거 | DevOps, 테크 리드 | opossum 채택. timeout: 5000ms, errorThresholdPercentage: 50, resetTimeout: 30000ms |
| I4 | 이메일 피싱/폭탄 방어 | 보안 엔지니어 | DKIM/SPF/DMARC 설정 + 동일 resource 신청 rate limiting (24시간/3회) |
| I5 | 감사 로그 M1 포함 | 아키텍트, 보안 | audit_logs 테이블: actor_id, action, resource, ip_address, user_agent, metadata(jsonb), created_at |
| I6 | notification 도메인 분리 기준 | 시니어 아키텍트 | 권한신청 → notification 단방향 의존. 분리 트리거: 채널 3개 이상 or TPS 100 이상 |
| I7 | expires_at 만료 처리 | 아키텍트, 테크 리드 | cron 1시간 주기로 pending + expires_at < now() → expired 전이 + 신청자 알림 |
| I8 | 핵심 유저 시나리오 보완 | 시니어 PM | Knox 최초 신청, 승인자 부재/위임, 다단계 승인(AND/OR) 시나리오 정의 |
| I9 | API key 로테이션 SOP | 시니어 아키텍트 | dual-key 24시간 → 구 키 폐기. 분기 1회 정기 로테이션 |

### 선택 개선 (Nice-to-have)

| # | 개선 사항 | 제안자 | 구체적 수정안 |
|---|----------|--------|-------------|
| N1 | optimistic locking | 아키텍트 | version 컬럼 추가, 충돌 시 409 응답 |
| N2 | circuit breaker open 시 hub UX | 아키텍트 | "알림 지연 중" 배너 표시 |
| N3 | dead letter queue + 수동 재처리 | DevOps | dead_letter_queue 테이블 + 관리자 재처리 버튼 |
| N4 | feature flag 런타임 토글 | DevOps | 환경변수 기반, 재배포 불필요 |
| N5 | 이메일 XSS 방어 | 보안 | 템플릿 auto-escape 활성화 |
| N6 | resource_id 존재 검증 | 보안 | 신청 시 hub API로 리소스 존재 확인 |
| N7 | recipient_email 암호화 | 보안 | AES-256 암호화 저장, Vault 키 관리 |
| N8 | 구조화 로그 표준 | DevOps | JSON 포맷 + traceId |
| N9 | DB 마이그레이션 롤백 | DevOps, 테크 리드 | up/down 스크립트 + 롤백 SOP |
| N10 | email_logs 보존 정책 | DevOps, PM | 90일 보존 후 아카이브 |
| N11 | 모바일 반응형 이메일 | PM | M2 이후 |
| N12 | pending 적체 모니터링 | 테크 리드 | 24시간 초과 시 Slack 알림 |
| N13 | 에러 코드 체계 | 테크 리드 | PERM_001~099 |
| N14 | 고객사 커스터마이즈 경계 | PM | 허용/불허 항목 문서화 |
| N15 | 부하 테스트 | DevOps | 동시 100건/분, k6 |

---

## 충돌 해소

| 쟁점 | 의견 A | 의견 B | 종합 판단 | 근거 |
|------|--------|--------|-----------|------|
| 일정 산정 | 테크 리드: 7~8일 | PM: 8~9일 | **8일** (PoC 실패 시 9일) | PM 관점이 현실적. QA/배포/코드리뷰 포함 필수 |
| 감사 로그 시점 | 아키텍트: M1 포함 | (암묵적 M1 외) | **M1 포함** | 보안 엔지니어도 동의. 권한 기능에서 감사 로그는 보안 요구사항 |
| API 인증 방식 | 아키텍트: shared key + 로테이션 | 보안: HMAC 서명 | **HMAC 서명** | 키 자체를 전송하지 않으므로 근본적으로 안전. 구현 +1일 미만 |
| 알림 실패 대응 | DevOps: 인앱 stub M1 포함 | 아키텍트: M2에서 채널 확장 | **M1에 인터페이스 추상화 + 이메일만. 인앱 stub은 M1.5** | 완전한 인앱은 스코프 초과. 인터페이스 먼저 정의 |
| CB 설정 접근 | DevOps: 운영 데이터 기반 | 테크 리드: 라이브러리 선정 우선 | **opossum + 보수적 초기값 → 2주 운영 후 튜닝** | 둘 다 필요 |

---

## 빠진 관점 종합

1. **JWT 키 관리 전략** — 서명 키 생성·저장·로테이션·폐기 라이프사이클 없음 (보안)
2. **DB 마이그레이션 전략** — up/down 스크립트, 제로 다운타임 마이그레이션 미정의 (DevOps, 테크 리드)
3. **에러 핸들링 표준** — 에러 코드 체계, 클라이언트 vs 서버 메시지 분리 없음 (테크 리드)
4. **로그 포맷 및 관측성** — 구조화 로그, trace ID, 메트릭 수집 전반 부재 (DevOps)
5. **배포 순서 및 호환성** — DB → 서비스 → hub 순서와 롤백 시나리오 미정의 (DevOps)
6. **데이터 보존 정책** — email_logs, audit_logs TTL 및 개인정보 법적 요구사항 미고려 (PM, DevOps)
7. **모바일 접근성** — 승인 이메일 모바일 반응형 대응 없음 (PM)
8. **pending 적체 가시성** — 방치된 신청 건 감지/에스컬레이션 메커니즘 없음 (테크 리드)

---

## 액션 아이템

**Critical (M1 착수 전 반드시 해결)**
- [ ] (C1) shared API key → HMAC 서명 전환, Vault/환경변수 키 관리
- [ ] (C2) 원클릭 승인 JWT: 승인자 바인딩 + jti 1회 사용 + TTL 15분
- [ ] (C3) notification 채널 인터페이스 추상화 + 폐쇄망 대응 문서화
- [ ] (C4) M1 성공 지표 4개 정의
- [ ] (C5) Drizzle partial index 지원 확인 + DDL 검증

**Important (M1 구현 중 병행)**
- [ ] (I1) 일정 8일로 재산정
- [ ] (I2) Nodemailer + Bun PoC (Day 1)
- [ ] (I3) opossum circuit breaker 설정값 문서화
- [ ] (I4) DKIM/SPF/DMARC + rate limiting
- [ ] (I5) audit_logs 테이블 M1 스코프 포함
- [ ] (I6) notification 도메인 분리 기준 문서화
- [ ] (I7) expires_at 만료 cron 구현
- [ ] (I8) Knox 최초 신청 + 승인자 부재 시나리오 정의
- [ ] (I9) API key 로테이션 SOP

**Nice-to-have (M1 이후)**
- [ ] (N1~N15) 위 선택 개선 목록 참조

---

## 개별 리뷰 전문

<details>
<summary>시니어 아키텍트의 리뷰 (등급: B+)</summary>

- SSoT 원칙 관철, 장애 격리 다층 설계, hub 변경 최소화, 의사결정 과정 투명성 우수
- partial unique index DDL 문법 오류 수정 필요
- notification 도메인 분리 기준을 M1에서 정의해야 함
- expires_at 만료 처리 메커니즘, shared API key 로테이션 절차 추가 필요
- 빠진: 감사 로그 M1 포함, 동시성 제어 방식, circuit breaker open 시 hub UX

</details>

<details>
<summary>보안 엔지니어의 리뷰 (등급: C)</summary>

- shared API key = 평문 패스워드 → HMAC 서명 필수
- 원클릭 승인 JWT 탈취 가능 → 승인자 바인딩 + 1회 사용 + 15분 TTL
- 이메일 피싱 공격 표면 → DKIM/SPF/DMARC
- 신청 반복 이메일 폭탄 → rate limiting + 쿨다운
- 빠진: 이메일 XSS, JWT 키 관리, PII 암호화, Knox 토큰 체이닝

</details>

<details>
<summary>DevOps/SRE의 리뷰 (등급: B)</summary>

- 폐쇄망 SMTP 불가 시나리오 전혀 없음 → 내부 릴레이 or 인앱 stub
- circuit breaker 설정값 근거 없음 → opossum + 보수적 초기값
- 이메일 실패율 집계/알람 임계치 필요
- feature flag 런타임 토글 vs 재배포 명확히
- 빠진: 로그 포맷, DB 마이그레이션 롤백, email_logs TTL, 배포 순서, 부하 테스트

</details>

<details>
<summary>시니어 PM의 리뷰 (등급: B)</summary>

- 성공 지표(KPI) 전혀 없음 → 4개 KPI 정의 필요
- 유저 시나리오 누락: Knox 최초 신청, 승인자 부재/위임, 재신청
- 고객사별 커스터마이즈 스코프 경계 미명시
- 5.5일에 QA/배포/코드리뷰 미포함 → 실제 8~9일
- 빠진: 모바일 접근성, 다국어, 데이터 보존 정책

</details>

<details>
<summary>테크 리드의 리뷰 (등급: B)</summary>

- 5.5일 과소 산정 → 7~8일. Nodemailer+Bun PoC 필수
- Drizzle partial index 지원 확인 필요
- circuit breaker 라이브러리 미명시 → opossum or 자체 구현
- E2E 테스트 인프라 셋업 미산정
- 빠진: DB 마이그레이션 전략, 에러 핸들링 표준, pending 적체 모니터링

</details>
