"""Plan the next uploads ahead, so the dashboard shows real topics and each slot makes the one planned for it.

    python plan.py             -> fill runs/plan.json: a topic for each of the next 6 slots of every signed-in channel
    python plan.py --next ID   -> print the topic planned for channel ID's next upload, and take it off the plan
    python plan.py --due       -> which channels post now (hope.yml's slot step), as KEY=value lines for $GITHUB_ENV

Hopeverse posts every 2 hours from 07:00 India time; other channels post 2 a day on slots counted from their "first" hour
(default 7) in their audience's time zone "tz" (default India),
set in channels.json: Instinct on Paris time, Kissa in the Indian evening.

hope.yml runs the first after every slot and passes the second to Mr. Hope (or series.py for Kissa), who still
checks that a news topic is fresh. Existing entries are kept; only empty slots are planned, by Mr. Focus (Sonnet).
"""
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from agents import (DAILY_BUDGET, HELPER_MODEL, HERE, OUTBOX, WEB_SEARCH, _channels, _cost, client, log_spend,
                    spent_today)

PLAN = HERE / "runs" / "plan.json"
IST = ZoneInfo("Asia/Kolkata")
SHORTS_PER_DAY = min(6, int(os.environ.get("SHORTS_PER_DAY") or 6))
SERIES_PER_DAY = int(os.environ.get("SERIES_PER_DAY") or 2)


def planned_slots(channel: dict) -> list:
    """Which of the six slots (1-6) post for this channel. Hopeverse Media posts SHORTS_PER_DAY; every other channel
    posts "per_day" (default 2, owner's pick 2026-10-26; Kissa SERIES_PER_DAY), spaced to end on its last slot."""
    if channel["platform"] != "youtube" or channel.get("status") not in ("live", "series"):
        return []
    if channel["id"] == "yt-hopeverse":
        return list(range(1, SHORTS_PER_DAY + 1))
    every = 6 // (channel.get("per_day") or (SERIES_PER_DAY if channel.get("status") == "series" else 2))
    return [s for s in range(1, 7) if (6 - s) % every == 0]


def live_channels() -> list:
    """Channels that post on a schedule and are signed in here."""
    return [c for c in _channels() if planned_slots(c) and (HERE / c.get("token", "token.json")).exists()]


def slot_start(channel: dict, n: int, day: datetime) -> datetime:
    """When slot n starts on `day` (a time in the channel's zone), in India time."""
    hour = channel.get("first", 7) + 2 * (n - 1)
    return day.replace(hour=hour, minute=0, second=0, microsecond=0).astimezone(IST)


def next_slots(channel: dict, k: int = 6, after: datetime = None) -> list:
    """The channel's next k (slot number, time) pairs after `after` (default now), India time."""
    after = after or datetime.now(IST)
    local = after.astimezone(ZoneInfo(channel.get("tz", "Asia/Kolkata")))
    out = [(n, slot_start(channel, n, local + timedelta(days=d))) for d in range(4) for n in planned_slots(channel)]
    return [(n, w) for n, w in out if w > after][:k]


