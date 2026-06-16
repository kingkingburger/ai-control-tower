---
date: 2026-03-16
session: yt-dlp Windows 사용 및 Claude Code Skill 스코핑 탐구
---

# TIL: yt-dlp Windows 환경 함정 및 Claude Code Skill 스코핑

## 1. 기술적 배움

### yt-dlp: pip 설치 후 PATH 미등록 문제

- **현상**: `pip install yt-dlp`로 설치해도 Windows에서 `yt-dlp` 명령어가 동작하지 않는다.
- **원인**: pip의 스크립트 디렉토리(`~\AppData\Local\Programs\Python\PythonXX\Scripts`)가 PATH에 없는 경우가 많다.
- **해결**: `python -m yt_dlp` 형태로 모듈로 직접 실행한다. PATH 설정 없이도 항상 동작한다.
- **규칙**: Windows에서 pip 설치 CLI 도구가 안 될 때 `python -m <module_name>` 패턴을 먼저 시도한다.

### yt-dlp: Windows cp949 인코딩 JSON 출력 깨짐

- **현상**: `yt-dlp --dump-json` 출력이 한글/특수문자에서 깨지거나 오류 발생.
- **원인**: Windows 기본 콘솔 인코딩이 cp949(EUC-KR)이며, yt-dlp JSON 출력이 이를 따른다.
- **해결**: 실행 전 환경변수 설정 `PYTHONIOENCODING=utf-8` 또는 명령어 앞에 붙인다:
  ```bash
  PYTHONIOENCODING=utf-8 python -m yt_dlp --dump-json <url>
  ```
- **규칙**: Windows에서 Python CLI 도구가 비ASCII 문자를 출력할 때 인코딩 오류가 나면 `PYTHONIOENCODING=utf-8`을 먼저 적용한다.

### yt-dlp: --convert-subs 플래그 변경

- **현상**: `--convert-subs json3` 옵션이 최신 버전에서 동작하지 않는다.
- **원인**: yt-dlp 버전업으로 플래그 동작이 변경됨. 자막 형식 변환 옵션은 `--sub-format`으로 지정해야 한다.
- **해결**: `--sub-format json3`으로 교체. 자막을 다운로드할 때 형식과 변환을 분리해서 지정한다:
  ```bash
  python -m yt_dlp --write-subs --sub-format json3 --skip-download <url>
  ```
- **규칙**: yt-dlp 문서에서 "deprecated" 경고가 있는 플래그는 바로 대체 플래그로 교체한다. yt-dlp changelog를 주기적으로 확인한다.

### Claude Code Skill 스코핑 계층

- **발견**: Claude Code의 Skill은 설치 위치에 따라 적용 범위가 다르다.

  | 위치 | 스코프 | 설명 |
  |------|--------|------|
  | `~/.claude/skills/omc-learned/` | 유저 전역 | 모든 프로젝트에서 사용 가능 |
  | `.claude/skills/` | 프로젝트 | 현재 프로젝트 내에서만 사용 |
  | `~/.claude/plugins/` | 플러그인 | 플러그인 번들에 포함된 스킬 |
  | `.agents/skills/` | 에이전트 | 에이전트 런타임용 스킬 |

- **`npx skills add` 동작**: `.claude/skills/`와 `.agents/skills/` 양쪽에 설치하며, 경우에 따라 `omc-learned`에도 복사된다. 설치 후 어느 위치에 들어갔는지 확인이 필요하다.
- **규칙**: 특정 프로젝트에서만 쓸 스킬은 `.claude/skills/`에, 범용 스킬은 `~/.claude/skills/omc-learned/`에 두는 것이 의도된 구분이다.

## 2. 워크플로우 패턴 (잘 된 것)

### Python 모듈 직접 실행 패턴

PATH 문제를 우회하는 가장 빠른 해결책. `pip install` 후 바로 `python -m <module>` 형태로 실행하면 OS 환경 설정에 무관하게 동작한다. 특히 CI/CD, Claude Code Bash 실행처럼 환경이 제한된 곳에서 유용하다.

### 인코딩 환경변수 선제 적용

Windows에서 Python 외부 도구를 Bash로 호출할 때 `PYTHONIOENCODING=utf-8`을 항상 앞에 붙이는 습관을 들이면 한글 관련 인코딩 오류를 사전에 차단할 수 있다.

## 3. 실수와 비효율 (개선점)

### PATH 문제를 늦게 인지

- yt-dlp 실행 오류 시 처음에 설치 자체를 의심했다. Windows PATH 미등록이 원인임을 바로 의심했으면 더 빨리 해결됐다.
- **개선**: Windows에서 CLI 도구 not found 오류 → PATH 문제 → `python -m` 패턴으로 즉시 전환.

### yt-dlp 플래그 구버전 사용

- 오래된 레퍼런스를 그대로 복붙해서 deprecated 플래그를 사용했다. yt-dlp는 업데이트가 빠른 도구이므로 명령어 레퍼런스를 항상 `--help`로 확인해야 한다.

## 4. 재사용 가능한 패턴 (향후 적용)

| 패턴 | 설명 | 적용 시점 |
|------|------|----------|
| **python -m 우선** | Windows에서 CLI 도구 not found → `python -m <module>` 시도 | pip 설치 도구 실행 오류 시 |
| **PYTHONIOENCODING=utf-8** | 비ASCII 출력 오류 시 선제 적용 | Windows + Python CLI + 한글/특수문자 출력 |
| **yt-dlp --help 확인** | 오래된 플래그 대신 현재 플래그 확인 | yt-dlp 명령어 작성 전 |
| **Skill 위치 확인** | `npx skills add` 후 어느 스코프에 설치됐는지 확인 | Skill 설치 직후 |
