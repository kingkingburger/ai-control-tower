---
date: 2026-03-23
session: YouTube transcript extraction, yt-dlp dead code cleanup, README rewrite
---

# TIL: YouTube subtitle/transcript extraction on Windows + Python API deprecation patterns

## 1. Technical Discoveries (yt-dlp on Windows)

### Chrome/Edge DPAPI cookie decryption fails; Firefox cookies work

- **Problem**: yt-dlp on Windows cannot decrypt Chrome/Edge cookies via DPAPI, blocking cookie-based authentication.
- **Workaround**: Use Firefox cookies instead. Firefox stores plaintext cookies, bypassing DPAPI issues.
- **Implication**: For Windows users who need cookie-based YouTube access, Firefox is the reliable browser for yt-dlp integration.
- **Testing**: Verify Firefox cookie export path (`%APPDATA%\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite`) before running yt-dlp.

### yt-dlp requires explicit remote JS runtime configuration for YouTube

- **Discovery**: YouTube's video/subtitle fetching triggers JS challenges that yt-dlp cannot solve without explicit setup.
- **Solution**: Pass `--remote-components ejs:github --js-runtimes node` when running yt-dlp.
  - `--remote-components ejs:github`: Fetches embedded JS components from GitHub.
  - `--js-runtimes node`: Uses Node.js runtime to execute JS (alternative: python).
- **Impact**: Subtitles may fail to extract without these flags, appearing as format check failures.

### --ignore-errors bypasses subtitle format check failures

- **Pattern**: When yt-dlp encounters missing subtitle formats (e.g., vtt, srt not available), it exits with failure even if subtitles exist in other formats.
- **Solution**: Use `--ignore-errors` flag to proceed with available subtitle formats.
- **Trade-off**: May silently skip some formats; inspect output logs to confirm what was downloaded.
- **Verified**: Works when combined with `--remote-components` and `--js-runtimes` flags.

## 2. Python API Deprecation Patterns

### youtube-transcript-api: API contract changed in recent versions

- **Old**: `transcript_list = client.list_transcripts(video_id)` (returns object with methods).
- **New**: `transcripts = client.list_transcripts(video_id)` → `.list_transcripts()` method signature changed (function returns list instead of Transcripts object).
- **Impact**: Code using `.get_transcript()` may fail if API returns a simple list instead of Transcripts object.
- **Migration**: Check return type before calling methods; add version pinning in requirements if consistency matters.

### YouTube blocks transcript API calls by IP

- **Observation**: youtube-transcript-api fails with 403 Forbidden even with valid video IDs when called from non-residential IPs.
- **Workaround**: Use residential proxy or VPN; API is less strict than yt-dlp but still IP-sensitive.
- **Implication**: Batch transcript extraction may require rotating IPs or rate limiting.

## 3. Code Quality Patterns (Dead Code Detection)

### Imported modules from non-existent packages = dead code indicator

- **Example**: `monitor.py` imports from `.downloader` module that doesn't exist in the codebase.
- **Pattern**: When a Python file imports from a sibling module that was never created or was deleted, it's a strong signal that:
  - The importer was written but never executed (dead code).
  - A refactor deleted the module but didn't update importers.
  - The codebase has incomplete commits.
- **Check**: Run `grep -r "from \.downloader import"` to find all references and decide: delete the import or implement the module.

## 4. Workflow Insights

### Batch operations across repos should be scoped to current work only

- **Feedback**: When cleaning up multiple repos, user preference is to **scope work to the current repository only**, not batch-process all related repos.
- **Implication**:
  - Don't assume "I found this pattern in repo A, let me fix it in repos B, C, D as well."
  - Ask first, or focus on the repo that triggered the discovery.
  - Batch operations feel inefficient unless explicitly requested.
- **Rule**: Single-repo focus = faster feedback loops.

## 5. Reusable Patterns (Future Sessions)

| Pattern | Description | When to Use |
|---------|-------------|------------|
| **yt-dlp Windows setup** | Firefox cookies + `--remote-components` + `--js-runtimes` | YouTube subtitle extraction on Windows |
| **API version detection** | Check return type before calling methods on API results | Integrating external Python packages |
| **Dead code via imports** | Search for imports from non-existent modules | Code cleanup / tech debt identification |
| **Scope to current work** | Ask before batch-fixing across repos | Multi-repo discovery patterns |
| **Transcript API fallback** | Keep yt-dlp as primary, youtube-transcript-api as fallback (IP-sensitive) | Robust subtitle extraction workflows |

## 6. Known Limitations

- yt-dlp with `--remote-components ejs:github` requires internet access to GitHub (adds latency).
- Firefox cookie-based auth is less convenient than browser-integrated methods (manual export needed).
- youtube-transcript-api IP blocking is unpredictable; no official documentation on rate limits.
