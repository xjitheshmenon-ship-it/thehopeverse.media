"""Keep Hope's memory (outbox packages, run logs, lessons.md, characters.md) on the `state` branch on GitHub,
so the daily run can happen on GitHub's servers instead of one PC. Videos and sign-in tokens are never saved.

    python state.py load    -> copy the saved files into this folder
    python state.py save    -> save this folder's files as a new commit on the state branch
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent  # same paths as agents.py, without needing an API key
OUTBOX, LESSONS, CAST = HERE / "outbox", HERE / "lessons.md", HERE / "characters.md"

BRANCH = "state"


def git(*args, **kw) -> str:
    return subprocess.run(["git", *args], cwd=HERE, check=True, capture_output=True, text=True, **kw).stdout.strip()


def files() -> list:
    runs = HERE / "runs"
    found = [*OUTBOX.glob("*.json"), *OUTBOX.glob("*/board.json"), *runs.glob("*.md"), *runs.glob("*.jsonl"),
             LESSONS, CAST]
    return [str(p.relative_to(HERE)) for p in found if p.exists()]


def load() -> None:
    if subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0:
        saved = git("ls-tree", "-r", "--name-only", "FETCH_HEAD").splitlines()
        git("restore", "--source=FETCH_HEAD", "--worktree", "--", *saved)
        print(f"Loaded {len(saved)} files from the {BRANCH} branch")


def save() -> None:
    env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tempfile.mkdtemp(), "index"),
           "GIT_AUTHOR_NAME": "Mr. Hope", "GIT_AUTHOR_EMAIL": "hope@localhost",
           "GIT_COMMITTER_NAME": "Mr. Hope", "GIT_COMMITTER_EMAIL": "hope@localhost"}
    git("add", "-f", "--", *files(), env=env)
    tree = git("write-tree", env=env)
    parent = subprocess.run(["git", "fetch", "origin", BRANCH], cwd=HERE, capture_output=True).returncode == 0
    commit = git("commit-tree", tree, *(["-p", "FETCH_HEAD"] if parent else []), "-m", "Hope's memory", env=env)
    git("push", "origin", f"{commit}:refs/heads/{BRANCH}")
    print(f"Saved {len(files())} files to the {BRANCH} branch")


if __name__ == "__main__":
    {"load": load, "save": save}[sys.argv[1]]()
