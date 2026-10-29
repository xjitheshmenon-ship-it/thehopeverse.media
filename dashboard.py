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

import breakout
import credits
import predict
from agents import DAILY_BUDGET, HERE, HISTORY, OUTBOX, _channels
from state import approvals, notes, topic_id
from plan import AUTO_OK, START_HOUR, verdict, STEP, SERIES_PER_DAY, day_order, planned_slots, live_channels, load, made_today, next_slots

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
    rows, checked = [], predict.load()
    for p, d in packages:
        s = yt.get(d.get("youtube_id"), {})
        num = lambda k: int(s[k]) if k in s else None
        status = "On Instagram" if d.get("instagram_id") else "On YouTube" if d.get("youtube_id") else \
            "Held: low relevance" if d.get("held") else "Video made" if p.with_suffix(".mp4").exists() else "Scripted"
        rel = d.get("relevance") or {}
        published = datetime.fromisoformat(s["published"].replace("Z", "+00:00")).astimezone(IST) \
            if "published" in s else None
        rows.append({"id": p.stem, "channel": d["channel_id"], "day": f"{published:%Y-%m-%d}" if published else None,
                     "published": f"{published:%Y-%m-%d %H:%M}" if published else None,
                     "url": f"https://youtu.be/{d['youtube_id']}" if d.get("youtube_id") else None,
                     "title": d["title"], "status": status,
                     "relevance": rel.get("score"), "relevance_why": rel.get("why"),
                     "predicted_48h": rel.get("views48"), "actual_48h": checked.get(p.stem, {}).get("actual"),
                     "youtube_id": d.get("youtube_id"), "yt_views": num("viewCount"),
                     "yt_likes": num("likeCount"), "yt_comments": num("commentCount"),
                     "instagram_id": d.get("instagram_id"), "ig_views": None, "ig_likes": None, "ig_comments": None,
                     **(_ig(d["instagram_id"]) if d.get("instagram_id") and os.environ.get("INSTAGRAM_TOKEN") else {})})
    return rows


def film_uploads(rows: list) -> list:
    """Uploads of YouTube channels that post outside the Shorts outbox (ÆTHER's films, posted by film.py), read
    from the channel itself, so scheduled ones show with their go-live time."""
    from video import uploads
    out, piped = [], {r["channel"] for r in rows}
    for c in _channels():
        token = HERE / c.get("token", "token.json")
        if c["platform"] != "youtube" or c["id"] in piped or not token.exists():
            continue
        try:
            videos = uploads(token)
        except Exception as e:
            print(f"::warning::Uploads for {c['id']}: {str(e)[:300]}")
            continue
        for vid, v in videos.items():
            scheduled = v["privacy"] == "private" and v.get("publish_at")
            when = datetime.fromisoformat((v.get("publish_at") if scheduled else v["published"]).replace("Z", "+00:00")).astimezone(IST)
            num = lambda k: int(v[k]) if k in v else None
            out.append({"id": f"{c['id']}-{vid}", "channel": c["id"], "day": f"{when:%Y-%m-%d}",
                        "published": f"{when:%Y-%m-%d %H:%M}", "url": f"https://youtu.be/{vid}", "title": v["title"],
                        "status": "Scheduled" if scheduled else "On YouTube" if v["privacy"] == "public" else v["privacy"].title(),
                        "relevance": None, "relevance_why": None, "predicted_48h": None, "actual_48h": None,
                        "youtube_id": vid, "yt_views": num("viewCount"), "yt_likes": num("likeCount"),
                        "yt_comments": num("commentCount"), "instagram_id": None, "ig_views": None, "ig_likes": None,
                        "ig_comments": None})
    return out


