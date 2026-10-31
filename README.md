# One Pace Addon Subs

The subtitle backend for the **One Pace Addon**. One Pace publishes its subtitles as `.ass` files, which many players cannot display properly, including web platforms, Apple devices and TVs, so this repo converts them to WebVTT and publishes an index the addon can serve.

**[Install the addon](https://onepace.e6ip.com)**, or find it on [Stremio Addons](https://stremio-addons.net/addons/one-pace-rd).

> These are extra plain-text tracks. The styled subtitles, with their fonts, colors and positioned signs, are the ones already embedded in the video file.

## How it works

`subs.py` reads the file tree of [one-pace/one-pace-public-subtitles](https://github.com/one-pace/one-pace-public-subtitles), downloads only the `.ass` files whose blob SHA changed since the last run, converts them to WebVTT, merges the opening and ending lyrics from that same repo into the right timestamps, and writes the result to `meta/subs/` with an index at `meta/subtitles.json`.

The converter drops karaoke layers, typesetting and drawing commands, and invisible spacer text, so what ships is the dialogue a viewer needs rather than everything the source file carries. Lines tagged `title`, `caption` or `sign` are kept and wrapped in `<b>`.

## What's in here

```
subs.py                the pipeline
hashes.json            blob SHA per .ass file, so unchanged files are skipped
meta/
    subtitles.json     episode id -> [{ id, url, lang, label }]
    subs/              <Arc>/<episode>/<episode_id>_<lang>.vtt
    external.json      what the hand-added subtitles produced
external/              complete .ass files for episodes the One Pace repo
                       does not cover (the sources stay out of git)
```

Episode ids are the short prefixes from [`config.json`](https://github.com/6ip/onepace-streams/blob/main/config.json): `AR_3`, `RO_1`, `special_fan_1`, not full arc names.

`external/` is gap-fill only and can never override a repo track. See [`external/README.md`](external/README.md) for what is tracked and what is not.

## Languages

Available: Arabic, Chinese, Czech, English, Finnish, French, German, Hebrew, Italian, Japanese, Polish, Portuguese, Russian, Spanish and Turkish. Spanish and Portuguese each ship a second regional track, labeled Latin America and Brazil.

Coverage varies a lot. English is close to complete, and some languages only cover a few arcs.

These come from the One Pace team's own repository, so this pipeline can only publish what has already been translated. **If your language is missing or thin, One Pace is [looking for translators](https://onepace.net/en/recruitment).** That is the way to change it.

## Arabic and RTL

Arabic goes through an extra pass that fixes punctuation typed visually in Aegisub, such as flipped brackets and punctuation on the wrong side, and wraps each line in BiDi markers so players render it correctly.

## Generated, not hand-edited

A GitHub Action rebuilds `meta/subs/` and `meta/subtitles.json` every six hours. Anything edited there by hand is overwritten on the next run. Send pull requests for `subs.py`, and open an issue for the data.

**Wrong or missing text inside a subtitle comes from the source `.ass` file**, so it belongs upstream in the [One Pace subtitles repo](https://github.com/one-pace/one-pace-public-subtitles), not here.

## Running it locally

```bash
pip install pysubs2
python subs.py
```

It reads `config.json` from [6ip/onepace-streams](https://github.com/6ip/onepace-streams) at runtime for the arc-to-prefix mapping, so there is nothing to configure. Output lands in `meta/` relative to where you run it.

## Credits

Most of these subtitles, and the opening and ending lyrics merged into them, come from the [One Pace public subtitles repository](https://github.com/one-pace/one-pace-public-subtitles): the work of the One Pace team and their translators.

The Shaved Egghead and Kuma Cut tracks come from Kanes31 and Rai, who made those edits, and are carried here only to fill episodes One Pace has not subtitled. They are not One Pace releases.

## License

MIT covers `subs.py` and the rest of the tooling here.

It does **not** cover the subtitles. Files under `meta/subs/` are converted from their original `.ass` sources and remain the work of the teams and translators who made them, whether that is the One Pace project or one of the alternative edits. They are mirrored here only so the addon can serve them.
