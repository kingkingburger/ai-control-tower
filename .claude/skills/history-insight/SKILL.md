---
name: history-insight
description: 사용자가 Claude Code 세션 히스토리에 접근, 캡처, 참조하길 원할 때 사용한다. 사용자가 "세션 캡처", "세션 히스토리 저장"이라고 말하거나 저장, 추출, 요약, 리뷰 목적과 관계없이 과거/현재 대화를 소스로 참조할 때 트리거한다. "우리가 논의한 내용", "오늘 작업", "세션 히스토리" 언급이나 "우리 대화에서"처럼 대화 자체를 원자료로 다루는 경우를 포함한다.
version: 1.1.0
user-invocable: true
---

# History Insight 스킬

Claude Code 세션 히스토리를 분석하고 인사이트를 추출합니다.

---

## 데이터 위치

```
~/.claude/projects/<encoded-cwd>/*.jsonl
```

**경로 인코딩:** `/Users/foo/project` → `-Users-foo-project`

> 상세 파일 포맷: `${baseDir}/references/session-file-format.md`

---

## 실행 알고리즘

### 1단계: 범위 확인 [필수]

**스코프 결정:**

1. **명시된 경우** (AskUserQuestion 생략 가능):
   - "현재 프로젝트만" / "이 프로젝트" → `current_project`
   - "모든 세션" / "전체" → `all_sessions`

2. **명시되지 않은 경우** - AskUserQuestion 호출:
   ```
   question: "세션 검색 범위를 선택하세요"
   options:
     - "현재 프로젝트만" → ~/.claude/projects/<encoded-cwd>/*.jsonl
     - "모든 Claude Code 세션" → ~/.claude/projects/**/*.jsonl
   ```

---

### 2단계: 세션 파일 찾기

```bash
# 현재 프로젝트만
find ~/.claude/projects/<encoded-cwd> -name "*.jsonl" -type f

# 모든 세션
find ~/.claude/projects -name "*.jsonl" -type f
```

**날짜 필터링**: 파일의 mtime(수정시간) 확인 후 필터. OS별 `stat` 옵션 다름:
- macOS: `stat -f "%Sm" -t "%Y-%m-%d" <file>`
- Linux: `stat -c "%y" <file>`

---

### 3단계: 세션 처리

#### 결정 트리

```
세션 파일을 찾았는가?
├─ 아니오 → 오류: "No sessions found"
└─ 예 → 파일이 몇 개인가?
    ├─ 1-3개 파일 → 직접 Read + 파싱
    └─ 4개 이상 파일 → 배치 추출 파이프라인
```

#### 1-3개 파일

직접 Read로 JSONL 파싱. 파일이 크면(≥5000 tokens) `extract-session.sh` 사용:
```bash
${baseDir}/scripts/extract-session.sh <session.jsonl>
```

#### 4개 이상 파일: 배치 추출 파이프라인

1. 캐시 디렉토리 생성 (`/tmp/cc-cache/<analysis-name>/`)
2. 세션 목록 저장 (`sessions.txt`)
3. jq로 메시지 일괄 추출 (`user_messages.txt`)
4. 정리 및 필터링 (`clean_messages.txt`)
5. Task(opus)로 종합 분석

#### 파일이 너무 클 때: 병렬 배치 분석

`clean_messages.txt`가 너무 커서 Read 실패 시:

1. **파일 분할**:
   ```bash
   split -l 2000 clean_messages.txt /tmp/cc-cache/<name>/batch_
   ```

2. **병렬 Task(opus) 호출**:
   ```
   Task(subagent_type="general-purpose", model="opus", run_in_background=true)
   prompt: "batch_XX 파일을 읽고 주제/패턴 요약해줘"
   ```

3. **결과 병합**: Task(opus)로 종합

---

### 4단계: 결과 보고

```markdown
## 세션 캡처 완료

- **세션:** N개 파일 처리
- **메시지:** 전체 X개, 필터 후 Y개

### 추출된 인사이트
[분석 결과]
```

---

## 에러 처리

| 시나리오 | 응답 |
|----------|----------|
| 세션 파일 없음 | "이 프로젝트의 세션 파일을 찾지 못했습니다." |
| 파일이 너무 큼 | extract-session.sh로 자동 전처리 |
| jq 미설치 | "오류: jq가 필요합니다. brew install jq로 설치하세요." |
| Task 실패 | "경고: [file]을 처리하지 못했습니다. 건너뜁니다." |
| 관련 세션 0개 | "조건에 맞는 세션이 없습니다." |

---

## 보안 참고사항

- 출력에 전체 경로 노출 금지 (`~` prefix 사용)

---

## 관련 리소스

- **`${baseDir}/scripts/extract-session.sh`** - JSONL 압축 (thinking, tool_use 제거)
- **`${baseDir}/references/session-file-format.md`** - JSONL 구조 및 파싱
