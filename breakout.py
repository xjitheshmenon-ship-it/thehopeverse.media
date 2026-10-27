"""Breakout studies (owner's ask, 27 Oct 2026): when a Short clearly beats its channel's usual views, Mr. Hope studies
why in depth (numbers, hook, psychology, timing, title, audience, algorithm) and proposes changes for the team. The
study waits on Hopeverse HQ; once the owner approves it, its changes go into every agent prompt for that channel.

    dashboard.py calls run() on the hourly numbers run (BREAKOUTS=1 in hope.yml's stats job)
    python breakout.py --demo -> check the detector without any API

A breakout: at least BREAKOUT_X (default 3) times the median views of the channel's other Shorts and at least
BREAKOUT_MIN_VIEWS (default 50; 300 missed Sawaal's 78-view Short against a usual 9), posted in the last 14 days, the channel having 3+ other Shorts to compare with.
Studies live in runs/breakouts.json on the state branch; the owner's Approve/Reject goes in approvals.json under
the study's id, the same way as topics (state.py approve).
"""
import json
import os
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from state import approvals, topic_id

HERE = Path(__file__).parent
FILE = HERE / "runs" / "breakouts.json"
X = float(os.environ.get("BREAKOUT_X") or 3)
MIN_VIEWS = int(os.environ.get("BREAKOUT_MIN_VIEWS") or 50)
KEEP = 3  # approved studies per channel whose changes the agents follow; older ones give way to new ones


class Change(BaseModel):
    agent: Literal["Mr. Focus", "Mr. Pen", "Mr. Cut", "Mr. Spark", "Mr. Cast", "Mr. Hope"]
    rule: str  # one specific instruction for that agent's next Shorts on this channel


class Study(BaseModel):
    summary: str  # 2-3 sentences: why it broke out
    report: str   # the deep study, Markdown
    changes: list[Change]
    owner: str    # what only the owner can do by hand (pinned comment, community post, publish times)


def load() -> dict:
    return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}


def rules(channel: str, agent: str = None) -> str:
    """The changes from the owner's approved studies of this channel, for one agent (all agents when None)."""
    said = approvals()
    mine = [s for i, s in load().items() if s["channel"] == channel and said.get(i) == "ok"]
    mine = sorted(mine, key=lambda s: s["studied"])[-KEEP:]
    return "\n".join(f"- {c['rule']} (from the breakout \"{s['title']}\")" for s in mine for c in s["changes"]
                     if agent in (None, c["agent"]))


def find(rows: list, studied: dict, now: datetime) -> list:
    """Shorts (dashboard rows: channel, youtube_id, yt_views, published) that beat their channel's median by X."""
    out = []
    for r in rows:
        if r.get("yt_views") is None or not r.get("published") or topic_id(r["channel"], r["youtube_id"]) in studied:
            continue
        others = [o["yt_views"] for o in rows if o["channel"] == r["channel"] and o is not r and o.get("yt_views") is not None]
        if len(others) < 3 or now - datetime.fromisoformat(r["published"]) > timedelta(days=14):
            continue
        # ponytail: median over all the channel's other Shorts, young ones included; age-match it if that misfires
        usual = statistics.median(others)
        if r["yt_views"] >= max(MIN_VIEWS, X * max(usual, 1)):
            out.append({**r, "usual": usual})
    return out


def analytics(channel: dict, video_id: str, since: str) -> dict:
    """YouTube Analytics for one video (about 2 days behind): retention, traffic sources, countries."""
    from video import youtube
    api = youtube(False, HERE / channel.get("token", "token.json"), ("youtubeAnalytics", "v2"))
    q = lambda **kw: api.reports().query(ids="channel==MINE", startDate=since, endDate=f"{datetime.now():%Y-%m-%d}",
                                         filters=f"video=={video_id}", **kw).execute().get("rows")
    out = {}
    for key, kw in {"totals": {"metrics": "views,averageViewPercentage,averageViewDuration,likes,shares,comments,subscribersGained"},
                    "traffic": {"metrics": "views", "dimensions": "insightTrafficSourceType", "sort": "-views"},
                    "countries": {"metrics": "views", "dimensions": "country", "sort": "-views", "maxResults": 8}}.items():
        try:
            out[key] = q(**kw)
        except Exception as e:  # the study still runs on public numbers
            out[key] = f"unavailable: {str(e)[:200]}"
    return out


