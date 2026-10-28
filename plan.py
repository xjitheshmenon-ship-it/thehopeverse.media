"""Plan the next uploads ahead, so the dashboard shows real topics and each video makes the one planned for it.

    python plan.py             -> fill runs/plan.json: a topic for each of the next 6 videos of every signed-in channel
    python plan.py --next ID   -> print the next topic the owner approved for channel ID, and take it off the plan
                                  (--any: the first planned one when none is approved, for Post now)
    python plan.py --due       -> the next video to make (hope.yml), as KEY=value lines for $GITHUB_ENV

From 4 AM India time (owner's change 2026-10-27; was 6 AM) hope.yml makes one video at a time, one channel after another in channels.json order, round
after round until each has its daily count (Hopeverse 6, the others 2); each run starts the next when it ends.
Mr. Hope (or series.py for Kissa) still checks that a news topic is fresh. Existing entries are kept; only empty
ones are planned, by Mr. Focus (Sonnet).

Owner's rule 2026-10-26: no script is written before the owner approves its topic on the dashboard (approvals.json,
see approve.yml). Since 2026-10-27 a topic Mr. Focus scored AUTO_OK (80) or more counts as approved until the owner
answers it; the owner's own approvals go first and a Reject still drops it. A channel whose topics all wait is
skipped and the next channel with an approved topic goes
instead; rejected topics are dropped and planned again. When nothing is approved the chain stops, and the next
approval starts it again.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from breakout import rules
from predict import ASK, track
from state import approvals, topic_id
from agents import (DAILY_BUDGET, HELPER_MODEL, HERE, OUTBOX, WEB_SEARCH, _channels, _cost, client, log_spend,
                    spent_today)

PLAN = HERE / "runs" / "plan.json"
IST = ZoneInfo("Asia/Kolkata")
SHORTS_PER_DAY = min(6, int(os.environ.get("SHORTS_PER_DAY") or 6))
SERIES_PER_DAY = int(os.environ.get("SERIES_PER_DAY") or 2)
START_HOUR = 4  # the chain starts 04:00 IST (hope.yml cron 30 22 UTC); owner's change 2026-10-27
STEP = 25  # minutes a video takes, roughly, for the dashboard's estimated times


def story_file(cid: str) -> Path:
    """A series channel's story so far: series.json for Kissa (the first), series-<id>.json for the others."""
    return HERE / ("series.json" if cid == "yt-kissa" else f"series-{cid}.json")


def planned_slots(channel: dict) -> list:
    """This channel's videos of the day, 1..its daily count: Hopeverse Media SHORTS_PER_DAY, every other channel
    "per_day" (default 2, owner's pick 2026-10-26; Kissa SERIES_PER_DAY). Since 2026-10-28 Hopeverse and Instinct
    post 4 a day (channels.json per_day, which overrides SHORTS_PER_DAY)."""
    if channel["platform"] != "youtube" or channel.get("status") not in ("live", "series"):
        return []
    if channel["id"] == "yt-hopeverse" and not channel.get("per_day"):
        return list(range(1, SHORTS_PER_DAY + 1))
    return list(range(1, (channel.get("per_day") or (SERIES_PER_DAY if channel.get("status") == "series" else 2)) + 1))


def live_channels() -> list:
    """Channels that post every day and are signed in here, in channels.json order (the order of each round)."""
    return [c for c in _channels() if planned_slots(c) and (HERE / c.get("token", "token.json")).exists()]


def day_order(channels: list = None) -> list:
    """The day's videos in making order: one video per channel, then the next round, until each channel has its
    count (owner's rule 2026-10-26: start early (4 AM IST since 2026-10-28), one video at a time). [(channel, n), ...]"""
    channels = live_channels() if channels is None else channels
    return [(c, n) for n in range(1, 7) for c in channels if n in planned_slots(c)]


def made_today(now: datetime = None) -> dict:
    """How many videos each channel has started today (runs/slots.jsonl, India date)."""
    now, log = (now or datetime.now()).astimezone(IST), HERE / "runs" / "slots.jsonl"
    counts = {}
    for line in log.read_text(encoding="utf-8").splitlines() if log.exists() else []:
        made = json.loads(line).get("made", "")
        if made.startswith(f"{now:%Y-%m-%d} "):
            cid = made.split()[1]
            counts[cid] = counts.get(cid, 0) + 1
    return counts


def next_slots(channel: dict, k: int = 6, after: datetime = None) -> list:
    """The channel's next k (n, estimated time) pairs, India time: the day starts at START_HOUR and a video takes about
    STEP minutes, so the estimate is the video's place in the day's order."""
    after = (after or datetime.now()).astimezone(IST)
    order, done = day_order(), made_today(after).get(channel["id"], 0)
    out = []
    for d in range(4):
        start = (after + timedelta(days=d)).replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
        out += [(n, start + timedelta(minutes=STEP * i)) for i, (c, n) in enumerate(order)
                if c["id"] == channel["id"] and (d or n > done)]
    return out[:k]


