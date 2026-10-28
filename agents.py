"""Utube: Mr. Hope, the primary agent, and the mini agents he directs.

    mr_hope       -> primary decision maker: picks channel names/niches, what to make, where
    focus         -> Mr. Focus, the researcher: today's 5 best topics, deep research, fact-checks
    cast          -> Mr. Cast: recurring characters (saved in characters.md)
    pen           -> Mr. Pen: hook and full script
    cut           -> Mr. Cut: shot-by-shot edit plan
    spark         -> Mr. Spark: titles, description, hashtags, thumbnail
    post          -> Mr. Post: manages channels in channels.json (Hope proposes, you create by hand)
    grow          -> Mr. Grow: once a day (python agents.py --grow), turns the numbers and trends into runs/growth.md

Run:  python agents.py "Decide my first three channels and draft a video for one"
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
from anthropic import beta_tool

MODEL = "claude-opus-5-5"          # Mr. Hope: makes the decisions
HELPER_MODEL = "claude-sonnet-5-5"  # the mini agents: about half the price per token
HERE = Path(__file__).parent
CHANNELS = HERE / "channels.json"
OUTBOX = HERE / "outbox"
CAST = HERE / "characters.md"
TEAM_FILE = HERE / "team.md"
LESSONS = HERE / "lessons.md"  # Mr. Hope writes this himself after every run
GROWTH = HERE / "runs" / "growth.md"  # Mr. Grow rewrites this every morning; each agent gets its own section
HISTORY = HERE / "runs" / "history.jsonl"
SLOTS = HERE / "runs" / "slots.json"  # {channel id: ["HH:MM", ...]}: publish times Mr. Grow moved from channels.json
LOG = HERE / "runs" / f"{datetime.now():%Y-%m-%d_%H%M}.md"
WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 6}  # 3 ran out when the daily topics and a fact-check shared a call
WEB_FETCH = {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 4}

# Hard spending cap per run, in US dollars. Change it with: setx HOPE_BUDGET 3
BUDGET = float(os.environ.get("HOPE_BUDGET", "2"))
# Cap for the whole day across all runs (Shorts, series, channel idea). Set it as a repo variable in GitHub.
RAISED = {"2026-10-26": 50.0, "2026-10-27": 25.0}  # one-day raises the owner approved; the usual cap returns the next day
DAILY_BUDGET = max(RAISED.get(f"{datetime.now():%Y-%m-%d}", 0), float(os.environ.get("DAILY_BUDGET") or "20"))
# $ per million tokens: input, output, cache read, cache write
PRICES = {MODEL: (4, 20, 0.20, 5), HELPER_MODEL: (2, 10, 0.20, 2.5)}
spent = 0.0


def _cost(model: str, usage) -> float:
    i, o, cr, cw = PRICES[model]
    tools = getattr(usage, "server_tool_use", None)
    searches = (getattr(tools, "web_search_requests", 0) or 0) if tools else 0
    return ((usage.input_tokens or 0) * i + (usage.output_tokens or 0) * o
            + (usage.cache_read_input_tokens or 0) * cr + (usage.cache_creation_input_tokens or 0) * cw) / 1e6 \
        + searches * 0.01

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip() or None)  # a pasted secret often ends in a newline


def _sections(path: Path) -> dict:
    """Split a Markdown file into {heading: text} on "## <name>" headings."""
    if not path.exists():
        return {}
    team, name = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            team[name] = []
        elif name:
            team[name].append(line)
    return {k: "\n".join(v).strip() for k, v in team.items()}


# Each agent's instructions live in team.md under a "## <name>" heading, so they can be edited as text.
TEAM = _sections(TEAM_FILE)


def run_agent(name: str, system: str, prompt: str, tools: list, effort: str = "medium",
              model: str = HELPER_MODEL) -> str:
    """One agent = a system prompt + tools, driven by the SDK's tool runner. Output is saved to runs/."""
    global spent
    if spent >= BUDGET:
        return f"[budget of ${BUDGET:.2f} reached; stop now and summarize what you have]"
    print(f"... {name} is working (spent so far ${spent:.2f})", flush=True)
    own = TEAM.get(f"{name} ({os.environ.get('HOPE_CHANNEL')})")  # e.g. "## Mr. Pen (yt-sawaal)" in team.md
    if own:
        system += "\n\nRules for this channel (they win over the general rules above):\n" + own
    from breakout import rules  # changes from breakout studies the owner approved on the dashboard
    found = rules(os.environ.get("HOPE_CHANNEL", ""), name.split(" (")[0])
    if found:
        system += "\n\nLearned from this channel's breakout Shorts, approved by the owner (follow them):\n" + found
    lessons = _sections(LESSONS).get(name)
    if lessons:
        system += "\n\nLessons Mr. Hope has learned from past runs (follow them):\n" + lessons
    if name == "Mr. Hope":
        from state import notes
        recent = [n for n in notes(5) if n["at"] >= f"{datetime.now() - timedelta(days=2):%Y-%m-%d %H:%M}"]
        if recent:
            system += ("\n\nMessages from the owner, sent from the dashboard (India time; they win over lessons). "
                       "Follow them, and start your summary with a one-line reply to any you haven't answered yet:\n"
                       + "\n".join(f"- {n['at']}: {n['text']}" for n in recent))
    growth = _sections(GROWTH).get(name)
    if growth:
        system += "\n\nToday's growth notes from Mr. Grow (follow them):\n" + growth
    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=16000,
        system=system,
        tools=tools,
        output_config={"effort": effort},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        cache_control={"type": "ephemeral"},
        max_iterations=12,
        messages=[{"role": "user", "content": prompt}],
    )
    final = None
    for message in runner:
        final = message
        spent += _cost(model, message.usage)
        if spent >= BUDGET:
            print(f"!!! budget of ${BUDGET:.2f} reached, stopping", flush=True)
            break
    if final.stop_reason == "refusal":
        text = f"[declined: {final.stop_details.explanation if final.stop_details else 'no detail'}]"
    else:
        text = "".join(b.text for b in final.content if b.type == "text")
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"## {name}\n\n**Asked:** {prompt}\n\n{text}\n\n")
    return text


