"""Turn outbox packages into videos and upload them to YouTube as public videos.

    python video.py            # every outbox package that has no video yet

Voice: ElevenLabs (ELEVENLABS_API_KEY), else free Microsoft Edge voices (edge-tts). All lines are joined into one
continuous voice track with a fixed pause between them, then laid under the finished picture, so lines never overlap or cut.
Pictures (always moving video, never still photos): a host talking on screen is a lip-synced Kling avatar video from fal.ai
(FAL_KEY); other shots are real stock footage from Pixabay (PIXABAY_API_KEY), else a Kling AI video clip, else NASA (no key).
Paid AI clips are capped per Short (AI_CLIPS_PER_SHORT) and by DAILY_BUDGET. Upload: needs client_secret.json from Google Cloud (see README).

Dub channels: every new Short is also re-voiced for each channel in channels.json with a "lang" (e.g. Hindi), reusing
the same footage, once that channel is signed in:  python video.py --connect hi

Series channels (series.py writes one Hindi episode a day) bring their own scenes and cast; sign in once with
python video.py --connect <channel id>
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request
import wave
from datetime import datetime
from pathlib import Path

import edge_tts
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, ImageClip, VideoFileClip, vfx
from moviepy.config import FFMPEG_BINARY
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from agents import DAILY_BUDGET, HELPER_MODEL, HISTORY, OUTBOX, TEAM, _channels, client, read_cast, spent_today
from approve import approved

HERE = Path(__file__).parent
VOICE = os.environ.get("HOPE_VOICE", "en-US-AndrewNeural")
PORTRAIT_MODEL = "fal-ai/flux-pro/v1.1-ultra"  # about $0.06, once per host; raw mode looks like a real photo, not a render
HOST_MODEL = "fal-ai/flux-pro/kontext"  # about $0.04; the host's face from their reference photo, posed for the shot
AVATAR_MODEL = "fal-ai/kling-video/ai-avatar/v2/standard"  # $0.0562 a second: that pose talks, lip-synced to the line
VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/text-to-video"  # $0.35 per 5 s clip, when stock footage has nothing
AI_CLIPS = int(os.environ.get("AI_CLIPS_PER_SHORT") or "3")  # paid AI video shots per Short; the rest is free stock
ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL") or "eleven_multilingual_v2"  # speaks English and Hindi
# ElevenLabs voice ids. Change them in GitHub > Settings > Secrets and variables > Actions > Variables:
# ELEVEN_VOICE_ARJUN, ELEVEN_VOICE_MEERA (any character by name), or ELEVEN_VOICE_MALE / ELEVEN_VOICE_FEMALE for the rest.
ELEVEN_MALE = os.environ.get("ELEVEN_VOICE_MALE") or "nPczCjzI2devNBz1zQrb"  # Brian (premade)
ELEVEN_FEMALE = os.environ.get("ELEVEN_VOICE_FEMALE") or "EXAVITQu4vr4xnVq9mPl"  # Sarah (premade)
GAP = 0.25  # seconds of quiet between two lines
RATE = 44100
HOSTS_DIR = HERE / "hosts"  # one reference photo per host, made once and then reused in every Short
# The two hosts in every Short. Change a look and delete hosts/<name>.png to give them a new face.
HOSTS = {
    "Arjun": {"voice": "en-IN-PrabhatNeural",
              "look": "Indian man, about 35, warm brown skin, short neat black hair, trimmed beard, "
                      "deep-teal field jacket over a white shirt"},
    "Meera": {"voice": "en-IN-NeerjaNeural",
              "look": "Indian woman, about 29, medium-brown skin, shoulder-length wavy black hair, "
                      "small gold earrings, rust-coloured kurta-style top"},
}
MUSIC_MODEL = "fal-ai/stable-audio-3/medium/base/text-to-audio"  # about $0.05 per track
MUSIC_VOLUME = 0.12  # background music level under the voice (1 = full)
STYLE = ("photorealistic, real people with natural skin texture, shot on a cinema camera, natural light, documentary "
         "style, vertical 9:16, not a cartoon, not an illustration, not CGI, not 3D, no text, no words")
SECRET, TOKEN = HERE / "client_secret.json", HERE / "token.json"
LOGO = HERE / "logo.png"  # replace this file to change the watermark
# Stock sites refuse Python's default user agent (HTTP 403), so every download identifies as a browser.
_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")]
urllib.request.install_opener(_opener)


class Scene(BaseModel):
    narration: str
    on_screen_text: str
    picture_search: str
    image_prompt: str
    speaker: str = ""  # Arjun or Meera: whose voice reads this line
    host_on_screen: bool = False  # True: the speaker is shown (from their reference photo), not stock footage


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
                                  "dub_of": path.stem, "scenes": [s.model_dump() for s in scenes]},
                                 indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def storyboard(package: dict) -> Storyboard:
    """Ask Claude to cut the package into scenes the renderer can use."""
    return client.messages.parse(
        model=HELPER_MODEL,
        max_tokens=16000,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content":
                   "Split this video package into scenes for narration, following Mr. Cut's edit plan shot by shot: Mr. Pen "
                   "and Mr. Cut have already chosen which character and which background each shot shows. narration: "
                   "exactly what the voice says (only spoken words, no stage directions). on_screen_text: at most 8 words. "
                   "picture_search: Mr. Cut's footage search for the shot, or else 2-5 concrete words for real live-action "
                   "stock video showing that character in that background (e.g. 'woman astronaut looking at earth'). "
                   "image_prompt: a photo-real description of the same shot (person, setting, camera angle); when a "
                   "recurring character appears, copy their look from the cast below word for word. Real footage only, "
                   "never cartoon. "
                   "speaker: who says the line, Arjun or Meera (the two hosts; use both in every Short). "
                   "host_on_screen: true when the shot shows that host talking (about every third scene, including "
                   "the first), then image_prompt describes only their pose, expression and setting. "
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


def _nasa(query: str, used: set, work: Path):
    """Download a public-domain clip from NASA's video library (no key needed), or return None."""
    url = "https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": query, "media_type": "video", "page_size": 10})
    for item in json.load(urllib.request.urlopen(url, timeout=20))["collection"]["items"]:
        nasa_id = item["data"][0]["nasa_id"]
        if nasa_id in used:
            continue
        files = json.load(urllib.request.urlopen(urllib.parse.quote(item["href"], safe=":/~"), timeout=20))
        mp4 = next((f for size in ("~medium.mp4", "~small.mp4", "~mobile.mp4") for f in files if f.endswith(size)), None)
        if not mp4:
            continue
        used.add(nasa_id)
        path = work / f"nasa-{len(used):03}.mp4"
        if not path.exists():  # ponytail: downloads the whole clip; long NASA videos can be 100+ MB
            urllib.request.urlretrieve(urllib.parse.quote(mp4, safe=":/~"), path)
        return path
    return None


