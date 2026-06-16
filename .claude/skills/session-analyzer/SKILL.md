---
name: session-analyzer
description: 사용자가 "analyze session", "세션 분석", "evaluate skill execution", "스킬 실행 검증", "check session logs", "로그 분석"을 요청하거나, 세션 ID와 스킬 경로를 함께 제공하거나, 과거 세션에서 스킬이 제대로 실행됐는지 검증하려 할 때 사용한다. Claude Code 세션을 사후 분석해 스킬/에이전트/훅 동작이 SKILL.md 명세와 맞는지 검증한다.
version: 1.0.0
user-invocable: true
---

# Session Analyzer 스킬

Claude Code 세션 동작이 SKILL.md 명세를 따랐는지 검증하는 사후 분석 도구.

## 목적

완료된 세션을 분석해 다음을 검증한다.
1. **예상 동작 vs 실제 동작** - 스킬이 SKILL.md 워크플로우를 따랐는가?
2. **구성요소 호출** - SubAgent, Hook, Tool이 올바르게 호출됐는가?
3. **산출물** - 예상 파일이 생성/삭제됐는가?
4. **버그 탐지** - 예상 밖 오류나 이탈이 있었는가?

---

## 입력 요구사항

| 매개변수 | 필수 | 설명 |
|-----------|------|------|
| `sessionId` | YES | 분석할 세션의 UUID |
| `targetSkill` | YES | 검증 기준으로 사용할 SKILL.md 경로 |
| `additionalRequirements` | NO | 추가 검증 기준 |

---

## 1단계: 세션 파일 찾기

### 1.1단계: 세션 파일 위치 찾기

세션 파일은 `~/.claude/` 아래에 있다.

```bash
# 메인 세션 로그
~/.claude/projects/-{encoded-cwd}/{sessionId}.jsonl

# 디버그 로그(상세)
~/.claude/debug/{sessionId}.txt

# 에이전트 transcript(SubAgent를 사용한 경우)
~/.claude/projects/-{encoded-cwd}/agent-{agentId}.jsonl
```

스크립트로 파일을 찾는다.
```bash
${baseDir}/scripts/find-session-files.sh {sessionId}
```

### 1.2단계: 파일 존재 확인

진행 전에 필요한 파일이 모두 있는지 확인한다. 디버그 로그가 없으면 분석 범위가 제한된다.

---

## 2단계: 대상 SKILL.md 파싱

### 2.1단계: 예상 구성요소 추출

대상 SKILL.md를 읽고 다음을 식별한다.

**YAML frontmatter에서:**
- `hooks.PreToolUse` - 예상 PreToolUse 훅과 matcher
- `hooks.PostToolUse` - 예상 PostToolUse 훅
- `hooks.Stop` - 예상 Stop 훅
- `hooks.SubagentStop` - 예상 SubagentStop 훅
- `allowed-tools` - 스킬에서 사용할 수 있는 도구

**Markdown 본문에서:**
- 언급된 SubAgent(`Task(subagent_type="...")`)
- 호출된 스킬(`Skill("...")`)
- 생성된 산출물(`.dev-flow/drafts/`, `.dev-flow/plans/` 등)
- 워크플로우 단계와 조건

### 2.2단계: 예상 동작 체크리스트 작성

SKILL.md 분석 결과로 체크리스트를 만든다.

```markdown
## 예상 동작

### 서브에이전트
- [ ] Explore agent 호출됨(병렬, run_in_background)
- [ ] plan 생성 전에 gap-analyzer 호출됨
- [ ] plan 생성 후 reviewer 호출됨

### 훅
- [ ] PreToolUse[Edit|Write]가 plan-guard.sh 트리거
- [ ] Stop hook이 reviewer 승인 검증

### Artifacts
- [ ] Draft file이 .dev-flow/drafts/{name}.md에 생성됨
- [ ] 계획 파일이 .dev-flow/plans/{name}.md에 생성됨
- [ ] OKAY 후 Draft file 삭제됨

### 워크플로
- [ ] 계획 생성 전에 인터뷰 모드 수행
- [ ] 사용자 명시 요청이 plan generation을 트리거
- [ ] Reviewer REJECT 시 revision loop 수행
```

---

## 3단계: 디버그 로그 분석

디버그 로그(`~/.claude/debug/{sessionId}.txt`)에는 상세 실행 trace가 들어 있다.

### 3.1단계: SubAgent 호출 추출

검색 패턴:
```
SubagentStart with query: {agent-name}
SubagentStop with query: {agent-id}
```

스크립트 사용:
```bash
${baseDir}/scripts/extract-subagent-calls.sh {debug-log-path}
```

### 3.2단계: 훅 이벤트 추출

