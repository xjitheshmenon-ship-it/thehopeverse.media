"""Predicted views next to the relevance score, checked against YouTube and fed back (owner's ask, 28 Oct 2026).

Mr. Focus (plan.py) predicts each topic's YouTube views 48 hours after posting, and the relevance check before upload
(video.py) predicts them again on the final script; that last guess is the one that gets checked. Once a Short is
48-72 hours old, the hourly numbers run (dashboard.py) records its real views next to the guess in
runs/predictions.json on the state branch. Both predictions are asked with the channel's track record (its last
guesses against what really happened, and how far off they ran), so every new guess corrects the last ones.

Every day (first hourly numbers run after midnight IST, owner's ask 2 Nov 2026) daily() also reads each channel's
current pattern, free and with no AI call: YouTube Analytics for the last 28 days (views per day as a trend, traffic
sources, retention against views per Short, subscribers or not) plus, from Hope's own rows, views by the Short's age
and 48-hour views by the hour it went up. It goes into runs/patterns.json and every prediction prompt via track().

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
PATTERNS = HERE / "runs" / "patterns.json"  # {channel: {"day", "text"}}; saved only by daily()

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
    """The channel's track record and today's pattern, for a prompt."""
    p = patterns().get(channel)
    return _track(channel) + (f"\nThis channel's pattern right now (checked {p['day']}):\n{p['text']}" if p else "")


def _track(channel: str) -> str:
    """Recent guesses against real 48-hour views, and the bias."""
    mine = sorted((r for r in load().values() if r["channel"] == channel), key=lambda r: r["at"])[-TRACK:]
    if not mine:
        return f"This channel has no {HOURS}-hour results yet: guess low, new Shorts channels often get under 100 views."
    a = accuracy(mine)
    bias = (f" Your guesses ran {a['bias']}x the real views (median), {a['within_2x']}% within 2x: correct for that."
            if a["bias"] else "")
    return (f"This channel's last {len(mine)} Shorts, real views at {HOURS} hours (median {a['median_actual']:.0f}):\n"
            + "\n".join(f"- {r['actual']} real" + (f", {r['predicted']} guessed" if r.get("predicted") is not None else "")
                        + f": {r['title']}" for r in mine) + "\n" + bias.strip())


def _median(xs):
    return round(statistics.median(xs)) if xs else None


def _own(channel: str, rows: list, now: datetime) -> list:
    """Patterns from Hope's own rows, no API: views by the Short's age now, 48-hour views by hour posted (IST)."""
    mine = [r for r in rows if r["channel"] == channel and r.get("published") and r.get("yt_views") is not None]
    age = lambda r: (now - datetime.fromisoformat(r["published"])).total_seconds() / 3600
    out = []
    ages = [(n, [r["yt_views"] for r in mine if lo <= age(r) < hi]) for n, lo, hi in
            [("under 1 day", 0, 24), ("1-2 days", 24, 48), ("2-7 days", 48, 168), ("over a week", 168, 1e9)]]
    if any(v for _, v in ages):
        out.append("Median views by age now: " + ", ".join(f"{n} {_median(v)} ({len(v)} Shorts)" for n, v in ages if v))
    done, slots = load(), {}
    for r in mine:
        if r["id"] in done:
            h = int(r["published"][11:13])
            slots.setdefault("night 0-6" if h < 6 else "morning 6-12" if h < 12 else "afternoon 12-18" if h < 18
                             else "evening 18-24", []).append(done[r["id"]]["actual"])
    if slots:
        out.append("Median 48-hour views by hour posted (IST): " + ", ".join(f"{k} {_median(v)} ({len(v)})" for k, v in sorted(slots.items())))
    return out


def _analytics(channel: dict, now: datetime) -> list:
    """The channel's last 28 days in YouTube Analytics (about 2 days behind): trend, traffic, retention, subscribers."""
    from video import youtube
    api = youtube(False, HERE / channel.get("token", "token.json"), ("youtubeAnalytics", "v2"))
    q = lambda **kw: api.reports().query(ids="channel==MINE", startDate=f"{now - timedelta(days=28):%Y-%m-%d}",
                                         endDate=f"{now:%Y-%m-%d}", **kw).execute().get("rows") or []
    out = []
    days = [v for _, v in sorted(q(metrics="views", dimensions="day"))]
    if len(days) >= 8:
        last, before = sum(days[-7:]), sum(days[-14:-7])
        out.append(f"Channel views, last 7 days {last} vs the 7 before {before}"
                   + (f" ({100 * (last - before) / before:+.0f}%)" if before else ""))
    traffic = q(metrics="views", dimensions="insightTrafficSourceType", sort="-views")
    total = sum(v for _, v in traffic)
    if total:
        out.append("Where views came from (28 days): " + ", ".join(f"{k} {100 * v / total:.0f}%" for k, v in traffic[:5]))
    vids = [(v, p) for _, v, p in q(metrics="views,averageViewPercentage", dimensions="video", sort="-views", maxResults=200) if v]
    if len(vids) >= 4:
        cut = statistics.median(p for _, p in vids)
        hi, lo = [v for v, p in vids if p >= cut], [v for v, p in vids if p < cut]
        out.append(f"Retention: median Short watched {cut:.0f}%; Shorts above that got median {_median(hi)} views, "
                   f"below it {_median(lo)}")
    sub = {k: v for k, v, *_ in q(metrics="views", dimensions="subscribedStatus")}
    if sum(sub.values()):
        out.append(f"Views from non-subscribers: {100 * sub.get('UNSUBSCRIBED', 0) / sum(sub.values()):.0f}%")
    return out