# The team card on HQ. Keep in step with team.md and agents.py when an agent is added.
AGENTS = [
    {"agent": "Mr. Hope", "role": "Decision maker", "model": "Opus", "does": "Picks the topic, calls each helper in order, fixes the script after the fact-check", "output": "Run summary", "then": "Reviews the day and rewrites lessons.md"},
    {"agent": "Mr. Grow", "role": "Audience growth", "model": "Sonnet", "does": "Runs first each day: channel numbers and today's trends, notes for the other agents, to-dos for the owner", "output": "Notes per agent, owner to-dos", "then": ""},
    {"agent": "Mr. Focus", "role": "Research", "model": "Sonnet", "does": "Daily topics for India, US and EU across categories; deep research with the rare detail; fact-check of the script", "output": "Topics, dated sources, claim-by-claim check", "then": ""},
    {"agent": "Mr. Cast", "role": "Characters", "model": "Sonnet", "does": "Real-looking characters mixed with open-source photos and video of the real subject", "output": "Cast list in characters.md", "then": ""},
    {"agent": "Mr. Pen", "role": "Script", "model": "Sonnet", "does": "Curiosity-gap hook, an open question, a twist, a payoff; about 130 words", "output": "Timed script", "then": ""},
    {"agent": "Mr. Cut", "role": "Edit plan", "model": "Sonnet", "does": "Shot list with a cut every 2-3 s and a footage search per shot", "output": "Edit plan", "then": ""},
    {"agent": "Mr. Spark", "role": "Title and thumbnail", "model": "Sonnet", "does": "3 honest titles, a striking description with the story behind it, hashtags, Instagram caption", "output": "Title, description, thumbnail ideas", "then": ""},
    {"agent": "Mr. Raga", "role": "Music director", "model": "Sonnet, ElevenLabs Music", "does": "Original cinematic scores for ÆTHER: briefs from ragas, talas and film-scoring craft (music.md), 2 takes per track; Shorts music only when MUSIC_RAGA=1", "output": "Track brief and takes (music-tracks branch)", "then": ""},
    {"agent": "Mr. Post", "role": "Outbox", "model": "Sonnet", "does": "Queues the finished package for a live channel", "output": "outbox/<channel>-N.json", "then": ""},
]


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
        start = NOW.replace(hour=START_HOUR, minute=0, second=0, microsecond=0) + timedelta(minutes=STEP * i)
        status = "Posted" if short else "Running" if made.get(c["id"], 0) >= n else "Upcoming"
        out.append({"key": f"{c['id']}-{n}", "channel": c["id"], "name": c["name"], "slot": n,
                    "time": short["published"][11:] if short else f"{start:%H:%M}", "status": status,
                    "title": short["title"] if short else None, "url": short["url"] if short else None})
    return out


ACTIONS = "https://github.com/" + (os.environ.get("GITHUB_REPOSITORY") or "xjitheshmenon-ship-it/thehopeverse.media") + "/actions/workflows/"


def one_click(cid: str) -> bool:
    """A Post-now workflow with nothing to choose exists for this channel."""
    return (HERE / ".github" / "workflows" / f"post-now-{cid}.yml").exists()


def _why(e: dict) -> str:
    """The planner's reason, led by the topic's relevance score (plan.RUBRIC) when it has one."""
    auto = " (goes ahead unless rejected)" if e.get("score", 0) >= AUTO_OK else ""
    return (f"Relevance {e['score']}/100{auto} · " if "score" in e else "") + (e.get("why") or "")


def upcoming() -> list:
    """The next 6 videos the pipeline will make: only approved topics, in each channel's queue order (plan.py makes
    a channel's approved topics first and skips a channel with none), with estimated times."""
    plan, said = load(), approvals()
    out = []
    for c in live_channels():
        approved = [e for e in plan.get(c["id"], []) if verdict(c["id"], e, said) in ("ok", "auto")]
        approved.sort(key=lambda e: verdict(c["id"], e, said) != "ok")  # same order as plan.next_topic
        series = c.get("status") == "series"
        for (n, when), e in zip(next_slots(c), approved):
            out.append({"key": f"{c['id']}-{when:%Y%m%d%H}", "when": f"{when:%Y-%m-%d %H:%M}", "channel": c["id"],
                        "name": c["name"], "plan": e["topic"],
                        "why": _why(e), "score": e.get("score"), "views48": e.get("views48"), "post_now": ACTIONS + (
                            "episode.yml" if series else f"post-now-{c['id']}.yml" if one_click(c["id"]) else "hope.yml"),
                        "how": f"Run workflow, channel: {c['id']}" if series and c["id"] != "yt-kissa"
                        else "Run workflow, then the green Run workflow" if series or one_click(c["id"])
                        else f"Run workflow, job: one, channel: {c['id']}"})
    return sorted(out, key=lambda r: r["when"])[:6]


def topics() -> list:
    """Every planned topic with the owner's choice: Waiting (no script until approved), Approved or Rejected."""
    plan, said = load(), approvals()
    return [{"id": topic_id(c["id"], e["topic"]), "channel": c["id"], "name": c["name"], "when": e.get("when", ""),
             "topic": e["topic"], "why": _why(e), "score": e.get("score"), "views48": e.get("views48"),
             "status": {"ok": "Approved", "no": "Rejected"}.get(verdict(c["id"], e, said), "Waiting")}
            for c in live_channels() for e in plan.get(c["id"], [])]


