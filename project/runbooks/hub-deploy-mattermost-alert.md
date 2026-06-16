# Hub 배포 브랜치 Mattermost 알림

Hub front/server 배포 브랜치가 갱신되면 Mattermost의
`hub-develop-alarm` 채널에 날짜, 변경 내용, 변경자를 보낸다.

채널 확인 URL: <https://chat.flexing.ai/uvc/channels/hub-develop-alarm>

## 실행 방식

알림 전송에는 Mattermost 채널 URL이 아니라 Incoming Webhook URL이 필요하다.
Webhook URL은 `MATTERMOST_WEBHOOK_URL`로 주입하고, GitHub private repo 또는
rate limit 회피를 위해 `GITHUB_TOKEN`을 함께 넣는다.

```bash
export MATTERMOST_WEBHOOK_URL="https://chat.flexing.ai/hooks/..."
export GITHUB_TOKEN="github_pat_..."
uv run scripts/hub_deploy_mattermost.py
```

첫 실행은 현재 브랜치 SHA를 상태 파일에 기록만 하고 알림은 보내지 않는다.
현재 커밋으로 메시지 모양을 확인하려면 다음처럼 dry-run을 쓴다.

```bash
uv run scripts/hub_deploy_mattermost.py --dry-run --notify-on-bootstrap
```

상태 파일 기본값은 `.omc/state/hub-deploy-mattermost-state.json`이다. 운영 서버나
Jenkins에서 실행할 때는 사라지지 않는 경로를 지정한다.

```bash
export HUB_DEPLOY_WATCH_STATE="/var/lib/ai-control-tower/hub-deploy-mattermost-state.json"
```

## 감시 대상

| 영역 | 저장소 | 브랜치 | 의미 |
| --- | --- | --- | --- |
| hub-front | `uvcdev/octopus` | `develop-origin` | octoto 없는 버전 |
| hub-front | `uvcdev/octopus` | `develop` | octoto 있는 버전 |
| hub-front | `uvcdev/octopus` | `develop-shi` | 중공업 버전 |
| hub-front | `uvcdev/octopus` | `develop-ewlk` | 잉글우드랩 버전 |
| hub-server | `uvcdev/octopus-hub-server` | `main` | octoto 적용 안된 main |
| hub-server | `uvcdev/octopus-hub-server` | `main-octoto` | octoto 적용된 main |
| hub-server | `uvcdev/octopus-hub-server` | `uvc-dev` | dev.flexing.ai 연결, push하면 deploy |
| hub-server | `uvcdev/octopus-hub-server` | `uvc-main` | uvc.flexing.ai 연결 |
| hub-server | `uvcdev/octopus-hub-server` | `dev-samsung-heavy/main` | 삼성중공업용 |

## 스케줄링

Jenkins, cron, Windows Task Scheduler 중 하나에서 1-5분 간격으로 실행한다. 같은
상태 파일을 계속 사용해야 이미 알린 커밋을 다시 보내지 않는다.

예시 cron:

```cron
*/3 * * * * cd /d/reference2/ai-control-tower && /path/to/uv run scripts/hub_deploy_mattermost.py >> logs/hub-deploy-mattermost.log 2>&1
```

메시지는 브랜치별로 최신 SHA 변경을 감지하고 GitHub compare API로 커밋 목록을
만든다. force push처럼 compare가 불가능하면 새 HEAD 커밋 1개를 알림에 싣는다.