# ---------- channel manager tools (local state only) ----------

def _channels() -> list:
    """channels.json, with the publish times Mr. Grow has moved since (runs/slots.json, kept on the state branch)."""
    channels = json.loads(CHANNELS.read_text()) if CHANNELS.exists() else []
    moved = json.loads(SLOTS.read_text()) if SLOTS.exists() else {}
    return [{**c, "publish_at": moved[c["id"]]} if c["id"] in moved else c for c in channels]


@beta_tool
def set_publish_times(channel_id: str, times: list[str]) -> str:
    """Move a channel's daily publish times (24-hour "HH:MM", local to the channel's "tz"). Keep the same number
    of times, so the channel still posts as often; only move them when the views per slot show a better hour.

    Args:
        channel_id: The id of a channel from list_channels that has publish_at.
        times: The new local times, e.g. ["07:30", "20:00"].
    """
    channel = next((c for c in _channels() if c["id"] == channel_id), None)
    if not channel or not channel.get("publish_at"):
        return f"error: '{channel_id}' has no publish times"
    if len(times) != len(channel["publish_at"]) or not all(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", t) for t in times):
        return f"error: give {len(channel['publish_at'])} times as HH:MM"
    moved = json.loads(SLOTS.read_text()) if SLOTS.exists() else {}
    SLOTS.parent.mkdir(exist_ok=True)
    SLOTS.write_text(json.dumps({**moved, channel_id: sorted(times)}, indent=1))
    return f"{channel['name']} now publishes at {', '.join(sorted(times))} {channel.get('tz', 'UTC')}"


@beta_tool
def list_channels() -> str:
    """List the YouTube channels and Instagram accounts the owner has set up, with niche and audience."""
    return json.dumps(_channels(), indent=2)


@beta_tool
def list_outbox() -> str:
    """List the titles of drafts already saved to the outbox, so you don't repeat a topic."""
    drafts = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OUTBOX.glob("*.json"))]
    return json.dumps([{"channel_id": d["channel_id"], "title": d["title"]} for d in drafts])


