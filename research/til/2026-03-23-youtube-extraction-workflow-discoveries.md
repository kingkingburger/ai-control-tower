---
date: 2026-03-23
session: YouTube 트랜스크립트 추출, yt-dlp dead code 정리, README 재작성
---

# TIL: Windows에서 YouTube 자막/트랜스크립트 추출과 Python API 폐기 패턴

## 1. 기술 발견 (Windows의 yt-dlp)

### Chrome/Edge DPAPI 쿠키 복호화는 실패하고 Firefox 쿠키는 동작함

- **문제**: Windows의 yt-dlp는 DPAPI를 통해 Chrome/Edge 쿠키를 복호화하지 못해 쿠키 기반 인증이 막힌다.
- **우회 방법**: Firefox 쿠키를 사용한다. Firefox는 쿠키를 평문 형태로 저장하므로 DPAPI 문제를 피할 수 있다.
- **의미**: Windows에서 쿠키 기반 YouTube 접근이 필요하면 Firefox가 yt-dlp 연동에 가장 안정적인 브라우저다.
- **검증**: yt-dlp 실행 전에 Firefox 쿠키 내보내기 경로(`%APPDATA%\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite`)를 확인한다.

### YouTube용 yt-dlp에는 원격 JS 런타임 설정이 명시적으로 필요함

- **발견**: YouTube 영상/자막 가져오기는 JS challenge를 발생시키며, 명시 설정이 없으면 yt-dlp가 이를 해결하지 못한다.
- **해결**: yt-dlp 실행 시 `--remote-components ejs:github --js-runtimes node`를 전달한다.
  - `--remote-components ejs:github`: GitHub에서 내장 JS 컴포넌트를 가져온다.
  - `--js-runtimes node`: Node.js 런타임으로 JS를 실행한다. 대안은 python이다.
- **영향**: 이 플래그가 없으면 자막 추출이 형식 검사 실패처럼 보이며 중단될 수 있다.

### `--ignore-errors`는 자막 포맷 확인 실패를 우회함

- **패턴**: yt-dlp가 누락된 자막 포맷(vtt, srt 없음 등)을 만나면 다른 포맷 자막이 있어도 실패로 종료한다.
- **해결**: `--ignore-errors` 플래그로 사용 가능한 자막 포맷 처리를 계속한다.
- **트레이드오프**: 일부 포맷을 조용히 건너뛸 수 있으므로 출력 로그로 내려받은 항목을 확인해야 한다.
- **검증됨**: `--remote-components`, `--js-runtimes` 플래그와 함께 사용할 때 동작한다.

## 2. Python API 폐기 패턴

### youtube-transcript-api: 최근 버전에서 API 계약 변경

- **이전 방식**: `transcript_list = client.list_transcripts(video_id)`가 메서드를 가진 객체를 반환했다.
- **새 방식**: `transcripts = client.list_transcripts(video_id)`처럼 `.list_transcripts()` 시그니처가 바뀌어 Transcripts 객체 대신 list를 반환할 수 있다.
- **영향**: API가 단순 list를 반환하면 `.get_transcript()`를 쓰는 코드가 실패할 수 있다.
- **마이그레이션**: 메서드 호출 전에 반환 타입을 확인하고, 일관성이 중요하면 requirements에 버전을 고정한다.

### YouTube는 IP 기준으로 트랜스크립트 API 호출을 차단할 수 있음

- **관찰**: 비주거용 IP에서 호출하면 유효한 영상 ID라도 youtube-transcript-api가 403 Forbidden으로 실패한다.
- **우회 방법**: 주거용 프록시나 VPN을 사용한다. 이 API는 yt-dlp보다 덜 엄격하지만 여전히 IP에 민감하다.
- **의미**: 대량 트랜스크립트 추출에는 IP 순환이나 rate limit 제어가 필요할 수 있다.

## 3. 코드 품질 패턴 (dead code 탐지)

### 존재하지 않는 패키지에서 import하는 코드는 dead code 신호

- **예시**: `monitor.py`가 코드베이스에 존재하지 않는 `.downloader` 모듈을 import한다.
- **패턴**: Python 파일이 만들어진 적 없거나 삭제된 sibling module을 import하면 다음을 의심할 강한 신호다.
  - importer가 작성됐지만 실행된 적 없는 dead code다.
  - 리팩터링으로 모듈을 삭제했지만 import 쪽을 갱신하지 않았다.
  - 코드베이스에 미완성 커밋이 있다.
- **확인**: `grep -r "from \.downloader import"`로 모든 참조를 찾고, import 삭제 또는 모듈 구현 중 하나를 결정한다.

## 4. 워크플로우 인사이트

### 여러 저장소 일괄 작업은 현재 작업 범위로 제한해야 함

- **피드백**: 여러 저장소를 정리할 때 사용자는 관련 저장소 전체를 일괄 처리하기보다 **현재 저장소에만 범위를 한정**하기를 선호한다.
- **의미**:
  - "A 저장소에서 이 패턴을 찾았으니 B, C, D 저장소도 고치자"고 추정하지 않는다.
  - 먼저 묻거나, 발견이 발생한 저장소에 집중한다.
  - 명시 요청이 없으면 일괄 작업은 비효율적으로 느껴질 수 있다.
- **규칙**: 단일 저장소 집중은 더 빠른 피드백 루프를 만든다.

## 5. 재사용 패턴 (이후 세션)

| 패턴 | 설명 | 사용할 때 |
|---------|-------------|------------|
| **yt-dlp Windows 설정** | Firefox cookies + `--remote-components` + `--js-runtimes` | Windows에서 YouTube 자막 추출 |
| **API 버전 탐지** | API 결과에 메서드를 호출하기 전에 반환 타입 확인 | 외부 Python 패키지 연동 |
| **import 기반 dead code 탐지** | 존재하지 않는 모듈에서 가져오는 import 검색 | 코드 정리 / 기술 부채 식별 |
| **현재 작업으로 범위 제한** | 여러 저장소를 한꺼번에 고치기 전에 먼저 질문 | 멀티 저장소 발견 패턴 |
| **Transcript API fallback** | yt-dlp를 기본으로 두고 youtube-transcript-api는 보조로 유지(IP 민감) | 견고한 자막 추출 워크플로우 |

## 6. 알려진 한계

- `--remote-components ejs:github`를 쓰는 yt-dlp는 GitHub 인터넷 접근이 필요하며 지연 시간이 늘어난다.
- Firefox 쿠키 기반 인증은 브라우저 통합 방식보다 불편하다. 수동 export가 필요하다.
- youtube-transcript-api의 IP 차단은 예측하기 어렵고 rate limit 공식 문서가 없다.
