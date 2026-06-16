#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx2[http2,brotli,zstd]",
#     "pydantic",
#     "rich",
#     "typer",
# ]
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run scripts/hub_deploy_mattermost.py [ARGS]
# 3. Or make executable and run:
#      chmod +x scripts/hub_deploy_mattermost.py && ./scripts/hub_deploy_mattermost.py
# ──────────────────

from __future__ import annotations

import json
import logging
import os
import socket
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, ClassVar, Final, TypedDict
from urllib.parse import quote

import httpx2
import typer
from pydantic import BaseModel, ConfigDict, Field
from rich import print as rprint

LOGGER: Final = logging.getLogger("hub-deploy-mattermost")
MATTERMOST_CHANNEL_URL: Final = "https://chat.flexing.ai/uvc/channels/hub-develop-alarm"
DEFAULT_STATE_PATH: Final = Path(".omc/state/hub-deploy-mattermost-state.json")
KST: Final = timezone(timedelta(hours=9), "KST")

LIMITS: Final = httpx2.Limits(
    max_connections=200,
    max_keepalive_connections=40,
    keepalive_expiry=30.0,
)
TIMEOUT: Final = httpx2.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0)
SOCKET_OPTIONS: Final = [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]
EMPTY_HEADERS: Final[Mapping[str, str]] = MappingProxyType({})


class MattermostPayload(TypedDict):
    text: str


class FrozenModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)


class GitActor(FrozenModel):
    name: str


class GitCommitBody(FrozenModel):
    message: str
    author: GitActor | None = None
    committer: GitActor | None = None


class BranchCommitRef(FrozenModel):
    sha: str


class BranchResponse(FrozenModel):
    commit: BranchCommitRef


class CommitResponse(FrozenModel):
    sha: str
    html_url: str
    commit: GitCommitBody


class CompareResponse(FrozenModel):
    commits: tuple[CommitResponse, ...]


class StateFile(FrozenModel):
    snapshots: dict[str, str] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BranchWatch:
    repo: str
    repo_label: str
    branch: str
    branch_label: str

    @property
    def key(self) -> str:
        return f"{self.repo}#{self.branch}"


@dataclass(frozen=True, slots=True)
class CommitInfo:
    sha: str
    author: str
    message: str
    url: str


@dataclass(frozen=True, slots=True)
class BranchChange:
    watch: BranchWatch
    before_sha: str | None
    after_sha: str
    commits: tuple[CommitInfo, ...]


WATCHES: Final = (
    BranchWatch("uvcdev/octopus", "hub-front", "develop-origin", "octoto 없는 버전"),
    BranchWatch("uvcdev/octopus", "hub-front", "develop", "octoto 있는 버전"),
    BranchWatch("uvcdev/octopus", "hub-front", "develop-shi", "중공업 버전"),
    BranchWatch("uvcdev/octopus", "hub-front", "develop-ewlk", "잉글우드랩 버전"),
    BranchWatch("uvcdev/octopus-hub-server", "hub-server", "main", "octoto 적용 안된 main"),
    BranchWatch("uvcdev/octopus-hub-server", "hub-server", "main-octoto", "octoto 적용된 main"),
    BranchWatch("uvcdev/octopus-hub-server", "hub-server", "uvc-dev", "dev.flexing.ai 연결"),
    BranchWatch("uvcdev/octopus-hub-server", "hub-server", "uvc-main", "uvc.flexing.ai 연결"),
    BranchWatch("uvcdev/octopus-hub-server", "hub-server", "dev-samsung-heavy/main", "삼성중공업용"),
)


def log_response(response: httpx2.Response) -> None:
    LOGGER.debug(
        "HTTP %s %s -> %d %s",
        response.request.method,
        response.request.url,
        response.status_code,
        response.http_version,
    )


def create_client(headers: Mapping[str, str] = EMPTY_HEADERS) -> httpx2.Client:
    transport = httpx2.HTTPTransport(
        http2=True,
        retries=3,
        limits=LIMITS,
        socket_options=SOCKET_OPTIONS,
    )
    return httpx2.Client(
        transport=transport,
        timeout=TIMEOUT,
        headers=dict(headers),
        event_hooks={"response": [log_response]},
        follow_redirects=True,
    )


