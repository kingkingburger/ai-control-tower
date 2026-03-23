"""segments.json으로부터 slides.md와 slides.html을 생성하는 스크립트."""

import html
import json
import sys
from pathlib import Path


def generate_markdown(segments: list[dict], title: str, url: str, channel: str, date: str, duration: str) -> str:
    """마크다운 슬라이드 문서를 생성한다."""
    lines = [
        "---",
        f'title: "{title}"',
        f"url: {url}",
        f"channel: {channel}",
        f"date: {date}",
        f"duration: {duration}",
        "---",
        "",
        f"# {title}",
        "",
    ]

    for seg in segments:
        lines.append(f"## [{seg['timestamp']}]")
        lines.append("")
        lines.append(f"![{seg['timestamp']}](images/{seg['image']})")
        lines.append("")
        lines.append(f"> {seg['text']}")
        lines.append("")

    return "\n".join(lines)


def generate_html(segments: list[dict], title: str, url: str, channel: str, date: str, duration: str) -> str:
    """HTML 슬라이드 뷰어를 생성한다."""
    title_escaped = html.escape(title)
    channel_escaped = html.escape(channel)

    toc_items = ""
    for i, seg in enumerate(segments):
        text_preview = html.escape(seg["text"][:60])
        toc_items += f'                <li><a href="#slide-{i}"><span class="ts">{seg["timestamp"]}</span>{text_preview}</a></li>\n'

    slides_html = ""
    for i, seg in enumerate(segments):
        text_escaped = html.escape(seg["text"])
        slides_html += f"""        <div class="slide" id="slide-{i}">
            <div class="slide-image">
                <img src="images/{seg['image']}" alt="{seg['timestamp']}" loading="lazy">
                <span class="timestamp">{seg['timestamp']}</span>
            </div>
            <div class="slide-text">
                <p>{text_escaped}</p>
            </div>
        </div>
"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
            background: #0f0f0f;
            color: #e1e1e1;
        }}
        .header {{
            background: #1a1a2e;
            padding: 2rem 1rem;
            text-align: center;
            border-bottom: 2px solid #7c83ff;
        }}
        .header h1 {{
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
            color: #fff;
        }}
        .header .meta {{
            font-size: 0.85rem;
            color: #aaa;
            margin-bottom: 0.5rem;
        }}
        .header a {{
            color: #7c83ff;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        .header a:hover {{ text-decoration: underline; }}
        .container {{
            max-width: 960px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .slide {{
            background: #1e1e1e;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.4);
            transition: transform 0.2s;
        }}
        .slide:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(124, 131, 255, 0.15);
        }}
        .slide-image {{
            position: relative;
            background: #000;
        }}
        .slide-image img {{
            width: 100%;
            display: block;
        }}
        .timestamp {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(0,0,0,0.75);
            color: #7c83ff;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-weight: 600;
        }}
        .slide-text {{
            padding: 1.2rem 1.5rem;
        }}
        .slide-text p {{
            font-size: 1rem;
            line-height: 1.8;
            color: #d4d4d4;
        }}
        .stats {{
            text-align: center;
            color: #666;
            padding: 2rem;
            font-size: 0.85rem;
        }}
        .toc {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .toc h2 {{
            font-size: 1rem;
            color: #7c83ff;
            margin-bottom: 1rem;
        }}
        .toc-list {{
            list-style: none;
            max-height: 300px;
            overflow-y: auto;
        }}
        .toc-list li {{
            padding: 0.3rem 0;
        }}
        .toc-list a {{
            color: #aaa;
            text-decoration: none;
            font-size: 0.85rem;
        }}
        .toc-list a:hover {{ color: #7c83ff; }}
        .toc-list .ts {{
            color: #7c83ff;
            font-family: monospace;
            margin-right: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title_escaped}</h1>
        <div class="meta">{channel_escaped} | {date} | {duration}</div>
        <a href="{url}" target="_blank">YouTube에서 보기 &rarr;</a>
    </div>
    <div class="container">
        <div class="toc">
            <h2>목차 ({len(segments)}개 슬라이드)</h2>
            <ul class="toc-list">
{toc_items}            </ul>
        </div>
{slides_html}    </div>
    <div class="stats">{len(segments)}개 슬라이드 | Generated by youtube-slides</div>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_output.py <output_dir> --title T --url U --channel C --date D --duration DUR")
        sys.exit(1)

    output_dir = sys.argv[1]
    args = {}
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            args[key] = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    segments_path = Path(output_dir) / "segments.json"
    with open(segments_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    title = args.get("title", "Untitled")
    url = args.get("url", "")
    channel = args.get("channel", "")
    date = args.get("date", "")
    duration = args.get("duration", "")

    md_path = Path(output_dir) / "slides.md"
    md_content = generate_markdown(segments, title, url, channel, date, duration)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Generated: {md_path}")

    html_path = Path(output_dir) / "slides.html"
    html_content = generate_html(segments, title, url, channel, date, duration)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {html_path}")


if __name__ == "__main__":
    main()
