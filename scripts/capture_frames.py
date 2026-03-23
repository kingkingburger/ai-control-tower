"""YouTube JSON3 자막 기반 프레임 캡쳐 스크립트."""

import json
import subprocess
import sys
from pathlib import Path


def parse_json3(json3_path: str) -> list[dict]:
    """JSON3 자막 파일에서 타임스탬프와 텍스트를 추출한다."""
    with open(json3_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            continue
        # aAppend=1인 이벤트는 이전 자막에 이어붙이는 것이므로 스킵
        if event.get("aAppend"):
            continue

        text = "".join(s.get("utf8", "") for s in segs).strip()
        if not text or text == "\n":
            continue

        t_start_ms = event.get("tStartMs", 0)
        segments.append({
            "timestamp_sec": t_start_ms / 1000.0,
            "text": text,
        })

    return segments


def merge_segments(segments: list[dict], min_interval: float = 3.0) -> list[dict]:
    """너무 가까운 세그먼트를 병합한다."""
    if not segments:
        return []

    merged = [segments[0]]
    for seg in segments[1:]:
        prev = merged[-1]
        if seg["timestamp_sec"] - prev["timestamp_sec"] < min_interval:
            prev["text"] += " " + seg["text"]
        else:
            merged.append(seg)

    return merged


def format_timestamp(seconds: float) -> str:
    """초를 MM-SS 형식으로 변환한다."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}-{s:02d}"


def format_display_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환한다."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def capture_frame(video_path: str, timestamp_sec: float, output_path: str, ffmpeg_path: str = "ffmpeg"):
    """ffmpeg로 특정 타임스탬프에서 프레임을 캡쳐한다."""
    cmd = [
        ffmpeg_path, "-ss", str(timestamp_sec),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        "-y", output_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def main():
    if len(sys.argv) < 4:
        print("Usage: capture_frames.py <video_path> <subtitle_json3_path> <output_dir> [--min-interval N]")
        sys.exit(1)

    video_path = sys.argv[1]
    subtitle_path = sys.argv[2]
    output_dir = sys.argv[3]

    min_interval = 3.0
    if "--min-interval" in sys.argv:
        idx = sys.argv.index("--min-interval")
        min_interval = float(sys.argv[idx + 1])

    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing subtitles: {subtitle_path}")
    segments = parse_json3(subtitle_path)
    print(f"Found {len(segments)} raw segments")

    segments = merge_segments(segments, min_interval)
    print(f"After merging (min_interval={min_interval}s): {len(segments)} segments")

    results = []
    for i, seg in enumerate(segments):
        ts = format_timestamp(seg["timestamp_sec"])
        display_ts = format_display_timestamp(seg["timestamp_sec"])
        filename = f"frame_{i:04d}_{ts}.jpg"
        output_path = str(images_dir / filename)

        print(f"  [{i+1}/{len(segments)}] Capturing frame at {display_ts}...")
        try:
            capture_frame(video_path, seg["timestamp_sec"], output_path)
        except subprocess.CalledProcessError as e:
            print(f"    WARNING: Failed to capture frame at {display_ts}: {e}")
            continue

        results.append({
            "index": i,
            "timestamp": display_ts,
            "timestamp_sec": seg["timestamp_sec"],
            "text": seg["text"],
            "image": filename,
        })

    segments_json_path = Path(output_dir) / "segments.json"
    with open(segments_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Captured {len(results)} frames.")
    print(f"Segments saved to: {segments_json_path}")


if __name__ == "__main__":
    main()
