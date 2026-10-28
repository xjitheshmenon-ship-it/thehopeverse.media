"""Predicted views next to the relevance score, checked against YouTube and fed back (owner's ask, 28 Oct 2026).

Mr. Focus (plan.py) predicts each topic's YouTube views 48 hours after posting, and the relevance check before upload
(video.py) predicts them again on the final script; that last guess is the one that gets checked. Once a Short is
48-72 hours old, the hourly numbers run (dashboard.py) records its real views next to the guess in
runs/predictions.json on the state branch. Both predictions are asked with the channel's track record (its last
guesses against what really happened, and how far off they ran), so every new guess corrects the last ones.

    python predict.py --demo -> check the bookkeeping without any API
"""
import json
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
FILE = HERE / "runs" / "predictions.json"  # {short id: {channel, title, predicted, actual, at}}; saved only by record()
HOURS = 48
TRACK = 15  # recent results per channel shown to the predictor

ASK = (f"views48: predict this Short's YouTube views {HOURS} hours after it goes up, as a whole number. Base it on the "
       "channel's real numbers below, not on hope; a Short that matches what broke out before can beat them.")


def load() -> dict:
    return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}


def record(rows: list, now: datetime) -> list:
    """Save the real views of every Short now 48-72 hours old (dashboard rows), next to its prediction; new ids.
    Older ones are skipped: their views today are not their 48-hour views."""
    seen, new = load(), []
    for r in rows:
        if r["id"] in seen or r.get("yt_views") is None or not r.get("published"):
            continue
        age = now - datetime.fromisoformat(r["published"])
        if timedelta(hours=HOURS) <= age < timedelta(hours=HOURS + 24):
            seen[r["id"]] = {"channel": r["channel"], "title": r["title"], "predicted": r.get("predicted_48h"),
                             "actual": r["yt_views"], "at": f"{now:%Y-%m-%d %H:%M}"}
            new.append(r["id"])
    if new:
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
        from state import save
        save([str(FILE.relative_to(HERE))])  # only this file, like breakouts: never in state.files(), so no run undoes it
    return new


def accuracy(results: list) -> dict:
    """How the guesses did: median real views, median guess/real ratio (bias) and share within 2x either way."""
    pairs = [(r["predicted"], r["actual"]) for r in results if r.get("predicted") is not None]
    ratio = [max(p, 1) / max(a, 1) for p, a in pairs]
    return {"shorts": len(results), "median_actual": statistics.median(r["actual"] for r in results) if results else None,
            "checked": len(pairs), "bias": round(statistics.median(ratio), 2) if ratio else None,
            "within_2x": round(100 * sum(0.5 <= x <= 2 for x in ratio) / len(ratio)) if ratio else None}


def track(channel: str) -> str:
    """The channel's track record, for a prompt: recent guesses against real 48-hour views, and the bias."""
    mine = sorted((r for r in load().values() if r["channel"] == channel), key=lambda r: r["at"])[-TRACK:]
    if not mine:
        return f"This channel has no {HOURS}-hour results yet: guess low, new Shorts channels often get under 100 views."
    a = accuracy(mine)
    bias = (f" Your guesses ran {a['bias']}x the real views (median), {a['within_2x']}% within 2x: correct for that."
            if a["bias"] else "")
    return (f"This channel's last {len(mine)} Shorts, real views at {HOURS} hours (median {a['median_actual']:.0f}):\n"
            + "\n".join(f"- {r['actual']} real" + (f", {r['predicted']} guessed" if r.get("predicted") is not None else "")
                        + f": {r['title']}" for r in mine) + "\n" + bias.strip())


def demo():
    global FILE, HERE
    import tempfile
    HERE = Path(tempfile.mkdtemp())
    FILE = HERE / "p.json"
    import state
    state.save = lambda only=None: None
    now = datetime(2026, 10, 30, 12)
    row = lambda i, h, v, p=None: {"id": i, "channel": "yt-x", "title": i, "yt_views": v, "predicted_48h": p,
                                   "published": f"{now - timedelta(hours=h):%Y-%m-%d %H:%M}"}
    rows = [row("a", 50, 40, 200), row("b", 30, 10, 50), row("c", 100, 900, 100), row("d", 60, 100, 100), row("e", 49, 5)]
    assert record(rows, now) == ["a", "d", "e"]  # b too young, c too old
    assert record(rows, now) == []  # recorded once
    a = accuracy(list(load().values()))
    assert (a["checked"], a["bias"], a["within_2x"], a["median_actual"]) == (2, 3.0, 50, 40), a  # a 5x high, d spot on
    assert "3.0x" in track("yt-x") and "no 48-hour" in track("yt-y")
    print("ok")


if __name__ == "__main__" and sys.argv[1:] == ["--demo"]:
    demo()
