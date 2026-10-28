"""Mr. Pen (story): a true animal rescue or friendship story, re-enacted shot by shot with AI, for a channel.

    python story.py yt-instinct  -> one story Short in outbox/, which video.py then makes and posts

The format copies a viral rescue video (owner's pick, 28 Oct): one silent hero, the same human and animal in every
shot (posed from one reference photo each), handheld phone look, short storybook captions, time jumps, a callback
ending. Unlike Kissa it must be a real, documented story, since Instinct promises verifiable stories.
"""
import json
import sys
from pathlib import Path

from pydantic import BaseModel

from agents import DAILY_BUDGET, MODEL, OUTBOX, WEB_SEARCH, _channels, _cost, client, log_spend, next_outbox_path, spent_today
from series import Character
from video import Scene


class Story(BaseModel):
    source: str  # the real story: who, where, when, and the article it comes from
    title: str
    description: str
    music: str
    cast: list[Character]
    scenes: list[Scene]


def write_story(channel_id: str, topic: str = "") -> Path:
    """topic: a story the owner picked (e.g. "the Presidio owl that keeps returning to John Murnane"), else one is found."""
    channel = next(c for c in _channels() if c["id"] == channel_id)
    packages = {p: json.loads(p.read_text(encoding="utf-8")) for p in OUTBOX.glob(f"{channel_id}-*.json")}
    for p, package in packages.items():  # one story at a time: a story not posted yet is made again, not a new one
        if package.get("source") and "youtube_id" not in package and not package.get("held"):
            print(f"Story not posted yet, making it again: {p.name}")
            return p
    told = [package.get("source", "") for package in packages.values()]
    response = client.messages.parse(
        model=MODEL, max_tokens=16000, output_config={"effort": "medium"}, output_format=Story,
        tools=[WEB_SEARCH],
        messages=[{"role": "user", "content":
                   f"Write a YouTube Short for {channel['name']} ({channel['niche']}; audience: {channel['audience']}; "
                   f"language: {channel['language']}).\n\n"
                   + (f"First web_search this REAL story and confirm its facts and latest news: {topic}. "
                      if topic else
                      "First web_search for a REAL, well-documented story of a person rescuing a wild animal that later "
                      "came back or stayed bonded to them (like the penguin Dindim returning every year to the fisherman "
                      "who saved him in Brazil), reported by reliable outlets, from the last 12 months if possible: "
                      "fresh stories pass the relevance check. Not one already told: "
                      f"{[s for s in told if s] or 'none yet'}. ")
                   + "Keep to the facts and to any doubt the reports state; you may picture moments the reports "
                   "describe, never invent events.\n\n"
                   "Tell it the way viral rescue Shorts do: open on the animal in trouble within 3 seconds, one silent "
                   "hero the viewer follows, a ticking clock and a low point, relief, time jumps ('Quelques semaines "
                   "plus tard...', 'Un an après...'), and a callback ending where the animal returns. 10 to 14 shots, "
                   "45 to 60 seconds in all.\n\n"
                   f"Return: source (who, where, when, and the outlet and URL you used); title ({channel['language']}, "
                   "under 80 characters, a curiosity hook, ending with '(histoire vraie)' or its translation); "
                   f"description (2-3 {channel['language']} lines that say it is a true story re-enacted with AI and "
                   "name the source, then 3-5 hashtags ending with #Shorts); music (an English prompt for an "
                   "emotional score, no vocals); cast (exactly 2: the person and the animal. name: a first name, "
                   "or the animal's real name; look in English: for the person 'man' or 'woman' then nationality, "
                   "age, face, hair and clothes, one distinctive piece of clothing they always wear; for the animal "
                   "its species, age, size and markings; voice and pitch: any, nobody speaks on screen); scenes (one "
                   f"per shot, in order: narration one short storybook sentence in {channel['language']}, at most 12 "
                   "words, read by the narrator; speaker empty; on_screen_text the same sentence, shortened if it's "
                   "over 8 words; on_screen the cast name the camera is on; image_prompt the shot as handheld phone "
                   "footage at eye level: that character's action and expression, the place and light, each place "
                   "described the same way in every shot; picture_search 2-4 English words for the place)."}])
    story = response.parsed_output
    names = [c.name for c in story.cast]
    for s in story.scenes:  # narrated, and someone from the cast is always in shot
        s.speaker, s.host_on_screen = "", False
        s.on_screen = s.on_screen if s.on_screen in names else names[0]
    OUTBOX.mkdir(exist_ok=True)
    path = next_outbox_path(channel_id)
    path.write_text(json.dumps({"channel_id": channel_id, "title": story.title, "description": story.description,
                                "lang": channel["lang"], "category": channel.get("category", "15"),
                                "footer": channel.get("footer", ""), "music": story.music, "source": story.source,
                                "script": "\n".join(s.narration for s in story.scenes),  # what the relevance check reads
                                "cast": [c.model_dump() for c in story.cast],
                                "scenes": [s.model_dump() for s in story.scenes]}, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    cost = _cost(MODEL, response.usage)
    log_spend(cost, channel_id)
    print(f"Story: {story.title} (${cost:.2f}) -> {path.name}\n    source: {story.source}")
    return path


if __name__ == "__main__":
    if spent_today() >= DAILY_BUDGET:
        raise SystemExit(f"Daily budget of ${DAILY_BUDGET:.2f} reached; no story today.")
    write_story(sys.argv[1] if len(sys.argv) > 1 else "yt-instinct", " ".join(sys.argv[2:]))
