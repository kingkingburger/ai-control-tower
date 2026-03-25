#!/bin/bash
# YouTube 자막 추출 (JSON3 형식)
# Usage: extract_transcript.sh "<URL>" "<output_dir>" [--cookies <path>]

URL="$1"
OUTPUT_DIR="$2"
shift 2
EXTRA_ARGS="$@"

if [ -z "$URL" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: extract_transcript.sh <URL> <output_dir> [--cookies <path>]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR/source"

# 수동 자막 시도 (ko → en)
python -m yt_dlp --remote-components ejs:github $EXTRA_ARGS \
    --skip-download --write-sub --sub-lang "ko,en" --sub-format json3 \
    -o "$OUTPUT_DIR/source/%(id)s" "$URL" 2>/dev/null

# 수동 자막이 없으면 자동 생성 자막 시도
if ! ls "$OUTPUT_DIR/source/"*.json3 1>/dev/null 2>&1; then
    python -m yt_dlp --remote-components ejs:github $EXTRA_ARGS \
        --skip-download --write-auto-sub --sub-lang "ko,en" --sub-format json3 \
        -o "$OUTPUT_DIR/source/%(id)s" "$URL"
fi

# 결과 확인
ls -la "$OUTPUT_DIR/source/"*.json3 2>/dev/null || echo "WARNING: No subtitles found"
