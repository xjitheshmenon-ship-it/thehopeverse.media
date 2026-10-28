"""A cinematic Short cut to a music track: one Kling AI clip per shot, each trimmed to end on its beat.

    python film.py films/exiled-king.json   -> films/exiled-king.mp4 (not uploaded; the owner reviews it first)

The shots' "end" times follow the track's sections (tease, hit, walk, drop, mass, punch), so the cuts land on the music.
HeyGen Video first (HEYGEN_API_KEY, about $0.09 a 5 s shot, slowed down to fill longer shots), else Kling on fal.ai
(FAL_KEY, $0.35 per 5 s shot, $0.70 up to 10 s).
"""
import json
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
work = film_path.with_suffix("")
work.mkdir(exist_ok=True)
starts = [0] + [s["end"] for s in film["shots"][:-1]]


def make(i: int) -> Path:
    shot, start = film["shots"][i], starts[i]
    raw, part = work / f"raw-{i:02}.mp4", work / f"part-{i:02}.mp4"
    if not raw.exists():
        try:
            heygen_clip(f"{shot['prompt']}. {film['look']}", raw)
        except Exception as e:
            print(f"shot {i + 1}: HeyGen failed ({e}); using Kling")
    if not raw.exists():
        result = fal_client.subscribe(MODEL, arguments={
            "prompt": f"{shot['prompt']}. {film['look']}", "aspect_ratio": "9:16",
            "duration": "5" if shot["end"] - start <= 5 else "10",
            "negative_prompt": "cartoon, anime, CGI, 3D render, text, watermark, people, rider, saddle, blur"})
        urllib.request.urlretrieve(result["video"]["url"], raw)
    text = shot.get("text", "").replace("'", "’").replace(":", "\\:")
    caption = (f",drawtext=fontfile={FONT}:text='{text}':fontcolor=white:fontsize=64:borderw=4:bordercolor=black@0.6"
               ":x=(w-tw)/2:y=h*0.72") if text else ""
    length = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
                                  capture_output=True, text=True).stdout or 5)
    slow = max(1.0, (shot["end"] - start) / length)  # a 5 s shot fills a longer beat in slow motion
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(raw), "-t", f"{shot['end'] - start:.3f}", "-an", "-vf",
                    f"setpts={slow:.3f}*PTS,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,fps=30"
                    + caption, "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(part)],
                   check=True)
    print(f"shot {i + 1}: {start}-{shot['end']} s")
    return part


with ThreadPoolExecutor(6) as pool:
    parts = list(pool.map(make, range(len(film["shots"]))))
listing = work / "parts.txt"
listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
out = film_path.with_suffix(".mp4")
subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-i", film["music"],
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
               check=True)
print(f"Film: {out} ({len(parts)} shots)")
