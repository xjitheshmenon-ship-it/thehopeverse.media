"""A cinematic Short cut to a music track: one Kling AI clip per shot, each trimmed to end on its beat.

    python film.py films/exiled-king.json   -> films/exiled-king.mp4 (not uploaded; the owner reviews it first)
    POST=yt-aether python film.py ...       -> also uploads it there (film.yml input "post", after the owner's review)
    POST=yt-aether VIDEO=<id> python film.py ...  -> only rewrites that posted film's title and description

The shots' "end" times follow the track's sections (tease, hit, walk, drop, mass, punch), so the cuts land on the music.
HeyGen Video first (HEYGEN_API_KEY, about $0.09 a 5 s shot, slowed down to fill longer shots), else Kling on fal.ai
(FAL_KEY, $0.35 per 5 s shot, $0.70 up to 10 s).
A shot with "image" starts from that photo, so the same man, face and clothes appear in every shot; with "frame" it starts
from a still posed from that photo for this shot (Kontext), which keeps faces far steadier than a portrait start.
"refs" makes those photos first (fal Flux, then Kontext for the same face); REFS_ONLY=1 stops after them for a review.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fal_client
from imageio_ffmpeg import get_ffmpeg_exe

from video import heygen_clip

MODEL = "fal-ai/kling-video/v2.5-turbo/pro/text-to-video"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FF = shutil.which("ffmpeg") or get_ffmpeg_exe()  # the system ffmpeg has drawtext for captions; the pip one does not

film_path = Path(sys.argv[1])
film = json.loads(film_path.read_text(encoding="utf-8"))
if video_id := os.environ.get("VIDEO"):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    channel = next(c for c in json.loads(Path("channels.json").read_text(encoding="utf-8")) if c["id"] == os.environ["POST"])
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(channel["token"]))  # connect.py's full scope
    snippet = yt.videos().list(part="snippet", id=video_id).execute()["items"][0]["snippet"]
    yt.videos().update(part="snippet", body={"id": video_id, "snippet": {
        **{k: snippet[k] for k in ("categoryId", "tags", "defaultLanguage", "defaultAudioLanguage") if k in snippet},
        "title": film["title"][:100], "description": f"{film.get('description', film['title'])}\n\n{channel['footer']}"}}).execute()
    sys.exit(print(f"Updated https://youtu.be/{video_id}"))
work = film_path.with_suffix("")
work.mkdir(exist_ok=True)
cost = []  # usd per new fal.ai / HeyGen call; film.yml adds the total to history.jsonl so the dashboard counts it
starts = [0] + [s["end"] for s in film["shots"][:-1]]
refs = film.get("refs", {})  # {"ref-x.jpg": prompt}: the first photo is made from text, the rest from it (same face and clothes)
for k, (name, prompt) in enumerate(refs.items()):
    if (work / name).exists():
        continue
    result = fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={
        "prompt": f"The same people, same faces, hair and clothes: {prompt}", "aspect_ratio": "9:16",
        "image_url": fal_client.encode_file(str(work / next(iter(refs))))}) if k else fal_client.subscribe(
        "fal-ai/flux-pro/v1.1-ultra", arguments={"prompt": f"{prompt}. {film['look']}", "aspect_ratio": "9:16"})
    urllib.request.urlretrieve(result["images"][0]["url"], work / name)
    cost.append(0.04 if k else 0.06)
for i, shot in enumerate(film["shots"]):  # "frame": this shot's first frame, posed from its photo (same faces)
    if shot.get("frame") and not (work / f"frame-{i:02}.jpg").exists():
        result = fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={
            "prompt": f"The same people, same faces, hair, beard and clothes, same heights: {shot['frame']}",
            "aspect_ratio": "9:16", "image_url": fal_client.encode_file(shot["image"])})
        urllib.request.urlretrieve(result["images"][0]["url"], work / f"frame-{i:02}.jpg")
        cost.append(0.04)
film_path.with_suffix(".cost").write_text(f"{sum(cost):.2f}")
if os.environ.get("REFS_ONLY"):  # make and review the photos (and first frames) before paying for the shots
    sys.exit(print(f"Reference photos: {', '.join(refs)}"))


def make(i: int) -> Path:
    shot, start = film["shots"][i], starts[i]
    raw, part = work / f"raw-{i:02}.mp4", work / f"part-{i:02}.mp4"
    image = work / f"frame-{i:02}.jpg" if shot.get("frame") else Path(shot["image"]) if shot.get("image") else None
    if not raw.exists() and film.get("maker") != "kling":  # "maker": "kling" holds faces better from a start frame
        try:
            heygen_clip(f"{shot['prompt']}. {shot.get('look', film['look'])}", raw, image)
            cost.append(0.09)
        except Exception as e:
            print(f"shot {i + 1}: HeyGen failed ({e}); using Kling")
    if not raw.exists():
        result = fal_client.subscribe(MODEL.replace("text-to-video", "image-to-video") if image else MODEL, arguments={
            **({"image_url": fal_client.encode_file(str(image))} if image else {"aspect_ratio": "9:16"}),
            "prompt": f"{shot['prompt']}. {shot.get('look', film['look'])}",
            "duration": "5" if shot["end"] - start <= 5 else "10",
            "negative_prompt": film.get("negative", "cartoon, anime, CGI, 3D render, text, watermark, people, rider, saddle, blur")})
        urllib.request.urlretrieve(result["video"]["url"], raw)
        cost.append(0.35 if shot["end"] - start <= 5 else 0.70)
    text = shot.get("text", "").replace("'", "’").replace(":", "\\:")
    caption = (f",drawtext=fontfile={FONT}:text='{text}':fontcolor=white:fontsize=64:borderw=4:bordercolor=black@0.6"
               ":x=(w-tw)/2:y=h*0.72") if text else ""
    length = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
                                  capture_output=True, text=True).stdout or 5)
    skip = film.get("skip", 0) if shot.get("image") else 0  # every photo shot opens on the same frame; cut that start
    length -= skip
    slow = max(1.0, (shot["end"] - start) / length)  # a 5 s shot fills a longer beat in slow motion
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", f"{skip}", "-i", str(raw), "-t", f"{shot['end'] - start:.3f}", "-an", "-vf",
                    f"setpts={slow:.3f}*PTS,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,fps=30"
                    + caption, "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(part)],
                   check=True)
    print(f"shot {i + 1}: {start}-{shot['end']} s")
    return part


if film.get("file"):  # a finished video file (e.g. a music visualizer), only posted
    out = Path(film["file"])
else:
    with ThreadPoolExecutor(6) as pool:
        parts = list(pool.map(make, range(len(film["shots"]))))
    listing = work / "parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    out = film_path.with_suffix(".mp4")
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-i", film["music"],
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
                   check=True)
    film_path.with_suffix(".cost").write_text(f"{sum(cost):.2f}")
    print(f"Film: {out} ({len(parts)} shots, ${sum(cost):.2f} new AI shots)")
if post := os.environ.get("POST"):
    from video import upload
    channel = next(c for c in json.loads(Path("channels.json").read_text(encoding="utf-8")) if c["id"] == post)
    package = {"title": film["title"], "description": film.get("description", film["title"]),
               "category": channel.get("category", "10"), "lang": channel.get("lang", "en"),
               **({"publish_at": film["publish_at"]} if film.get("publish_at") else {})}  # e.g. "2026-10-29T17:20:00Z": scheduled, not public now
    print(f"Posted on {channel['name']}: https://youtu.be/{upload(out, package, Path(channel['token']), channel)}")
