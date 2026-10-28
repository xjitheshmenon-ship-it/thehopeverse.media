"""Turn outbox packages into videos and upload them to YouTube as public videos.

    python video.py            # every outbox package that has no video yet

Voice: ElevenLabs (ELEVENLABS_API_KEY), else free Microsoft Edge voices (edge-tts). All lines are joined into one
continuous voice track with a fixed pause between them, then laid under the finished picture, so lines never overlap or cut.
Pictures (always moving video, never still photos): a host talking on screen is a lip-synced Kling avatar video from fal.ai
(FAL_KEY), or HeyGen when HEYGEN_API_KEY is set; other shots are real stock footage from Pixabay (PIXABAY_API_KEY), else NASA, else an AI
clip from HeyGen Video (HEYGEN_API_KEY), else Kling.
Paid AI clips are capped per Short (AI_CLIPS_PER_SHORT) and by DAILY_BUDGET. Upload: needs client_secret.json from Google Cloud (see README).

Dub channels: every new Short is also re-voiced for each channel in channels.json with a "lang" (e.g. Hindi), reusing
the same footage, once that channel is signed in:  python video.py --connect hi

Series channels (series.py writes one Hindi episode a day) bring their own scenes and cast; sign in once with
python video.py --connect <channel id>
"""
import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import textwrap
import threading
import time
import urllib.parse
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from pathlib import Path

import edge_tts
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, ImageClip, VideoFileClip, vfx
from moviepy.config import FFMPEG_BINARY
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from agents import DAILY_BUDGET, HELPER_MODEL, WEB_SEARCH, _cost, OUTBOX, TEAM, _channels, client, log_spend, read_cast, spent_today
from approve import approved
import predict

HERE = Path(__file__).parent
VOICE = os.environ.get("HOPE_VOICE", "en-US-AndrewNeural")
PORTRAIT_MODEL = "fal-ai/flux-pro/v1.1-ultra"  # about $0.06, once per host; raw mode looks like a real photo, not a render
HOST_MODEL = "fal-ai/flux-pro/kontext"  # about $0.04; the host's face from their reference photo, posed for the shot
# That pose then talks, lip-synced to the line: HeyGen Avatar IV when HEYGEN_API_KEY is set, else (or if it fails) Kling.
AVATAR_MODEL = "fal-ai/kling-video/ai-avatar/v2/standard"  # $0.0562 a second
VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/text-to-video"  # $0.35 per 5 s clip, when stock footage has nothing
ACT_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"  # $0.35 per 5 s: a series character acting, no lines
AI_CLIPS = int(os.environ.get("AI_CLIPS_PER_SHORT") or "3")  # paid AI video shots per Short; the rest is free stock
SCENE_WORKERS = int(os.environ.get("SCENE_WORKERS") or "6")  # scenes made at once
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL") or "eleven_multilingual_v2"  # speaks English and Hindi
# ElevenLabs voice ids. Change them in GitHub > Settings > Secrets and variables > Actions > Variables:
# ELEVEN_VOICE_ARJUN, ELEVEN_VOICE_MEERA (any character by name), or ELEVEN_VOICE_MALE / ELEVEN_VOICE_FEMALE for the rest.
# Unset, a man's or woman's voice is picked from the account's voices: ElevenLabs' own studio voices first, in this order.
ELEVEN_PREFER = ("Brian", "Daniel", "George", "Sarah", "Alice", "Matilda")
# Steady, clean delivery: a lower similarity_boost stops a voice copying the noise of the recording it was made from.
ELEVEN_SETTINGS = {"stability": 0.55, "similarity_boost": 0.6, "style": 0.0, "use_speaker_boost": True}
GAP = 0.25  # seconds of quiet between two lines
RATE = 44100
HOSTS_DIR = HERE / "hosts"  # one reference photo per host, made once and then reused in every Short
# The two hosts in every Short. Change a look and delete hosts/<name>.png to give them a new face.
HOSTS = {
    "Arjun": {"voice": "en-IN-PrabhatNeural", "voice_hi": "hi-IN-MadhurNeural",
              "look": "Indian man, about 35, warm brown skin, short neat black hair, trimmed beard, "
                      "deep-teal field jacket over a white shirt"},
    "Meera": {"voice": "en-IN-NeerjaNeural", "voice_hi": "hi-IN-SwaraNeural",
              "look": "Indian woman, about 29, medium-brown skin, shoulder-length wavy black hair, "
                      "small gold earrings, rust-coloured kurta-style top"},
}
MUSIC_MODEL = "fal-ai/stable-audio-3/medium/base/text-to-audio"  # about $0.05 per track
MUSIC_VOLUME = 0.12  # background music level under the voice (1 = full)
STYLE = ("photorealistic, real people with natural skin texture, handheld smartphone footage at eye level, natural "
         "overcast daylight, documentary style, vertical 9:16, not a cartoon, not an illustration, not CGI, not 3D, no text, no words")
SECRET, TOKEN = HERE / "client_secret.json", HERE / "token.json"
# Stock sites refuse Python's default user agent (HTTP 403), so every download identifies as a browser.
_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")]
urllib.request.install_opener(_opener)


class Scene(BaseModel):
    narration: str
    on_screen_text: str
    picture_search: str
    image_prompt: str
    speaker: str = ""  # Arjun or Meera (or the channel's own anchors): whose voice reads this line
    host_on_screen: bool = False  # True: the speaker is shown (from their reference photo), not stock footage
    on_screen: str = ""  # series: the character this shot shows when nobody is talking (e.g. during narration)
    photo: str = ""  # channels with "photos": a Wikimedia Commons search for a real photo or clip (a politician, a flag)


class Storyboard(BaseModel):
    scenes: list[Scene]


class DubLine(BaseModel):
    narration: str
    on_screen_text: str


class Dub(BaseModel):
    title: str
    description: str
    lines: list[DubLine]