def next_outbox_path(channel_id: str) -> Path:
    """The next free outbox file for a channel. Counting files reused a posted Short's number once a number was
    skipped (yt-hopeverse-12 was overwritten on 26 Oct), so take the highest number plus one."""
    nums = [int(p.stem.rsplit("-", 1)[1]) for p in OUTBOX.glob(f"{channel_id}-*.json") if p.stem.rsplit("-", 1)[1].isdigit()]
    return OUTBOX / f"{channel_id}-{max(nums, default=0) + 1}.json"


@beta_tool
def queue_post(channel_id: str, title: str, description: str, script: str) -> str:
    """Save a finished video package to the outbox for a channel. The outbox is a private review
    folder: nothing is published until the owner reviews and uploads it, so queue drafts freely.

    Args:
        channel_id: The id of a channel from list_channels.
        title: Video or reel title.
        description: Description / caption with hashtags.
        script: Full script and edit plan.
    """
    channel = next((c for c in _channels() if c["id"] == channel_id), None)
    if not channel:
        return f"error: unknown channel '{channel_id}'. Call list_channels."
    if channel.get("status") != "live":
        return f"error: '{channel_id}' is not live yet; the owner must create it by hand and set status to live."
    OUTBOX.mkdir(exist_ok=True)
    path = next_outbox_path(channel_id)
    path.write_text(json.dumps(
        {"channel_id": channel_id, "title": title, "description": description, "script": script,
         # a channel brings its language (Instinct), footer, YouTube category, anchors and photo rule (Sankalp, Sawaal)
         **{k: channel[k] for k in ("lang", "footer", "category", "hosts", "photos") if k in channel}}, indent=2, ensure_ascii=False))
    # ponytail: writes to outbox only; real upload needs YouTube Data API / Instagram Graph API OAuth per channel
    return f"queued at {path.name}"


@beta_tool
def propose_channel(channel_id: str, platform: str, name: str, niche: str, audience: str) -> str:
    """Decide a new channel. It is saved as needs_setup; the owner creates it by hand, then sets status to live.

    Args:
        channel_id: Short slug, e.g. "yt-tech".
        platform: "youtube" or "instagram".
        name: The channel or account name you chose.
        niche: What the channel covers.
        audience: Who it is for (age, region, language).
    """
    if platform not in ("youtube", "instagram"):
        return "error: platform must be youtube or instagram"
    channels = _channels()
    if any(c["id"] == channel_id for c in channels):
        return f"error: '{channel_id}' already exists"
    channels.append({"id": channel_id, "platform": platform, "name": name, "niche": niche,
                     "audience": audience, "status": "needs_setup", "url": ""})
    CHANNELS.write_text(json.dumps(channels, indent=2))
    return f"saved '{name}' as needs_setup"


@beta_tool
def performance() -> str:
    """Past Shorts with their YouTube views, likes and comments (once YouTube is connected), plus the cost of recent runs."""
    drafts = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OUTBOX.glob("*.json"))]
    ids = [d["youtube_id"] for d in drafts if d.get("youtube_id")]
    numbers, note = {}, ""
    if ids:
        try:
            from video import stats
            numbers = stats(ids)
        except Exception as e:
            note = f"Could not read YouTube numbers: {e}"
    else:
        note = "Nothing uploaded to YouTube yet, so there are no view counts."
    shorts = [{"channel_id": d["channel_id"], "title": d["title"], "youtube_id": d.get("youtube_id"),
               "scheduled_for": d.get("publish_at"), **numbers.get(d.get("youtube_id"), {})} for d in drafts]
    runs = HISTORY.read_text(encoding="utf-8").splitlines()[-14:] if HISTORY.exists() else []
    return json.dumps({"shorts": shorts, "recent_runs": [json.loads(r) for r in runs], "note": note}, indent=1)


