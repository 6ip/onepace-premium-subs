"""Print a commit message describing the staged changes.

Run after `git add`, before `git commit`:
    python -u report.py > msg.txt || echo "[auto] subtitles refreshed" > msg.txt
    git commit -F msg.txt

Reporting must never block the commit, so the caller keeps a fallback message.
"""
import json
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX = "meta/subtitles.json"
HASHES = "hashes.json"
MAX_LISTED = 6

LANG_NAMES = {
    "ara": "Arabic", "cze": "Czech", "dut": "Dutch", "eng": "English",
    "fin": "Finnish", "fre": "French", "ger": "German", "heb": "Hebrew",
    "ind": "Indonesian", "ita": "Italian", "jpn": "Japanese", "pol": "Polish",
    "por": "Portuguese", "rus": "Russian", "spa": "Spanish", "tur": "Turkish",
    "vie": "Vietnamese",
}


def git(*args):
    out = subprocess.run(
        ["git", *args], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8"
    )
    return out.stdout if out.returncode == 0 else ""


def blob(rev, path):
    try:
        return json.loads(git("show", f"{rev}:{path}"))
    except ValueError:
        return {}


def episode_name(url_or_path):
    """'meta/subs/08 Reverse Mountain/02/RM_2_ru.vtt' -> 'Reverse Mountain 2'."""
    tail = url_or_path.replace("%20", " ")
    if "meta/subs/" not in tail:
        return None
    part = tail.split("meta/subs/")[-1].split("/")
    if len(part) < 2:
        return None
    arc = re.sub(r"^\d+\s+", "", part[0])
    return f"{arc} {int(part[1])}" if part[1].isdigit() else arc


def path_langs(index):
    """Map a repo path to its language, using the urls in the index."""
    out = {}
    for entries in index.values():
        for e in entries:
            url = e.get("url", "").replace("%20", " ")
            if "meta/subs/" in url:
                out["meta/subs/" + url.split("meta/subs/")[-1]] = e.get("lang", "")
    return out


def lang(code):
    return LANG_NAMES.get(code, code)


def name_for(ep_id, index):
    """Prefer the arc name from the path; fall back to the raw episode id."""
    entries = index.get(ep_id) or []
    if entries:
        got = episode_name(entries[0].get("url", ""))
        if got:
            return got
    return ep_id


def natural(text):
    """Sort 'Alabasta 2' before 'Alabasta 12'."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", text)]


def join_capped(items):
    items = sorted(set(items), key=natural)
    shown = items[:MAX_LISTED]
    extra = len(items) - len(shown)
    return ", ".join(shown) + (f" +{extra} more" if extra else "")


def staged_files():
    """Subtitle files added, modified, renamed and deleted in the index."""
    added, modified, renamed, deleted = [], [], [], []
    out = git("diff", "--cached", "--name-status", "-M", "--", "meta/subs/")
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        if not path.endswith(".vtt"):
            continue
        if status.startswith("R"):
            renamed.append(path)
        elif status.startswith("A"):
            added.append(path)
        elif status.startswith("M"):
            modified.append(path)
        elif status.startswith("D"):
            deleted.append(path)
    return added, modified, renamed, deleted


def index_change():
    """Tracks gained and lost, plus episodes appearing for the first time."""
    before = blob("HEAD", INDEX)
    after = blob("", INDEX) or blob(":0", INDEX)
    if not after:
        return {}, {}, set()
    gained, lost = {}, {}
    for ep, entries in after.items():
        old_ids = {e.get("id") for e in before.get(ep, [])}
        new = [e for e in entries if e.get("id") not in old_ids]
        if new:
            gained[ep] = [e.get("lang", "?") for e in new]
    for ep, entries in before.items():
        new_ids = {e.get("id") for e in after.get(ep, [])}
        gone = [e for e in entries if e.get("id") not in new_ids]
        if gone:
            lost[ep] = [e.get("lang", "?") for e in gone]
    return gained, lost, set(after) - set(before)


def converter_rebuilt():
    before = blob("HEAD", HASHES).get("_converter_version")
    after = (blob("", HASHES) or blob(":0", HASHES)).get("_converter_version")
    return after is not None and before != after, after


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    added, modified, renamed, deleted = staged_files()
    gained, lost, new_eps = index_change()
    index = blob("", INDEX) or blob(":0", INDEX)
    plangs = path_langs(index)
    rebuilt, version = converter_rebuilt()

    lines, body = [], []

    if rebuilt:
        touched = len(added) + len(modified)
        lines.append(f"[auto] converter rebuild - {touched} subtitles rewritten")
        body.append(f"Converter:   version {version}")
    elif renamed and not added and not modified:
        lines.append(f"[auto] renamed {len(renamed)} subtitle files")
    else:
        head = []
        if gained:
            langs = {lang(c) for cs in gained.values() for c in cs}
            if len(gained) == 1 and len(langs) == 1:
                ep = next(iter(gained))
                head.append(f"{next(iter(langs))} added for {name_for(ep, index)}")
            elif new_eps:
                head.append(f"{len(new_eps)} episode{'s' if len(new_eps) > 1 else ''} gained subtitles")
            else:
                head.append(f"{sum(len(v) for v in gained.values())} subtitles added")
        if modified:
            mlangs = {plangs.get(p) for p in modified} - {None, ""}
            noun = "subtitle" + ("s" if len(modified) > 1 else "")
            named = f"{lang(next(iter(mlangs)))} " if len(mlangs) == 1 else ""
            eps = {episode_name(p) or p for p in modified}
            span = f" across {len(eps)} episodes" if len(eps) < len(modified) else ""
            head.append(f"{len(modified)} {named}{noun} updated{span}")
        if renamed:
            head.append(f"{len(renamed)} renamed")
        if lost and not head:
            n = sum(len(v) for v in lost.values())
            head.append(f"{n} subtitle{'s' if n > 1 else ''} removed")
        if not head:
            head.append("refreshed source hashes" if not deleted else "removed stale files")
        lines.append(f"[auto] {', '.join(head)}")

    if gained:
        body.append("New:         " + join_capped(
            f"{name_for(ep, index)} ({', '.join(sorted({lang(c) for c in cs}))})"
            for ep, cs in gained.items()))
    # After a rebuild every file is listed, so naming them says nothing.
    if modified and not rebuilt:
        mlangs = {plangs.get(p) for p in modified} - {None, ""}
        names = [episode_name(p) or os.path.basename(p) for p in modified]
        suffix = f" ({lang(next(iter(mlangs)))})" if len(mlangs) == 1 else ""
        body.append("Updated:     " + join_capped(names) + suffix)
    if lost:
        body.append("Removed:     " + join_capped(
            f"{name_for(ep, index)} ({', '.join(sorted({lang(c) for c in cs}))})"
            for ep, cs in lost.items()))

    if body:
        lines += ["", *body]
    sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
