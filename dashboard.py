"""Collect live numbers for the Hopeverse HQ dashboard and push them to the dashboard-data branch on GitHub.

    python dashboard.py      (Task Scheduler runs it every hour: see schedule_hope.bat)

Writes runs/dashboard.json: every Short with its YouTube and Instagram views, likes and comments,
Claude spend per day, and how many tasks each agent did per day. The dashboard reads it from GitHub.
"""
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone

from agents import HERE, HISTORY, OUTBOX

OUT = HERE / "runs" / "dashboard.json"
BRANCH = "dashboard-data"


def _ig(media_id: str) -> dict:
    """Instagram Reel numbers. Views need the instagram_business_manage_insights permission on the token."""
    from video import _graph
    out = {}
    try:
        m = _graph(media_id, fields="like_count,comments_count")
        out = {"ig_likes": m.get("like_count"), "ig_comments": m.get("comments_count")}
        out["ig_views"] = _graph(f"{media_id}/insights", metric="views")["data"][0]["values"][0]["value"]
    except Exception as e:  # one Reel's missing numbers shouldn't stop the rest
        print(f"    Instagram numbers for {media_id}: {e}")
    return out


def shorts() -> list:
    packages = [(p, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(OUTBOX.glob("*.json"))]
    yt = {}
    ids = [d["youtube_id"] for _, d in packages if d.get("youtube_id")]
    if ids:
        try:
            from video import stats
            for i in range(0, len(ids), 50):
                yt.update(stats(ids[i:i + 50]))
        except Exception as e:
            print(f"    YouTube numbers: {e}")
    rows = []
    for p, d in packages:
        s = yt.get(d.get("youtube_id"), {})
        num = lambda k: int(s[k]) if k in s else None
        status = "On Instagram" if d.get("instagram_id") else "On YouTube" if d.get("youtube_id") else \
            "Video made" if p.with_suffix(".mp4").exists() else "Scripted"
        rows.append({"id": p.stem, "day": f"{datetime.fromtimestamp(p.stat().st_mtime):%Y-%m-%d}",
                     "title": d["title"], "status": status,
                     "youtube_id": d.get("youtube_id"), "yt_views": num("viewCount"),
                     "yt_likes": num("likeCount"), "yt_comments": num("commentCount"),
                     "instagram_id": d.get("instagram_id"), "ig_views": None, "ig_likes": None, "ig_comments": None,
                     **(_ig(d["instagram_id"]) if d.get("instagram_id") and os.environ.get("INSTAGRAM_TOKEN") else {})})
    return rows


def spend() -> list:
    days = {}
    for line in (HISTORY.read_text(encoding="utf-8").splitlines() if HISTORY.exists() else []):
        if line.strip():
            r = json.loads(line)
            d = days.setdefault(r["date"][:10], {"day": r["date"][:10], "runs": 0, "cost_usd": 0.0})
            d["runs"] += 1
            d["cost_usd"] = round(d["cost_usd"] + r["cost_usd"], 2)
    return sorted(days.values(), key=lambda d: d["day"])


def agent_work() -> list:
    """Tasks per agent per day, counted from the "## <agent>" sections agents.py writes to runs/<date>.md."""
    work = Counter()
    for log in (HERE / "runs").glob("20*.md"):
        for name in re.findall(r"^## (Mr\. [^\n]+)$", log.read_text(encoding="utf-8"), re.M):
            work[(log.name[:10], name.strip())] += 1
    return [{"day": day, "agent": agent, "tasks": n} for (day, agent), n in sorted(work.items())]


def push(path) -> None:
    """Replace the dashboard-data branch with a single commit holding dashboard.json (main is untouched)."""
    git = lambda *a, **kw: subprocess.run(["git", *a], cwd=HERE, check=True, capture_output=True, text=True, **kw).stdout.strip()
    blob = git("hash-object", "-w", str(path))
    tree = git("mktree", input=f"100644 blob {blob}\tdashboard.json\n")
    env = {**os.environ, "GIT_AUTHOR_NAME": "Mr. Hope", "GIT_AUTHOR_EMAIL": "hope@localhost",
           "GIT_COMMITTER_NAME": "Mr. Hope", "GIT_COMMITTER_EMAIL": "hope@localhost"}
    commit = git("commit-tree", tree, "-m", "Dashboard numbers", env=env)
    git("push", "-f", "origin", f"{commit}:refs/heads/{BRANCH}")


if __name__ == "__main__":
    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "shorts": shorts(), "spend": spend(), "agent_work": agent_work()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT} ({len(data['shorts'])} Shorts)")
    push(OUT)
    print(f"Pushed to the {BRANCH} branch")