@beta_tool
def read_lessons() -> str:
    """Read Mr. Hope's lessons file: strategy, business goals and per-agent lessons."""
    return LESSONS.read_text(encoding="utf-8") if LESSONS.exists() else "(no lessons yet)"


@beta_tool
def save_lessons(lessons: str) -> str:
    """Replace the lessons file. Pass the whole file, using "## Mr. Hope", "## Mr. Focus", "## Mr. Cast", "## Mr. Pen",
    "## Mr. Cut", "## Mr. Spark" and "## Mr. Post" headings: each agent automatically receives its own section.

    Args:
        lessons: The full lessons file in Markdown.
    """
    LESSONS.write_text(lessons, encoding="utf-8")
    return "saved"


# ---------- Perplexity search for Mr. Focus (optional: setx PERPLEXITY_API_KEY pplx-...) ----------

PPLX_KEY = os.environ.get("PERPLEXITY_API_KEY")


@beta_tool
def perplexity(query: str) -> str:
    """Search the live web with Perplexity. Returns a sourced answer with dated citations.

    Args:
        query: A specific question, e.g. "top trending tech news in India today with numbers".
    """
    global spent
    if spent >= BUDGET:
        return f"[budget of ${BUDGET:.2f} reached]"
    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        json.dumps({"model": "sonar", "messages": [{"role": "user", "content": query}]}).encode(),
        {"Authorization": f"Bearer {PPLX_KEY}", "Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=60))
    except Exception as e:
        return f"[perplexity failed: {e}; use web_search instead]"
    # Sonar: $1/M tokens + about $0.005 per request; use the API's own figure when it sends one
    spent += (r.get("usage", {}).get("cost") or {}).get("total_cost") or 0.006
    sources = r.get("search_results") or [{"url": u} for u in r.get("citations", [])]
    return r["choices"][0]["message"]["content"] + "\n\nSources:\n" + "\n".join(
        f"[{i}] {x.get('title', '')} {x.get('date', '')} {x['url']}" for i, x in enumerate(sources, 1))


# ---------- sub-agents, exposed to Hope as tools ----------

@beta_tool
def focus(request: str) -> str:
    """Ask Mr. Focus, the researcher. Three kinds of request:
    "DAILY: <niche notes>" for today's 5 best video topics; a topic name to research it in depth;
    or "FACT-CHECK:" followed by a finished script to verify before it is queued.

    Args:
        request: "DAILY: ...", a topic to research, or "FACT-CHECK: <script>".
    """
    if PPLX_KEY:
        return run_agent(
            "Mr. Focus",
            TEAM["Mr. Focus"] + "\n\nSearch with the perplexity tool first; use web_search only if it fails.",
            request, [perplexity, WEB_SEARCH, WEB_FETCH], effort="medium")
    return run_agent(
        "Mr. Focus",
        TEAM["Mr. Focus"],
        request, [WEB_SEARCH, WEB_FETCH], effort="medium")


@beta_tool
def read_cast() -> str:
    """Read the channel's recurring characters (names, looks, voices, personalities)."""
    if CAST.exists():
        return CAST.read_text(encoding="utf-8")
    return ("- The Hopeverse Navigator: the channel's narrator, a real person in their 30s in a dark jacket, "
            "shown in live-action footage looking up at the night sky.")


@beta_tool
def save_cast(cast: str) -> str:
    """Replace the recurring-character list. Pass the full list, including characters you kept unchanged.

    Args:
        cast: Every recurring character, in Markdown.
    """
    CAST.write_text(cast, encoding="utf-8")
    return "saved"


@beta_tool
def cast(brief: str) -> str:
    """Ask Mr. Cast, the character designer, which recurring characters appear in this video and how they look and sound.
    Call this before pen.

    Args:
        brief: Topic, channel and format of the video.
    """
    return run_agent(
        "Mr. Cast",
        TEAM["Mr. Cast"],
        brief, [read_cast, save_cast], effort="medium")


@beta_tool
def pen(brief: str) -> str:
    """Ask Mr. Pen, the script writer, for the full script.

    Args:
        brief: Topic, Mr. Focus's research, the characters, channel, format and length.
    """
    return run_agent(
        "Mr. Pen",
        TEAM["Mr. Pen"],
        brief, [], effort="medium")


@beta_tool
def cut(script: str) -> str:
    """Ask Mr. Cut, the video editor, for the edit plan of a finished script.

    Args:
        script: The final script, with format and characters.
    """
    return run_agent(
        "Mr. Cut",
        TEAM["Mr. Cut"],
        script, [], effort="medium")


@beta_tool
def spark(script: str) -> str:
    """Ask Mr. Spark for titles, description, hashtags and the thumbnail.

    Args:
        script: The final script, with channel and format.
    """
    return run_agent(
        "Mr. Spark",
        TEAM["Mr. Spark"],
        script, [], effort="medium")


@beta_tool
def post(task: str) -> str:
    """Ask Mr. Post, the channel manager, to look up channels or queue a finished video package for one.

    Args:
        task: What to do, e.g. "queue this package for the tech channel: ...".
    """
    return run_agent(
        "Mr. Post", TEAM["Mr. Post"],
        task, [list_channels, queue_post], effort="low")


@beta_tool
def raga(request: str) -> str:
    """Ask Mr. Raga, the music expert (Indian classical, folk, film, Qawwali and old Asian music), for
    music story ideas or facts to research. Each Short's background music is chosen by him automatically.

    Args:
        request: What you need, e.g. "3 Short ideas about ragas for Hopeverse Media".
    """
    return run_agent(
        "Mr. Raga",
        "\n\n".join([TEAM["Mr. Raga"]] + [(HERE / f).read_text(encoding="utf-8") for f in ("music.md", "music-theory.md")]),
        request, [], effort="low")


HOPE = TEAM["Mr. Hope"]
SPEND = HERE / "runs" / "spend-report.md"


def spent_today() -> float:
    today = f"{datetime.now():%Y-%m-%d}"
    runs = HISTORY.read_text(encoding="utf-8").splitlines() if HISTORY.exists() else []
    return sum(r["cost_usd"] for r in map(json.loads, filter(str.strip, runs)) if r["date"].startswith(today))


def log_spend(cost: float, channel: str = "") -> None:
    """Add a run's cost to history.jsonl; channel (a channels.json id, "" for shared work) feeds the dashboard."""
    HISTORY.parent.mkdir(exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "cost_usd": round(cost, 2),
                            "channel": channel}) + "\n")


