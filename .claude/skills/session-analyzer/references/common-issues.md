# 흔한 문제와 문제 해결

Claude Code 세션을 분석할 때 알려진 문제와 진단 방법.

---

## 세션 파일 문제

### 문제: 디버그 로그를 찾을 수 없음

**증상**: `~/.claude/debug/{sessionId}.txt`가 존재하지 않음

**가능한 원인**:
1. 세션이 너무 오래되어 디버그 로그가 정리됨
2. 디버그 로깅이 비활성화됨
3. 세션 ID가 잘못됨

**우회 방법**:
- 제한적 분석에는 메인 세션 로그(`.jsonl`)를 사용
- 메인 로그에는 도구 호출은 있지만 상세 훅 실행 정보는 없음

### 문제: 큰 디버그 로그(>50MB)

**증상**: 로그 파일이 너무 커서 전체를 읽기 어려움

**해결책**:
- 전체 파일을 읽지 말고 특정 패턴으로 `grep` 사용
- 최근 항목은 `tail`로 확인
- Read 도구로 읽을 때는 `offset`과 `limit` 사용

---

## SubAgent 분석 문제

### 문제: SubAgent가 기록되지 않음

**증상**: 예상한 SubAgent 호출이 로그에 없음

**가능한 원인**:
1. SubAgent가 실제로 호출되지 않음
2. SubAgent 타입 이름이 예상과 다름(대소문자 구분)
3. 로그가 잘림

**진단**:
```bash
# 고유 SubAgent 타입 모두 나열
grep "SubagentStart with query:" debug.txt | sed 's/.*query: //' | sort | uniq
```

### 문제: SubAgent 결과 누락

**증상**: `SubagentStart`는 있지만 `SubagentStop`이 없음

**가능한 원인**:
1. SubAgent가 아직 실행 중임(백그라운드 작업)
2. SubAgent가 crash됨
3. SubAgent 완료 전에 세션이 끝남

**진단**:
```bash
# 시작/종료 개수 비교
grep -c "SubagentStart" debug.txt
grep -c "SubagentStop" debug.txt
```

---

## 훅 분석 문제

### 문제: 훅이 트리거되지 않음

**증상**: `Getting matching hook commands` 항목에서 예상 훅을 찾을 수 없음

**가능한 원인**:
1. matcher 패턴이 도구 이름과 맞지 않음
2. 훅이 등록되지 않음(스킬이 로드되지 않음)
3. 훅의 이벤트 타입이 잘못됨

**진단**:
```bash
# 스킬 훅 등록 여부 확인
grep "Registered.*hooks from skill" debug.txt

# 어떤 훅이 조회되는지 확인
grep "Getting matching hook commands for" debug.txt | head -20
```

### 문제: 훅은 트리거됐지만 효과가 없음

**증상**: 훅이 매칭됐지만(count > 0) 예상 동작이 발생하지 않음

**가능한 원인**:
1. 훅 스크립트가 오류를 반환함
2. `deny`를 반환해야 하는 상황에서 훅이 `allow`를 반환함
3. 프롬프트 훅 조건이 충족되지 않음

**진단**:
```bash
# 훅 실행 결과 확인
grep -A5 "Matched.*unique hooks" debug.txt | grep -E "permissionDecision|ok"
```

### 문제: 프롬프트 훅이 항상 false를 반환함

**증상**: `Prompt hook condition was not met`가 계속 발생함

**가능한 원인**:
1. 프롬프트가 너무 모호해 모델이 이해하지 못함
2. 컨텍스트에 필요한 정보가 없음
3. 모델이 기준을 잘못 해석함

**진단**:
```bash
# 전체 모델 응답 확인
grep -A20 "Hooks: Model response:" debug.txt
```

---

## 산출물 문제

### 문제: 파일이 생성되지 않음

**증상**: 예상 산출물 파일이 `written atomically` 로그에 없음

**가능한 원인**:
1. Write가 PreToolUse 훅에 의해 차단됨
2. 경로가 잘못됨
3. Write 도구가 호출되지 않음

