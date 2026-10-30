# slides.py <pictures dir> <music> <out.mp4> [start_s end_s]: 14 stills with slow zoom, crossfades, cut to the song
import subprocess, sys, glob
d, music, out = sys.argv[1:4]
a, b = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0.0, None)
pics = sorted(glob.glob(f"{d}/frame-*.jpg"))
if b is None:
    b = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", music], capture_output=True, text=True).stdout)
total, fade, fps = b - a, 1.0, 30
if len(sys.argv) > 6: pics = [pics[int(i)] for i in sys.argv[6].split(",")]
n = len(pics); each = (total + fade * (n - 1)) / n
inputs, chains = [], []
for i, p in enumerate(pics):
    inputs += ["-loop", "1", "-t", f"{each:.3f}", "-i", p]
    frames = int(each * fps) + 1
    z = f"1+0.10*on/{frames}" if i % 2 == 0 else f"1.10-0.10*on/{frames}"  # zoom in, then out, alternating
    chains.append(f"[{i}]scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},setsar=1,format=yuv420p[v{i}]")
last = "v0"
for i in range(1, n):
    chains.append(f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={i * (each - fade):.3f}[x{i}]"); last = f"x{i}"
fl = "afade=t=in:d=0.3," if a else ""
chains.append(f"[{n}]atrim={a}:{b},asetpts=PTS-STARTPTS,{fl}afade=t=out:st={total - 1.5:.3f}:d=1.5[aud]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-i", music, "-filter_complex", ";".join(chains),
                "-map", f"[{last}]", "-map", "[aud]", "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