def daily(rows: list, now: datetime, channels: list) -> list:
    """Once a day per YouTube channel: save its current pattern for the predictor (free; no AI). Channels done."""
    seen, done, today = patterns(), [], f"{now:%Y-%m-%d}"
    for c in channels:
        if c["platform"] != "youtube" or seen.get(c["id"], {}).get("day") == today:
            continue
        lines = _own(c["id"], rows, now)
        try:
            lines += _analytics(c, now) if (HERE / c.get("token", "token.json")).exists() else []
        except Exception as e:  # expired sign-in (invalid_grant) etc.: keep the free part, say so once
            print(f"::warning::Analytics patterns for {c['id']}: {str(e)[:200]}")
            lines.append("(YouTube Analytics unavailable today: sign-in needs reconnecting)")
        if lines:
            seen[c["id"]] = {"day": today, "text": "\n".join(f"- {x}" for x in lines)}
            done.append(c["id"])
    if done:
        PATTERNS.parent.mkdir(exist_ok=True)
        PATTERNS.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
        from state import save
        save([str(PATTERNS.relative_to(HERE))])  # alone, like predictions.json
    return done


def patterns() -> dict:
    return json.loads(PATTERNS.read_text(encoding="utf-8")) if PATTERNS.exists() else {}


def demo():
    global FILE, HERE, PATTERNS, _analytics
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
    import types  # the Analytics parsing, on a fake API that answers like YouTube's
    canned = {"day": [[f"d{i:02}", 10 + i] for i in range(14)], "insightTrafficSourceType": [["SHORTS", 90], ["SEARCH", 10]],
              "video": [["v1", 500, 80.0], ["v2", 300, 70.0], ["v3", 20, 30.0], ["v4", 10, 20.0]],
              "subscribedStatus": [["UNSUBSCRIBED", 95], ["SUBSCRIBED", 5]]}
    call = lambda **kw: types.SimpleNamespace(execute=lambda: {"rows": canned[kw["dimensions"]]})
    sys.modules["video"] = types.SimpleNamespace(youtube=lambda *a: types.SimpleNamespace(reports=lambda: types.SimpleNamespace(query=call)))
    got = "\n".join(_analytics({}, now))
    assert "last 7 days 140 vs the 7 before 91 (+54%)" in got and "SHORTS 90%" in got, got
    assert "watched 50%; Shorts above that got median 400 views, below it 15" in got and "non-subscribers: 95%" in got, got
    PATTERNS = HERE / "pat.json"
    _analytics = lambda c, now: (_ for _ in ()).throw(RuntimeError("invalid_grant"))  # expired sign-in
    (HERE / "token.json").write_text("{}")
    chans = [{"id": "yt-x", "platform": "youtube"}, {"id": "ig-x", "platform": "instagram"}]
    assert daily(rows, now, chans) == ["yt-x"] and daily(rows, now, chans) == []  # once a day
    t = track("yt-x")
    assert "under 1 day" not in t and "2-7 days 70 (4 Shorts)" in t and "unavailable" in t, t
    assert "night 0-6" in t or "morning" in t or "afternoon" in t or "evening" in t, t
    print("ok")


if __name__ == "__main__" and sys.argv[1:] == ["--demo"]:
    demo()