def dub(path: Path, channel: dict) -> Path:
    """Write a translated copy of an outbox package for a dub channel; the scenes keep the original footage."""
    package = json.loads(path.read_text(encoding="utf-8"))
    board = Storyboard.model_validate_json((path.with_suffix("") / "board.json").read_text(encoding="utf-8"))
    out = client.messages.parse(
        model=HELPER_MODEL,
        max_tokens=16000,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content":
                   f"Adapt this YouTube Short for a {channel['language']} audience. Write natural, spoken "
                   f"{channel['language']} the way a popular creator from that audience talks, not a word-for-word "
                   "translation: keep the curiosity hook, swap examples or units for local ones where it helps, and "
                   "keep every fact true. Give one line per scene, in the same order, so it still matches the "
                   "footage; on_screen_text at most 8 words. Title under 100 characters, description with hashtags "
                   "ending in #Shorts.\n\nTitle: " + package["title"] + "\n\nDescription: " + package["description"]
                   + "\n\nScenes:\n" + json.dumps([[s.narration, s.on_screen_text] for s in board.scenes],
                                                    ensure_ascii=False)}],
        output_format=Dub,
    ).parsed_output
    scenes = [s.model_copy(update=line.model_dump()) for s, line in zip(board.scenes, out.lines)]
    target = path.with_suffix(f".{channel['lang']}.json")
    target.write_text(json.dumps({"channel_id": channel["id"], "title": out.title, "description": out.description,
                                  "dub_of": path.stem, "lang": channel["lang"], "scenes": [s.model_dump() for s in scenes],
                                  **{k: package[k] for k in ("footer", "category", "hosts", "photos") if k in package}},
                                 indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def storyboard(package: dict) -> Storyboard:
    """Ask Claude to cut the package into scenes the renderer can use."""
    a, b = list(package.get("hosts") or ("Arjun", "Meera"))[:2]
    return client.messages.parse(
        model=HELPER_MODEL,
        max_tokens=16000,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content":
                   "Split this video package into scenes for narration, following Mr. Cut's edit plan shot by shot: Mr. Pen "
                   "and Mr. Cut have already chosen which character and which background each shot shows. narration: "
                   "exactly what the voice says (only spoken words, no stage directions). on_screen_text: at most 8 words. "
                   "picture_search: Mr. Cut's footage search for the shot, or else 2-5 concrete words for real live-action "
                   "stock video of the literal subject of that line, the thing a viewer must see (e.g. 'rocket "
                   "launch night', 'astronaut training centrifuge', 'Mumbai street traffic'), never a mood or "
                   "metaphor and never a brand or mission name a stock site won't know (say 'Indian rocket launch', "
                   "not 'Gaganyaan'). "
                   "image_prompt: a photo-real description of the same shot (person, setting, camera angle); when a "
                   "recurring character appears, copy their look from the cast below word for word. Real footage only, "
                   "never cartoon. Never ask for a real, identifiable person in picture_search or image_prompt (no "
                   "politician, official or celebrity by name or likeness): show the place, building, crowd, document "
                   "or object instead, so no shot is a fake of a real person. "
                   + ("photo: when the line is about a named real person, party, flag, election symbol or landmark, a "
                      "2-5 word Wikimedia Commons search for a REAL photo or video of it (e.g. 'Narendra Modi 2024', "
                      "'Flag of the Bharatiya Janata Party', 'Rahul Gandhi rally', 'Parliament House New Delhi'), else "
                      "empty; use it on about half the scenes that aren't anchors talking. "
                      if package.get("photos") else "photo: always empty. ")
                   + ("speaker: always empty and host_on_screen always false: one narrator reads every line, in the "
                      f"package's own language, never {a} or {b}. picture_search stays in English. "
                      if package.get("lang") else
                      f"speaker: who says the line, {a} or {b} (the two hosts; use both in every Short). "
                      "host_on_screen: true when the shot shows that host talking (about every third scene, including "
                      "the first), then image_prompt describes only their pose, expression and setting. ") +
                   "It is a YouTube Short: keep it under 60 seconds "
                   "of narration.\n\nCast:\n" + read_cast.call({}) + "\n\nPackage:\n"
                   + json.dumps(package)}],
        output_format=Storyboard,
    ).parsed_output


def _font(size: int, lang: str = ""):
    # Arial has no Hindi letters; Nirmala UI ships with Windows and covers Devanagari.
    names = ("NirmalaB.ttf", "Nirmala.ttc", "Nirmala.ttf", "NotoSansDevanagari-Bold.ttf") if lang == "hi" else ()
    for name in names + ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def _pixabay(kind: str, query: str) -> list:
    """Search Pixabay's free library: kind is "videos/" for footage or "" for photos."""
    params = {"key": os.environ["PIXABAY_API_KEY"], "q": query[:100], "safesearch": "true", "per_page": 10,
              "video_type": "film", "image_type": "photo"}  # real footage and photos only, no animation
    url = f"https://pixabay.com/api/{kind}?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(url, timeout=20))["hits"]


def _nasa(scene: "Scene", query: str, used: set, work: Path):
    """A public-domain NASA clip (no key needed) that Claude agrees shows the shot, or None."""
    url = "https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": query, "media_type": "video", "page_size": 10})
    items = [it for it in json.load(urllib.request.urlopen(url, timeout=20))["collection"]["items"]
             if it["data"][0]["nasa_id"] not in used and it.get("links")]
    k = _pick(scene, [it["links"][0]["href"] for it in items])
    if k < 0:
        return None
    item = items[k]
    files = json.load(urllib.request.urlopen(urllib.parse.quote(item["href"], safe=":/~"), timeout=20))
    mp4 = next((f for size in ("~medium.mp4", "~small.mp4", "~mobile.mp4") for f in files if f.endswith(size)), None)
    if not mp4:
        return None
    used.add(item["data"][0]["nasa_id"])
    path = work / f"nasa-{len(used):03}.mp4"
    if not path.exists():  # ponytail: downloads the whole clip; long NASA videos can be 100+ MB
        urllib.request.urlretrieve(urllib.parse.quote(mp4, safe=":/~"), path)
    return path


credits = []  # Wikimedia Commons files used in the video being made, credited in its description


def _commons(scene: "Scene", size: tuple, duration: float, work: Path, used: set):
    """A real photo or clip from Wikimedia Commons (free licences, credited) that Claude agrees shows scene.photo,
    or None. Photos get a slow zoom, so the picture still moves."""
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrsearch": scene.photo, "gsrnamespace": 6,
        "gsrlimit": 10, "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1440})
    pages = json.load(urllib.request.urlopen(url, timeout=20)).get("query", {}).get("pages", {}).values()
    hits = [(p["title"], p["imageinfo"][0]) for p in sorted(pages, key=lambda p: p.get("index", 0))
            if p.get("imageinfo") and p["title"] not in used and p["imageinfo"][0].get("thumburl")
            and p["imageinfo"][0]["mime"].split("/")[0] in ("image", "video")
            and not (p["imageinfo"][0]["mime"].startswith("video") and p["imageinfo"][0].get("size", 0) > 80e6)]
    k = _pick(scene, [info["thumburl"] for _, info in hits])
    if k < 0:
        return None
    title, info = hits[k]
    used.add(title)
    meta = info.get("extmetadata", {})
    artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip() or "unknown"
    credits.append(f"{title[5:]} by {artist} ({meta.get('LicenseShortName', {}).get('value', 'see Commons')}), "
                   f"{info.get('descriptionurl', '')}")
    video = info["mime"].startswith("video")
    path = work / f"commons-{len(used):03}{Path(urllib.parse.urlparse(info['url'] if video else info['thumburl']).path).suffix}"
    if not path.exists():
        urllib.request.urlretrieve(info["url"] if video else info["thumburl"], path)
    if video:
        shots.append(path)
        return _clip(path, size, duration)
    photo = ImageClip(str(path)).with_duration(duration)
    s = max(size[0] / photo.w, size[1] / photo.h)
    photo = photo.resized(lambda t: s * (1 + 0.08 * t / duration))  # slow push-in
    return CompositeVideoClip([photo.with_position(("center", "center"))], size=size).with_duration(duration)


