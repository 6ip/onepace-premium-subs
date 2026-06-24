# One Pace Premium Subs

Automated subtitle pipeline for [One Pace](https://onepace.net) — fetches `.ass` files from the community subtitles repo, converts them to WebVTT, injects opening/ending translations, and publishes a ready-to-consume index for Stremio and compatible players.

This repo is the subtitle backend for the **[One Pace Premium](https://onepace-premium.e6ip.com/) Stremio addon** — a community-built addon that streams One Pace directly through your Debrid account with no buffering, no dead torrents, and native multi-language subtitle support out of the box.

---

## One Pace Premium addon

[**onepace-premium.e6ip.com**](https://onepace-premium.e6ip.com/)

The addon pulls subtitle data from this repo's `meta/subtitles.json` index and serves it alongside streams in Stremio. Features:

- Zero-buffer playback routed through your Debrid account (Real-Debrid, TorBox, Premiumize, AllDebrid, Debrid-Link)
- Supports standard One Pace, Muhn Pace English Dub, Onigashima Paced, and Shaved Egghead & Kuma Cut — all cleanly separated
- 1,800+ subtitles across 15+ languages, perfectly synced
- Auto-updates the moment a new episode drops

Your API key is encoded directly into your manifest URL and is never stored or logged server-side.

**Install:** go to the site, pick your provider, paste your API key, hit Install.

---

## How it works

A GitHub Actions workflow runs `subs.py` on a schedule. The script:

1. Pulls the full file tree from [`one-pace/one-pace-public-subtitles`](https://github.com/one-pace/one-pace-public-subtitles) via the GitHub API
2. Reads `sub.properties` to resolve which OP/ED template belongs to each episode and language
3. Downloads only changed `.ass` files (SHA-based diffing via `hashes.json`)
4. Converts each file to `.vtt` — cleaning karaoke layers, typesetting artifacts, drawing commands, and invisible spacing tricks
5. Merges OP/ED lyrics into the correct timestamp window of the episode
6. Writes all subtitles to `meta/subs/` and updates `meta/subtitles.json`

The JSON index maps Stremio episode IDs (e.g. `ARLONG_PARK_3`) to an array of subtitle entries with language codes and CDN URLs.

---

## Output structure

```
meta/
├── subtitles.json          # Master index: episode ID → [{id, url, lang}]
└── subs/
    └── <Arc Name>/
        └── <episode number>/
            └── <episode_id>_<lang>.vtt
```

---

## Language support

| Code  | Language     |
|-------|--------------|
| eng   | English      |
| ara   | Arabic (RTL) |
| ger   | German       |
| spa   | Spanish      |
| fre   | French       |
| por   | Portuguese   |
| rus   | Russian      |
| ita   | Italian      |
| pol   | Polish       |
| tur   | Turkish      |
| jpn   | Japanese     |
| +more | ...          |

Arabic subtitles go through an additional RTL normalisation pass that fixes punctuation visually typed in Aegisub (flipped brackets, misplaced terminals) and wraps each line in proper BiDi markers.

---

## Skipped content

The converter intentionally drops:

- Karaoke / romaji / furigana layers
- Drawing commands (`\p1`, `\p2`, …)
- Typesetter-only lines (effects: `code`, `template`, `fxgroup`)
- Invisible spacer text (`fillLLLl`, `fillerfil`, …)
- Single-character noise that isn't a meaningful syllable

Lines tagged as `title`, `caption`, or `sign` are wrapped in `<b>` in the output.

---

## Local usage

```bash
pip install pysubs2
python subs.py
```

The script reads `config.json` from [`6ip/onepace-streams`](https://github.com/6ip/onepace-streams) at runtime for the arc→prefix mapping, so no local config is needed.

Output lands in `meta/` relative to wherever you run the script.

---

## Hashing / incremental updates

`hashes.json` stores the GitHub blob SHA for every processed `.ass` file. On subsequent runs, a file is only re-downloaded and re-converted if its SHA has changed. This keeps CI runs fast and avoids hammering GitHub's rate limits.

Progress is autosaved to `hashes.json` every 50 files so a partial run doesn't lose work.

---

## Credits

Subtitles sourced from the [One Pace public subtitles repository](https://github.com/one-pace/one-pace-public-subtitles).  
One Pace is a fan project — support the translators and the original editors who made the files this pipeline builds on.

If the addon saved you the headache of manually managing torrents, consider [supporting server costs on Ko-fi](https://ko-fi.com/not6ip).
