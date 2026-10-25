"""Mr. Hope (scout): one new channel idea a day, with a finished brand kit in the Hopeverse "Signal" style.

    python scout.py          -> ideas/<date>-<id>/ with kit.md (name, About text, keywords, setup steps) and the
                                images (profile, dark profile, banner, watermark); the idea also goes in the daily
                                report, runs/spend-report.md
    python scout.py --demo   -> render a sample kit without calling Claude, to check the look

Every kit shares Signal's system (Inter Display Black lowercase, a coloured dot, JetBrains Mono labels, ink
background with a hairline grid) and changes only the name, monogram and accent colour, so the channels read as
one network. Create the channel by hand in YouTube, then upload the images from the idea's folder.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pydantic import BaseModel

HERE = Path(__file__).parent
IDEAS = HERE / "ideas"
FONTS = HERE / "brand" / "fonts"
INK, FG, DIM = (11, 11, 12), (241, 241, 236), (92, 92, 90)
# Hopeverse Media keeps acid lime; every new channel gets one of these.
ACCENTS = {"signal orange": (255, 90, 31), "electric blue": (77, 124, 255), "mint": (62, 240, 168),
           "violet": (167, 139, 250), "saffron": (255, 178, 26), "rose": (255, 92, 138), "cyan": (46, 230, 255),
           "sand": (232, 217, 181)}


class Kit(BaseModel):
    id: str  # slug, e.g. "yt-paisa-pro"
    name: str  # in Latin letters, 1-3 words
    handle: str  # without the @
    label: str  # 2-4 words for the banner, e.g. "money for gen z"
    audience: str
    language: str
    niche: str
    why: str
    first_videos: list[str]
    tagline: str
    description: str
    keywords: list[str]
    accent: Literal[tuple(ACCENTS)]


def _font(name: str, size: int):
    return ImageFont.truetype(str(FONTS / name), size)


def _mark(ch: str, color, dot) -> Image.Image:
    """The monogram: one lowercase letter plus a round dot on its baseline, like Hopeverse's "h."."""
    im = Image.new("RGBA", (2400, 1800))
    d = ImageDraw.Draw(im)
    _, _, right, _ = d.textbbox((200, 1400), ch, font=_font("InterDisplay-Black.otf", 1200), anchor="ls")
    d.text((200, 1400), ch, font=_font("InterDisplay-Black.otf", 1200), fill=color, anchor="ls")
    d.ellipse((right + 90, 1400 - 205, right + 295, 1400), fill=dot)
    return im.crop(im.getbbox())


def _place(glyph: Image.Image, size: int, bg, width_frac: float = 0.52, lift: float = 0.025) -> Image.Image:
    w = round(size * width_frac)
    g = glyph.resize((w, round(glyph.height * w / glyph.width)), Image.LANCZOS)
    if g.height > size * 0.6:  # tall letters (l, k) are fitted by height instead
        h = round(size * 0.6)
        g = glyph.resize((round(glyph.width * h / glyph.height), h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg)
    canvas.alpha_composite(g, ((size - g.width) // 2, round((size - g.height) / 2 - size * lift)))
    return canvas


def _banner(kit: Kit, accent) -> Image.Image:
    im = Image.new("RGBA", (2560, 1440), INK + (255,))
    glow = Image.new("L", (2560, 1440))
    ImageDraw.Draw(glow).ellipse((380, 270, 2180, 1170), fill=16)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", im.size, accent).split(),
                                            glow.filter(ImageFilter.GaussianBlur(260)))))
    grid = Image.new("RGBA", im.size)
    g = ImageDraw.Draw(grid)
    for i in range(-3, 12):  # lines run through the safe area's edges (1546x424 at 507,508)
        g.line([(507 + i * 193.25, 0), (507 + i * 193.25, 1440)], fill=(255, 255, 255, 12))
    for i in range(-5, 10):
        g.line([(0, 508 + i * 106), (2560, 508 + i * 106)], fill=(255, 255, 255, 12))
    im.alpha_composite(grid)
    d = ImageDraw.Draw(im)
    for x, y in ((507, 508), (2053, 508), (507, 932), (2053, 932)):
        d.line([(x - 14, y), (x + 14, y)], fill=DIM, width=2)
        d.line([(x, y - 14), (x, y + 14)], fill=DIM, width=2)
    mono = lambda size: _font("JetBrainsMono-Medium.ttf", size)
    corner = f"[HV/NETWORK] — {kit.id.upper()} "
    d.text((150, 150), corner, font=mono(20), fill=DIM)
    d.text((150 + d.textlength(corner, font=mono(20)), 150), "●", font=mono(20), fill=accent)
    d.text((2410, 1290), f"A HOPEVERSE CHANNEL · {kit.language.upper()}", font=mono(20), fill=DIM, anchor="rd")

    word, size = kit.name.lower(), 262
    # Signal's tight tracking (-7px at 262px); Pillow has no letter-spacing, so letters are placed one by one
    wide = lambda s: sum(d.textlength(c, font=_font("InterDisplay-Black.otf", s)) - s * 0.027 for c in word)
    while wide(size) + size * 0.22 > 1326:
        size -= 4
    big = _font("InterDisplay-Black.otf", size)
    left, base = 507 + 110, 508 + 424 // 2 + round(size * 0.28)
    d.text((left, base - size * 0.78 - 34), f"[01]  {kit.label.upper()}", font=mono(22), fill=DIM, anchor="ls")
    d.text((left + 1326, base - size * 0.78 - 34), f"YT / IG  @{kit.handle.upper()}", font=mono(22), fill=DIM,
           anchor="rs")
    x = left - 8
    for c in word:
        d.text((x, base), c, font=big, fill=FG, anchor="ls")
        x += d.textlength(c, font=big) - size * 0.027
    r, dot = x + size * 0.08, size * 0.16
    d.ellipse((r, base - dot, r + dot, base), fill=accent)
    d.text((left, base + round(size * 0.34)), f"→ {kit.tagline}", font=mono(36), fill=accent, anchor="ls")
    return im


