#!/bin/bash
# YouTube 영상 메타데이터 추출
# Usage: extract_metadata.sh "<URL>" [--cookies <path>]

URL="$1"
shift
EXTRA_ARGS="$@"

if [ -z "$URL" ]; then
    echo "Usage: extract_metadata.sh <URL> [--cookies <path>]"
    exit 1
fi

# yt-dlp가 PATH에 없을 수 있으므로 python -m yt_dlp 사용
python -m yt_dlp --remote-components ejs:github $EXTRA_ARGS \
    --skip-download --print "%(title)s|||%(channel)s|||%(upload_date)s|||%(duration_string)s|||%(id)s" "$URL"