검색 패턴:
```
Getting matching hook commands for {HookEvent} with query: {tool-name}
Matched {N} unique hooks for query "{query}"
Hooks: Processing prompt hook with prompt: {prompt}
Hooks: Prompt hook condition was met/not met
permissionDecision: allow/deny
```

스크립트 사용:
```bash
${baseDir}/scripts/extract-hook-events.sh {debug-log-path}
```

### 3.3단계: 도구 호출 추출

검색 패턴:
```
executePreToolHooks called for tool: {tool-name}
File {path} written atomically
```

### 3.4단계: 훅 결과 추출

프롬프트 기반 훅은 모델 응답을 찾는다.
```
Hooks: Model response: {
  "ok": true/false,
  "reason": "..."
}
```

---

## 4단계: 산출물 검증

### 4.1단계: 파일 생성 확인

각 예상 산출물마다 다음을 확인한다.
1. 디버그 로그에서 `FileHistory: Tracked file modification for {path}` 검색
2. `File {path} written atomically` 검색
3. 현재 파일시스템 상태 확인

### 4.2단계: 파일 삭제 확인

삭제되어야 하는 파일마다 다음을 확인한다.
1. Bash 호출에서 `rm` 명령 검색
2. 파일시스템에서 파일이 더 이상 없는지 확인

---

## 5단계: 예상 동작과 실제 동작 비교

### 5.1단계: 비교 표 작성

```markdown
| 구성요소 | 예상 | 실제 | 상태 |
|-----------|----------|--------|--------|
| Explore agent | 병렬 호출 2회 | 09:39:26에 2회 호출 | ✅ |
| gap-analyzer | plan 전 호출 | 09:43:08에 호출 | ✅ |
| reviewer | 계획 후 호출 | 2회 호출(REJECT→OKAY) | ✅ |
| PreToolUse hook | Edit\|Write matcher | Write에서 트리거됨 | ✅ |
| Stop hook | 승인 검증 | ok:true 반환 | ✅ |
| Draft file | 생성 후 삭제 | 생성→삭제 | ✅ |
| Plan file | 생성됨 | 존재함(10KB) | ✅ |
```

### 5.2단계: 이탈 사항 식별

불일치가 있으면 표시한다.
- 누락된 구성요소 호출
- 잘못된 작업 순서
- 훅 실패
- 누락된 산출물
- 예상 밖 오류

---

## 6단계: 보고서 생성

### 보고서 템플릿

```markdown
# 세션 분석 보고서

## 세션 정보
- **세션 ID**: {sessionId}
- **대상 스킬**: {skillPath}
- **분석일**: {date}

---

## 1. 예상 동작(SKILL.md 기준)

[예상 workflow 요약]

---

## 2. Skill/SubAgent/Hook 검증

### 서브에이전트
| SubAgent | 예상 | 실제 | 시간 | 결과 |
|----------|----------|--------|------|--------|
| ... | ... | ... | ... | ✅/❌ |

### 훅
| Hook | Matcher | 트리거 여부 | 결과 |
|------|---------|-----------|--------|
| ... | ... | ... | ✅/❌ |

---

## 3. 산출물 검증

| 산출물 | 경로 | 예상 상태 | 실제 상태 |
|----------|------|----------------|--------------|
| ... | ... | ... | ✅/❌ |

---

## 4. 이슈/버그

| 심각도 | 설명 | 위치 |
|----------|-------------|----------|
| ... | ... | ... |

---

## 5. 전체 결과

**판정**: ✅ PASS / ❌ FAIL

**요약**: [1-2문장 요약]
```

---

## 스크립트 참조

| 스크립트 | 목적 |
|--------|------|
| `find-session-files.sh` | 세션 ID에 해당하는 모든 파일 찾기 |
| `extract-subagent-calls.sh` | 디버그 로그에서 SubAgent 호출 파싱 |
| `extract-hook-events.sh` | 디버그 로그에서 훅 이벤트 파싱 |

---

## 사용 예시

```
User: "Analyze session 3cc71c9f-d27a-4233-9dbc-c4f07ea6ec5b against .claude/skills/specify/SKILL.md"

1. 세션 파일 찾기
2. SKILL.md 파싱 → 예상: Explore, gap-analyzer, reviewer, hooks
3. 디버그 로그 분석 → 실제 호출 추출
4. 산출물 검증 → .dev-flow/ 확인
5. 비교 → 검증 표 작성
6. 보고서 생성 → 세부 PASS/FAIL 기록
```

---

## 추가 리소스

### 참조 파일
- **`references/analysis-patterns.md`** - 로그 분석용 상세 grep 패턴
- **`references/common-issues.md`** - 알려진 문제와 문제 해결

### 스크립트
- **`scripts/find-session-files.sh`** - 세션 파일 찾기
- **`scripts/extract-subagent-calls.sh`** - SubAgent 호출 추출기
- **`scripts/extract-hook-events.sh`** - 훅 이벤트 추출기
