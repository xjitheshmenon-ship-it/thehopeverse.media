"""Turn outbox packages into videos and upload them to YouTube as public videos.

    python video.py            # every outbox package that has no video yet

Voice: free Microsoft Edge voices (edge-tts). Pictures: real moving stock footage from Pixabay (free, PIXABAY_API_KEY) or NASA (no key)
for each shot in Mr. Cut's edit plan, else a photo-real AI image from fal.ai (FAL_KEY), else a plain colour. Upload: needs client_secret.json from Google Cloud (see README).

Dub channels: every new Short is also re-voiced for each channel in channels.json with a "lang" (e.g. Hindi), reusing
the same footage, once that channel is signed in:  python video.py --connect hi
"""
import asyncio
import json
import os
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

import edge_tts
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, ImageClip, VideoFileClip, vfx
from moviepy.config import FFMPEG_BINARY
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from agents import HELPER_MODEL, OUTBOX, _channels, client, read_cast
from approve import approved

HERE = Path(__file__).parent
VOICE = os.environ.get("HOPE_VOICE", "en-US-AndrewNeural")
FAL_MODEL = "fal-ai/flux/schnell"  # about $0.006 per Short-sized image
STYLE = ("photorealistic real photograph, shot on 35mm film camera, natural light, documentary style, vertical 9:16, "
         "not a cartoon, not an illustration, not CGI, no text, no words")
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


def _zoom(img: Image.Image, size: tuple, duration: float):
    clip = _fill(ImageClip(np.array(img.convert("RGB"))), size).with_duration(duration)
    return clip.resized(lambda t: 1 + 0.06 * t / duration).with_position("center")  # slow push-in


def background(scene: "Scene", size: tuple, duration: float, work: Path, used: set):
    """Real stock footage from Pixabay (PIXABAY_API_KEY), else NASA's free library, else a photo-real AI image
    from fal.ai (FAL_KEY), else a Pixabay photo, else a plain colour."""
    query = scene.picture_search
    if os.environ.get("PIXABAY_API_KEY"):
        try:
            for video in _pixabay("videos/", query):
                if video["id"] in used:
                    continue
                used.add(video["id"])
                path = work / f"clip-{video['id']}.mp4"
                if not path.exists():
                    urllib.request.urlretrieve(video["videos"]["medium"]["url"], path)  # 1080p, or 720p on old clips
                return _clip(path, size, duration)
        except Exception as e:  # missing footage is not worth losing the video over
            print(f"    no footage for '{query}': {e}")
    try:
        path = _nasa(query, used, work)
        if path:
            return _clip(path, size, duration, skip=0.2)  # skip NASA title cards at the start
    except Exception as e:
        print(f"    no NASA footage for '{query}': {e}")
    if os.environ.get("FAL_KEY"):
        try:
            import fal_client
            path = work / f"ai-{len(used):03}.png"
            used.add(path.name)
            if not path.exists():
                result = fal_client.subscribe(FAL_MODEL, arguments={
                    "prompt": f"{scene.image_prompt}. {STYLE}", "image_size": "portrait_16_9", "num_images": 1})
                urllib.request.urlretrieve(result["images"][0]["url"], path)
            return _zoom(Image.open(path), size, duration)
        except Exception as e:
            print(f"    no AI image for this scene: {e}")
    if os.environ.get("PIXABAY_API_KEY"):
        try:
            photo = _pixabay("", query)[0]
            img = Image.open(BytesIO(urllib.request.urlopen(photo["largeImageURL"], timeout=30).read())).convert("RGB")
            return _zoom(img, size, duration)
        except Exception as e:
            print(f"    no photo for '{query}': {e}")
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


def speak(text: str, voice: str, path: Path):
    """Edge's free voice service sometimes returns an empty or broken file, so check it and try again."""
    for attempt in range(4):
        try:
            asyncio.run(edge_tts.Communicate(text, voice).save(str(path)))
            AudioFileClip(str(path)).close()  # raises if ffmpeg can't read it
            return
        except Exception as e:
            if attempt == 3:
                raise
            print(f"    voice failed ({e.__class__.__name__}), retrying")
            time.sleep(5 * (attempt + 1))