def render(kit: Kit, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    accent = ACCENTS[kit.accent]
    ch = next((c for c in kit.name.lower() if c.isalpha()), "h")
    avatar = _place(_mark(ch, INK, INK), 800, accent + (255,))
    avatar.convert("RGB").save(out / "profile-800.png")
    _place(_mark(ch, FG, accent), 800, INK + (255,)).convert("RGB").save(out / "profile-800-dark.png")
    mask = Image.new("L", (600, 600))
    ImageDraw.Draw(mask).ellipse((0, 0, 599, 599), fill=255)
    wm = avatar.resize((600, 600), Image.LANCZOS)
    wm.putalpha(mask)
    wm.resize((150, 150), Image.LANCZOS).save(out / "watermark-150.png")
    _banner(kit, accent).convert("RGB").save(out / "banner-2560x1440.png", optimize=True)
    (out / "kit.json").write_text(kit.model_dump_json(indent=2), encoding="utf-8")
    videos = "\n".join(f"{i}. {v}" for i, v in enumerate(kit.first_videos, 1))
    (out / "kit.md").write_text(f"""# {kit.name}  (@{kit.handle})

**{kit.tagline}**

- Audience: {kit.audience} ({kit.language})
- Niche: {kit.niche}
- Why now: {kit.why}

## Channel description (paste into YouTube > Customisation > Basic info)

{kit.description}

## Keywords

{", ".join(kit.keywords)}

## First videos

{videos}

## Images in this folder

- profile-800.png: profile picture (dark version: profile-800-dark.png)
- banner-2560x1440.png: banner image (the text sits inside YouTube's safe area)
- watermark-150.png: video watermark (Customisation > Branding)

## To launch it

1. In YouTube, Switch account > Create a channel, named "{kit.name}", handle @{kit.handle}.
2. Upload the images above and paste the description and keywords.
3. Tell Claude "launch {kit.name}": it adds `{kit.id}` to channels.json and gives you the one sign-in step.
""", encoding="utf-8")


def scout() -> Path:
    from agents import DAILY_BUDGET, HISTORY, MODEL, WEB_SEARCH, _channels, _cost, client, spent_today
    if spent_today() >= DAILY_BUDGET:
        sys.exit(f"Daily budget of ${DAILY_BUDGET:.2f} reached; no channel idea today.")
    past = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(IDEAS.glob("*/kit.json"))]
    known = [f"{c['name']}: {c['niche']} ({c['audience']})" for c in _channels()] + \
            [f"{k['name']}: {k['niche']} ({k['audience']})" for k in past]
    response = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        output_config={"effort": "medium"},
        tools=[WEB_SEARCH],
        system=(
            "You are Mr. Hope, who runs Hopeverse Media, an AI-run studio of faceless YouTube Shorts channels "
            "(tagline \"Made by AI. Made with hope.\"). Each day you propose ONE new channel that reaches an audience "
            "the network doesn't reach yet. Main markets: India, the US and the EU; any language Edge TTS speaks. "
            "Pick an audience with real demand and advertiser value that Shorts made from stock footage, AI images "
            "and an AI voice can serve well, and that is safe to monetise (no reused content, no copied shows, no "
            "medical or financial advice). Search the web for evidence (growing searches, successful channels, CPM)."),
        messages=[{"role": "user", "content":
                   "Channels and ideas that already exist, don't repeat them:\n- " + "\n- ".join(known) + "\n\n"
                   "Return: id (slug starting 'yt-'); name (1-3 words, Latin letters, memorable, premium, easy to say "
                   "in the audience's language, no 'TV', 'Official' or numbers); handle (no @, letters and digits, "
                   "probably free on YouTube); label (2-4 words for the banner, lowercase); audience (region, age, "
                   "language); language; niche (one line); why (2 sentences of evidence, with numbers); "
                   "first_videos (5 Short ideas with curiosity hooks); tagline (under 34 characters, calm and "
                   "confident, like a premium magazine); description (the YouTube About text: 3 short paragraphs, "
                   "what viewers get, how often (6 Shorts a day), one line saying it's an AI-made Hopeverse "
                   "channel, in the audience's language, no emojis, no hype words like 'ultimate' or 'insane'); "
                   "keywords (10-15); accent (the colour that suits the mood)."}],
        output_format=Kit,
    )
    kit, cost = response.parsed_output, _cost(MODEL, response.usage)
    out = IDEAS / f"{datetime.now():%Y-%m-%d}-{kit.id}"
    render(kit, out)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "cost_usd": round(cost, 2)}) + "\n")
    print(f"New channel idea: {kit.name} (${cost:.2f}) -> {out}")
    return out


DEMO = Kit(id="yt-paisa-pro", name="Paisa Pro", handle="PaisaProShorts", label="money for gen z india",
           audience="India, 18-30", language="Hinglish", niche="Money habits and how India's economy works",
           why="Demo kit.", first_videos=["Why a ₹10 coin costs more to make than it's worth"],
           tagline="Money, minus the noise.", description="Demo.", keywords=["money"], accent="saffron")

if __name__ == "__main__":
    if "--demo" in sys.argv:
        render(DEMO, IDEAS / "demo")
    else:
        scout()
        from agents import spend_report
        spend_report()
