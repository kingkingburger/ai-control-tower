import json, os, html as html_mod

YTDIR = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'yt-digest')
OUTDIR = 'D:/reference2/ai-control-tower/research/readings/youtube'

with open(os.path.join(YTDIR, 'chapters.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

VIDEO_ID = 'kwSVtQ7dziU'

def format_ts(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def yt_link(sec):
    return f"https://www.youtube.com/watch?v={VIDEO_ID}&t={sec}s"

# Build chapter HTML
chapters_html = ""
toc_html = ""

for i, ch in enumerate(data['chapters']):
    ch_id = f"ch-{i}"
    toc_html += f'<li><a href="#{ch_id}"><span class="ts">[{ch["timestamp"]}]</span> {html_mod.escape(ch["title"])}</a></li>\n'

    transcript_blocks = ""
    en_lines = ch.get('en', [])
    ko_lines = ch.get('ko', [])

    for j, en_item in enumerate(en_lines):
        en_text, en_sec = en_item
        ts = format_ts(en_sec)
        link = yt_link(en_sec)
        ko_text = ko_lines[j][0] if j < len(ko_lines) else ""

        transcript_blocks += f'''
        <div class="segment">
          <a href="{link}" target="_blank" class="timestamp">[{ts}]</a>
          <div class="text">
            <p class="en">{html_mod.escape(en_text)}</p>
            <p class="ko">{html_mod.escape(ko_text)}</p>
          </div>
        </div>'''

    chapters_html += f'''
    <section id="{ch_id}" class="chapter">
      <h2><a href="{yt_link(ch['sec'])}" target="_blank" class="ch-ts">[{ch["timestamp"]}]</a> {html_mod.escape(ch["title"])}</h2>
      <div class="transcript">
        {transcript_blocks}
      </div>
    </section>'''

html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The End of Coding: Andrej Karpathy on Agents, AutoResearch, and the Loopy Era of AI</title>
<style>
:root {
  --bg: #0f0f0f;
  --surface: #1a1a2e;
  --surface2: #16213e;
  --accent: #e94560;
  --accent2: #0f3460;
  --text: #eee;
  --text-dim: #999;
  --text-ko: #8ec8f0;
  --ts-color: #e94560;
  --border: #2a2a4a;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
}
.hero {
  background: linear-gradient(135deg, var(--surface) 0%, var(--accent2) 100%);
  padding: 60px 40px;
  text-align: center;
  border-bottom: 3px solid var(--accent);
}
.hero h1 {
  font-size: 2.2em;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(90deg, #fff, #8ec8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero .meta {
  color: var(--text-dim);
  font-size: 0.95em;
  margin-bottom: 8px;
}
.hero .meta a {
  color: var(--accent);
  text-decoration: none;
}
.hero .meta a:hover { text-decoration: underline; }
.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px;
}
.summary {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 40px;
}
.summary h2 {
  color: var(--accent);
  font-size: 1.3em;
  margin-bottom: 16px;
}
.summary p { margin-bottom: 12px; }
.summary .key-points { list-style: none; padding: 0; }
.summary .key-points li {
  padding: 8px 0 8px 24px;
  position: relative;
}
.summary .key-points li::before {
  content: "\\25B6";
  position: absolute;
  left: 0;
  color: var(--accent);
  font-size: 0.7em;
  top: 12px;
}
.insights {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 40px;
}
.insights h2 {
  color: var(--text-ko);
  font-size: 1.3em;
  margin-bottom: 16px;
}
.insights h3 {
  color: var(--accent);
  font-size: 1.05em;
  margin: 20px 0 10px;
}
.insights ul { padding-left: 20px; }
.insights li { margin-bottom: 8px; }
.toc {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px 32px;
  margin-bottom: 40px;
}
.toc h2 {
  color: var(--accent);
  font-size: 1.2em;
  margin-bottom: 12px;
}
.toc ol { padding-left: 20px; }
.toc li { margin-bottom: 6px; }
.toc a { color: var(--text); text-decoration: none; }
.toc a:hover { color: var(--accent); }
.toc .ts {
  color: var(--ts-color);
  font-family: 'Consolas', monospace;
  font-size: 0.85em;
  margin-right: 6px;
}
.chapter { margin-bottom: 48px; }
.chapter h2 {
  font-size: 1.4em;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent);
  margin-bottom: 20px;
}
.ch-ts {
  color: var(--ts-color);
  text-decoration: none;
  font-family: 'Consolas', monospace;
  font-size: 0.75em;
  margin-right: 8px;
}
.ch-ts:hover { text-decoration: underline; }
.segment {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.segment:hover {
  background: rgba(233, 69, 96, 0.05);
  border-radius: 6px;
}
.timestamp {
  color: var(--ts-color);
  font-family: 'Consolas', monospace;
  font-size: 0.82em;
  white-space: nowrap;
  text-decoration: none;
  padding-top: 3px;
  min-width: 65px;
}
.timestamp:hover { text-decoration: underline; }
.text { flex: 1; }
.text .en { color: var(--text); margin-bottom: 4px; }
.text .ko { color: var(--text-ko); font-size: 0.92em; opacity: 0.85; }
.toggle-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.toggle-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 18px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s;
}
.toggle-btn:hover, .toggle-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
@media (max-width: 640px) {
  .hero { padding: 32px 16px; }
  .hero h1 { font-size: 1.5em; }
  .container { padding: 20px 12px; }
  .summary, .insights, .toc { padding: 20px; }
  .timestamp { min-width: 50px; font-size: 0.75em; }
}
</style>
</head>
<body>

<div class="hero">
  <h1>The End of Coding: Andrej Karpathy on Agents, AutoResearch, and the Loopy Era of AI</h1>
  <p class="meta"><strong>Channel:</strong> <a href="https://www.youtube.com/@NoPriorsPodcast" target="_blank">No Priors: AI, Machine Learning, Tech, &amp; Startups</a></p>
  <p class="meta"><strong>Guest:</strong> Andrej Karpathy &nbsp;|&nbsp; <strong>Host:</strong> Sarah Guo</p>
  <p class="meta"><strong>Date:</strong> 2026-03-20 &nbsp;|&nbsp; <strong>Duration:</strong> 1:06:31 &nbsp;|&nbsp; <a href="https://www.youtube.com/watch?v=kwSVtQ7dziU" target="_blank">YouTube Link</a></p>
</div>

<div class="container">

  <div class="summary">
    <h2>Summary</h2>
    <p>Andrej Karpathy가 No Priors 팟캐스트에서 AI 에이전트 시대의 코딩 변화, AutoResearch 프로젝트, 그리고 자율적으로 실험&middot;학습&middot;최적화하는 &ldquo;Loopy Era&rdquo;에 대해 논의한다. 2025년 12월을 코딩 에이전트의 전환점으로 지목하며, &ldquo;코드&rdquo;라는 동사 자체가 바뀌고 있다고 주장한다.</p>
    <ul class="key-points">
      <li><strong>코딩의 종말:</strong> 더 이상 코드를 직접 작성하는 것이 아니라, 자연어로 에이전트에게 의사를 전달하는 &ldquo;에이전틱 엔지니어링&rdquo; 시대가 도래했다.</li>
      <li><strong>AutoResearch:</strong> AI가 실험 설계, 데이터 수집, 모델 훈련, 최적화까지 자율적으로 수행하는 연구 루프를 닫는 프로젝트. SETI-at-Home처럼 분산 실험이 가능한 비전.</li>
      <li><strong>일자리 변화:</strong> Karpathy는 실제 구인 데이터를 분석하여 일자리가 즉시 사라지기보다 &ldquo;능력 확장&rdquo;이 일어나고 있으며, 적응하는 사람에게 기회가 열린다고 주장한다.</li>
    </ul>
  </div>

  <div class="insights">
    <h2>Insights</h2>
    <h3>핵심 아이디어</h3>
    <ul>
      <li><strong>Vibe Coding &rarr; Agentic Engineering:</strong> 2025년의 &ldquo;vibe coding&rdquo;은 시작일 뿐이었고, 이제는 에이전트 그리드를 tmux로 운영하며 하루 16시간 지시하는 수준으로 진화했다.</li>
      <li><strong>Model Speciation:</strong> 하나의 범용 모델이 아닌, 특화된 모델들이 생태계를 이루는 &ldquo;종 분화&rdquo;가 일어나고 있다.</li>
      <li><strong>루프의 시대:</strong> 인간이 루프 안에 있을 필요가 없어지면서, AI가 가설 수립 &rarr; 실험 &rarr; 검증 &rarr; 개선을 자율적으로 반복하는 시대가 왔다.</li>
    </ul>
    <h3>적용 가능한 점</h3>
    <ul>
      <li>코딩 에이전트를 &ldquo;도구&rdquo;가 아닌 &ldquo;팀원&rdquo;으로 대하는 워크플로우 설계가 필요하다.</li>
      <li>자연어 소통 능력(프롬프트 엔지니어링을 넘어서)이 핵심 기술이 된다.</li>
      <li>오픈소스 모델이 closed-source와 격차를 좁히고 있으므로, 자체 모델 운영 전략을 고려할 가치가 있다.</li>
    </ul>
  </div>

  <div class="toggle-bar">
    <button class="toggle-btn active" onclick="toggleLang('both')">EN + KO</button>
    <button class="toggle-btn" onclick="toggleLang('en')">English Only</button>
    <button class="toggle-btn" onclick="toggleLang('ko')">Korean Only</button>
  </div>

  <div class="toc">
    <h2>Chapters</h2>
    <ol>
      ''' + toc_html + '''
    </ol>
  </div>

  ''' + chapters_html + '''

</div>

<script>
function toggleLang(mode) {
  document.querySelectorAll('.toggle-btn').forEach(function(b) { b.classList.remove('active'); });
  event.target.classList.add('active');
  var enEls = document.querySelectorAll('.text .en');
  var koEls = document.querySelectorAll('.text .ko');
  if (mode === 'en') {
    enEls.forEach(function(el) { el.style.display = 'block'; });
    koEls.forEach(function(el) { el.style.display = 'none'; });
  } else if (mode === 'ko') {
    enEls.forEach(function(el) { el.style.display = 'none'; });
    koEls.forEach(function(el) { el.style.display = 'block'; });
  } else {
    enEls.forEach(function(el) { el.style.display = 'block'; });
    koEls.forEach(function(el) { el.style.display = 'block'; });
  }
}
</script>

</body>
</html>'''

outpath = os.path.join(OUTDIR, '2026-03-20-andrej-karpathy-end-of-coding.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML saved: {outpath}")
print(f"File size: {os.path.getsize(outpath) / 1024:.1f} KB")