def _clip(path: Path, size: tuple, duration: float, skip: float = 0):
    """A stock or AI clip filling the frame for `duration` seconds, starting `skip` of the way in. ffmpeg cuts just
    that stretch and scales and centre-crops it to the frame once (Lanczos, near-lossless), so 4K footage stays sharp
    and costs no extra render time."""
    src = VideoFileClip(str(path))
    start = min(src.duration * skip, max(0, src.duration - duration))
    src.close()
    part = path.with_name(f"{path.stem}-{size[1]}p-{start:.2f}-{duration:.2f}.mp4")
    if not part.exists():
        w, h = size
        tmp = part.with_suffix(f".{threading.get_ident()}.mp4")  # scenes run in parallel and can share a shot
        subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}",
                        "-i", str(path), "-an", "-vf",
                        f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},setsar=1",
                        "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(tmp)],
                       check=True)
        os.replace(tmp, part)
    clip = VideoFileClip(str(part)).without_audio()
    if clip.duration < duration:
        clip = clip.with_effects([vfx.Loop(duration=duration)])
    return clip.subclipped(0, duration)


def host_photo(name: str) -> Path:
    """The host's reference photo, made once from their look so every Short shows the same person."""
    path = HOSTS_DIR / f"{name.lower()}-real.png"  # "-real": the old cartoonish photos are left unused
    if not path.exists():
        import fal_client
        HOSTS_DIR.mkdir(exist_ok=True)
        result = fal_client.subscribe(PORTRAIT_MODEL, arguments={
            "prompt": f"Candid head-and-shoulders photo of an {HOSTS[name]['look']}, friendly, looking at the camera, "
                      f"soft daylight. {STYLE}", "aspect_ratio": "3:4", "raw": True})
        urllib.request.urlretrieve(result["images"][0]["url"], path)
        paid["usd"] += 0.06
    return path


paid = {"clips": 0, "usd": 0.0, "blank": 0, "limit": AI_CLIPS}  # spending (fal.ai, footage checks) of the video being made; render() resets it
shots = []  # stock clips already matched in this video, reused when nothing else fits a later line


_paying = threading.Lock()


def _can_pay() -> bool:
    """Reserve one AI clip if the video's cap and DAILY_BUDGET allow it. Scenes are made in parallel, so the
    check and the count happen together."""
    with _paying:
        if paid["clips"] < paid["limit"] and spent_today() + paid["usd"] < DAILY_BUDGET:
            paid["clips"] += 1
            return True
        return False


def _image(url: str) -> dict:
    """A thumbnail sent as data: Claude can't fetch Pixabay's thumbnail links itself ("Unable to download")."""
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        return {"type": "base64", "media_type": r.headers.get_content_type(), "data": base64.b64encode(r.read()).decode()}


def _pick(scene: "Scene", thumbnails: list) -> int:
    """Claude looks at the candidate clips' thumbnails and returns the index of the one that really shows what the
    line is about, or -1 when none does, so a car never stands in for a rocket."""
    if not thumbnails:
        return -1
    try:
        response = client.messages.create(model=HELPER_MODEL, max_tokens=200, thinking={"type": "between_tools"}, messages=[{"role": "user", "content": [
            *({"type": "image", "source": _image(u)} for u in thumbnails),
            {"type": "text", "text": f"These are {len(thumbnails)} stock video thumbnails, numbered 0 to "
             f"{len(thumbnails) - 1} in order. A YouTube Short says: \"{scene.narration}\" and this shot should "
             f"show: {scene.picture_search} ({scene.image_prompt}). Reply with only the number of the thumbnail that "
             "clearly shows that subject. Reply -1 if none does: a generic or loosely related picture (a car for a "
             "rocket, a random city for a named place, the wrong country) counts as none."}]}])
        paid["usd"] += _cost(HELPER_MODEL, response.usage)
        k = int(re.search(r"-?\d+", next(b.text for b in response.content if b.type == "text")).group())
        return k if k < len(thumbnails) else -1
    except Exception as e:  # can't check: take the search's best match, as before
        print(f"    could not check the footage: {e}")
        return 0


def _stock(scene: "Scene", query: str, size: tuple, duration: float, work: Path, used: set):
    """A real Pixabay clip for the query that Claude agrees shows the shot, or None."""
    hits = [v for v in _pixabay("videos/", query) if v["id"] not in used and v["videos"]["medium"].get("thumbnail")]
    k = _pick(scene, [v["videos"]["medium"]["thumbnail"] for v in hits])
    if k < 0:
        return None
    video = hits[k]
    used.add(video["id"])
    path = work / f"clip-{video['id']}.mp4"
    if not path.exists():
        # 4K when Pixabay has it: a landscape 1080p clip cropped to a vertical frame is blown up over 2x and looks soft
        urllib.request.urlretrieve(video["videos"]["large"]["url"] or video["videos"]["medium"]["url"], path)
    shots.append(path)
    return _clip(path, size, duration)


def _heygen_upload(file: Path) -> str:
    """Put a file in HeyGen's own storage, so HeyGen shots don't depend on fal.ai. Returns its asset id."""
    boundary = "hopeverse" + os.urandom(8).hex()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".wav": "audio/wav"}.get(file.suffix, "audio/mpeg")
    data = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n").encode() + file.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request("https://api.heygen.com/v3/assets", data=data, headers={
        "x-api-key": os.environ["HEYGEN_API_KEY"].strip(), "Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req, timeout=120))["data"]["asset_id"]


def _heygen_wait(url: str, path: Path) -> float:
    """Poll a HeyGen job until done, save the video to path and return its length in seconds."""
    headers = {"x-api-key": os.environ["HEYGEN_API_KEY"].strip()}
    for _ in range(90):  # usually a few minutes
        time.sleep(10)
        video = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60))["data"]
        if video["status"] == "completed":
            urllib.request.urlretrieve(video["video_url"], path)
            return video.get("duration") or 0
        if video["status"] in ("failed", "cancelled"):
            raise RuntimeError(video.get("failure_message") or video.get("failure_code"))
    raise RuntimeError("HeyGen took over 15 minutes")


def heygen_clip(prompt: str, path: Path, image: Path = None) -> float:
    """A 5 s silent-use shot from HeyGen Video ($0.018 a second at 768p): from the prompt alone, or starting on
    image (a character acting). Saves it to path and returns its cost in dollars."""
    body = {"model": "heygen-video-1", "prompt": prompt + " No music, no dialogue, no logos or printed words.",
            "duration": 5, "resolution": "768p"}
    body.update({"mode": "image_to_video", "image": {"type": "asset_id", "asset_id": _heygen_upload(image)}} if image
                else {"mode": "text_to_video", "aspect_ratio": "9:16"})
    req = urllib.request.Request("https://api.heygen.com/v3/models/videos", data=json.dumps(body).encode(), headers={
        "x-api-key": os.environ["HEYGEN_API_KEY"].strip(), "Content-Type": "application/json"})
    video_id = json.load(urllib.request.urlopen(req, timeout=60))["data"]["video_id"]
    return 0.018 * (_heygen_wait(f"https://api.heygen.com/v3/models/videos/{video_id}", path) or 5)


