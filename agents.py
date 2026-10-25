"""Utube: Mr. Hope, the primary agent, and the mini agents he directs.

    mr_hope       -> primary decision maker: picks channel names/niches, what to make, where
    focus         -> Mr. Focus, the researcher: today's 5 best topics, deep research, fact-checks
    cast          -> Mr. Cast: recurring characters (saved in characters.md)
    pen           -> Mr. Pen: hook and full script
    cut           -> Mr. Cut: shot-by-shot edit plan
    spark         -> Mr. Spark: titles, description, hashtags, thumbnail
    post          -> Mr. Post: manages channels in channels.json (Hope proposes, you create by hand)

Run:  python agents.py "Decide my first three channels and draft a video for one"
"""
import json
import os
import sys
from datetime import datetime
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
HISTORY = HERE / "runs" / "history.jsonl"
LOG = HERE / "runs" / f"{datetime.now():%Y-%m-%d_%H%M}.md"
WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
WEB_FETCH = {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 4}

# Hard spending cap per run, in US dollars. Change it with: setx HOPE_BUDGET 3
BUDGET = float(os.environ.get("HOPE_BUDGET", "2"))
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

client = anthropic.Anthropic()


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
    lessons = _sections(LESSONS).get(name)
    if lessons:
        system += "\n\nLessons Mr. Hope has learned from past runs (follow them):\n" + lessons
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
    return json.loads(CHANNELS.read_text()) if CHANNELS.exists() else []


@beta_tool
def list_channels() -> str:
    """List the YouTube channels and Instagram accounts the owner has set up, with niche and audience."""
    return json.dumps(_channels(), indent=2)


@beta_tool
def list_outbox() -> str:
    """List the titles of drafts already saved to the outbox, so you don't repeat a topic."""
    drafts = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OUTBOX.glob("*.json"))]
    return json.dumps([{"channel_id": d["channel_id"], "title": d["title"]} for d in drafts])


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
    path = OUTBOX / f"{channel_id}-{len(list(OUTBOX.glob(channel_id + '-*'))) + 1}.json"
    path.write_text(json.dumps(
        {"channel_id": channel_id, "title": title, "description": description, "script": script}, indent=2))
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
    shorts = [{"title": d["title"], "youtube_id": d.get("youtube_id"), **numbers.get(d.get("youtube_id"), {})}
              for d in drafts]
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


# ---------- sub-agents, exposed to Hope as tools ----------

@beta_tool
def focus(request: str) -> str:
    """Ask Mr. Focus, the researcher. Three kinds of request:
    "DAILY: <niche notes>" for today's 5 best video topics; a topic name to research it in depth;
    or "FACT-CHECK:" followed by a finished script to verify before it is queued.

    Args:
        request: "DAILY: ...", a topic to research, or "FACT-CHECK: <script>".
    """
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


HOPE = TEAM["Mr. Hope"]

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or (
        "Scheduled run: get today's 5 topics from Mr. Focus, check the outbox, then draft and queue "
        "the single best new YouTube Short for the live YouTube channel.")
    summary = run_agent("Mr. Hope", HOPE, goal, [list_channels, list_outbox, propose_channel, focus,
                                                 cast, pen, cut, spark, post],
                        effort="medium", model=MODEL)
    print(summary)
    HISTORY.parent.mkdir(exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "cost_usd": round(spent, 2)}) + "\n")
    cap, BUDGET = BUDGET, spent + 0.25  # ponytail: fixed $0.25 for the review; raise if lessons get cut off
    print(run_agent("Mr. Hope (review)", TEAM["Mr. Hope (review)"],
                    f"Today's run cost ${spent:.2f}. Mr. Hope's summary of today:\n\n{summary}",
                    [performance, read_lessons, save_lessons], effort="low", model=MODEL))
    print(f"\nEstimated cost of this run: ${spent:.2f} (cap ${cap:.2f} + $0.25 review)")
    print(f"Full scripts and research saved in {LOG}")
