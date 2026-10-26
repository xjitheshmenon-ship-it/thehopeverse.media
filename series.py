"""Mr. Pen (series): writes today's episode of the Hindi micro web series for the series channel in channels.json.

    python series.py    -> one new episode in outbox/, which video.py then makes and posts

The story so far (premise, cast with looks and voices, every episode's summary) is kept in series.json, so each
episode continues the last one. Instructions and the season idea are under "## Mr. Pen (series)" in team.md.
Delete series.json to start a new season.
"""
import json
import re
from pathlib import Path

from pydantic import BaseModel

from agents import DAILY_BUDGET, MODEL, OUTBOX, TEAM, _channels, _cost, client, log_spend, spent_today
from video import Scene

HERE = Path(__file__).parent
STORY = HERE / "series.json"
VOICES = "hi-IN-MadhurNeural (male) or hi-IN-SwaraNeural (female)"  # the two free Hindi Edge voices


class Character(BaseModel):
    name: str  # first name only, never Arjun or Meera (the Hopeverse hosts)
    role: str
    look: str
    voice: str
    pitch: str  # e.g. "-10Hz" for an older man, "+8Hz" for a younger woman, so two voices of one kind differ


class Episode(BaseModel):
    title: str
    description: str
    music: str
    summary: str
    premise: str
    cast: list[Character]
    scenes: list[Scene]


def write_episode() -> Path:
    channel = next(c for c in _channels() if c.get("status") == "series")
    story = json.loads(STORY.read_text(encoding="utf-8")) if STORY.exists() else {"premise": "", "cast": [], "episodes": []}
    n = len(story["episodes"]) + 1
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content":
                   f"Write episode {n} of the series for the YouTube channel {channel['name']}.\n\n"
                   f"Story so far:\n{json.dumps(story, ensure_ascii=False, indent=1)}\n\n"
                   "Return: title (Hindi in Devanagari, starting 'Ep " + str(n) + " |', under 90 characters); "
                   "description (2-3 gripping Hindi lines, then 3-5 hashtags ending with #Shorts); music (an English "
                   "prompt for the background score's mood, no vocals); summary (2 lines in English of what happens, "
                   "for the next episode); premise (the season's premise and arc in English, kept unless it must "
                   "change); cast (every character so far plus any new one: look in English, starting with "
                   f"'Indian man' or 'Indian woman' then age, face, hair and clothes; voice {VOICES}; pitch); scenes "
                   "(one per line of dialogue or narration: narration is the spoken Hindi in Devanagari, speaker is "
                   "the character's name or 'Narrator', on_screen_text the line's key words in Hindi (at most 8), "
                   "every shot shows one of the characters, never an empty setting: host_on_screen true when the "
                   "speaker is shown saying the line; on_screen the name of the character shown (for narration, "
                   "the one the line is about, doing what it describes); image_prompt a photo-real description of "
                   "that character's action, pose, expression and the setting, like a still from an Indian drama "
                   "series; picture_search 2-5 English words for the setting)."}],
        system=TEAM["Mr. Pen (series)"],
        output_format=Episode,
    )
    ep = response.parsed_output
    cost = _cost(MODEL, response.usage)
    for c in ep.cast:  # a voice or pitch Edge doesn't know would cost that character every line
        if c.voice not in ("hi-IN-MadhurNeural", "hi-IN-SwaraNeural"):
            c.voice = "hi-IN-SwaraNeural" if "woman" in c.look.lower() else "hi-IN-MadhurNeural"
        if not re.fullmatch(r"[+-]\d{1,2}Hz", c.pitch):
            c.pitch = "+0Hz"
    names = [c.name for c in ep.cast]
    for s in ep.scenes:
        s.speaker = s.speaker if s.speaker in names else ""  # the narrator uses the channel voice
        s.host_on_screen = bool(s.speaker)  # whoever speaks is seen speaking
        s.on_screen = s.on_screen if s.on_screen in names else s.speaker or names[0]  # someone is always in shot
    story = {"premise": ep.premise, "cast": [c.model_dump() for c in ep.cast],
             "episodes": story["episodes"] + [{"n": n, "title": ep.title, "summary": ep.summary}]}
    OUTBOX.mkdir(exist_ok=True)
    path = OUTBOX / f"{channel['id']}-{len(list(OUTBOX.glob(channel['id'] + '-*.json'))) + 1}.json"
    path.write_text(json.dumps({"channel_id": channel["id"], "title": ep.title, "description": ep.description,
                                "lang": channel["lang"], "category": "24",  # Entertainment
                                "footer": TEAM.get("Series footer", ""), "music": ep.music,
                                "cast": story["cast"], "scenes": [s.model_dump() for s in ep.scenes]},
                               indent=2, ensure_ascii=False), encoding="utf-8")
    STORY.write_text(json.dumps(story, indent=2, ensure_ascii=False), encoding="utf-8")
    log_spend(cost, channel["id"])  # counted in the spending report with the other runs
    print(f"Episode {n}: {ep.title} (${cost:.2f}) -> {path.name}")
    return path


if __name__ == "__main__":
    if spent_today() >= DAILY_BUDGET:
        raise SystemExit(f"Daily budget of ${DAILY_BUDGET:.2f} reached; no more episodes today.")
    write_episode()
