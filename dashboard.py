"""Collect live numbers for the Hopeverse HQ dashboard and push them to the dashboard-data branch on GitHub.

    python dashboard.py      (Task Scheduler runs it every hour: see schedule_hope.bat)

Writes runs/dashboard.json: every Short with its channel, upload time, views, likes and comments; spend per day
and channel; the budget limits; today's upload slots per channel; recent GitHub Actions runs; and how many tasks
each agent did per day. The dashboard reads it from GitHub.
"""
import json
import os
import re
import subprocess
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import credits
from agents import DAILY_BUDGET, HERE, HISTORY, OUTBOX, _channels
from plan import STEP, SERIES_PER_DAY, SHORTS_PER_DAY, day_order, live_channels, load, made_today, next_slots

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime.now(IST)
TODAY = f"{NOW:%Y-%m-%d}"

OUT = HERE / "runs" / "dashboard.json"
BRANCH = "dashboard-data"


def _ig(media_id: str) -> dict:
    """Instagram Reel numbers. Views need the instagram_business_manage_insights permission on the token."""
    from video import _graph
    out = {}
    for key, call in [("likes", lambda: _graph(media_id, fields="like_count,comments_count")),
                      ("views", lambda: _graph(f"{media_id}/insights", metric="views"))]:
        try:  # separately, so likes still show when the token can't read insights
            m = call()
            if key == "likes":
                out.update(ig_likes=m.get("like_count"), ig_comments=m.get("comments_count"))
            else:
                out["ig_views"] = m["data"][0]["values"][0]["value"]
        except Exception as e:  # one Reel's missing numbers shouldn't stop the rest
            print(f"    Instagram {key} for {media_id}: {e} {getattr(e, 'read', lambda: b'')()[:300]!r}")
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
        published = datetime.fromisoformat(s["published"].replace("Z", "+00:00")).astimezone(IST) \
            if "published" in s else None
        rows.append({"id": p.stem, "channel": d["channel_id"], "day": f"{published:%Y-%m-%d}" if published else None,
                     "published": f"{published:%Y-%m-%d %H:%M}" if published else None,
                     "url": f"https://youtu.be/{d['youtube_id']}" if d.get("youtube_id") else None,
                     "title": d["title"], "status": status,
                     "youtube_id": d.get("youtube_id"), "yt_views": num("viewCount"),
                     "yt_likes": num("likeCount"), "yt_comments": num("commentCount"),
                     "instagram_id": d.get("instagram_id"), "ig_views": None, "ig_likes": None, "ig_comments": None,
                     **(_ig(d["instagram_id"]) if d.get("instagram_id") and os.environ.get("INSTAGRAM_TOKEN") else {})})
    return rows


def spend() -> list:
    """Cost per day and channel from history.jsonl; channel "" is shared work (Mr. Grow, reviews, channel ideas)
    and every run logged before runs carried their channel (26 Oct 2026)."""
    days = {}
    for line in (HISTORY.read_text(encoding="utf-8").splitlines() if HISTORY.exists() else []):
        if line.strip():
            r = json.loads(line)
            key = (r["date"][:10], r.get("channel", ""))
            d = days.setdefault(key, {"day": key[0], "channel": key[1], "runs": 0, "cost_usd": 0.0})
            d["runs"] += 1
            d["cost_usd"] = round(d["cost_usd"] + r["cost_usd"], 2)
    return sorted(days.values(), key=lambda d: (d["day"], d["channel"]))


def slots(rows: list) -> list:
    """Today's videos per signed-in channel in making order: posted (with the Short), being made, or queued.
    The nth Short a channel posted today fills its nth video; times are estimates until it is posted."""
    out, made = [], made_today(NOW)
    for i, (c, n) in enumerate(day_order()):
        posted = sorted((r for r in rows if r["channel"] == c["id"] and r["day"] == TODAY), key=lambda r: r["published"])
        short = posted[n - 1] if len(posted) >= n else None
        start = NOW.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(minutes=STEP * i)
        status = "Posted" if short else "Running" if made.get(c["id"], 0) >= n else "Upcoming"
        out.append({"key": f"{c['id']}-{n}", "channel": c["id"], "name": c["name"], "slot": n,
                    "time": short["published"][11:] if short else f"{start:%H:%M}", "status": status,
                    "title": short["title"] if short else None, "url": short["url"] if short else None})
    return out


ACTIONS = "https://github.com/" + (os.environ.get("GITHUB_REPOSITORY") or "xjitheshmenon-ship-it/thehopeverse.media") + "/actions/workflows/"


def upcoming() -> list:
    """The next 6 uploads by time across the signed-in channels, with the topic plan.py planned for each slot."""
    plan = load()
    out = []
    for c in live_channels():
        planned = {e["when"]: e for e in plan.get(c["id"], [])}
        series = c.get("status") == "series"
        for n, when in next_slots(c):
            e = planned.get(f"{when:%Y-%m-%d %H:%M}", {})
            out.append({"key": f"{c['id']}-{when:%Y%m%d%H}", "when": f"{when:%Y-%m-%d %H:%M}", "channel": c["id"],
                        "name": c["name"], "plan": e.get("topic") or "Not planned yet: picked when the video is made",
                        "why": e.get("why"), "post_now": ACTIONS + ("episode.yml" if series else "hope.yml"),
                        "how": "Run workflow" if series else f"Run workflow, job: one, channel: {c['id']}"})
    return sorted(out, key=lambda r: r["when"])[:6]