def heygen(still: Path, audio: Path, path: Path) -> float:
    """The still talks, lip-synced to the line, with HeyGen's Avatar IV ($0.05 a second, HEYGEN_API_KEY).
    Saves the video to path and returns its length in seconds."""
    headers = {"x-api-key": os.environ["HEYGEN_API_KEY"].strip(), "Content-Type": "application/json"}
    body = {"type": "image", "image": {"type": "asset_id", "asset_id": _heygen_upload(still)},
            "audio_asset_id": _heygen_upload(audio), "aspect_ratio": "9:16", "title": path.stem}
    req = urllib.request.Request("https://api.heygen.com/v3/videos", data=json.dumps(body).encode(), headers=headers)
    video_id = json.load(urllib.request.urlopen(req, timeout=60))["data"]["video_id"]
    return _heygen_wait(f"https://api.heygen.com/v3/videos/{video_id}", path)


def _pose(scene: "Scene", name: str, i: int, work: Path, talking: bool) -> Path:
    """A photo of that host or character, same face and clothes, posed for this shot (Kontext)."""
    import fal_client
    still = work / f"host-{i:03}.png"
    if not still.exists():
        result = fal_client.subscribe(HOST_MODEL, arguments={
            "prompt": f"The same person, same face, hair and clothes: {scene.image_prompt}. "
                      f"{'Looking at the camera. ' if talking else ''}{STYLE}",
            "image_url": fal_client.upload_file(str(host_photo(name))), "aspect_ratio": "9:16"})
        urllib.request.urlretrieve(result["images"][0]["url"], still)
        paid["usd"] += 0.04
    return still


def background(scene: "Scene", i: int, audio: Path, size: tuple, duration: float, work: Path, used: set,
               cast_only: bool = False):
    """Moving video only: the host really talking (HeyGen or Kling), else Pixabay footage, else NASA
    footage (stock only when Claude agrees it shows the line), else a Kling AI clip, else Pixabay for a shorter
    search, else more of a clip this video already uses, else a plain colour.
    cast_only (a series): every shot shows one of its characters, talking or acting, never stock footage."""
    query = scene.picture_search
    if scene.host_on_screen and scene.speaker in HOSTS and (os.environ.get("HEYGEN_API_KEY") or os.environ.get("FAL_KEY")):
        path = work / f"avatar-{audio.stem}.mp4"  # per language, since the lips follow the voice
        if path.exists() or _can_pay():
            try:
                if not path.exists():
                    try:
                        still = _pose(scene, scene.speaker, i, work, talking=True)
                    except Exception as e:  # fal.ai down or out of credit: their usual photo still talks
                        print(f"    no posed photo ({e}); using {scene.speaker}'s reference photo")
                        still = host_photo(scene.speaker)
                    import fal_client
                    if os.environ.get("HEYGEN_API_KEY"):
                        try:
                            paid["usd"] += 0.05 * (heygen(still, audio, path) or duration)
                        except Exception as e:  # Kling below still gives a talking shot
                            print(f"    HeyGen failed ({e} {getattr(e, 'read', lambda: b'')()[:200]!r}); using Kling")
                    if not path.exists():
                        result = fal_client.subscribe(AVATAR_MODEL, arguments={
                            "image_url": fal_client.upload_file(str(still)),
                            "audio_url": fal_client.upload_file(str(audio)),
                            "prompt": "A real person talking naturally to the camera, small head and hand movements"})
                        urllib.request.urlretrieve(result["video"]["url"], path)
                        paid["usd"] += 0.0562 * (result.get("duration") or duration)
                shots.append(path)
                return _clip(path, size, duration)
            except Exception as e:
                print(f"    no talking shot of {scene.speaker}: {e}")
    actor = scene.on_screen if scene.on_screen in HOSTS else scene.speaker
    if cast_only and actor in HOSTS and (os.environ.get("HEYGEN_API_KEY") or os.environ.get("FAL_KEY")):
        path = work / f"act-{i:03}.mp4"  # no lips to match, so dubs reuse it
        if path.exists() or _can_pay():
            try:
                if not path.exists():
                    prompt = f"{scene.image_prompt}. Natural, subtle real movement, cinematic drama scene. {STYLE}"
                    try:
                        still = _pose(scene, actor, i, work, talking=False)
                    except Exception as e:  # fal.ai down or out of credit: their usual photo acts
                        print(f"    no posed photo ({e}); using {actor}'s reference photo")
                        still = host_photo(actor)
                    if os.environ.get("HEYGEN_API_KEY"):
                        try:
                            paid["usd"] += heygen_clip(prompt, path, image=still)
                        except Exception as e:  # Kling below
                            print(f"    HeyGen Video failed ({e} {getattr(e, 'read', lambda: b'')()[:200]!r}); using Kling")
                    if not path.exists():
                        import fal_client
                        result = fal_client.subscribe(ACT_MODEL, arguments={  # 5 s, looped if the line is longer
                            "prompt": prompt, "image_url": fal_client.upload_file(str(still)),
                            "duration": "5", "negative_prompt": "cartoon, anime, CGI, plastic skin, text, blur, talking"})
                        urllib.request.urlretrieve(result["video"]["url"], path)
                        paid["usd"] += 0.35
                shots.append(path)
                return _clip(path, size, duration)
            except Exception as e:
                print(f"    no acting shot of {actor}: {e}")
    if scene.photo:
        try:
            if clip := _commons(scene, size, duration, work, used):
                return clip
        except Exception as e:
            print(f"    no Commons picture for '{scene.photo}': {e}")
    if os.environ.get("PIXABAY_API_KEY") and not cast_only:
        try:
            if clip := _stock(scene, query, size, duration, work, used):
                return clip
        except Exception as e:  # missing footage is not worth losing the video over
            print(f"    no footage for '{query}': {e}")
    try:
        path = None if cast_only else _nasa(scene, query, used, work)
        if path:
            shots.append(path)
            return _clip(path, size, duration, skip=0.2)  # skip NASA title cards at the start
    except Exception as e:
        print(f"    no NASA footage for '{query}': {e}")
    if os.environ.get("HEYGEN_API_KEY") or os.environ.get("FAL_KEY"):
        path = work / f"ai-{i:03}.mp4"  # no lips to match, so dubs reuse it
        if path.exists() or _can_pay():
            try:
                if not path.exists():
                    if os.environ.get("HEYGEN_API_KEY"):  # HeyGen Video first: about $0.09 a clip against Kling's $0.35
                        try:
                            paid["usd"] += heygen_clip(f"{scene.image_prompt}. {STYLE}", path)
                        except Exception as e:
                            print(f"    HeyGen Video failed ({e} {getattr(e, 'read', lambda: b'')()[:200]!r}); using Kling")
                    if not path.exists():
                        import fal_client
                        result = fal_client.subscribe(VIDEO_MODEL, arguments={  # 5 s, looped if the line is longer
                            "prompt": f"{scene.image_prompt}. {STYLE}", "duration": "5", "aspect_ratio": "9:16",
                            "negative_prompt": "cartoon, anime, illustration, CGI, 3D render, plastic skin, text, blur"})
                        urllib.request.urlretrieve(result["video"]["url"], path)
                        paid["usd"] += 0.35
                shots.append(path)
                return _clip(path, size, duration)
            except Exception as e:
                print(f"    no AI video for this scene: {e}")
    if os.environ.get("PIXABAY_API_KEY") and len(query.split()) > 2 and not cast_only:
        try:
            if clip := _stock(scene, " ".join(query.split()[:2]), size, duration, work, used):
                return clip
        except Exception as e:
            print(f"    no footage for a shorter search: {e}")
    if shots:  # a later moment of a clip that already fits this video beats an off-topic one
        return _clip(shots[len(used) % len(shots)], size, duration, skip=0.5)
    paid["blank"] += 1
    return ColorClip(size, color=(12, 18, 48), duration=duration)


