# yt-w Project Profile

대상 저장소: `D:\reference2\yt-w`

## 분류

개인 프로젝트다. 프로젝트 운영 선호와 편의 맥락을 사용할 수 있지만, secrets,
브라우저 세션, credential, Discord webhook, 쿠키 원문은 문서나 코드에 남기지
않는다.

## 역할

YouTube 라이브 방송 자동 모니터링과 일반 동영상 다운로드를 위한 셀프호스팅
프로젝트다. Python 3.13, uv, FastAPI/Uvicorn, yt-dlp, Docker Compose,
PO token provider, ffmpeg를 사용한다.

## 시작 순서

1. `D:\reference2\AGENTS.md`와 ownership 원장을 확인한다.
2. `CLAUDE.md`, `README.md`, `pyproject.toml`을 읽는다.
3. Docker/runtime 작업이면 `docker-compose.yml`을 읽는다.
4. UI 작업이면 `web/`의 실제 HTML/JS를 읽고 렌더링 surface를 확인한다.
5. 라이브 감지나 다운로드 문제면 `docker compose logs yt-monitor`와 웹 상태
   surface를 우선 확인한다.

## 작업 기준

- 기존 스타일과 통일성을 최우선으로 둔다.
- Python 코드는 명시적 타입을 선호하고 `Any`를 피한다.
- 비즈니스 로직은 가능한 순수 함수로 두고 I/O는 entrypoint나 service 경계로
  밀어낸다.
- YouTube/yt-dlp 관련 정보는 최신성이 흔들릴 수 있으므로 외부 정책이나 버전
  사실이 중요하면 공식/현재 소스를 확인한다.
- 프론트엔드 기본 파일명, placeholder, 상태 표시 같은 작은 변경도 브라우저에서
  렌더링 값을 확인한다.

## 자주 쓰는 명령

```bash
uv sync
uv run pytest
python main.py --host 0.0.0.0 --port 8011
python monitoring.py
docker compose up -d --build
docker compose logs yt-monitor
curl http://localhost:8088/health
```

## 세션 종료 메모

반복되는 작업 규칙은 `agent-rules-candidates.md`로 올리고, 1회성 관찰은
`session-memory.md`에 둔다. 개인 프로젝트이므로 필요하면 프로젝트 운영 맥락을 더
적극적으로 활용하되, 비밀값은 저장하지 않는다.
