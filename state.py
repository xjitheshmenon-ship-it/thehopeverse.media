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
             *(HERE / "hosts").glob("*.png"), *(HERE / "tokens").glob("*.enc"), *(HERE / "ideas").glob("*/*"),
             LESSONS, CAST, HERE / "series.json", runs / "plan.json", runs / "breakouts.json"]
    return [str(p.relative_to(HERE)) for p in found if p.exists()]


def load() -> None:
    if subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0:
        saved = git("ls-tree", "-r", "--name-only", "FETCH_HEAD").splitlines()
        git("restore", "--source=FETCH_HEAD", "--worktree", "--", *saved)
        print(f"Loaded {len(saved)} files from the {BRANCH} branch")


def save(only: list = None) -> None:
    env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tempfile.mkdtemp(), "index"),
           "GIT_AUTHOR_NAME": "Mr. Hope", "GIT_AUTHOR_EMAIL": "hope@localhost",
           "GIT_COMMITTER_NAME": "Mr. Hope", "GIT_COMMITTER_EMAIL": "hope@localhost"}
    parent = subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0
    if parent:  # start from what's saved, so a run that loaded earlier never drops files saved since (sign-ins)
        git("read-tree", "FETCH_HEAD", env=env)
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


if __name__ == "__main__":
    if sys.argv[1] == "note":
        note(os.environ.get("BODY", ""))
    elif sys.argv[1] == "approve":
        got = approve(os.environ.get("BODY", ""))
        print(f"{sum(v == 'ok' for v in got.values())} approved, {sum(v == 'no' for v in got.values())} rejected")
    else:
        {"load": load, "save": save}[sys.argv[1]]()