def due(now: datetime = None) -> dict:
    """The next video to make now, as KEY=value env for hope.yml, and mark it started so the next run moves on."""
    now, log = (now or datetime.now()).astimezone(IST), HERE / "runs" / "slots.jsonl"
    done, said, plan = made_today(now), approvals(), load()
    ready = {c["id"] for c in live_channels() if any(verdict(c["id"], e, said) in ("ok", "auto") for e in plan.get(c["id"], []))}
    left = [(c, n) for c, n in day_order() if n > done.get(c["id"], 0)]
    todo = [(c, n) for c, n in left if c["id"] in ready]  # skip channels whose topics still wait for the owner
    if not todo:
        if left:
            print(f"::notice::{len(left)} videos left today wait for topics approved on the dashboard", file=sys.stderr)
        return {"RAN": 1} if left else {}  # RAN: plan again, so rejected topics get new ones
    c, n = todo[0]
    log.parent.mkdir(exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"made": f"{now:%Y-%m-%d} {c['id']} {n}"}) + "\n")
    return {"NEXT": c["id"], "N": n, "QUOTA": len(planned_slots(c)), "REVIEW": int(n == len(planned_slots(c))),
            "SERIES": int(c.get("status") == "series"), "GROW": int(not done), "MORE": int(len(todo) > 1), "RAN": 1}


AUTO_OK = int(os.environ.get("AUTO_APPROVE_SCORE") or 80)  # owner's pick 2026-10-27: topics scoring this go ahead unapproved


def verdict(cid: str, e: dict, said: dict) -> str:
    """"ok" (the owner approved), "auto" (not yet answered but scored AUTO_OK or more), "no" (rejected) or ""."""
    v = said.get(topic_id(cid, e["topic"]), "")
    return v or ("auto" if e.get("score", 0) >= AUTO_OK else "")


def redo(cid: str, now: datetime = None) -> bool:
    """A Short failed its relevance check before upload: take back its "made" mark so the chain makes this channel's
    video again with its next approved topic. Once per channel a day, so a bad news day can't loop."""
    now, log = (now or datetime.now()).astimezone(IST), HERE / "runs" / "slots.jsonl"
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    mark = json.dumps({"redo": f"{now:%Y-%m-%d} {cid}"})
    mine = [i for i, l in enumerate(lines) if json.loads(l).get("made", "").startswith(f"{now:%Y-%m-%d} {cid} ")]
    if mark in lines or not mine:
        return False
    del lines[mine[-1]]
    log.write_text("\n".join(lines + [mark]) + "\n", encoding="utf-8")
    return True


def load() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8")) if PLAN.exists() else {}


class Item(BaseModel):
    topic: str  # the Short's subject in one line, in English, specific (names, numbers), like a working title
    why: str    # one short line: why now / why it will get views
    score: int  # relevance 0-100, see RUBRIC
    views48: int  # predicted YouTube views 48 hours after posting (predict.py checks it against the real ones)


RUBRIC = ("Give each topic a relevance score from 0 to 100, the sum of: timeliness, is it today's story (0-30); "
          "fit for this channel's audience, region and language (0-30); demand, are people searching and watching "
          "it right now (0-25); uniqueness, an angle the big outlets missed (0-15). Be strict: 80+ only for a "
          "fresh story with clear demand. The owner sees it next to the topic.")


class Plan(BaseModel):
    items: list[Item]


