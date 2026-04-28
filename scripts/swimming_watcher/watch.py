# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///
"""의왕도시공사 평생학습관 수영장 정기수영 강좌 자리 감시.

JSON API(/rest/lecture/list)를 5분마다 조회하여 특정 강좌(class_cd)의
status가 'E'(마감) -> 'R'(접수중)로 바뀌거나 reg_person < capa가 되면
Discord webhook으로 알림을 보낸다.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATE_PATH = ROOT / "state.json"
LOG_PATH = ROOT / "watch.log"

API_URL = "https://reserve.uuc.or.kr/rest/lecture/list"
DETAIL_URL_TMPL = (
    "https://reserve.uuc.or.kr/fmcs/3"
    "?center=UUC03&action=read&page=1"
    "&event=1000000000&class=1000040000"
    "&comcd=UUC03&classcd={class_cd}&type=R"
)

API_PARAMS = {
    "company_code": "UUC03",
    "mem_no": "",
    "search_type": "R",
    "category_cd": "1000040000",
    "category_level": "2",
    "train_day": "",
    "page": "1",
    "page_size": "50",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": (
        "https://reserve.uuc.or.kr/fmcs/3"
        "?page=1&lecture_type=R&center=UUC03"
        "&event=1000000000&class=1000040000"
    ),
}


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"config.json not found: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fetch_lecture(target_class_cd: str) -> dict | None:
    params = dict(API_PARAMS)
    params["_"] = str(int(time.time() * 1000))
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    for item in resp.json():
        if str(item.get("class_cd")) == target_class_cd:
            return item
    return None


def is_open(item: dict) -> bool:
    """접수 가능 판정: status가 R이고 정원 미달."""
    if item.get("status") != "R":
        return False
    try:
        return int(item.get("reg_person", 0)) < int(item.get("capa", 0))
    except (TypeError, ValueError):
        return item.get("status") == "R"


def notify(webhook_url: str, content: str) -> None:
    resp = requests.post(webhook_url, json={"content": content}, timeout=15)
    resp.raise_for_status()


def main() -> int:
    config = load_config()
    webhook = config["webhook_url"]
    target = str(config["target_classcd"])
    label = config.get("label", target)

    try:
        item = fetch_lecture(target)
    except Exception as e:  # noqa: BLE001
        log(f"fetch error: {e}")
        return 1

    if item is None:
        log(f"target class_cd={target} not found in API response")
        return 0

    open_now = is_open(item)
    snapshot = (
        f"status={item.get('status')} "
        f"reg={item.get('reg_person')}/{item.get('capa')} "
        f"online={item.get('online_cnt')}/{item.get('online_capa')}"
    )

    state = load_state()
    prev_open = state.get("open")
    log(f"{label} class_cd={target} {snapshot} open={open_now} (prev={prev_open})")

    detail_url = DETAIL_URL_TMPL.format(class_cd=target)

    if prev_open is None:
        pass  # 최초 실행 — 알림 없이 baseline만 기록
    elif (not prev_open) and open_now:
        msg = (
            f"@here :swimmer: 자리 났어요!\n"
            f"**{item.get('class_nm')}** "
            f"({item.get('train_day_nm')} "
            f"{item.get('train_stime')}~{item.get('train_etime')}, "
            f"{item.get('reg_person')}/{item.get('capa')})\n"
            f"바로 신청: {detail_url}"
        )
        try:
            notify(webhook, msg)
            log("notified: 마감 -> 가능")
        except Exception as e:  # noqa: BLE001
            log(f"discord notify failed: {e}")
            return 1
    elif prev_open and (not open_now):
        msg = (
            f":no_entry: **{item.get('class_nm')}** 자리가 다시 마감됐어요. "
            f"({item.get('reg_person')}/{item.get('capa')})"
        )
        try:
            notify(webhook, msg)
            log("notified: 가능 -> 마감")
        except Exception as e:  # noqa: BLE001
            log(f"discord notify failed: {e}")

    state.update(
        {
            "open": open_now,
            "status": item.get("status"),
            "reg_person": item.get("reg_person"),
            "capa": item.get("capa"),
            "checked_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
