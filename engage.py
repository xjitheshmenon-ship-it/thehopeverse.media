"""After posting (owner, 4 Nov 2026: "get high volume of traffic to our shorts after posting"): for 48 hours after
a Short goes public, Mr. Spark posts a question as its first comment, adds the Short to its channel's playlist, and
answers new comments in the video's language. Pinning, the related-video link and community posts have no API:
the owner does those in YouTube Studio.

    dashboard.py calls run() on the hourly numbers run (BREAKOUTS=true in hope.yml's stats job)
    python engage.py --demo -> check the selection logic without any API

One small Sonnet call per Short that has work (well under $0.01), counted in DAILY_BUDGET. Done work is kept in
runs/engage.json on the state branch, saved alone (like predictions.json), so a video run can't undo it.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel

HERE = Path(__file__).parent
FILE = HERE / "runs" / "engage.json"
WINDOW = timedelta(hours=48)  # YouTube tests a new Short hardest in its first two days
MAX_REPLIES = 20  # per run: each posted comment costs 50 of the day's YouTube API quota
LANG = {"en": "English", "hi": "Hindi", "fr": "French", "ja": "Japanese", "de": "German", "es": "Spanish"}
RULES = ("Rules: write like a friendly, real person from the channel, 1-2 short sentences, no hashtags, no links, "
         "never ask for likes or subscribers. Never argue. Never state any opinion for or against a politician, party, "
         "religion or government; thank people and add a sourced fact or a question instead. If a comment is spam, "
         "abuse, hate, a scam or makes no sense, give an empty reply (skipped). Reply in the commenter's language when "
         "it is clear, else in the video's language.")


class Reply(BaseModel):
    id: str
    text: str  # "" = leave this comment alone


class Engagement(BaseModel):
    question: str  # the first comment: one short question that makes viewers want to answer; "" if not asked for
    replies: list[Reply]


def load() -> dict:
    return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}


def due(rows: list, now: datetime) -> list:
    """Shorts uploaded to YouTube in the last WINDOW (the dashboard's IST "published" times)."""
    return [r for r in rows if r.get("youtube_id") and r.get("published")
            and timedelta(0) <= now - datetime.strptime(r["published"], "%Y-%m-%d %H:%M") <= WINDOW]


def to_answer(threads: list, own: str, done: set) -> list:
    """Top-level comments by viewers that the channel hasn't answered yet: [(comment id, author, text)]."""
    out = []
    for t in threads:
        top = t["snippet"]["topLevelComment"]
        s = top["snippet"]
        replied = any(c["snippet"].get("authorChannelId", {}).get("value") == own for c in t.get("replies", {}).get("comments", []))
        if s.get("authorChannelId", {}).get("value") != own and not replied and top["id"] not in done:
            out.append((top["id"], s.get("authorDisplayName", ""), s.get("textOriginal", "")[:500]))
    return out


def _client(token: Path):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    # the saved sign-in carries the full "youtube" scope from connect.py, which commenting needs
    return build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(token)))


def playlist(yt, channel: dict, saved: dict) -> str:
    """The channel's Shorts playlist (channels.json "playlist" title), found or made once."""
    title = channel.get("playlist") or f"{channel['name']} Shorts"
    if channel["id"] not in saved:
        mine = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()["items"]
        found = next((p["id"] for p in mine if p["snippet"]["title"] == title), None)
        saved[channel["id"]] = found or yt.playlists().insert(part="snippet,status", body={
            "snippet": {"title": title, "description": channel.get("branding", {}).get("tagline", "")},
            "status": {"privacyStatus": "public"}}).execute()["id"]
    return saved[channel["id"]]


def write(package: dict, channel: dict, ask: bool, comments: list) -> tuple:
    from agents import HELPER_MODEL, _cost, client
    lang = LANG.get(package.get("lang") or channel.get("lang") or "en", channel.get("language") or "English")
    response = client.messages.parse(
        model=HELPER_MODEL, max_tokens=2000, output_config={"effort": "low"}, output_format=Engagement,
        messages=[{"role": "user", "content":
                   f"You are Mr. Spark, looking after the comments of a YouTube Short on {channel['name']} "
                   f"({channel.get('niche', '')}). The video is in {lang}.\n\nTitle: {package['title']}\n\n"
                   f"Description: {package['description'][:1500]}\n\n"
                   + ("question: write the channel's first comment, in the video's language: one short, personal "
                      "question about this Short that viewers will want to answer (no yes/no question).\n"
                      if ask else "question: \"\" (already posted).\n")
                   + "replies: one per comment below, same id. " + RULES + "\n\nComments:\n"
                   + json.dumps([{"id": i, "author": a, "text": t} for i, a, t in comments], ensure_ascii=False)}])
    return response.parsed_output, _cost(HELPER_MODEL, response.usage)