def caption(text: str, size: tuple, lang: str = "") -> np.ndarray:
    """Caption on a transparent layer, laid over the footage."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _font(size[0] // 14, lang)
    lines = textwrap.wrap(text, width=18)
    line_h = font.size + 16
    top = int(size[1] * 0.72) - line_h * len(lines) // 2
    draw.rectangle((0, top - 30, size[0], top + line_h * len(lines) + 30), fill=(0, 0, 0, 150))
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font)
        draw.text(((size[0] - w) / 2, top + i * line_h), line, font=font, fill="white")
    return np.array(img)


@cache
def eleven_voice(gender: str) -> str:
    """A voice id from the ElevenLabs account for "male" or "female" (ELEVEN_VOICE_MALE/FEMALE win), or ""."""
    if os.environ.get(f"ELEVEN_VOICE_{gender.upper()}"):
        return os.environ[f"ELEVEN_VOICE_{gender.upper()}"]
    if not os.environ.get("ELEVENLABS_API_KEY"):
        return ""
    try:
        req = urllib.request.Request("https://api.elevenlabs.io/v1/voices",
                                     headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"].strip()})
        voices = [v for v in json.load(urllib.request.urlopen(req, timeout=30))["voices"]
                  if (v.get("labels") or {}).get("gender") == gender]
        # ElevenLabs' own studio voices first: community library voices (e.g. Kreobox) carry their recording's
        # background hiss into every line. Then the preferred names, then Indian-accented ones.
        voices.sort(key=lambda v: (v.get("category") != "premade",
                                   next((i for i, n in enumerate(ELEVEN_PREFER) if v["name"].startswith(n)), 99),
                                   "indian" not in str(v.get("labels", {}).get("accent", "")).lower()))
        print(f"    ElevenLabs {gender} voice: {voices[0]['name'] if voices else 'none on the account'}")
        return voices[0]["voice_id"] if voices else ""
    except Exception as e:  # e.g. a key without "Voices: read" permission: use a premade voice
        print(f"    could not list ElevenLabs voices: {e}")
        return {"male": "nPczCjzI2devNBz1zQrb", "female": "21m00Tcm4TlvDq8ykWAM"}[gender]  # Brian, Rachel


def speak(text: str, voice: str, path: Path, pitch: str = "+0Hz", eleven: str = "", before: str = "",
          after: str = "") -> bool:
    """ElevenLabs when ELEVENLABS_API_KEY is set (the lines around this one keep the delivery flowing), else Edge.
    Edge's free voice service sometimes returns an empty or broken file, so check it and try again.
    Returns False if it never works, so the caller can drop that scene instead of losing the whole video."""
    if eleven and os.environ.get("ELEVENLABS_API_KEY"):
        try:
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{eleven}?output_format=mp3_44100_192",
                data=json.dumps({"text": text, "model_id": ELEVEN_MODEL, "voice_settings": ELEVEN_SETTINGS,
                                 "previous_text": before,
                                 "next_text": after}).encode(),
                headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"].strip(), "Content-Type": "application/json"})
            path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            return True
        except Exception as e:  # out of credits or a bad voice id: the free voice keeps the video coming
            print(f"    ElevenLabs failed ({e} {getattr(e, 'read', lambda: b'')()[:200]!r}); using Edge for this line")
    for attempt in range(6):  # about 2.5 minutes in all, so a short internet drop doesn't cost a scene
        try:
            asyncio.run(edge_tts.Communicate(text, voice, pitch=pitch).save(str(path)))
            AudioFileClip(str(path)).close()  # raises if ffmpeg can't read it
            return True
        except Exception as e:
            print(f"    voice failed ({e.__class__.__name__}), size {path.stat().st_size if path.exists() else 0} bytes")
            time.sleep(10 * (attempt + 1))
    print(f"    skipping this scene; the voice could not read: {text!r}")
    return False


def _wav(src: Path) -> bytes:
    """The line as 16-bit mono samples with the quiet at both ends cut, so lines join with exactly GAP between them."""
    trim = "silenceremove=start_periods=1:start_threshold=-50dB"
    out = src.with_suffix(".wav")
    subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-i", str(src), "-af", f"{trim},areverse,{trim},areverse",
                    "-ac", "1", "-ar", str(RATE), "-c:a", "pcm_s16le", str(out)], check=True)
    with wave.open(str(out)) as w:
        return w.readframes(w.getnframes())


def music(work: Path, seconds: float, mood: str = "") -> Path | None:
    """One background track per Short from fal.ai, in the mood set by "## Music" in team.md. Dubs reuse it."""
    path = work / "music.mp3"
    if path.exists() or not os.environ.get("FAL_KEY"):
        return path if path.exists() else None
    try:
        import fal_client
        result = fal_client.subscribe(MUSIC_MODEL, arguments={
            "prompt": mood or TEAM.get("Music", "mysterious, curious ambient underscore, no vocals"),
            "duration": min(seconds + 2, 380), "negative_prompt": "vocals, singing, speech"})
        urllib.request.urlretrieve(result["audio"]["url"], path)
        return path
    except Exception as e:  # no music is better than no video
        print(f"    no background music: {e}")
        return None


def render(package_path: Path, voice: str = VOICE) -> Path:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    size = (1440, 2560)  # vertical; YouTube streams 1440p+ uploads in its sharper codec (VP9), so Shorts look clearer
    lang = package_path.suffixes[0][1:] if len(package_path.suffixes) > 1 else package.get("lang", "")
    # A series episode's characters are shown and voiced the same way as the hosts.
    HOSTS.update({c["name"]: c for c in package.get("cast", [])})
    HOSTS.update(package.get("hosts", {}))  # a channel's own anchors (Sankalp, Sawaal)
    credits.clear()
    if "scenes" in package:  # a dub reuses the original's folder, so its footage is already downloaded
        board, work = Storyboard(scenes=package["scenes"]), OUTBOX / package.get("dub_of", package_path.stem)
        work.mkdir(exist_ok=True)
    else:
        board, work = storyboard(package), package_path.with_suffix("")
        work.mkdir(exist_ok=True)
        (work / "board.json").write_text(board.model_dump_json(), encoding="utf-8")
    prefix = f"{lang}-" if lang else ""
    logo = None
    # Channel watermark, top-left, clear of the Shorts buttons on the right: a channel's own "watermark" in
    # channels.json (Kissa), else logo.png (Hopeverse).
    mark = HERE / next((c.get("watermark", "logo.png") for c in _channels() if c["id"] == package.get("channel_id")),
                       "logo.png")
    if mark.exists():
        logo = ImageClip(str(mark), transparent=True).resized(width=200).with_opacity(0.85).with_position((80, 227))
    # A series shows its own characters in every shot, so its AI clips are capped only by DAILY_BUDGET.
    paid.update(clips=0, usd=0.0, blank=0, limit=10 ** 6 if package.get("cast") else AI_CLIPS)
    shots.clear()
    # 1. Every line into one voice track, back to back with GAP between them: nothing can overlap or cut off.
    lines, voice_track = [], work / f"{prefix}voice.wav"
    spoken = [(i, s) for i, s in enumerate(board.scenes) if any(ch.isalnum() for ch in s.narration)]
    with wave.open(str(voice_track), "wb") as track:
        track.setnchannels(1)
        track.setsampwidth(2)
        track.setframerate(RATE)
        for k, (i, scene) in enumerate(spoken):
            audio = work / f"{prefix}{i:03}.mp3"
            # Dubs keep their channel's voice; English lines are read by the host who says them.
            who = HOSTS.get(scene.speaker, {})
            if "dub_of" in package:  # the same anchor in the dub's language, else the channel's voice
                who = {**who, "voice": who.get(f"voice_{lang}", voice)}
            eleven = os.environ.get(f"ELEVEN_VOICE_{scene.speaker.upper()}") or eleven_voice(
                "female" if "woman" in who.get("look", "").lower() else "male")
            if lang not in ("", "hi"):  # ElevenLabs picks Indian-accented voices; French etc. keep the channel's Edge voice
                eleven = ""
            if not speak(scene.narration, who.get("voice", voice), audio, who.get("pitch", "+0Hz"), eleven,
                         spoken[k - 1][1].narration if k else "",
                         spoken[k + 1][1].narration if k + 1 < len(spoken) else ""):
                continue
            samples = _wav(audio)
            if not samples:
                continue
            start = track.tell() / RATE
            track.writeframes(samples + b"\0\0" * int(GAP * RATE))
            lines.append((i, scene, audio.with_suffix(".wav"), start, track.tell() / RATE))
    # 2. The picture for each line, silent, cut on whole frames so it never drifts from the voice. Scenes are made
    # in parallel: most of the time is spent waiting on HeyGen, fal.ai and the footage check, not on this machine.
    used = set()

    def make(line):
        i, scene, audio, start, end = line
        duration = (round(end * 30) - round(start * 30)) / 30
        layers = [background(scene, i, audio, size, duration, work, used, bool(package.get("cast"))),
                  ImageClip(caption(scene.on_screen_text, size, lang), transparent=True).with_duration(duration)]
        if logo:
            layers.append(logo.with_duration(duration))
        clip = CompositeVideoClip(layers, size=size).with_duration(duration)
        # Each scene is written to disk and closed straight away, so only a few scenes' footage is in memory.
        part = work / f"{prefix}scene-{i:03}.mp4"
        clip.write_videofile(str(part), fps=30, codec="libx264", audio=False, preset="slow",
                             ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p"], logger=None)  # high quality before YouTube re-encodes
        for c in (clip, *layers):
            c.close()
        print(f"    scene {i + 1}/{len(board.scenes)} ({time.time() - began:.0f} s)")
        return part

    began = time.time()
    with ThreadPoolExecutor(SCENE_WORKERS) as pool:
        parts = list(pool.map(make, lines))  # in line order, whatever order they finish in
    if paid["usd"]:  # counted in DAILY_BUDGET with the Claude costs
        log_spend(paid["usd"], package["channel_id"])
        print(f"    fal.ai video cost ${paid['usd']:.2f}")
    if credits:  # the description credits every Commons file, as their licences ask
        package["credits"] = list(dict.fromkeys(credits))
        package_path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    if paid["blank"] * 3 > len(lines):  # never post a Short that is mostly empty frames; the next run retries it
        raise RuntimeError(f"{paid['blank']} of {len(lines)} shots have no picture (is fal.ai out of credit?)")
    # 3. Picture, voice track and music put together once.
    out = package_path.with_suffix(".mp4")
    picture = work / f"{prefix}picture.mp4"
    listing = work / f"{prefix}scenes.txt"
    listing.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(picture)], check=True)
    track = music(work, lines[-1][4], package.get("music", ""))
    # Music loops if it's short and stops when the voice ends; the video is copied, only the sound is encoded.
    mix = (["-stream_loop", "-1", "-i", str(track), "-filter_complex",
            f"[2:a]volume={MUSIC_VOLUME}[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]", "-map", "[a]"]
           if track else ["-map", "1:a"])
    subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-i", str(picture), "-i", str(voice_track), *mix,
                    "-map", "0:v", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    return out


RELEVANCE_MIN = int(os.environ.get("RELEVANCE_MIN") or 60)  # the final script must score this much to be made and posted


class Relevance(BaseModel):
    score: int  # 0-100
    why: str    # one line
    views48: int  # predicted YouTube views after 48 hours (predict.py)


def relevance(package: dict, channel: dict) -> Relevance:
    """Score the finished Short just before it is made and posted (owner's rule 2026-10-27): is the story still current,
    does the script deliver what the title promises, does it fit the channel. Checked on the final script, which is
    what the video says, so a failing Short costs no render."""
    news = bool(channel.get("news") or channel.get("dub"))
    response = client.messages.parse(
        model=HELPER_MODEL, max_tokens=4000, output_config={"effort": "low"}, output_format=Relevance,
        tools=[{**WEB_SEARCH, "max_uses": 3}] if news else [],
        messages=[{"role": "user", "content":
                   f"Today is {time.strftime('%d %b %Y')}. This YouTube Short is about to be posted on {channel.get('name')} "
                   f"(niche: {channel.get('niche')}; audience: {channel.get('audience')}).\n"
                   f"Title: {package.get('title')}\nScript:\n{package.get('script')}\n\n"
                   + ("First web_search the story: is it still current, has anything newer changed or contradicted it? "
                      if news else "")
                   + "Score its relevance right now from 0 to 100: timeliness (0-30), fit for the channel's audience, "
                     "region and language (0-30), viewer demand today (0-25), and whether the script delivers what the "
                     "title promises without stale or wrong facts (0-15). A story overtaken by newer events, or a "
                     "script that doesn't match its title, scores under 50. why: one line.\n"
                   + predict.ASK + "\n" + predict.track(package["channel_id"])}])
    log_spend(_cost(HELPER_MODEL, response.usage), package["channel_id"])
    return response.parsed_output


def youtube(interactive: bool = True, token: Path = TOKEN, api: tuple = ("youtube", "v3")):
    """A signed-in YouTube API client. Upload, plus read-only access so Mr. Hope can see view counts.
    api=("youtubeAnalytics", "v2") gives the Analytics API with the same sign-in (youtube.readonly covers it)."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.readonly"]
    creds = Credentials.from_authorized_user_file(str(token), scopes) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid or not set(scopes) <= set(creds.scopes or []):
        if not interactive:
            raise RuntimeError("YouTube not connected yet; run python video.py once by hand")
        creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), scopes).run_local_server(port=0)
    token.write_text(creds.to_json())
    return build(*api, credentials=creds)