def _clip(path: Path, size: tuple, duration: float, skip: float = 0):
    """A stock clip filling the frame for `duration` seconds, starting `skip` of the way in."""
    clip = _fill(VideoFileClip(str(path)).without_audio(), size)
    clip = clip.subclipped(min(clip.duration * skip, max(0, clip.duration - duration)))
    if clip.duration < duration:
        clip = clip.with_effects([vfx.Loop(duration=duration)])
    return clip.subclipped(0, duration)


def _fill(clip, size: tuple):
    """Scale and centre-crop a clip to exactly fill the frame."""
    clip = clip.resized(max(size[0] / clip.w, size[1] / clip.h))
    return clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=size[0], height=size[1])


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


paid = {"clips": 0, "usd": 0.0}  # fal.ai spending of the video being made; render() resets it


def _can_pay() -> bool:
    return paid["clips"] < AI_CLIPS and spent_today() + paid["usd"] < DAILY_BUDGET


def _stock(query: str, size: tuple, duration: float, work: Path, used: set):
    """A real Pixabay clip for the query, or None."""
    for video in _pixabay("videos/", query):
        if video["id"] in used:
            continue
        used.add(video["id"])
        path = work / f"clip-{video['id']}.mp4"
        if not path.exists():
            urllib.request.urlretrieve(video["videos"]["medium"]["url"], path)  # 1080p, or 720p on old clips
        return _clip(path, size, duration)
    return None


