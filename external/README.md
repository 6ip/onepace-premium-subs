# external subtitles

Complete `.ass` files — OP + episode + ED in one file, so nothing is injected during
conversion.

They are **gap-fill only**: if the One Pace subs repo already covers that episode in that
language, the external file is skipped. Nothing here can override a repo track.

## The sources are not in the repo

Everything in this folder except this README is gitignored. The `.ass` files stay on your
machine. What survives in git is:

| file | tracked | what it is |
|---|---|---|
| `external/*.ass` | no | your sources, local only |
| `external/index.json` | no | which source maps to which episode |
| `meta/external.json` | **yes** | what those sources produced |
| `meta/subs/**/*.vtt` | **yes** | the converted subtitles the CDN serves |

`meta/external.json` is why this works without the sources. A run that has them converts
and records what it built; **every** run then replays that record — including the 6-hourly
bot, which has no `.ass` files at all. Without it the bot would rebuild `subtitles.json`,
find no external entries, and quietly delete them.

## Adding a file

Drop the `.ass` in here and list it in `index.json`:

```json
[
  { "file": "romancedawn 01 ar.ass", "id": "RO_1", "lang": "ara",
    "tag": "muhn", "label": "Muhn Pace" }
]
```

| field | required | meaning |
|---|---|---|
| `file` | yes | filename inside `external/` |
| `id` | yes | the Stremio episode id, e.g. `RO_1` — must match one exactly, or it attaches to nothing |
| `lang` | yes | ISO 639-2/B code: `ara`, `heb`, `spa`, `fre`, … |
| `tag` | no | short word marking the source; becomes part of the track id |
| `label` | no | display text for the tag, defaults to the capitalised tag |
| `dir` | no | output folder under `meta/subs/`, e.g. `12 Alabasta/03` — only needed if the automatic placement fails |

### Where the file ends up

`meta/subs/<arc folder>/<episode>/<track id>.vtt`. That folder is worked out for you:

1. **Beside the episode's existing tracks** — the folder is read from another subtitle for
   the same `id`. This is the normal case and it cannot be wrong.
2. **From the arc prefix** — `RO_1` → `RO` → the arc folder named in upstream
   `sub.properties`.

If both fail, the run says `cannot place <id> - add a "dir" to index.json` and skips that
file. Set `dir` yourself and it is used as-is, which covers an arc the map has never heard
of. Paths containing `..` are refused.

The `id` is a top-level key of `meta/subtitles.json` — copy it from there rather than
guessing. A wrong id fails silently: the file converts, but nothing ever shows it.

Then run `python subs.py`. With that entry the track id is `RO_1_muhn_ar` and it shows as
**Arabic (Muhn Pace)**. Commit the new `.vtt`, `meta/external.json` and `meta/subtitles.json`.

To see where a file would actually land:

```bash
python -c "import json,collections; d=json.load(open('meta/subtitles.json',encoding='utf-8')); c=collections.Counter(l for s in d.values() for l in {x['lang'] for x in s}); print(sorted(((len(d)-n, k) for k,n in c.items()), reverse=True))"
```

That prints gaps per language. English is already at every episode, so an external English
file would never appear.

## What the rules are

- A file converts once, and again only when its bytes change, tracked in `hashes.json`
  under `external/<file>`.
- A record is **never dropped automatically**. If the repo starts shipping that language
  the entry disappears from `subtitles.json` but the record stays, so it comes back if the
  repo ever drops it again.
- Deleting a source `.ass` does **not** remove anything — delete the record from
  `meta/external.json` and the `.vtt` under `meta/subs/` by hand.
- Bumping `CONVERTER_VERSION` rebuilds every subtitle **except** these, since the bot has
  no sources. Re-run locally afterwards to bring them up to date.
