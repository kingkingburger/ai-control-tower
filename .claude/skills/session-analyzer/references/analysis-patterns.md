# Session Analyzer 분석 패턴

Claude Code 디버그 로그에서 정보를 추출할 때 쓰는 상세 grep/search 패턴.

---

## 디버그 로그 구조

디버그 로그는 `~/.claude/debug/{sessionId}.txt`에 있으며 timestamp가 붙은 항목을 포함한다.

```
2026-01-13T09:39:26.905Z [DEBUG] {message}
```

---

## SubAgent 패턴

### SubAgent 시작
```bash
# 패턴
grep "SubagentStart with query:" debug.txt

# 예시 출력
2026-01-13T09:39:26.905Z [DEBUG] Getting matching hook commands for SubagentStart with query: Explore
```

### SubAgent 종료
```bash
# 패턴
grep "SubagentStop with query:" debug.txt

# agent ID 포함(세션 추적)
grep "agent_id.*agent_transcript_path" debug.txt
```

### SubAgent 세션 등록
```bash
# 패턴 - SubAgent용 훅이 등록되는 시점을 보여준다
grep "Registered.*frontmatter hook.*from agent" debug.txt

# 예시
2026-01-13T09:43:08.203Z [DEBUG] Registered 1 frontmatter hook(s) from agent 'gap-analyzer' for session a373157
```

---

## 훅 패턴

### PreToolUse 훅 트리거
```bash
# 패턴
grep "executePreToolHooks called for tool:" debug.txt

# 예시
2026-01-13T09:39:40.000Z [DEBUG] executePreToolHooks called for tool: Write
```

### 훅 matcher 확인
```bash
# 패턴
grep "Getting matching hook commands for PreToolUse with query:" debug.txt

# 매칭 개수 포함
grep "Matched.*unique hooks for query" debug.txt

# 예시
2026-01-13T09:39:40.000Z [DEBUG] Matched 1 unique hooks for query "Write" (1 before deduplication)
```

### 훅 권한 결정
```bash
# 패턴
grep "permissionDecision" debug.txt

# 예시(allow)
"permissionDecision": "allow"

# 예시(deny)
"permissionDecision": "deny"
```

### 프롬프트 기반 훅 처리
```bash
# 패턴 - 훅 처리 중
grep "Hooks: Processing prompt hook with prompt:" debug.txt

# 패턴 - 모델 응답
grep "Hooks: Model response:" debug.txt

# 패턴 - 조건 결과
grep "Prompt hook condition was" debug.txt

# 예시(충족)
2026-01-13T09:48:09.076Z [DEBUG] Hooks: Prompt hook condition was met

# 예시(미충족)
2026-01-13T09:45:59.297Z [DEBUG] Hooks: Prompt hook condition was not met: REJECT - ...
```

### Stop 훅 이벤트
```bash
# 패턴
grep "Getting matching hook commands for Stop" debug.txt
```

### SubagentStop 훅 이벤트
```bash
# 패턴 - Stop에서 SubagentStop으로 변환됨
grep "Converting Stop hook to SubagentStop" debug.txt

# 예시
2026-01-13T09:43:08.202Z [DEBUG] Converting Stop hook to SubagentStop for agent 'gap-analyzer'
```

---

## 도구 사용 패턴

### 도구 실행
```bash
# 패턴
grep "executePreToolHooks called for tool:" debug.txt
```

### 파일 쓰기 작업
```bash
# 패턴 - 파일 생성/수정
grep "FileHistory: Tracked file modification for" debug.txt

# 패턴 - atomic write
grep "File.*written atomically" debug.txt

# 예시
2026-01-13T09:39:40.036Z [DEBUG] File /path/to/file.md written atomically
```

### Bash 명령 실행
```bash
# 패턴 - Bash용 PreToolHooks
grep "executePreToolHooks called for tool: Bash" debug.txt
```

---

## 스킬/세션 패턴

### 스킬 로딩
```bash
# 패턴 - 스킬 훅 등록
grep "Added session hook for event" debug.txt
grep "Registered.*hooks from skill" debug.txt

# 예시
2026-01-13T09:39:14.449Z [DEBUG] Added session hook for event PreToolUse in session 3cc71c9f-...
2026-01-13T09:39:14.449Z [DEBUG] Registered 2 hooks from skill 'specify'
```

### 세션 훅 정리
```bash
# 패턴
grep "Cleared all session hooks for session" debug.txt
```

---

## AskUserQuestion 패턴

```bash
# 패턴 - PreToolHooks
grep "executePreToolHooks called for tool: AskUserQuestion" debug.txt

# 패턴 - PostToolHooks
grep "PostToolUse with query: AskUserQuestion" debug.txt
```

---

## 오류 패턴

### 훅 오류
```bash
# 패턴
grep -i "error\|failed\|exception" debug.txt | grep -i hook
```

### 도구 오류
```bash
# 패턴
grep "Tool.*error\|Tool.*failed" debug.txt
```

---

## reviewer 전용 패턴

### reviewer 판정 추출
```bash
# 패턴 - OKAY 또는 REJECT가 포함된 모델 응답 찾기
grep -A5 "Hooks: Model response:" debug.txt | grep -E '"ok":|"reason":'

# 예시(OKAY)
{
  "ok": true,
  "reason": "Plan approved by reviewer..."
}

# 예시(REJECT)
{
  "ok": false,
  "reason": "REJECT - The plan has a critical contradiction..."
}
```

---

## 산출물 패턴

### draft 파일 작업
```bash
# 패턴 - draft 생성
grep "\.dev-flow/drafts/" debug.txt | grep "written atomically"

# 패턴 - draft 삭제(rm 명령 찾기)
grep "rm.*\.dev-flow/drafts/" debug.txt
```

### plan 파일 작업
```bash
# 패턴 - plan 생성
grep "\.dev-flow/plans/" debug.txt | grep "written atomically"
```

---

## timeline 재구성

세션 timeline을 재구성하려면 다음을 사용한다.

```bash
# 주요 작업의 timestamp 포함 이벤트를 모두 추출
grep -E "(SubagentStart|SubagentStop|executePreToolHooks|Prompt hook condition|written atomically)" debug.txt | sort
```

---

## 통합 분석 쿼리

specify 스킬 세션 전체 분석:

```bash
# 1. Explore 에이전트 확인
grep "SubagentStart with query: Explore" debug.txt | wc -l

# 2. gap-analyzer 확인
grep "SubagentStart with query: gap-analyzer" debug.txt

# 3. reviewer 호출과 결과 확인
grep -E "(SubagentStart with query: reviewer|Prompt hook condition)" debug.txt

# 4. plan-guard.sh 훅 확인
grep "permissionDecision" debug.txt

# 5. 산출물 확인
grep -E "(\.dev-flow/drafts/|\.dev-flow/plans/).*written atomically" debug.txt

# 6. 최종 Stop 훅 결과
grep -A10 "Getting matching hook commands for Stop" debug.txt | tail -20
```
