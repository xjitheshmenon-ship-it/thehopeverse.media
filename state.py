"""Keep Hope's memory (outbox packages, run logs, lessons.md, characters.md,
the hosts' reference photos, the series story so far) on the `state` branch on GitHub,
so the daily run can happen on GitHub's servers instead of one PC. Videos are never saved; sign-ins only encrypted (tokens/*.enc).

    python state.py load    -> copy the saved files into this folder
    python state.py save    -> save this folder's files as a new commit on the state branch
    python state.py approve -> apply the owner's dashboard choices ($BODY: "ok <id>" / "no <id>" lines) to
                               approvals.json and save only that file
    python state.py note    -> add the owner's message from the dashboard ($BODY) to notes.jsonl and save only that
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent  # same paths as agents.py, without needing an API key
OUTBOX, LESSONS, CAST = HERE / "outbox", HERE / "lessons.md", HERE / "characters.md"

BRANCH = "state"
APPROVALS = HERE / "approvals.json"  # {topic id: "ok" | "no"}, the owner's choices; written only by approve.yml,
# never by a video run, so a run that loaded earlier can't undo a choice (it isn't in files())


NOTES = HERE / "notes.jsonl"  # the owner's messages to Mr. Hope, sent from the dashboard (same rule as approvals)


def topic_id(channel: str, topic: str) -> str:
    return hashlib.sha1(f"{channel}|{topic}".encode()).hexdigest()[:8]


def approvals() -> dict:
    return json.loads(APPROVALS.read_text(encoding="utf-8")) if APPROVALS.exists() else {}


def git(*args, **kw) -> str:
    return subprocess.run(["git", *args], cwd=HERE, check=True, capture_output=True, text=True, **kw).stdout.strip()


def files() -> list:
    runs = HERE / "runs"
    found = [*OUTBOX.glob("*.json"), *OUTBOX.glob("*/board.json"), *runs.glob("*.md"), *runs.glob("*.jsonl"),
             *(HERE / "hosts").glob("*.png"), *(HERE / "beds").glob("*/*.mp3"), *(HERE / "tokens").glob("*.enc"), *(HERE / "ideas").glob("*/*"), *HERE.glob("series-*.json"),
             LESSONS, CAST, HERE / "series.json", runs / "plan.json", runs / "breakouts.json", runs / "slots.json"]
    return [str(p.relative_to(HERE)) for p in found if p.exists()]


def load() -> None:
    if subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0:
        saved = git("ls-tree", "-r", "-z", "--name-only", "FETCH_HEAD").split("\0")  # -z: "l'éléphanteau" isn't quoted
        saved = [f for f in saved if f]
        git("restore", "--source=FETCH_HEAD", "--worktree", "--", *saved)
        print(f"Loaded {len(saved)} files from the {BRANCH} branch")


def merge_log(path: Path, saved: str) -> None:
    """runs/*.jsonl are append-only logs (history.jsonl is the spend log the daily budget reads). Two runs side by side
    each saved their own copy, so the last save dropped the other's lines, and a run that failed to load saved a log of
    one line (1 Nov 2026: 345 spend lines lost). Keep every saved line and add this run's lines the save lacks."""
    left = saved.splitlines()
    # ponytail: an identical line logged by two parallel runs in the same minute is kept once
    new = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not _take(left, line)]
    path.write_text("".join(f"{line}\n" for line in saved.splitlines() + new), encoding="utf-8")


def _take(lines: list, line: str) -> bool:
    if line in lines:
        lines.remove(line)
        return True
    return False


def save(only: list = None) -> None:
    env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tempfile.mkdtemp(), "index"),
           "GIT_AUTHOR_NAME": "Mr. Hope", "GIT_AUTHOR_EMAIL": "hope@localhost",
           "GIT_COMMITTER_NAME": "Mr. Hope", "GIT_COMMITTER_EMAIL": "hope@localhost"}
    parent = subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0
    if parent:  # start from what's saved, so a run that loaded earlier never drops files saved since (sign-ins)
        git("read-tree", "FETCH_HEAD", env=env)
        for name in only or files():
            if name.startswith("runs/") and name.endswith(".jsonl"):
                merge_log(HERE / name, subprocess.run(["git", "show", f"FETCH_HEAD:{name}"], cwd=HERE,
                                                      capture_output=True, text=True).stdout)
    git("add", "-f", "--", *(only or files()), env=env)
    tree = git("write-tree", env=env)
    commit = git("commit-tree", tree, *(["-p", "FETCH_HEAD"] if parent else []), "-m", "Hope's memory", env=env)
    git("push", "origin", f"{commit}:refs/heads/{BRANCH}")
    print(f"Saved {len(only or files())} files to the {BRANCH} branch")


def approve(body: str) -> dict:
    """Record the owner's Approve/Reject choices from the dashboard (an issue body) and save them."""
    got = {i: v.lower() for v, i in re.findall(r"\b(ok|no)\s+([0-9a-f]{8})\b", body, re.I)}
    if got:
        APPROVALS.write_text(json.dumps({**approvals(), **got}, indent=1), encoding="utf-8")
        save([APPROVALS.name])
    return got


def note(text: str) -> None:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    with NOTES.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": f"{datetime.now(ZoneInfo('Asia/Kolkata')):%Y-%m-%d %H:%M}", "text": text.strip()[:2000]},
                           ensure_ascii=False) + "\n")
    save([NOTES.name])


def notes(k: int = 30) -> list:
    return [json.loads(x) for x in NOTES.read_text(encoding="utf-8").splitlines()[-k:]] if NOTES.exists() else []


# Notes meant only for the owner (a publish slot to set, a pinned comment to post) once leaked into a public
# description (Instinct, 31 Oct 2026). Any line opening with one of these labels, to the end of its paragraph, is cut.
OWNER_NOTE = re.compile(r"^\W*(publish(ing)? (slot|time)|pinned comment|community post|posting time|owner notes?)\b[^:\n]{0,40}:"
                        r"|notes? for (the )?owner", re.I)


def split_owner_notes(text: str) -> tuple:
    """(public description, [owner notes]) with every owner note taken out."""
    keep, cut = [], []
    for para in re.split(r"\n\s*\n", text or ""):
        lines = para.split("\n")
        i = next((n for n, x in enumerate(lines) if OWNER_NOTE.search(x)), len(lines))
        keep += ["\n".join(lines[:i]).strip()] if i else []
        cut += ["\n".join(lines[i:]).strip()] if i < len(lines) else []
    return "\n\n".join(k for k in keep if k), cut


if __name__ == "__main__":
    if sys.argv[1] == "note":
        note(os.environ.get("BODY", ""))
    elif sys.argv[1] == "approve":
        got = approve(os.environ.get("BODY", ""))
        print(f"{sum(v == 'ok' for v in got.values())} approved, {sum(v == 'no' for v in got.values())} rejected")
    else:
        {"load": load, "save": save}[sys.argv[1]]()
