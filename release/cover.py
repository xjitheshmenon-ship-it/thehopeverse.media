"""3000x3000 Spotify covers in the ÆTHER Shockwave look: title wall, spectrum bars of the real track breaking through it."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FF = "ffmpeg"
BIG = "/root/.claude/skills/synced/54e1e9f6-013a-4703-b66a-e4b26fa3f1fd_68cccd3c-b1fa-48be-a32b-b12f1c4f1e32/canvas-design/canvas-fonts/BigShoulders-Bold.ttf"
BR = "/mnt/project-files/utube/brand/fonts/"
LOCK = "/mnt/project-files/music/locked/"
W = 3000
M = 200
SETS = {1: ("060608", "ff1a3c", "4b1fd1", "f4f4f2"), 2: ("08080a", "1e9bff", "ff2e93", "f4f4f2"),
        3: ("1a2fc4", "ff5a3c", "5a8cff", "ffffff"), 4: ("a996e0", "d8ff1f", "ff5a3c", "1a1033"),
        5: ("031417", "ff9a1f", "0f6b73", "f4ecd8"), 6: ("0b0b0c", "c8f53a", "7a3dff", "f1f1ec")}


def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def levels(mp3, at):
    pcm = np.frombuffer(subprocess.run([FF, "-v", "error", "-i", mp3, "-ac", "1", "-ar", "44100", "-f", "f32le", "-"],
                                       capture_output=True, check=True).stdout, np.float32)
    seg = pcm[int(at * 44100):int(at * 44100) + 8192] * np.hanning(8192)
    spec = np.abs(np.fft.rfft(seg))
    idx = np.unique(np.geomspace(5, 2200, 64).astype(int))
    db = 20 * np.log10(np.array([spec[a:b + 1].mean() for a, b in zip(idx[:-1], idx[1:])]) + 1e-9)
    return np.clip((db - db.min()) / (db.max() - db.min()), 0, 1) ** 1.3


def fit(text, path, width, cap):
    lo, hi = 10, cap
    while hi - lo > 1:
        mid = (lo + hi) // 2
        b = ImageFont.truetype(path, mid).getbbox(text)
        lo, hi = (mid, hi) if b[2] - b[0] <= width else (lo, mid)
    return ImageFont.truetype(path, lo)


def cover(out, lines, mp3, at, s, sub):
    BLK, RED, IND, WHT = map(hexc, SETS[s])
    img = Image.new("RGBA", (W, W), BLK)
    haze = Image.new("RGBA", (W, W))
    ImageDraw.Draw(haze).ellipse([-W * .4, W * .45, W * 1.4, W * 1.4], fill=IND[:3] + (150,))
    img = Image.alpha_composite(img, haze.filter(ImageFilter.GaussianBlur(400)))
    cap = 1100
    while True:  # shrink until the title block fits above the bars' floor
        fonts = [fit(t, BIG, W - 2 * M, cap) for t in lines]
        if sum(f.getbbox(t)[3] + 30 for t, f in zip(lines, fonts)) <= 1750:
            break
        cap -= 20
    title = Image.new("L", (W, W))
    td, y, pos = ImageDraw.Draw(title), 470, []
    for t, f in zip(lines, fonts):
        td.text((W / 2, y), t, font=f, fill=255, anchor="mt")
        pos.append((y, t, f))
        y += f.getbbox(t)[3] + 30
    img.paste(Image.new("RGBA", (W, W), WHT), mask=title)
    lvl, n, base = levels(mp3, at), 24, 2560
    bars = Image.new("RGBA", (W, W))
    bd, bw = ImageDraw.Draw(bars), (W - 2 * M) / n
    for i in range(n):
        top = base - (350 + 900 * lvl[int(i * len(lvl) / n)])
        bd.rectangle([M + i * bw + 14, top, M + (i + 1) * bw - 14, base], fill=RED)
    img = Image.alpha_composite(img, Image.alpha_composite(bars.filter(ImageFilter.GaussianBlur(100)), bars))
    knock = np.minimum(np.array(title), np.array(bars.getchannel("A")))
    img.paste(Image.new("RGBA", (W, W), BLK), mask=Image.fromarray(knock))
    d = ImageDraw.Draw(img)
    d.rectangle([M, base + 70, W - M, base + 86], fill=WHT)
    d.text((M, 230), "ÆTHER", font=ImageFont.truetype(BR + "InterDisplay-Black.otf", 140), fill=WHT, anchor="lm")
    if sub:
        d.text((W - M, base + 200), sub, font=ImageFont.truetype(BR + "JetBrainsMono-Medium.ttf", 84), fill=RED, anchor="rm")
    a = np.array(img.convert("RGB"), np.float32) + np.random.default_rng(3).normal(0, 7, (W, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=95)


COVERS = [("aether-vol-1.jpg", ["ORIGINAL", "SCORE", "VOL. 1"], "the-return.mp3", 6.3, 1, ""),
          ("yaaru-nee.jpg", ["YAARU", "NEE?"], "yaaru-nee-full.mp3", 40, 4, ""),
          ("steppu-veyyi-raa.jpg", ["STEPPU", "VEYYI", "RAA"], "steppu-veyyi-raa.mp3", 20, 6, "")]
if __name__ == "__main__":
    for out, lines, mp3, at, s, sub in COVERS:
        p = "/mnt/project-files/spotify/covers/" + out
        cover(p, lines, LOCK + mp3, at, s, sub)
        assert Image.open(p).size == (3000, 3000), p
        print(p)