def render(package_path: Path, voice: str = VOICE) -> Path:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    size = (1080, 1920)  # YouTube Shorts are vertical
    lang = package_path.suffixes[0][1:] if len(package_path.suffixes) > 1 else ""
    if "dub_of" in package:  # a dub reuses the original's folder, so its footage is already downloaded
        board, work = Storyboard(scenes=package["scenes"]), OUTBOX / package["dub_of"]
    else:
        board, work = storyboard(package), package_path.with_suffix("")
        work.mkdir(exist_ok=True)
        (work / "board.json").write_text(board.model_dump_json(), encoding="utf-8")
    prefix = f"{lang}-" if lang else ""
    logo = None
    if LOGO.exists():  # channel watermark, top-left, clear of the Shorts buttons on the right
        logo = ImageClip(str(LOGO), transparent=True).resized(width=150).with_opacity(0.85).with_position((60, 170))
    parts, used = [], set()
    for i, scene in enumerate(board.scenes):
        if not any(ch.isalnum() for ch in scene.narration):  # nothing to say, so no sound file would come back
            continue
        audio = work / f"{prefix}{i:03}.mp3"
        speak(scene.narration, voice, audio)
        sound = AudioFileClip(str(audio))
        duration = sound.duration + 0.3
        layers = [background(scene, size, duration, work, used),
                  ImageClip(caption(scene.on_screen_text, size, lang), transparent=True).with_duration(duration)]
        if logo:
            layers.append(logo.with_duration(duration))
        clip = CompositeVideoClip(layers, size=size).with_duration(duration).with_audio(sound)
        # Each scene is written to disk and closed straight away, so only one scene's footage is in memory.
        part = work / f"{prefix}scene-{i:03}.mp4"
        clip.write_videofile(str(part), fps=30, codec="libx264", audio_codec="aac",
                             ffmpeg_params=["-pix_fmt", "yuv420p"], logger=None)
        for c in (clip, sound, *layers):
            c.close()
        parts.append(part)
        print(f"    scene {i + 1}/{len(board.scenes)}")
    out = package_path.with_suffix(".mp4")
    listing = work / f"{prefix}scenes.txt"
    listing.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run([FFMPEG_BINARY, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(out)], check=True)
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

    body = {"snippet": {"title": package["title"][:100], "description": package["description"][:5000],
                        "categoryId": "28"},  # Science & Technology
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
    if "--connect" in sys.argv:  # sign a dub channel in once: python video.py --connect hi
        lang = sys.argv[sys.argv.index("--connect") + 1]
        c = next(c for c in channels.values() if c.get("lang") == lang)
        print(f"Sign in and pick the {c['name']} channel in the browser.")
        youtube(token=HERE / c["token"])
        sys.exit()
    dubs = [c for c in channels.values() if c.get("lang") and (HERE / c["token"]).exists()]
    platform = {i: c["platform"] for i, c in channels.items()}
    for path in sorted(OUTBOX.glob("*.json")):
        package = json.loads(path.read_text(encoding="utf-8"))
        video = path.with_suffix(".mp4")
        voice = channels.get(package["channel_id"], {}).get("voice", VOICE)
        if not video.exists():
            print(f"Making video for {path.name}")
            render(path, voice)
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
            if not SECRET.exists():
                print("Skipping upload: client_secret.json not found (see README).")
                continue
            print(f"Uploading {video.name} to YouTube as public")
            package["youtube_id"] = upload(video, package, HERE / channels[package["channel_id"]].get("token", "token.json"))
            path.write_text(json.dumps(package, indent=2), encoding="utf-8")
            print(f"    https://youtu.be/{package['youtube_id']}")
        if "dub_of" in package:  # dubs go to their own YouTube channel only
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