def talk() -> list:
    """The owner's messages from the dashboard and Mr. Hope's run summaries, newest last."""
    said = HERE / "runs" / "hope-said.jsonl"
    hope = [json.loads(x) for x in said.read_text(encoding="utf-8").splitlines()[-30:]] if said.exists() else []
    rows = [{"at": n["at"], "who": "You", "text": n["text"]} for n in notes()]
    rows += [{"at": h["at"], "who": "Mr. Hope" + (f" ({h['channel']})" if h.get("channel") else ""), "text": h["text"]} for h in hope]
    return [{"key": f"{i}", **r} for i, r in enumerate(sorted(rows, key=lambda r: r["at"])[-40:])]


def breakouts() -> list:
    """Breakout studies (breakout.py), newest first, with the owner's choice: Waiting, Approved or Rejected."""
    said, names = approvals(), {c["id"]: c["name"] for c in _channels()}
    return [{"id": i, "channel": s["channel"], "name": names.get(s["channel"], s["channel"]), "title": s["title"],
             "url": s["url"], "views": s["views"], "usual": round(s["usual"]), "times": round(s["views"] / max(s["usual"], 1), 1),
             "studied": s["studied"], "summary": s["summary"], "report": s["report"], "owner": s["owner"],
             "changes": "\n".join(f"{c['agent']}: {c['rule']}" for c in s["changes"]),
             "status": {"ok": "Approved", "no": "Rejected"}.get(said.get(i), "Waiting")}
            for i, s in sorted(breakout.load().items(), key=lambda x: x[1]["studied"], reverse=True)]


def predictions() -> list:
    """Per channel: how Hope's 48-hour view predictions did against YouTube (predict.py)."""
    done, names = predict.load(), {c["id"]: c["name"] for c in _channels()}
    return [{"channel": c, "name": names.get(c, c), **predict.accuracy([r for r in done.values() if r["channel"] == c])}
            # every YouTube channel gets a row, even before its first 48-hour result: an empty file fails to load on HQ
            for c in sorted({r["channel"] for r in done.values()} | {c["id"] for c in _channels() if c["platform"] == "youtube"})]


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
    ids = list(dict.fromkeys([p["channel"] for p in plan] + [r["channel"] for r in rows] + [c["channel"] for c in costs] + list(totals)))
    out = []
    for i in ids:
        mine = [p for p in plan if p["channel"] == i]
        today = [r for r in rows if r["channel"] == i and r["day"] == TODAY]
        out.append({"channel": i or "shared",
                    "name": f"{names.get(i, i)} ({i.split('-')[0].upper()})" if i.startswith("ig-") else
                    names.get(i, i) if i else "Shared work and older runs",
                    # a channel outside the daily round (ÆTHER) plans what it scheduled for today
                    "planned": len(mine) or len(today), "posted_today": sum(r["status"] != "Scheduled" for r in today),
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
        {"item": "Hopeverse Shorts a day", "value": len(planned_slots(next(c for c in _channels() if c["id"] == "yt-hopeverse"))), "unit": "count", "note": "Hopeverse Media and Instinct 4 a day, other channels 2 (channels.json per_day); from 4 AM IST one video at a time, channel by channel"},
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
    if os.environ.get("BREAKOUTS") == "true":  # the hourly numbers run only, so two runs never study the same Short
        breakout.run(rows)
        predict.record(rows, NOW.replace(tzinfo=None))  # real 48-hour views next to each prediction
    rows += film_uploads(rows)  # after breakouts and predictions, which are about Shorts
    plan = slots(rows)
    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "shorts": rows, "spend": costs, "agent_work": agent_work(), "limits": limits(costs),
            "slots": plan, "channels": channels(rows, costs, plan, youtube_totals()), "runs": runs(), "upcoming": upcoming(), "credits": credits.check(),
            "topics": topics(), "agents": AGENTS, "talk": talk(), "breakouts": breakouts(), "predictions": predictions()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT} ({len(rows)} Shorts)")
    for w in credits.warnings(data["credits"]):
        print(f"::warning::{w}")  # shows on the run's page in GitHub Actions
    push(OUT)
    print(f"Pushed to the {BRANCH} branch")