def run(rows: list, now: datetime) -> list:
    """Do the first-48-hours work for every due Short; returns the latest 60 comments seen, for the HQ page."""
    from agents import OUTBOX, _channels, budget_ok, log_spend
    channels, saved, seen = {c["id"]: c for c in _channels()}, load(), []
    lists, left, changed = saved.setdefault("_playlists", {}), MAX_REPLIES, False
    by_channel = {}
    for r in due(rows, now):
        by_channel.setdefault(r["channel"], []).append(r)
    for cid, shorts in by_channel.items():
        c = channels.get(cid, {})
        token = HERE / c.get("token", "token.json")
        if not token.exists():
            continue
        try:
            yt = _client(token)
            videos = {v["id"]: v for v in yt.videos().list(part="status,snippet", id=",".join(r["youtube_id"] for r in shorts)).execute()["items"]}
            for r in shorts:
                v = videos.get(r["youtube_id"])
                if not v or v["status"]["privacyStatus"] != "public":
                    continue  # still scheduled: comments open when it goes public
                vid, own = v["id"], v["snippet"]["channelId"]
                state = saved.setdefault(vid, {"replied": []})
                if not state.get("playlist"):
                    yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": playlist(yt, c, lists),
                                              "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
                    state["playlist"], changed = True, True
                threads = yt.commentThreads().list(part="snippet,replies", videoId=vid, maxResults=50, order="time").execute()["items"]
                answer = to_answer(threads, own, set(state["replied"]))[:left]
                shown = [{"id": i, "at": f"{now:%Y-%m-%d %H:%M}", "short": r["id"], "channel": cid, "title": r["title"], "url": r["url"], "author": a, "text": t,
                          "reply": None} for i, a, t in answer]
                seen += shown
                ask = not state.get("question")
                if not (ask or answer) or not budget_ok(0.05):
                    continue
                package = json.loads((OUTBOX / f"{r['id']}.json").read_text(encoding="utf-8"))
                out, cost = write(package, c, ask, answer)
                log_spend(cost, cid)
                changed = True
                if ask and out.question.strip():
                    yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid, "topLevelComment": {
                        "snippet": {"textOriginal": out.question.strip()}}}}).execute()
                    state["question"] = out.question.strip()
                    print(f"Question on https://youtu.be/{vid}: {state['question']}")
                texts = {x.id: x.text.strip() for x in out.replies}
                for (i, _, _), row in zip(answer, shown):
                    if texts.get(i):
                        yt.comments().insert(part="snippet", body={"snippet": {"parentId": i, "textOriginal": texts[i]}}).execute()
                        left -= 1
                        row["reply"] = texts[i]
                    state["replied"].append(i)  # a skipped (spam) comment isn't sent to Claude again
        except Exception as e:  # one channel's sign-in or quota problem shouldn't stop the others
            print(f"::warning::After-posting work on {cid}: {str(e)[:300]}")
    if seen:  # the HQ page shows the latest comments and what was answered, newest first
        latest = {x["id"]: x for x in reversed(seen + saved.get("_recent", []))}  # a comment shown again: newest wins
        saved["_recent"], changed = list(reversed(latest.values()))[:60], True
    if changed:
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
        from state import save
        logs = [p for p in ("runs/history.jsonl",) if (HERE / p).exists()]  # the stats run saves nothing else: keep the spend
        save([str(FILE.relative_to(HERE)), *logs])
    return saved.get("_recent", [])


def demo():
    now = datetime(2026, 11, 4, 18)
    rows = [{"youtube_id": "a", "published": "2026-11-04 12:00"}, {"youtube_id": "b", "published": "2026-11-01 12:00"},
            {"youtube_id": "c", "published": "2026-11-04 19:00"}, {"youtube_id": None, "published": "2026-11-04 12:00"}]
    assert [r["youtube_id"] for r in due(rows, now)] == ["a"]  # b too old, c scheduled for later, last not uploaded
    me = {"value": "ME"}
    thread = lambda i, who, replies=(): {"snippet": {"topLevelComment": {"id": i, "snippet": {
        "authorChannelId": {"value": who}, "authorDisplayName": who, "textOriginal": f"hi {i}"}}},
        "replies": {"comments": [{"snippet": {"authorChannelId": {"value": x}}} for x in replies]}}
    threads = [thread("1", "fan"), thread("2", "ME"), thread("3", "fan", ["ME"]), thread("4", "fan", ["other"]), thread("5", "fan")]
    assert [i for i, _, _ in to_answer(threads, me["value"], {"5"})] == ["1", "4"]  # own, answered, done are skipped
    print("ok")


if __name__ == "__main__" and sys.argv[1:] == ["--demo"]:
    demo()
