FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir requests==2.32.3

ENV PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul \
    INTERVAL_SEC=300

CMD ["sh", "-c", "while true; do python /app/watch.py; sleep \"$INTERVAL_SEC\"; done"]
