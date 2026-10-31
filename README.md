# One Pace Addon Subs

The subtitle backend for the **One Pace Addon**: it converts the One Pace team's `.ass` subtitles into WebVTT and publishes an index the addon can serve.

**[Install the addon](https://onepace.e6ip.com)**, or find it on [Stremio Addons](https://stremio-addons.net/addons/one-pace-rd).

## How it works

A GitHub Action runs `subs.py` every six hours. It reads the file tree of [one-pace/one-pace-public-subtitles](https://github.com/one-pace/one-pace-public-subtitles), downloads only the `.ass` files whose blob SHA changed since the last run, converts them to WebVTT, merges the opening and ending lyrics into the right timestamps, and writes the result to `meta/subs/` with an index at `meta/subtitles.json`.

The converter drops karaoke layers, typesetting and drawing commands, and invisible spacer text, so what ships is the dialogue a viewer needs rather than everything the source file carries. Lines tagged `title`, `caption` or `sign` are kept and wrapped in `<b>`.

## What's in here

```
meta/
    subtitles.json     episode id -> [{ id, url, lang, label }]
    subs/              <Arc>/<episode>/<episode_id>_<lang>.vtt
    external.json      what the hand-added subtitles produced
hashes.json            blob SHA per .ass file, so unchanged files are skipped
subs.py                the pipeline
```

Episode ids are the short prefixes from [`config.json`](https://github.com/6ip/onepace-streams/blob/main/config.json) — `AR_3`, `RO_1`, `special_fan_1` — not full arc names.

`external/` holds complete `.ass` files for episodes the One Pace repo doesn't cover. They are gap-fill only and can never override a repo track; see [`external/README.md`](external/README.md) for how the sources stay out of git while their output doesn't.

## Languages

Fourteen so far: Arabic, Czech, English, Finnish, French, German, Hebrew, Italian, Japanese, Polish, Portuguese, Russian, Spanish and Turkish. Coverage varies a lot — English is close to complete, and some languages only cover a few arcs.

These come from the One Pace team's own repository, so this pipeline can only publish what has already been translated. **If your language is missing or thin, One Pace is [looking for translators](https://onepace.net/en/recruitment)** — that's the way to change it.

## Arabic and RTL

Arabic goes through an extra pass that fixes punctuation typed visually in Aegisub — flipped brackets, terminals on the wrong end — and wraps each line in BiDi markers so players render it correctly.

## Generated, not hand-edited

A GitHub Action rebuilds `meta/subs/` and `meta/subtitles.json` every six hours. Anything edited there by hand is overwritten on the next run. Send pull requests for `subs.py`, and open an issue for the data.

**Wrong or missing text inside a subtitle comes from the source `.ass` file**, so it belongs upstream in the [One Pace subtitles repo](https://github.com/one-pace/one-pace-public-subtitles), not here.

## Running it locally

```bash
pip install pysubs2
python subs.py
```

It reads `config.json` from [6ip/onepace-streams](https://github.com/6ip/onepace-streams) at runtime for the arc-to-prefix mapping, so there's nothing to configure. Output lands in `meta/` relative to where you run it.

## Credits

Subtitles come from the [One Pace public subtitles repository](https://github.com/one-pace/one-pace-public-subtitles) — the work of the One Pace team and their translators. This pipeline only converts and republishes them so the addon can serve them.

## License

MIT covers `subs.py` and the rest of the tooling here.

It does **not** cover the subtitles. Files under `meta/subs/` are converted from the One Pace public subtitles and remain the work of the One Pace team and their translators; they are mirrored here only so the addon can serve them.
