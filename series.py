"""Mr. Pen (series): writes today's episode for a series channel in channels.json (status "series").

    python series.py                 -> one new Kissa episode in outbox/, which video.py then makes and posts
    python series.py yt-unoreverse   -> the same for another series channel

The story so far (premise, cast with looks and voices, every episode's summary) is kept in series.json (Kissa) or
series-<channel id>.json, so each episode continues the last one. Instructions are under "## Mr. Pen (<channel id>)"
in team.md, else "## Mr. Pen (series)". Delete the story file to start a new season.
"""
import json
import re
import sys
from pathlib import Path

from pydantic import BaseModel

from agents import DAILY_BUDGET, next_outbox_path, MODEL, OUTBOX, TEAM, _channels, _cost, client, log_spend, spent_today
from breakout import rules
from plan import next_topic, story_file
from video import Scene

HERE = Path(__file__).parent
# The two free Edge voices (male, female) per channel language; English ones read in an Indian accent
VOICES = {"hi": ("hi-IN-MadhurNeural", "hi-IN-SwaraNeural"), "": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")}


class Character(BaseModel):
    name: str  # first name only, never Arjun or Meera (the Hopeverse hosts)
    role: str
    look: str
    voice: str
    pitch: str  # e.g. "-10Hz" for an older man, "+8Hz" for a younger woman, so two voices of one kind differ


class Episode(BaseModel):
    screenplay: str  # written first, so the shots follow a real script
    title: str
    description: str
    music: str
    summary: str
    premise: str
    cast: list[Character]
    scenes: list[Scene]


def write_episode(cid: str = "") -> Path:
    channel = next(c for c in _channels() if c.get("status") == "series" and c["id"] == (cid or c["id"]))
    STORY, lang = story_file(channel["id"]), channel.get("lang", "")
    tongue = channel.get("language", "Hindi") + (" in Devanagari" if lang == "hi" else "")  # Nima speaks English
    male, female = VOICES[lang]
    story = json.loads(STORY.read_text(encoding="utf-8")) if STORY.exists() else {"premise": "", "cast": [], "episodes": []}
    n = len(story["episodes"]) + 1
    planned = next_topic(channel["id"])  # the logline shown on the dashboard, from plan.py
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content":
                   f"Write episode {n} of the series for the YouTube channel {channel['name']}.\n\n"
                   f"Story so far:\n{json.dumps(story, ensure_ascii=False, indent=1)}\n\n"
                   + (f"Planned for this episode (follow it unless it breaks the story): {planned}\n\n" if planned else "")
                   +
                   "Return: screenplay (the episode as a proper film screenplay: scene headings like 'INT. "
                   "BAKERY - NIGHT', short English action lines, " + tongue + " dialogue under each character's "
                   "name; no narrator); title (" + channel.get("title_rule", f"Hindi in Devanagari, starting 'Ep {n} |'")
                   + ", under 90 characters); "
                   f"description (2-3 gripping {tongue} lines, then 3-5 hashtags ending with #Shorts); music (an English "
                   "prompt for the background score's mood, no vocals); summary (2 lines in English of what happens, "
                   "for the next episode); premise (the season's premise and arc in English, kept unless it must "
                   "change); cast (only the characters the season still needs, at most 4, the two leads first; drop "
                   "anyone the story no longer needs, add someone only if the story can't work without them; look "
                   "in English, starting with "
                   f"'Indian man' or 'Indian woman' then age, face, hair and clothes; voice {male} (male) or {female} "
                   "(female); pitch); scenes "
                   "(the screenplay cut into shots, one per line of dialogue, in order: narration is the line in "
                   f"{tongue}, speaker the character saying it (never a narrator), on_screen_text the line's key "
                   f"words in {tongue} (at most 8), on_screen the character the camera is on (the speaker, or the one "
                   "reacting to them); image_prompt a cinematic film still: camera framing (close-up, "
                   "over-the-shoulder, two-shot, low angle), that character's action and expression, the location "
                   "and light from the scene heading, described the same way in every shot of that scene; "
                   "picture_search 2-5 English words for the location)."}],
        system=TEAM.get(f"Mr. Pen ({channel['id']})", TEAM["Mr. Pen (series)"])  # a channel's own section first
        + (f"\n\nLearned from this channel's breakout episodes, approved by the owner "
           f"(follow them):\n{learned}" if (learned := rules(channel["id"])) else ""),
        output_format=Episode,
    )
    ep = response.parsed_output
    cost = _cost(MODEL, response.usage)
    for c in ep.cast:  # a voice or pitch Edge doesn't know would cost that character every line
        if c.voice not in (male, female):
            c.voice = female if "woman" in c.look.lower() else male
        if not re.fullmatch(r"[+-]\d{1,2}Hz", c.pitch):
            c.pitch = "+0Hz"
    names = [c.name for c in ep.cast]
    for s in ep.scenes:
        s.speaker = s.speaker if s.speaker in names else ""  # a stray line falls back to the channel voice
        s.on_screen = s.on_screen if s.on_screen in names else s.speaker or names[0]  # someone is always in shot
        s.host_on_screen = bool(s.speaker) and s.on_screen == s.speaker  # else a reaction shot, the voice off screen
    story = {"premise": ep.premise, "cast": [c.model_dump() for c in ep.cast],
             "episodes": story["episodes"] + [{"n": n, "title": ep.title, "summary": ep.summary}]}
    OUTBOX.mkdir(exist_ok=True)
    path = next_outbox_path(channel['id'])
    path.write_text(json.dumps({"channel_id": channel["id"], "title": ep.title, "description": ep.description,
                                **({"lang": lang} if lang else {}), "category": channel.get("category", "24"),  # Entertainment
                                "footer": channel.get("footer", TEAM.get("Series footer", "")), "music": ep.music,
                                "cast": story["cast"], "screenplay": ep.screenplay,
                                "scenes": [s.model_dump() for s in ep.scenes]},
                               indent=2, ensure_ascii=False), encoding="utf-8")
    STORY.write_text(json.dumps(story, indent=2, ensure_ascii=False), encoding="utf-8")
    log_spend(cost, channel["id"])  # counted in the spending report with the other runs
    print(f"Episode {n}: {ep.title} (${cost:.2f}) -> {path.name}")
    return path


if __name__ == "__main__":
    if spent_today() >= DAILY_BUDGET:
        raise SystemExit(f"Daily budget of ${DAILY_BUDGET:.2f} reached; no more episodes today.")
    write_episode(sys.argv[1] if len(sys.argv) > 1 else "")
