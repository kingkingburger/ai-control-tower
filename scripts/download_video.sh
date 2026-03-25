#!/bin/bash
# YouTube 영상 다운로드 (720p 이하)
# Usage: download_video.sh "<URL>" "<output_dir>" [--cookies <path>]

URL="$1"
OUTPUT_DIR="$2"
shift 2
EXTRA_ARGS="$@"

if [ -z "$URL" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: download_video.sh <URL> <output_dir> [--cookies <path>]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR/source"

python -m yt_dlp --remote-components ejs:github $EXTRA_ARGS \
    -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
    --merge-output-format mp4 \
    -o "$OUTPUT_DIR/source/%(id)s.mp4" "$URL"