def github_headers(token: str | None) -> Mapping[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def read_state(path: Path) -> StateFile:
    if not path.exists():
        return StateFile()
    with path.open("r", encoding="utf-8") as handle:
        return StateFile.model_validate(json.load(handle))


def write_state(path: Path, state: StateFile) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        _ = handle.write(state.model_dump_json(indent=2))
        _ = handle.write("\n")


def fetch_branch_sha(client: httpx2.Client, watch: BranchWatch) -> str:
    branch = quote(watch.branch, safe="")
    response = client.get(f"https://api.github.com/repos/{watch.repo}/branches/{branch}")
    _ = response.raise_for_status()
    return BranchResponse.model_validate(response.json()).commit.sha


def commit_info(commit: CommitResponse) -> CommitInfo:
    actor = commit.commit.author or commit.commit.committer
    author = actor.name if actor else "unknown"
    return CommitInfo(
        sha=commit.sha,
        author=author,
        message=commit.commit.message.splitlines()[0],
        url=commit.html_url,
    )


def fetch_commit(client: httpx2.Client, watch: BranchWatch, sha: str) -> CommitInfo:
    response = client.get(f"https://api.github.com/repos/{watch.repo}/commits/{sha}")
    _ = response.raise_for_status()
    return commit_info(CommitResponse.model_validate(response.json()))


def fetch_commits(client: httpx2.Client, watch: BranchWatch, before_sha: str, after_sha: str) -> tuple[CommitInfo, ...]:
    response = client.get(f"https://api.github.com/repos/{watch.repo}/compare/{before_sha}...{after_sha}")
    if response.status_code == 404:
        return (fetch_commit(client, watch, after_sha),)
    _ = response.raise_for_status()
    compare = CompareResponse.model_validate(response.json())
    if len(compare.commits) == 0:
        return (fetch_commit(client, watch, after_sha),)
    return tuple(commit_info(commit) for commit in compare.commits)


def collect_changes(client: httpx2.Client, state: StateFile, notify_on_bootstrap: bool) -> tuple[tuple[BranchChange, ...], StateFile]:
    next_snapshots = dict(state.snapshots)
    changes: list[BranchChange] = []
    for watch in WATCHES:
        after_sha = fetch_branch_sha(client, watch)
        before_sha = state.snapshots.get(watch.key)
        next_snapshots[watch.key] = after_sha
        if before_sha is None:
            if notify_on_bootstrap:
                changes.append(BranchChange(watch, None, after_sha, (fetch_commit(client, watch, after_sha),)))
        elif before_sha != after_sha:
            changes.append(BranchChange(watch, before_sha, after_sha, fetch_commits(client, watch, before_sha, after_sha)))
    return tuple(changes), StateFile(snapshots=next_snapshots)


def render_change(change: BranchChange) -> str:
    authors = ", ".join(sorted({commit.author for commit in change.commits}))
    before = change.before_sha[:7] if change.before_sha else "bootstrap"
    lines = [
        f"#### {change.watch.repo_label} `{change.watch.branch}`",
        f"- 구분: {change.watch.branch_label}",
        f"- 저장소: `{change.watch.repo}`",
        f"- 변경자: {authors}",
        f"- 범위: `{before}` -> `{change.after_sha[:7]}`",
        "- 변경한 것:",
    ]
    shown = change.commits[:12]
    for commit in shown:
        lines.append(f"  - [`{commit.sha[:7]}`]({commit.url}) {commit.author}: {commit.message}")
    remaining = len(change.commits) - len(shown)
    if remaining > 0:
        lines.append(f"  - 외 {remaining}개 커밋")
    return "\n".join(lines)


def render_message(changes: tuple[BranchChange, ...], now: datetime) -> str:
    header = [
        "### Hub 브랜치 배포 알림",
        f"- 날짜: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- 채널: {MATTERMOST_CHANNEL_URL}",
    ]
    return "\n\n".join(("\n".join(header), *(render_change(change) for change in changes)))


def post_mattermost(client: httpx2.Client, webhook_url: str, text: str) -> None:
    payload: MattermostPayload = {"text": text}
    response = client.post(webhook_url, json=payload)
    _ = response.raise_for_status()


def require_webhook_url() -> str:
    webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL")
    if webhook_url is None:
        raise typer.BadParameter("MATTERMOST_WEBHOOK_URL is required unless --dry-run is set.")
    return webhook_url


def run_self_test() -> None:
    commit = CommitInfo(
        "b" * 40,
        "홍길동",
        "hub-server: deploy smoke check",
        "https://github.com/uvcdev/octopus-hub-server/commit/example",
    )
    change = BranchChange(
        watch=WATCHES[6],
        before_sha="a" * 40,
        after_sha="b" * 40,
        commits=(commit,),
    )
    message = render_message((change,), datetime(2026, 6, 15, 18, 0, 0, tzinfo=KST))
    assert "날짜: 2026-06-15 18:00:00 KST" in message
    assert "변경자: 홍길동" in message
    assert "hub-server: deploy smoke check" in message
    assert "dev.flexing.ai 연결" in message
    rprint("[green]self-test passed[/green]")


def main(
    dry_run: Annotated[bool, typer.Option(help="Print the Mattermost payload without posting.")] = False,
    notify_on_bootstrap: Annotated[
        bool,
        typer.Option(help="Notify the latest commit for branches missing from state."),
    ] = False,
    state_path: Annotated[
        Path,
        typer.Option(envvar="HUB_DEPLOY_WATCH_STATE", help="State file path."),
    ] = DEFAULT_STATE_PATH,
    self_test: Annotated[bool, typer.Option(help="Run formatting self-test without network.")] = False,
) -> None:
    if self_test:
        run_self_test()
        return

    token = os.getenv("GITHUB_TOKEN")
    state = read_state(state_path)
    with create_client(github_headers(token)) as github_client:
        changes, next_state = collect_changes(github_client, state, notify_on_bootstrap)

    if len(changes) == 0:
        rprint("[green]No hub branch changes.[/green]")
        if not dry_run:
            write_state(state_path, next_state)
        return

    message = render_message(changes, datetime.now(KST))
    if dry_run:
        rprint(message)
        return

    webhook_url = require_webhook_url()
    with create_client() as mattermost_client:
        post_mattermost(mattermost_client, webhook_url, message)
    write_state(state_path, next_state)
    rprint(f"[green]Posted {len(changes)} hub branch change alert(s).[/green]")


if __name__ == "__main__":
    typer.run(main)