def due(force: int = 0, now: datetime = None) -> dict:
    """What posts now: each channel's slot whose 2-hour window this is, once a day (runs/slots.jsonl, so a late
    schedule next to a backup run doesn't post twice). force = that slot for every channel (the manual 5 PM run)."""
    now, log = (now or datetime.now()).astimezone(IST), HERE / "runs" / "slots.jsonl"
    done = set(log.read_text(encoding="utf-8").splitlines()) if log.exists() else set()
    marks, shorts, env = [], [], {}
    for c in live_channels():
        local = now.astimezone(ZoneInfo(c.get("tz", "Asia/Kolkata")))
        slot = force or (local.hour - c.get("first", 7)) // 2 + 1
        mark = json.dumps({"slot": f"{local:%Y-%m-%d} {c['id']} {slot}"})
        if slot not in planned_slots(c) or mark in done and not force:
            continue
        marks.append(mark)
        if c.get("status") == "series":
            env["SERIES"] = "1"
        else:  # id:slot:review (Mr. Hope reviews the day after the channel's last Short)
            shorts.append(f"{c['id']}:{slot}:{int(slot == max(planned_slots(c)))}")
            if c["id"] == "yt-hopeverse":
                env["SLOT"] = str(slot)
    report = json.dumps({"report": f"{now:%Y-%m-%d}"})  # the daily report and channel idea, 5 PM India time
    if force == 6 or (now.hour - 7) // 2 + 1 == 6 and report not in done:
        marks.append(report)
        env["REPORT"] = "1"
    if shorts:
        env["DUE"] = " ".join(shorts)
    if marks:
        env["RAN"] = "1"
        log.parent.mkdir(exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write("".join(m + "\n" for m in marks))
    return env


def audience(slot: int) -> str:
    """Hopeverse Media: 4 of the 6 daily Shorts for India, the rest international (as hope.yml)."""
    return "Indian viewers" if slot * 3 <= SHORTS_PER_DAY * 2 else "the international market"


def load() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8")) if PLAN.exists() else {}


class Item(BaseModel):
    topic: str  # the Short's subject in one line, in English, specific (names, numbers), like a working title
    why: str    # one short line: why now / why it will get views


class Plan(BaseModel):
    items: list[Item]


def _ask(channel: dict, slots: list, taken: list) -> list:
    """Mr. Focus plans topics for these slots (its cost goes in history.jsonl)."""
    cid = channel["id"]
    if channel.get("status") == "series":
        story = json.loads((HERE / "series.json").read_text(encoding="utf-8")) if (HERE / "series.json").exists() else {}
        first = len(story.get("episodes", [])) + 1 + len(taken)
        task = (f"Plan the next {len(slots)} episodes of the Hindi micro web series {channel['name']}, starting at episode "
                f"{first}. Premise: {story.get('premise', '')}\n"
                f"Last episodes: {json.dumps(story.get('episodes', [])[-10:], ensure_ascii=False)}\n"
                f"Already planned: {taken}\nFor each, topic = 'Ep <n>: <one-line logline in English with the twist>'.")
        tools = []
    else:
        drafted = [json.loads(p.read_text(encoding="utf-8")).get("title", "") for p in sorted(OUTBOX.glob(f"{cid}-*.json"))][-40:]
        when = "\n".join(f"- {w:%a %d %b %H:%M} IST" + (f", for {audience(n)}" if cid == "yt-hopeverse" else "")
                         for n, w in slots)
        task = (f"Plan one YouTube Short for each of these upload slots of the channel {channel['name']} "
                f"(niche: {channel['niche']}; audience: {channel['audience']}):\n{when}\n"
                f"Already made, don't repeat: {drafted}\nAlready planned: {taken}\n"
                + ("Current affairs: first run web_search for the top India and world news of the last 24-48 hours. "
                   "Every topic must name one specific, real, dated story you found (who, what, a number), never a "
                   "category like 'top headline'. Pick the stories with the most interest for each slot's audience."
                   if cid == "yt-hopeverse" else "Evergreen, well-sourced topics with a strong curiosity hook."))
        tools = [WEB_SEARCH] if cid == "yt-hopeverse" else []
    response = client.messages.parse(model=HELPER_MODEL, max_tokens=8000,
                                     output_config={"effort": "medium" if tools else "low"},
                                     tools=tools, output_format=Plan,
                                     messages=[{"role": "user", "content": task + f"\nReturn exactly {len(slots)} items, in slot order."}])
    cost = _cost(HELPER_MODEL, response.usage)
    log_spend(cost, cid)
    searched = getattr(getattr(response.usage, "server_tool_use", None), "web_search_requests", 0) or 0
    if tools and not searched:  # news topics planned without looking at the news are guesses: leave the slots open
        raise RuntimeError(f"planned without searching the news (${cost:.2f})")
    return response.parsed_output.items[:len(slots)]


def refresh() -> dict:
    plan, now = load(), datetime.now(IST)
    for c in live_channels():
        whens = next_slots(c)
        keep = {e["when"]: e for e in plan.get(c["id"], []) if e["when"] in {f"{w:%Y-%m-%d %H:%M}" for _, w in whens}}
        empty = [(n, w) for n, w in whens if f"{w:%Y-%m-%d %H:%M}" not in keep]
        if empty and spent_today() < DAILY_BUDGET:
            try:
                items = _ask(c, empty, [e["topic"] for e in keep.values()])
                for (n, w), it in zip(empty, items):
                    keep[f"{w:%Y-%m-%d %H:%M}"] = {"when": f"{w:%Y-%m-%d %H:%M}", "topic": it.topic, "why": it.why,
                                                   "planned": f"{now:%Y-%m-%d %H:%M}"}
            except Exception as e:  # a failed plan shouldn't stop the run; the slot then picks its own topic
                print(f"    planning {c['id']} failed: {e}")
        plan[c["id"]] = sorted(keep.values(), key=lambda e: e["when"])
        print(f"{c['name']}: " + "; ".join(f"{e['when'][5:]} {e['topic']}" for e in plan[c["id"]]))
    PLAN.parent.mkdir(exist_ok=True)
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    return plan


def next_topic(cid: str) -> str:
    """Take the earliest planned topic for this channel off the plan and return it ("" if none)."""
    plan = load()
    entries = plan.get(cid) or []
    if not entries:
        return ""
    plan[cid] = entries[1:]
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    return entries[0]["topic"]


if __name__ == "__main__":
    if sys.argv[1:2] == ["--next"]:
        print(next_topic(sys.argv[2]))
    elif sys.argv[1:2] == ["--due"]:
        print("\n".join(f"{k}={v}" for k, v in due(int(sys.argv[3]) if sys.argv[2:3] == ["--force"] else 0).items()))
    else:
        refresh()