def channel_stats(token: Path) -> dict:
    """The channel's own all-time totals from YouTube: views, subscribers and public videos."""
    s = youtube(False, token).channels().list(part="statistics", mine=True).execute()["items"][0]["statistics"]
    return {"views": int(s.get("viewCount", 0)), "subscribers": int(s.get("subscriberCount", 0)),
            "videos": int(s.get("videoCount", 0))}


def watch_minutes(token: Path) -> int:
    """All-time minutes watched on the channel this token signs in to (YouTube Analytics, about 2 days behind)."""
    report = youtube(False, token, ("youtubeAnalytics", "v2")).reports().query(
        ids="channel==MINE", startDate="2020-01-01", endDate=time.strftime("%Y-%m-%d"),
        metrics="estimatedMinutesWatched").execute()
    return int((report.get("rows") or [[0]])[0][0])


def stats(video_ids: list) -> dict:
    """Views, likes, comments and upload time per uploaded video id."""
    items = youtube(interactive=False).videos().list(part="statistics,status,snippet", id=",".join(video_ids)).execute()
    return {i["id"]: {**i["statistics"], "privacy": i["status"]["privacyStatus"],
                      "published": i["snippet"]["publishedAt"]} for i in items["items"]}


def next_publish(times: list, tz: str, taken=(), now=None) -> str:
    """The next free one of a channel's local publish times ("19:30"), as UTC ISO for YouTube's publishAt; "" if it's
    under 20 minutes away (then post at once). Instinct: two at 5 AM Paris, two at francophone peak hours (owner, 27 Oct 2026)."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    now = now or datetime.now(ZoneInfo(tz))
    slots = sorted(now.replace(hour=int(h), minute=int(m), second=0, microsecond=0) + timedelta(days=d)
                   for d in (0, 1) for h, m in (x.split(":") for x in times))
    iso = lambda s: s.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    slot = next((s for s in slots if s > now and iso(s) not in taken), None)
    return "" if not slot or slot - now < timedelta(minutes=20) else iso(slot)


def upload(video: Path, package: dict, token: Path = TOKEN, channel: dict = None) -> str:
    """Upload as a public video (the owner chose public by default on 2026-10-25), or scheduled for the channel's
    next "publish_at" time (local to its "tz") when it has them."""
    from googleapiclient.http import MediaFileUpload

    footer = package.get("footer", TEAM.get("YouTube footer", ""))  # edit it in team.md
    if package.get("credits"):
        footer = "Photos and clips: Wikimedia Commons\n" + "\n".join(f"- {c}" for c in package["credits"]) + "\n\n" + footer
    tags = list(dict.fromkeys(["Hopeverse Media", "Shorts", *re.findall(r"#(\w+)", package["description"])]))
    while len(",".join(tags)) > 450:  # YouTube allows 500 characters of tags
        tags.pop()
    body = {"snippet": {"title": package["title"][:100],
                        # Mr. Spark often ends the description with the footer already: don't print it twice
                        "description": (package['description'] if footer.strip() in package['description']
                                        else f"{package['description']}\n\n{footer}").strip()[:5000],
                        "tags": tags, "categoryId": package.get("category", "25"),  # 25 = News & Politics
                        # tells YouTube who to show it to (French for Instinct, Hindi for dubs and Kissa)
                        "defaultLanguage": package.get("lang", "en"), "defaultAudioLanguage": package.get("lang", "en")},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    if (channel or {}).get("publish_at"):
        taken = {json.loads(p.read_text(encoding="utf-8")).get("publish_at") for p in OUTBOX.glob(f"{channel['id']}-*.json")}
        if when := next_publish(channel["publish_at"], channel.get("tz", "UTC"), taken):
            body["status"].update(privacyStatus="private", publishAt=when)  # YouTube makes it public at that time
            package["publish_at"] = when  # saved with the package by the caller, so the next Short takes the next slot
    request = youtube(token=token).videos().insert(
        part="snippet,status", body=body, media_body=MediaFileUpload(str(video), resumable=True))
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]


GRAPH = "https://graph.instagram.com/v21.0"


def _graph(path: str, method: str = "GET", **params) -> dict:
    params["access_token"] = os.environ["INSTAGRAM_TOKEN"]
    query = urllib.parse.urlencode(params)
    req = (urllib.request.Request(f"{GRAPH}/{path}", data=query.encode(), method="POST") if method == "POST"
           else f"{GRAPH}/{path}?{query}")
    return json.load(urllib.request.urlopen(req, timeout=60))


def instagram(video: Path, caption: str) -> str:
    """Post the video as an Instagram Reel (public), with Instagram Login: no Facebook Page needed.
    Instagram fetches the video from a public link, so it is first uploaded to fal.ai's file storage (FAL_KEY)."""
    import fal_client
    reel = video.with_name(f"{video.stem}-1080.mp4")  # the YouTube file is 1440p; Reels are shown at 1080p, max 25 Mbps
    subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-i", str(video), "-vf", "scale=1080:1920:flags=lanczos",
                    "-c:v", "libx264", "-crf", "18", "-maxrate", "20M", "-bufsize", "40M", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", str(reel)], check=True)
    url = fal_client.upload_file(str(reel))
    ig = _graph("me", fields="user_id")["user_id"]
    container = _graph(f"{ig}/media", "POST", media_type="REELS", video_url=url, caption=caption[:2200])["id"]
    for _ in range(60):  # Instagram processes the video before it can be published
        status = _graph(container, fields="status_code,status")
        if status["status_code"] == "FINISHED":
            return _graph(f"{ig}/media_publish", "POST", creation_id=container)["id"]
        if status["status_code"] == "ERROR":
            raise RuntimeError(f"Instagram rejected the video: {status.get('status')}")
        time.sleep(10)
    raise RuntimeError("Instagram took over 10 minutes to process the video")