def spend_report() -> str:
    """Write runs/spend-report.md from history.jsonl: today, last 7 days, this month and a daily table."""
    runs = [json.loads(r) for r in HISTORY.read_text(encoding="utf-8").splitlines() if r.strip()] \
        if HISTORY.exists() else []
    days = {}
    for r in runs:
        d = days.setdefault(r["date"][:10], [0, 0.0])
        d[0] += 1
        d[1] += r["cost_usd"]
    now = datetime.now()
    total = lambda keep: sum(c for day, (_, c) in days.items() if keep(datetime.strptime(day, "%Y-%m-%d")))
    lines = [f"# Hopeverse spending report, {now:%d %b %Y %H:%M}", "",
             f"- Today: ${days.get(f'{now:%Y-%m-%d}', [0, 0])[1]:.2f} ({days.get(f'{now:%Y-%m-%d}', [0])[0]} runs)",
             f"- Last 7 days: ${total(lambda d: (now - d).days < 7):.2f}",
             f"- This month: ${total(lambda d: (d.year, d.month) == (now.year, now.month)):.2f}",
             f"- All time: ${sum(c for _, c in days.values()):.2f}", "",
             "Claude (Anthropic) costs as estimated by agents.py, review included. Video images from fal.ai add",
             "about $0.006 each (about $0.06 a Short). Exact bills: console.anthropic.com and fal.ai/dashboard.", "",
             "| Day | Runs | Cost |", "| --- | --- | --- |"]
    lines += [f"| {day} | {n} | ${c:.2f} |" for day, (n, c) in sorted(days.items(), reverse=True)[:14]]
    ideas = sorted((HERE / "ideas").glob("*/kit.md"))  # scout.py writes one a day
    if ideas:
        lines += ["", f"## Today's new channel idea (folder ideas/{ideas[-1].parent.name})", "",
                  ideas[-1].read_text(encoding="utf-8").split("## Images")[0].strip()]
    try:
        import credits
        rows = credits.check()
        lines += ["", "## Credits left", ""] + [f"- **{w}** - top it up today" for w in credits.warnings(rows)] + \
            [f"- {r['service']}: {r['left'] if r['left'] is not None else '?'} {r['unit']} ({r['note']})" for r in rows]
    except Exception as e:  # the report matters more than the credits table
        lines += ["", f"Credits check failed: {e}"]
    owner = _sections(GROWTH).get("Owner")
    if owner:
        lines += ["", "## Mr. Grow's to-dos for you today", "", owner]
    leads = _sections(GROWTH).get("Leads")
    if leads:
        lines += ["", "## Sponsorship and collab leads", "", leads]
    SPEND.parent.mkdir(exist_ok=True)
    SPEND.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(lines)