def background(scene: "Scene", i: int, audio: Path, size: tuple, duration: float, work: Path, used: set):
    """Moving video only: the host really talking (Kling avatar), else Pixabay footage, else a Kling AI clip,
    else NASA footage, else Pixabay footage for a shorter search, else a plain colour."""
    query = scene.picture_search
    if scene.host_on_screen and scene.speaker in HOSTS and os.environ.get("FAL_KEY"):
        path = work / f"avatar-{audio.stem}.mp4"  # per language, since the lips follow the voice
        if path.exists() or _can_pay():
            try:
                if not path.exists():
                    import fal_client
                    still = work / f"host-{i:03}.png"
                    if not still.exists():
                        result = fal_client.subscribe(HOST_MODEL, arguments={
                            "prompt": f"The same person, same face, hair and clothes: {scene.image_prompt}. Looking at "
                                      f"the camera. {STYLE}",
                            "image_url": fal_client.upload_file(str(host_photo(scene.speaker))), "aspect_ratio": "9:16"})
                        urllib.request.urlretrieve(result["images"][0]["url"], still)
                        paid["usd"] += 0.04
                    result = fal_client.subscribe(AVATAR_MODEL, arguments={
                        "image_url": fal_client.upload_file(str(still)), "audio_url": fal_client.upload_file(str(audio)),
                        "prompt": "A real person talking naturally to the camera, small head and hand movements"})
                    urllib.request.urlretrieve(result["video"]["url"], path)
                    paid["usd"] += 0.0562 * (result.get("duration") or duration)
                    paid["clips"] += 1
                return _clip(path, size, duration)
            except Exception as e:
                print(f"    no talking shot of {scene.speaker}: {e}")
    if os.environ.get("PIXABAY_API_KEY"):
        try:
            if clip := _stock(query, size, duration, work, used):
                return clip
        except Exception as e:  # missing footage is not worth losing the video over
            print(f"    no footage for '{query}': {e}")
    if os.environ.get("FAL_KEY"):
        path = work / f"ai-{i:03}.mp4"  # no lips to match, so dubs reuse it
        if path.exists() or _can_pay():
            try:
                if not path.exists():
                    import fal_client
                    result = fal_client.subscribe(VIDEO_MODEL, arguments={  # 5 s, looped if the line is longer
                        "prompt": f"{scene.image_prompt}. {STYLE}", "duration": "5", "aspect_ratio": "9:16",
                        "negative_prompt": "cartoon, anime, illustration, CGI, 3D render, plastic skin, text, blur"})
                    urllib.request.urlretrieve(result["video"]["url"], path)
                    paid["usd"] += 0.35
                    paid["clips"] += 1
                return _clip(path, size, duration)
            except Exception as e:
                print(f"    no AI video for this scene: {e}")
    try:
        path = _nasa(query, used, work)
        if path:
            return _clip(path, size, duration, skip=0.2)  # skip NASA title cards at the start
    except Exception as e:
        print(f"    no NASA footage for '{query}': {e}")
    if os.environ.get("PIXABAY_API_KEY") and len(query.split()) > 2:
        try:
            if clip := _stock(" ".join(query.split()[:2]), size, duration, work, used):
                return clip
        except Exception as e:
            print(f"    no footage for a shorter search: {e}")
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


def speak(text: str, voice: str, path: Path, pitch: str = "+0Hz", eleven: str = "", before: str = "",
          after: str = "") -> bool:
    """ElevenLabs when ELEVENLABS_API_KEY is set (the lines around this one keep the delivery flowing), else Edge.
    Edge's free voice service sometimes returns an empty or broken file, so check it and try again.
    Returns False if it never works, so the caller can drop that scene instead of losing the whole video."""
    if eleven and os.environ.get("ELEVENLABS_API_KEY"):
        try:
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{eleven}?output_format=mp3_44100_128",
                data=json.dumps({"text": text, "model_id": ELEVEN_MODEL, "previous_text": before,
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
    size = (1080, 1920)  # YouTube Shorts are vertical
    lang = package_path.suffixes[0][1:] if len(package_path.suffixes) > 1 else package.get("lang", "")
    # A series episode's characters are shown and voiced the same way as the hosts.
    HOSTS.update({c["name"]: c for c in package.get("cast", [])})
    if "scenes" in package:  # a dub reuses the original's folder, so its footage is already downloaded
        board, work = Storyboard(scenes=package["scenes"]), OUTBOX / package.get("dub_of", package_path.stem)
        work.mkdir(exist_ok=True)
    else:
        board, work = storyboard(package), package_path.with_suffix("")
        work.mkdir(exist_ok=True)
        (work / "board.json").write_text(board.model_dump_json(), encoding="utf-8")
    prefix = f"{lang}-" if lang else ""
    logo = None
    if LOGO.exists():  # channel watermark, top-left, clear of the Shorts buttons on the right
        logo = ImageClip(str(LOGO), transparent=True).resized(width=150).with_opacity(0.85).with_position((60, 170))
    paid.update(clips=0, usd=0.0)
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
            who = {} if "dub_of" in package else HOSTS.get(scene.speaker, {})
            eleven = os.environ.get(f"ELEVEN_VOICE_{scene.speaker.upper()}") or (
                ELEVEN_FEMALE if "woman" in who.get("look", "").lower() else ELEVEN_MALE)
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
    # 2. The picture for each line, silent, cut on whole frames so it never drifts from the voice.
    parts, used = [], set()
    for i, scene, audio, start, end in lines:
        duration = (round(end * 30) - round(start * 30)) / 30
        layers = [background(scene, i, audio, size, duration, work, used),
                  ImageClip(caption(scene.on_screen_text, size, lang), transparent=True).with_duration(duration)]
        if logo:
            layers.append(logo.with_duration(duration))
        clip = CompositeVideoClip(layers, size=size).with_duration(duration)
        # Each scene is written to disk and closed straight away, so only one scene's footage is in memory.
        part = work / f"{prefix}scene-{i:03}.mp4"
        clip.write_videofile(str(part), fps=30, codec="libx264", audio=False,
                             ffmpeg_params=["-pix_fmt", "yuv420p"], logger=None)
        for c in (clip, *layers):
            c.close()
        parts.append(part)
        print(f"    scene {i + 1}/{len(board.scenes)}")
    if paid["usd"]:  # counted in DAILY_BUDGET with the Claude costs
        HISTORY.parent.mkdir(exist_ok=True)
        with HISTORY.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "cost_usd": round(paid["usd"], 2)}) + "\n")
        print(f"    fal.ai video cost ${paid['usd']:.2f}")
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