def study(r: dict, rows: list, channel: dict) -> Study:
    from agents import MODEL, TEAM, WEB_SEARCH, _cost, client, log_spend
    package = json.loads((HERE / "outbox" / f"{r['id']}.json").read_text(encoding="utf-8"))
    others = [{k: o[k] for k in ("title", "published", "yt_views", "yt_likes", "yt_comments")}
              for o in rows if o["channel"] == r["channel"] and o is not r and o.get("youtube_id")]
    facts = {"short": {k: r[k] for k in ("title", "url", "published", "yt_views", "yt_likes", "yt_comments", "ig_views")},
             "usual_views_on_this_channel": r["usual"], "description": package.get("description"),
             "script": package.get("script") or package.get("screenplay"), "publish_time_zone_of_numbers": "India (IST)",
             "youtube_analytics": analytics(channel, r["youtube_id"], r["published"][:10]),
             "other_shorts_on_this_channel": others}
    response = client.messages.parse(
        model=MODEL, max_tokens=16000, output_config={"effort": "high"}, tools=[WEB_SEARCH], output_format=Study,
        system=TEAM["Mr. Hope (breakout)"],
        messages=[{"role": "user", "content":
                   f"Channel: {channel['name']} (niche: {channel.get('niche')}; audience: {channel.get('audience')}).\n"
                   f"This Short broke out: {r['yt_views']} views against a usual {r['usual']:.0f}.\n\n"
                   + json.dumps(facts, ensure_ascii=False, indent=1, default=str)}])
    log_spend(_cost(MODEL, response.usage), r["channel"])
    return response.parsed_output


def run(rows: list) -> list:
    """Study every new breakout in the dashboard's rows and save them; returns the new study ids."""
    from agents import DAILY_BUDGET, _channels, spent_today
    studies, channels = load(), {c["id"]: c for c in _channels()}
    new = []
    for r in find(rows, studies, datetime.now()):
        if spent_today() >= DAILY_BUDGET or r["channel"] not in channels:
            continue
        print(f"Breakout on {r['channel']}: {r['title']} ({r['yt_views']} views, usual {r['usual']:.0f}); studying it")
        try:
            s = study(r, rows, channels[r["channel"]])
        except Exception as e:  # one failed study shouldn't stop the dashboard
            print(f"::warning::Breakout study of {r['title']} failed: {str(e)[:300]}")
            continue
        sid = topic_id(r["channel"], r["youtube_id"])
        studies[sid] = {"channel": r["channel"], "title": r["title"], "url": r["url"], "views": r["yt_views"],
                        "usual": r["usual"], "studied": f"{datetime.now():%Y-%m-%d %H:%M}", **s.model_dump()}
        new.append(sid)
    if new:
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(studies, ensure_ascii=False, indent=1), encoding="utf-8")
        from state import save
        save([str(FILE.relative_to(HERE))])
    return new


def demo():
    now = datetime(2026, 10, 27, 20)
    row = lambda i, v, ch="yt-x", day=27: {"id": i, "channel": ch, "youtube_id": i, "yt_views": v, "published": f"2026-10-{day:02} 10:00"}
    rows = [row("a", 1036), row("b", 615), row("c", 12), row("d", 8), row("e", 40), row("f", 900, "yt-y"), row("g", 5000, day=1)]
    hits = [r["id"] for r in find(rows, {}, now)]
    assert hits == ["a", "b"], hits  # f: no channel history; g: too old
    assert find(rows, {topic_id("yt-x", "a"): {}}, now)[0]["id"] == "b"  # already studied
    small = [row("s1", 78, "yt-s"), row("s2", 20, "yt-s"), row("s3", 9, "yt-s"), row("s4", 7, "yt-s"), row("s5", 0, "yt-s")]
    assert [r["id"] for r in find(small, {}, now)] == ["s1"]  # Sawaal, 27 Oct: a breakout on a small channel
    print("ok")


if __name__ == "__main__" and sys.argv[1:] == ["--demo"]:
    demo()