def youtube_totals() -> dict:
    """Per signed-in YouTube channel: YouTube's own all-time views, subscribers and minutes watched."""
    from video import channel_stats, watch_minutes
    out = {}
    for c in _channels():
        token = HERE / c.get("token", "token.json")
        if c["platform"] != "youtube" or not token.exists():
            continue
        out[c["id"]] = {}
        try:
            out[c["id"]].update(channel_stats(token))
        except Exception as e:
            print(f"::warning::YouTube totals for {c['id']}: {str(e)[:300]}")
        try:
            out[c["id"]]["watch_min"] = watch_minutes(token)
        except Exception as e:  # e.g. the YouTube Analytics API not enabled in Google Cloud
            print(f"::warning::Watch time for {c['id']}: {str(e)[:300]}")
    return out


def channels(rows: list, costs: list, plan: list, totals: dict = None) -> list:
    """One row per channel: today's uploads against plan, today's and 7-day spend, all-time views and watch time.
    YouTube views: the channel's own total (it also counts deleted or replaced Shorts) or, while that total
    still lags, the sum over its Shorts, whichever is larger."""
    totals = totals or {}
    week = f"{NOW - timedelta(days=6):%Y-%m-%d}"
    names = {c["id"]: c["name"] for c in _channels()}
    ids = list(dict.fromkeys([p["channel"] for p in plan] + [r["channel"] for r in rows] + [c["channel"] for c in costs]))
    out = []
    for i in ids:
        mine = [p for p in plan if p["channel"] == i]
        out.append({"channel": i or "shared",
                    "name": f"{names.get(i, i)} ({i.split('-')[0].upper()})" if i.startswith("ig-") else
                    names.get(i, i) if i else "Shared work and older runs",
                    "planned": len(mine), "posted_today": sum(r["channel"] == i and r["day"] == TODAY for r in rows),
                    "due_now": sum(p["status"] in ("Posted", "Missed") for p in mine),
                    "missed": sum(p["status"] == "Missed" for p in mine),
                    "spend_today": round(sum(c["cost_usd"] for c in costs if c["channel"] == i and c["day"] == TODAY), 2),
                    "spend_7d": round(sum(c["cost_usd"] for c in costs if c["channel"] == i and c["day"] >= week), 2),
                    "yt_views": max(totals.get(i, {}).get("views", 0),  # the channel total lags a day or two
                                    sum(r["yt_views"] or 0 for r in rows if r["channel"] == i)),
                    "yt_subscribers": totals.get(i, {}).get("subscribers"),
                    "ig_views": sum(r["ig_views"] or 0 for r in rows if r["channel"] == i),
                    "yt_watch_min": totals.get(i, {}).get("watch_min"),
                    "updated": f"{NOW:%Y-%m-%d %H:%M}"})
    return [r for r in out if r["planned"] or r["posted_today"] or r["spend_7d"] or r["yt_views"] or r["ig_views"]]


def limits(costs: list) -> list:
    """The spending limits as the workflow sets them (repo variables), with today's spend against the daily cap."""
    today = round(sum(c["cost_usd"] for c in costs if c["day"] == TODAY), 2)
    clips = int(os.environ.get("AI_CLIPS_PER_SHORT") or 3)
    return [
        {"item": "Daily budget", "value": DAILY_BUDGET, "unit": "usd", "note": "All channels together; runs stop once reached (DAILY_BUDGET)"},
        {"item": "Spent today", "value": today, "unit": "usd", "note": f"{TODAY}, India time"},
        {"item": "Left today", "value": round(max(0, DAILY_BUDGET - today), 2), "unit": "usd", "note": "Before the cap stops runs"},
        {"item": "Hopeverse Shorts a day", "value": SHORTS_PER_DAY, "unit": "count", "note": "Hopeverse Media (SHORTS_PER_DAY); other channels 2 a day; from 6 AM IST one video at a time, channel by channel"},
        {"item": "Kissa episodes a day", "value": SERIES_PER_DAY, "unit": "count", "note": "Fully acted, about $4-5 each, inside the daily budget (SERIES_PER_DAY)"},
        {"item": "Paid AI clips per Short", "value": clips, "unit": "count", "note": "Kling video shots, about $0.35 each (AI_CLIPS_PER_SHORT)"},
        {"item": "HeyGen talking shot", "value": 0.05, "unit": "usd_per_s", "note": "Avatar IV, per second of speech"},
        {"item": "Kling talking shot (fallback)", "value": 0.0562, "unit": "usd_per_s", "note": "Used when HeyGen fails"},
        {"item": "Review allowance per run", "value": 0.25, "unit": "usd", "note": "Mr. Hope's lessons after the day's last Short"},
    ]


def runs() -> list:
    """The last 40 GitHub Actions runs, so failures show on the dashboard. Needs GH_TOKEN (hope.yml passes it)."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GH_TOKEN")
    if not (repo and token):
        return []
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=40",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        items = json.load(urllib.request.urlopen(req, timeout=30))["workflow_runs"]
    except Exception as e:
        print(f"    GitHub runs: {e}")
        return []
    return [{"id": r["id"], "workflow": r["name"], "number": r["run_number"], "event": r["event"],
             "started": f"{datetime.fromisoformat(r['run_started_at'].replace('Z', '+00:00')).astimezone(IST):%Y-%m-%d %H:%M}",
             "result": r["conclusion"] or r["status"], "url": r["html_url"]} for r in items]


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
    rows, costs = shorts(), spend()
    plan = slots(rows)
    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "shorts": rows, "spend": costs, "agent_work": agent_work(), "limits": limits(costs),
            "slots": plan, "channels": channels(rows, costs, plan, youtube_totals()), "runs": runs(), "upcoming": upcoming(), "credits": credits.check()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT} ({len(rows)} Shorts)")
    for w in credits.warnings(data["credits"]):
        print(f"::warning::{w}")  # shows on the run's page in GitHub Actions
    push(OUT)
    print(f"Pushed to the {BRANCH} branch")