def _ask(channel: dict, slots: list, taken: list, rejected: list = ()) -> list:
    """Mr. Focus plans topics for these slots (its cost goes in history.jsonl)."""
    cid = channel["id"]
    if channel.get("status") == "series":
        story = json.loads(story_file(cid).read_text(encoding="utf-8")) if story_file(cid).exists() else {}
        first = len(story.get("episodes", [])) + 1 + len(taken)
        task = (f"Plan the next {len(slots)} episodes of the series {channel['name']} ({channel['niche']}), starting at episode "
                f"{first}. Premise: {story.get('premise', '')}\n"
                f"Last episodes: {json.dumps(story.get('episodes', [])[-10:], ensure_ascii=False)}\n"
                f"Already planned: {taken}\nFor each, topic = 'Ep <n>: <one-line logline in English with the twist>'.")
        tools = []
    else:
        drafted = [json.loads(p.read_text(encoding="utf-8")).get("title", "") for p in sorted(OUTBOX.glob(f"{cid}-*.json"))][-40:]
        when = "\n".join(f"- {w:%a %d %b %H:%M} IST" for n, w in slots)
        task = (f"Plan one YouTube Short for each of these upload slots of the channel {channel['name']} "
                f"(niche: {channel['niche']}; audience: {channel['audience']}):\n{when}\n"
                f"Already made, don't repeat: {drafted}\nAlready planned: {taken}\n"
                + (f"The owner rejected these, don't suggest them or anything like them: {list(rejected)}\n" if rejected else "")
                + ("Current affairs: first run web_search for the top news of the last 24-48 hours for this channel's audience. "
                   "Every topic must name one specific, real, dated story you found (who, what, a number), never a "
                   "category like 'top headline'. Follow the curiosity: for each, find the unique, little-known angle that "
                   "the big outlets missed (a surprising number, a hidden cause or consequence, a 'why does this happen' "
                   "question) and make that the topic; every topic a different story. Never plan a placeholder like 'no "
                   "verified story': if the news is thin, pick a well-sourced curious explainer instead."
                   if channel.get("news") else "Evergreen, well-sourced topics with a strong curiosity hook.")
                + (f"\nChannel rules: {channel['plan_note']}" if channel.get("plan_note") else "")
                + (f"\nLearned from this channel's breakout Shorts (owner-approved):\n{learned}" if (learned := rules(cid, "Mr. Focus")) else ""))
        tools = [WEB_SEARCH] if channel.get("news") else []
    response = client.messages.parse(model=HELPER_MODEL, max_tokens=8000,
                                     output_config={"effort": "medium" if tools else "low"},
                                     tools=tools, output_format=Plan,
                                     messages=[{"role": "user", "content": task + "\n" + RUBRIC + "\n" + ASK + "\n" + track(cid)
                                                + f"\nReturn exactly {len(slots)} items, in slot order."}])
    cost = _cost(HELPER_MODEL, response.usage)
    log_spend(cost, cid)
    searched = getattr(getattr(response.usage, "server_tool_use", None), "web_search_requests", 0) or 0
    if tools and not searched:  # news topics planned without looking at the news are guesses: leave the slots open
        raise RuntimeError(f"planned without searching the news (${cost:.2f})")
    return response.parsed_output.items[:len(slots)]


def refresh() -> dict:
    plan, now, said = load(), datetime.now(IST), approvals()
    rejected, old = plan.get("rejected", {}), f"{now - timedelta(hours=36):%Y-%m-%d %H:%M}"
    for c in live_channels():
        cid, whens, keep = c["id"], next_slots(c), []
        for e in plan.get(cid, []):
            v = said.get(topic_id(cid, e["topic"]))
            if v == "no":
                rejected[cid] = (rejected.get(cid, []) + [e["topic"]])[-20:]
            elif v == "ok" or ("score" in e and not (c.get("news") and e.get("planned", "") < old)):
                # unapproved news goes stale; unapproved topics planned before scores (27 Oct) are planned again with
                # one, so they can be auto-approved (otherwise they wait for the owner forever)
                keep.append(e)
        keep = sorted(keep, key=lambda e: ("ok", "auto", "").index(verdict(cid, e, said)))[:len(whens)]  # approved, then 80+, go first
        empty = whens[len(keep):]
        if empty and spent_today() < DAILY_BUDGET:
            try:
                items = _ask(c, empty, [e["topic"] for e in keep], rejected.get(cid, []))
                keep += [{"topic": it.topic, "why": it.why, "score": max(0, min(100, it.score)),
                          "views48": max(0, it.views48), "planned": f"{now:%Y-%m-%d %H:%M}"} for it in items]
            except Exception as e:  # a failed plan shouldn't stop the run; the next run plans again
                print(f"    planning {cid} failed: {e}")
        for (n, w), e in zip(whens, keep):  # estimated times, in making order
            e["when"] = f"{w:%Y-%m-%d %H:%M}"
        plan[cid] = keep
        print(f"{c['name']}: " + "; ".join(f"{e['when'][5:]} {e['topic']}" for e in plan[cid]))
    plan["rejected"] = rejected
    PLAN.parent.mkdir(exist_ok=True)
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    return plan


def next_topic(cid: str, any_: bool = False) -> str:
    """Take this channel's first approved topic off the plan and return it ("" if none); any_: else the first one."""
    plan, said = load(), approvals()
    entries = plan.get(cid) or []
    pick = next((e for v in ("ok", "auto") for e in entries if verdict(cid, e, said) == v), entries[0] if any_ and entries else None)
    if not pick:
        return ""
    entries.remove(pick)
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    return pick["topic"]


if __name__ == "__main__":
    if sys.argv[1:2] == ["--next"]:
        print(next_topic(sys.argv[2], "--any" in sys.argv))
    elif sys.argv[1:2] == ["--due"]:
        print("\n".join(f"{k}={v}" for k, v in due().items()))
    else:
        refresh()