if __name__ == "__main__":
    if spent_today() >= DAILY_BUDGET:
        sys.exit(f"Daily budget of ${DAILY_BUDGET:.2f} reached; no more Shorts today.")
    if sys.argv[1:] == ["--grow"]:
        notes = run_agent("Mr. Grow", TEAM["Mr. Grow"],
                          f"Today is {datetime.now():%A %d %B %Y}. Channels:\n{list_channels()}\n\n"
                          f"Yesterday's leads (don't repeat them):\n{_sections(GROWTH).get('Leads', 'none')}",
                          [performance, read_lessons, set_publish_times, *([perplexity] if PPLX_KEY else []), WEB_SEARCH])
        if "## " in notes:  # keep yesterday's notes if the run was cut off by the budget
            GROWTH.parent.mkdir(exist_ok=True)
            GROWTH.write_text(notes[notes.index("## "):], encoding="utf-8")
        log_spend(spent)
        print(notes)
        sys.exit()
    goal = " ".join(sys.argv[1:]) or (
        "Scheduled run: get today's 5 topics from Mr. Focus, check the outbox, then draft and queue "
        "the single best new YouTube Short for the live YouTube channel.")
    summary = run_agent("Mr. Hope", HOPE, goal, [list_channels, list_outbox, propose_channel, focus,
                                                 cast, pen, cut, spark, post, raga],
                        effort="medium", model=MODEL)
    print(summary)
    with (HERE / "runs" / "hope-said.jsonl").open("a", encoding="utf-8") as f:  # shown on the dashboard next to the owner's messages
        f.write(json.dumps({"at": f"{datetime.now():%Y-%m-%d %H:%M}", "channel": os.environ.get("HOPE_CHANNEL", ""),
                            "text": summary[:1500]}, ensure_ascii=False) + "\n")
    cap, BUDGET = BUDGET, spent + 0.25  # ponytail: fixed $0.25 for the review; raise if lessons get cut off
    if os.environ.get("HOPE_REVIEW") != "0":  # the daily loop reviews once, after the day's last Short
        print(run_agent("Mr. Hope (review)", TEAM["Mr. Hope (review)"],
                        f"Today's run cost ${spent:.2f}. Mr. Hope's summary of today:\n\n{summary}",
                        [performance, read_lessons, save_lessons], effort="low", model=MODEL))
    log_spend(spent, os.environ.get("HOPE_CHANNEL", ""))  # logged after the review so its cost is counted too
    print(f"\nEstimated cost of this run: ${spent:.2f} (cap ${cap:.2f} + $0.25 review)")
    print(spend_report())
    print(f"Full scripts and research saved in {LOG}")