def youtube(interactive: bool = True, token: Path = TOKEN):
    """A signed-in YouTube API client. Upload, plus read-only access so Mr. Hope can see view counts."""
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
    return build("youtube", "v3", credentials=creds)


def stats(video_ids: list) -> dict:
    """Views, likes and comments per uploaded video id."""
    items = youtube(interactive=False).videos().list(part="statistics,status", id=",".join(video_ids)).execute()
    return {i["id"]: {**i["statistics"], "privacy": i["status"]["privacyStatus"]} for i in items["items"]}


def upload(video: Path, package: dict, token: Path = TOKEN) -> str:
    """Upload as a public video (the owner chose public by default on 2026-10-25)."""
    from googleapiclient.http import MediaFileUpload

    footer = package.get("footer", TEAM.get("YouTube footer", ""))  # edit it in team.md
    tags = list(dict.fromkeys(["Hopeverse Media", "Shorts", *re.findall(r"#(\w+)", package["description"])]))
    while len(",".join(tags)) > 450:  # YouTube allows 500 characters of tags
        tags.pop()
    body = {"snippet": {"title": package["title"][:100],
                        "description": f"{package['description']}\n\n{footer}".strip()[:5000],
                        "tags": tags, "categoryId": package.get("category", "28")},  # 28 = Science & Technology
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
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
    url = fal_client.upload_file(str(video))
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
    if "--connect" in sys.argv:  # sign a channel in once: python video.py --connect hi (or a channel id)
        lang = sys.argv[sys.argv.index("--connect") + 1]
        c = next(c for c in channels.values() if lang in (c.get("lang"), c["id"]))
        print(f"Sign in and pick the {c['name']} channel in the browser.")
        youtube(token=HERE / c["token"])
        sys.exit()
    dubs = [c for c in channels.values() if c.get("status") == "dub" and (HERE / c["token"]).exists()]
    platform = {i: c["platform"] for i, c in channels.items()}
    quota_left = True
    for path in sorted(OUTBOX.glob("*.json")):
        package = json.loads(path.read_text(encoding="utf-8"))
        if "--only" in sys.argv and package["channel_id"] != sys.argv[sys.argv.index("--only") + 1]:
            continue  # e.g. python video.py --only yt-kissa: post just that channel's videos
        video = path.with_suffix(".mp4")
        voice = channels.get(package["channel_id"], {}).get("voice", VOICE)
        if not video.exists() and "youtube_id" not in package:  # cloud runs don't keep videos; never remake posted ones
            print(f"Making video for {path.name}")
            try:
                render(path, voice)
            except Exception as e:  # with many Shorts a day, one broken package shouldn't stop the rest
                print(f"    failed: {e}")
                continue
        # Only Shorts made from now on have board.json, so older ones are never dubbed.
        for c in dubs if "dub_of" not in package and (path.with_suffix("") / "board.json").exists() else []:
            if not path.with_suffix(f".{c['lang']}.json").exists():
                print(f"Making the {c['language']} version of {path.name}")
                try:
                    render(dub(path, c), c["voice"])
                except Exception as e:  # a failed dub shouldn't stop the English video
                    print(f"    {c['language']} version failed: {e}")
        if "--no-upload" in sys.argv:  # the 4 PM run only makes videos; the 6 PM run posts them
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
                package["youtube_id"] = upload(video, package, HERE / channels[package["channel_id"]].get("token", "token.json"))
            except Exception as e:  # the daily API quota fits about 6 uploads; the rest go up on the next run
                print(f"    upload failed: {e}")
                quota_left = "quota" not in str(e).lower() and "uploadLimitExceeded" not in str(e)
                continue
            path.write_text(json.dumps(package, indent=2), encoding="utf-8")
            print(f"    https://youtu.be/{package['youtube_id']}")
        if channels.get(package["channel_id"], {}).get("lang"):  # Hindi dubs and series stay on their own channel
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