**진단**:
```bash
# Write 시도 여부 확인
grep "executePreToolHooks called for tool: Write" debug.txt

# 권한 결정 확인
grep -A10 "executePreToolHooks called for tool: Write" debug.txt | grep "permissionDecision"
```

### 문제: 삭제되어야 할 파일이 남아 있음

**증상**: 세션 종료 후에도 draft 파일이 남아 있음

**가능한 원인**:
1. Bash `rm` 명령이 실행되지 않음
2. 정리 단계 전에 스킬이 종료됨
3. `rm` 명령의 파일 경로가 잘못됨

**진단**:
```bash
# rm 명령 확인
grep "Bash" debug.txt | grep -i "rm"
```

---

## reviewer 전용 문제

### 문제: reviewer가 OKAY를 반환하지 않음

**증상**: REJECT 응답이 여러 번 나오고 OKAY가 없음

**가능한 원인**:
1. 계획에 실제 문제가 있고 아직 고쳐지지 않음
2. reviewer 기준이 너무 엄격함
3. 계획 수정이 reviewer 피드백을 반영하지 못함

**진단**:
```bash
# reviewer 응답 전체 추출
grep -B2 -A10 "Hooks: Model response:" debug.txt | grep -E '"ok"|"reason"'
```

### 문제: reviewer는 호출됐지만 훅 결과가 없음

**증상**: `SubagentStart with query: reviewer`는 있지만 `Prompt hook condition` 결과가 없음

**가능한 원인**:
1. reviewer SubAgent에 Stop 훅이 설정되지 않음
2. SubagentStop으로 훅 변환이 실패함
3. reviewer가 아직 실행 중임

**진단**:
```bash
# Stop 훅 변환 여부 확인
grep "Converting Stop hook to SubagentStop for agent 'reviewer'" debug.txt
```

---

## 타이밍 문제

### 문제: 이벤트 순서가 맞지 않음

**증상**: timeline이 말이 되지 않음(예: Start보다 Stop이 먼저 나옴)

**가능한 원인**:
1. 병렬 작업(의도된 동작)
2. 서로 다른 세션의 로그 항목이 섞임
3. 시계 동기화 문제

**해결책**:
- 같은 시간대에 여러 세션이 있으면 세션 ID로 필터링
- 전체 순서보다 특정 작업 sequence를 확인

### 문제: 큰 시간 간격

**증상**: 작업 사이에 긴 대기 시간이 있음

**가능한 원인**:
1. 사용자 상호작용(AskUserQuestion 대기)
2. API rate limiting
3. 모델 사고 시간

**진단**:
```bash
# 30초 초과 간격 찾기
awk -F'T|Z' '{print $2}' debug.txt | sort | uniq -c | sort -rn | head
```

---

## 분석 스크립트 문제

### 문제: 스크립트가 빈 JSON을 반환함

**증상**: 스크립트가 `{ "summary": { "total": 0 } }`을 반환함

**가능한 원인**:
1. 디버그 로그 경로가 잘못됨
2. 로그 형식이 변경됨
3. 이 세션에 매칭 이벤트가 없음

**해결책**:
- 디버그 로그 경로가 존재하고 내용이 있는지 확인
- 예상 패턴을 직접 grep해서 형식 확인

### 문제: 스크립트 권한 거부

**증상**: 스크립트 실행 시 `Permission denied` 발생

**해결책**:
```bash
chmod +x scripts/*.sh
```

---

## 검증 체크리스트

분석 결과가 이상해 보이면 다음을 확인한다.

1. **올바른 세션 ID**: UUID를 다시 확인
2. **파일 존재 여부**: 먼저 `find-session-files.sh` 실행
3. **스킬 로드 여부**: "Registered.*hooks from skill" 확인
4. **올바른 시간 범위**: timestamp가 예상 세션 시간과 맞는지 확인
5. **완료된 세션 여부**: 세션이 정상 종료됐는지 확인(중단 아님)
