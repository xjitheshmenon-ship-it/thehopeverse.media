"""Turn outbox packages into videos and upload them to YouTube as private drafts.

    python video.py            # every outbox package that has no video yet

Voice: free Microsoft Edge voices (edge-tts). Pictures: real moving stock footage from Pixabay (free, PIXABAY_API_KEY) or NASA (no key)
for each shot in Mr. Cut's edit plan, else a photo-real AI image from fal.ai (FAL_KEY), else a plain colour. Upload: needs client_secret.json from Google Cloud (see README).
"""
import asyncio
import json
import os
import textwrap
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

import edge_tts
import numpy as np
from moviepy import (AudioFileClip, ColorClip, CompositeVideoClip, ImageClip, VideoFileClip,
                     concatenate_videoclips, vfx)
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from agents import HELPER_MODEL, OUTBOX, _channels, client, read_cast

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


def _font(size: int):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
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


def caption(text: str, size: tuple) -> np.ndarray:
    """Caption on a transparent layer, laid over the footage."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _font(size[0] // 14)
    lines = textwrap.wrap(text, width=18)
    line_h = font.size + 16
    top = int(size[1] * 0.72) - line_h * len(lines) // 2
    draw.rectangle((0, top - 30, size[0], top + line_h * len(lines) + 30), fill=(0, 0, 0, 150))
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font)
        draw.text(((size[0] - w) / 2, top + i * line_h), line, font=font, fill="white")
    return np.array(img)


def render(package_path: Path) -> Path:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    board = storyboard(package)
    size = (1080, 1920)  # YouTube Shorts are vertical
    work = package_path.with_suffix("")
    work.mkdir(exist_ok=True)
    clips, used = [], set()
    for i, scene in enumerate(board.scenes):
        audio = work / f"{i:03}.mp3"
        asyncio.run(edge_tts.Communicate(scene.narration, VOICE).save(str(audio)))
        sound = AudioFileClip(str(audio))
        duration = sound.duration + 0.3
        layers = [background(scene, size, duration, work, used),
                  ImageClip(caption(scene.on_screen_text, size), transparent=True).with_duration(duration)]
        clips.append(CompositeVideoClip(layers, size=size).with_duration(duration).with_audio(sound))
        print(f"    scene {i + 1}/{len(board.scenes)}")
    video = concatenate_videoclips(clips)
    if LOGO.exists():  # channel watermark, top-left, clear of the Shorts buttons on the right
        logo = ImageClip(str(LOGO), transparent=True).resized(width=150).with_opacity(0.85)
        video = CompositeVideoClip([video, logo.with_position((60, 170)).with_duration(video.duration)], size=size)
    out = package_path.with_suffix(".mp4")
    video.write_videofile(str(out), fps=30, codec="libx264", audio_codec="aac",
                                                  ffmpeg_params=["-pix_fmt", "yuv420p"], logger=None)
    return out


def youtube(interactive: bool = True):
    """A signed-in YouTube API client. Upload, plus read-only access so Mr. Hope can see view counts."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.readonly"]
    creds = Credentials.from_authorized_user_file(str(TOKEN), scopes) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid or not set(scopes) <= set(creds.scopes or []):
        if not interactive:
            raise RuntimeError("YouTube not connected yet; run python video.py once by hand")
        creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), scopes).run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def stats(video_ids: list) -> dict:
    """Views, likes and comments per uploaded video id."""
    items = youtube(interactive=False).videos().list(part="statistics,status", id=",".join(video_ids)).execute()
    return {i["id"]: {**i["statistics"], "privacy": i["status"]["privacyStatus"]} for i in items["items"]}


def upload(video: Path, package: dict) -> str:
    """Upload as a private video, so nothing goes public until the owner checks it in YouTube Studio."""
    from googleapiclient.http import MediaFileUpload

    body = {"snippet": {"title": package["title"][:100], "description": package["description"][:5000],
                        "categoryId": "28"},  # Science & Technology
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    request = youtube().videos().insert(
        part="snippet,status", body=body, media_body=MediaFileUpload(str(video), resumable=True))
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]


if __name__ == "__main__":
    platform = {c["id"]: c["platform"] for c in _channels()}
    for path in sorted(OUTBOX.glob("*.json")):
        package = json.loads(path.read_text(encoding="utf-8"))
        video = path.with_suffix(".mp4")
        if not video.exists():
            print(f"Making video for {path.name}")
            render(path)
        if platform.get(package["channel_id"]) == "youtube" and "youtube_id" not in package:
            if not SECRET.exists():
                print("Skipping upload: client_secret.json not found (see README).")
                continue
            print(f"Uploading {video.name} to YouTube as private")
            package["youtube_id"] = upload(video, package)
            path.write_text(json.dumps(package, indent=2), encoding="utf-8")
            print(f"    https://youtu.be/{package['youtube_id']} (private)")
