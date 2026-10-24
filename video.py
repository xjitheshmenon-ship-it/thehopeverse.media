"""Turn outbox packages into videos and upload them to YouTube as private drafts.

    python video.py            # every outbox package that has no video yet

Voice: free Microsoft Edge voices (edge-tts). Pictures: Pexels photos when PEXELS_API_KEY is set,
otherwise plain coloured backgrounds. Upload: needs client_secret.json from Google Cloud (see README).
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
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from agents import HELPER_MODEL, OUTBOX, _channels, client

HERE = Path(__file__).parent
VOICE = os.environ.get("HOPE_VOICE", "en-US-AndrewNeural")
SECRET, TOKEN = HERE / "client_secret.json", HERE / "token.json"


class Scene(BaseModel):
    narration: str
    on_screen_text: str
    picture_search: str


class Storyboard(BaseModel):
    scenes: list[Scene]


def storyboard(package: dict) -> Storyboard:
    """Ask Claude to cut the package into scenes the renderer can use."""
    return client.messages.parse(
        model=HELPER_MODEL,
        max_tokens=16000,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content":
                   "Split this video package into scenes for narration. narration: exactly what the voice says "
                   "(only spoken words, no stage directions). on_screen_text: at most 8 words. picture_search: "
                   "2-4 words to search a stock photo site. It is a YouTube Short: keep it under 60 seconds "
                   "of narration.\n\n"
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


def _picture(query: str, size: tuple) -> Image.Image:
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        try:
            orient = "portrait" if size[1] > size[0] else "landscape"
            url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
                {"query": query, "per_page": 1, "orientation": orient})
            req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": "hopeverse"})
            photo = json.load(urllib.request.urlopen(req, timeout=20))["photos"][0]["src"]["large2x"]
            img = Image.open(BytesIO(urllib.request.urlopen(photo, timeout=30).read())).convert("RGB")
            scale = max(size[0] / img.width, size[1] / img.height)
            img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
            left, top = (img.width - size[0]) // 2, (img.height - size[1]) // 2
            return img.crop((left, top, left + size[0], top + size[1]))
        except Exception as e:  # no photo is not worth losing the video over
            print(f"    no picture for '{query}': {e}")
    return Image.new("RGB", size, (12, 18, 48))


def frame(scene: Scene, size: tuple) -> np.ndarray:
    img = _picture(scene.picture_search, size)
    draw = ImageDraw.Draw(img, "RGBA")
    font = _font(size[0] // 14)
    lines = textwrap.wrap(scene.on_screen_text, width=18 if size[1] > size[0] else 28)
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
    clips = []
    for i, scene in enumerate(board.scenes):
        audio = work / f"{i:03}.mp3"
        asyncio.run(edge_tts.Communicate(scene.narration, VOICE).save(str(audio)))
        sound = AudioFileClip(str(audio))
        clips.append(ImageClip(frame(scene, size)).with_duration(sound.duration + 0.3).with_audio(sound))
        print(f"    scene {i + 1}/{len(board.scenes)}")
    out = package_path.with_suffix(".mp4")
    concatenate_videoclips(clips).write_videofile(str(out), fps=24, codec="libx264", audio_codec="aac",
                                                  logger=None)
    return out


def upload(video: Path, package: dict) -> str:
    """Upload as a private video, so nothing goes public until the owner checks it in YouTube Studio."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = Credentials.from_authorized_user_file(str(TOKEN), scopes) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), scopes).run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    body = {"snippet": {"title": package["title"][:100], "description": package["description"][:5000],
                        "categoryId": "28"},  # Science & Technology
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    request = build("youtube", "v3", credentials=creds).videos().insert(
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