if __name__ == "__main__":
    channels = {c["id"]: c for c in _channels()}
    if "--publish" in sys.argv:  # make a scheduled Short public now: python video.py --publish <youtube id>
        vid = sys.argv[sys.argv.index("--publish") + 1]
        path = next(p for p in OUTBOX.glob("*.json") if json.loads(p.read_text(encoding="utf-8")).get("youtube_id") == vid)
        package = json.loads(path.read_text(encoding="utf-8"))
        youtube(False, HERE / channels[package["channel_id"]].get("token", "token.json")).videos().update(
            part="status", body={"id": vid, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                                                       "containsSyntheticMedia": True}}).execute()
        package.pop("publish_at", None)  # frees its slot for the next Short
        path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
        sys.exit(print(f"Public now: https://youtu.be/{vid}"))
    if "--connect" in sys.argv:  # sign a channel in once: python video.py --connect hi (or a channel id)
        lang = sys.argv[sys.argv.index("--connect") + 1]
        c = next(c for c in channels.values() if lang in (c.get("lang"), c["id"]))
        print(f"Sign in and pick the {c['name']} channel in the browser.")
        youtube(token=HERE / c["token"])
        sys.exit()
    dubs = [c for c in channels.values() if c.get("status") == "dub" and (HERE / c["token"]).exists()]
    platform = {i: c["platform"] for i, c in channels.items()}
    quota_left, failed, posted = True, [], 0
    paths = sorted(OUTBOX.glob("*.json"))
    for path in paths:  # dubs made below are appended, so they go up in the same run
        package = json.loads(path.read_text(encoding="utf-8"))
        if "--only" in sys.argv and package["channel_id"] != sys.argv[sys.argv.index("--only") + 1]:
            continue  # e.g. python video.py --only yt-kissa: post just that channel's videos
        if package.get("held"):
            continue  # failed its relevance check: never made or posted
        video = path.with_suffix(".mp4")
        voice = channels.get(package["channel_id"], {}).get("voice", VOICE)
        dub_path = path.with_suffix(f".{channels.get(package['channel_id'], {}).get('dub')}.json")
        if "youtube_id" not in package and dub_path.exists() and "youtube_id" in json.loads(dub_path.read_text(encoding="utf-8")):
            continue  # a dub-only channel's English cut is never posted: once its dub is up, don't remake it every run
        home = channels.get(package["channel_id"], {})
        if ("youtube_id" not in package and "relevance" not in package and "dub_of" not in package
                and home.get("status") != "series" and "--no-upload" not in sys.argv):  # Kissa is fiction: no check
            try:
                r = relevance(package, home)
            except Exception as e:  # a broken check shouldn't block the day's videos
                print(f"    relevance check failed, posting anyway: {e}")
                r = None
            if r:
                package["relevance"] = {"score": r.score, "why": r.why, "views48": max(0, r.views48)}
                print(f"Relevance of {path.name}: {r.score}/100, about {r.views48} views in 48 h ({r.why})")
                if r.score < RELEVANCE_MIN:
                    package["held"] = f"relevance {r.score}/100 under {RELEVANCE_MIN}: {r.why}"
                path.write_text(json.dumps(package, indent=2), encoding="utf-8")
                if package.get("held"):
                    print(f"::warning::Not making {path.name}: {package['held']}")
                    from plan import redo
                    if os.environ.get("NEXT") == package["channel_id"] and redo(package["channel_id"]):
                        print("    this channel's video is made again with its next approved topic")
                        with open(os.environ.get("GITHUB_ENV", os.devnull), "a") as f:
                            f.write("MORE=1\n")
                    continue
        if not video.exists() and "youtube_id" not in package:  # cloud runs don't keep videos; never remake posted ones
            print(f"Making video for {path.name}")
            try:
                render(path, voice)
            except Exception as e:  # with many Shorts a day, one broken package shouldn't stop the rest
                print(f"    failed: {e}")
                failed.append(path.name)
                continue
            package = json.loads(path.read_text(encoding="utf-8"))  # render adds photo credits
        # Only Shorts made from now on have board.json, so older ones are never dubbed.
        # Hopeverse's dub channels get a copy. A channel with "dub" (Sankalp, Sawaal) posts only the dub: the agents
        # write in English and viewers see Hindi only (owner's call, 27 Oct).
        dub_only = bool(home.get("dub")) and "dub_of" not in package
        targets = (dubs if package["channel_id"] == "yt-hopeverse" else []) + \
                  ([{**home, "lang": home["dub"], "language": home.get("dub_language", home["dub"])}] if dub_only else [])
        for c in targets if "dub_of" not in package and (path.with_suffix("") / "board.json").exists() else []:
            if not path.with_suffix(f".{c['lang']}.json").exists():
                print(f"Making the {c['language']} version of {path.name}")
                try:
                    render(target := dub(path, c), c["voice"])
                    paths.append(target)
                except Exception as e:  # a failed dub shouldn't stop the English video
                    print(f"    {c['language']} version failed: {e}")
        if "--no-upload" in sys.argv or dub_only:  # the 4 PM run only makes videos; a dub-only Short posts just its dub
            continue
        if "youtube_id" not in package and not approved(package):
            print(f"Not posting {path.name}: not approved on Telegram")
            continue
        if platform.get(package["channel_id"]) == "youtube" and "youtube_id" not in package:
            if not quota_left:
                continue
            if not SECRET.exists():
                print("Skipping upload: client_secret.json not found (see README).")
                continue
            print(f"Uploading {video.name} to YouTube as public")
            try:
                package["youtube_id"] = upload(video, package, HERE / channels[package["channel_id"]].get("token", "token.json"),
                                               channels[package["channel_id"]])
            except Exception as e:  # the daily API quota fits about 6 uploads; the rest go up on the next run
                print(f"    upload failed: {e}")
                failed.append(path.name)
                quota_left = "quota" not in str(e).lower() and "uploadLimitExceeded" not in str(e)
                continue
            path.write_text(json.dumps(package, indent=2), encoding="utf-8")
            print(f"    https://youtu.be/{package['youtube_id']}")
            posted += 1
        if channels.get(package["channel_id"], {}).get("lang") or package["channel_id"] != "yt-hopeverse":
            # only Hopeverse Media cross-posts to its Instagram; dubs, series and other channels stay on YouTube
            continue
        # A video is cross-posted to Instagram once it is public on YouTube; set a YouTube video to
        # private in Studio to keep it off Instagram.
        if os.environ.get("INSTAGRAM_TOKEN") and "youtube_id" in package and "instagram_id" not in package:
            try:
                if stats([package["youtube_id"]]).get(package["youtube_id"], {}).get("privacy") == "public":
                    print(f"Posting {video.name} to Instagram as a Reel")
                    package["instagram_id"] = instagram(video, package["description"].replace("#Shorts", "").strip())
                    path.write_text(json.dumps(package, indent=2), encoding="utf-8")
                    print("    posted")
            except Exception as e:  # one failed Reel shouldn't stop the other videos
                print(f"    Instagram post failed: {e}")
    if failed and not posted:  # nothing went up: show the run as failed instead of a quiet green tick
        sys.exit(f"No video was posted; failed: {', '.join(failed)}")
