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
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

MODEL = "claude-opus-5-5"
HERE = Path(__file__).parent
CHANNELS = HERE / "channels.json"
OUTBOX = HERE / "outbox"
CAST = HERE / "characters.md"
LOG = HERE / "runs" / f"{datetime.now():%Y-%m-%d_%H%M}.md"
WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
WEB_FETCH = {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 8}

client = anthropic.Anthropic()


def run_agent(name: str, system: str, prompt: str, tools: list, effort: str = "medium") -> str:
    """One agent = a system prompt + tools, driven by the SDK's tool runner. Output is saved to runs/."""
    print(f"... {name} is working", flush=True)
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=system,
        tools=tools,
        output_config={"effort": effort},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    final = None
    for message in runner:
        final = message
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
        "You are Mr. Focus, the researcher at Hopeverse Media. Search the web, then open and read the primary "
        "sources (YouTube trending and top videos, official agencies, papers, original reporting), not just "
        "headlines. Note each source's date and prefer the newest.\n"
        "DAILY: find the most-viewed topics on YouTube today and the most valuable topics of the day (big "
        "news, real public interest, lasting value). Return exactly 5 topics that are clearly different from "
        "each other. For each: the topic, why it matters today, evidence of views or interest with a dated "
        "link, the best format (Short, long video or Reel), and a one-line video idea. Prefer topics that fit "
        "the niche you are given, and say when one doesn't.\n"
        "TOPIC: return key facts each with a dated source link, 3 angles that would hook viewers, open "
        "questions, and anything to avoid (misinformation, copyright, platform policy).\n"
        "FACT-CHECK: go claim by claim and mark each as correct, wrong (with the fix) or unverified.",
        request, [WEB_SEARCH, WEB_FETCH], effort="high")


@beta_tool
def read_cast() -> str:
    """Read the channel's recurring characters (names, looks, voices, personalities)."""
    return CAST.read_text(encoding="utf-8") if CAST.exists() else "(no characters yet)"


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
        "You are Mr. Cast, the character designer at Hopeverse Media. Call read_cast first and reuse existing characters "
        "so the channel keeps a consistent cast; add a new one only when the video truly needs it, then "
        "save_cast with the full list. Return the characters for this video: name, role, look (for AI image "
        "or animation tools), voice and personality, and how they appear on screen.",
        brief, [read_cast, save_cast], effort="medium")


@beta_tool
def pen(brief: str) -> str:
    """Ask Mr. Pen, the script writer, for the full script.

    Args:
        brief: Topic, Mr. Focus's research, the characters, channel, format and length.
    """
    return run_agent(
        "Mr. Pen",
        "You are Mr. Pen, the script writer at Hopeverse Media. Using only facts from the research you are given, write "
        "a hook for the first 3 seconds and the full script with timestamps, speaker names and on-screen text. "
        "Keep the tone hopeful and curious. Match the format: Shorts and Reels under 60 seconds.",
        brief, [], effort="high")


@beta_tool
def cut(script: str) -> str:
    """Ask Mr. Cut, the video editor, for the edit plan of a finished script.

    Args:
        script: The final script, with format and characters.
    """
    return run_agent(
        "Mr. Cut",
        "You are Mr. Cut, the video editor at Hopeverse Media. Turn the script into a shot-by-shot edit plan with "
        "timestamps: visuals, b-roll and where to get it legally (public-domain NASA footage, stock, AI-made), "
        "captions, music mood, sound effects, transitions and pacing. Label any AI or artist's-concept visuals.",
        script, [], effort="medium")


@beta_tool
def spark(script: str) -> str:
    """Ask Mr. Spark for titles, description, hashtags and the thumbnail.

    Args:
        script: The final script, with channel and format.
    """
    return run_agent(
        "Mr. Spark",
        "You are Mr. Spark, the thumbnail and title specialist at Hopeverse Media. Give 3 honest, clickable titles (no "
        "clickbait the video doesn't deliver), with your pick; a description with keywords and hashtags for "
        "YouTube and a caption for Instagram; and 2 thumbnail concepts (image, text of 4 words or fewer, colours).",
        script, [], effort="medium")


@beta_tool
def post(task: str) -> str:
    """Ask Mr. Post, the channel manager, to look up channels or queue a finished video package for one.

    Args:
        task: What to do, e.g. "queue this package for the tech channel: ...".
    """
    return run_agent(
        "Mr. Post", "You are Mr. Post. You manage the owner's YouTube channels and Instagram accounts. You cannot create channels or "
        "accounts; the owner creates them by hand. Use list_channels to see them and queue_post to queue "
        "finished content. Pick the best-fitting channel when not told.",
        task, [list_channels, queue_post], effort="low")


HOPE = (
    "You are Mr. Hope, the primary decision maker of a content studio that runs several YouTube channels "
    "and Instagram accounts under the owner's one primary account. You decide which channels exist, "
    "their names and niches, and what each one publishes. Delegate: focus (Mr. Focus) for "
    "research: start each run with a DAILY request for today's 5 topics, pick one and ask focus to research "
    "it. Then, in order: cast (Mr. Cast) for the characters, pen (Mr. Pen) for the script (give it the "
    "research and cast), focus with FACT-CHECK: plus the script, and fix anything wrong; then cut "
    "and spark on the final script. Finally ask post to queue the whole package "
    "(script, edit plan, cast, titles, thumbnail). "
    "Check list_channels and list_outbox first; never repeat a drafted topic. "
    "To start a new channel, research the niche, then call propose_channel; "
    "the owner creates it by hand, so only queue posts for channels with status live. Finish with a "
    "short summary of what you decided, any channels the owner must create, and what was queued."
)

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or (
        "Scheduled run: get today's 5 topics from Mr. Focus, check the outbox, then draft and queue "
        "the single best new post for one live channel.")
    print(run_agent("Mr. Hope", HOPE, goal, [list_channels, list_outbox, propose_channel, focus,
                                          cast, pen, cut, spark,
                                          post],
                    effort="high"))
    print(f"\nFull scripts and research saved in {LOG}")
