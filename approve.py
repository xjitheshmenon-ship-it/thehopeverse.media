"""Telegram approvals: Hope sends each new Short at 4 PM, you tap Approve or Skip, and the 6 PM run posts
only what you approved. It also sends the daily spending report.

One-time setup: in Telegram, message @BotFather, send /newbot and copy the token, then send any message
to your new bot. Then: setx TELEGRAM_TOKEN "<token>". Optional: setx HOPE_APPROVAL auto to post everything
unless you tap Skip (the default, "approve", posts only what you approved).

    python approve.py ask       4 PM: send each finished Short for approval
    python approve.py collect   6 PM: read your taps into the outbox packages
    python approve.py report    6 PM: send the spending report and today's links
"""
import json
import os
import sys
import urllib.parse
import urllib.request

from agents import HERE, OUTBOX

CHAT = HERE / "runs" / "telegram.json"  # the chat id (found automatically) and the last update read


def _api(method: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/{method}"
    data = urllib.parse.urlencode({k: json.dumps(v) if isinstance(v, dict) else v for k, v in params.items()}).encode()
    return json.load(urllib.request.urlopen(url, data=data, timeout=60))["result"]


def _state() -> dict:
    return json.loads(CHAT.read_text()) if CHAT.exists() else {"offset": 0}


def _updates(state: dict) -> list:
    """New messages and button taps since the last read; also learns the owner's chat id from the first message."""
    updates = _api("getUpdates", offset=state["offset"], timeout=0)
    for u in updates:
        state["offset"] = u["update_id"] + 1
        msg = u.get("message") or u.get("callback_query", {}).get("message")
        if msg and "chat_id" not in state:
            state["chat_id"] = msg["chat"]["id"]
    CHAT.parent.mkdir(exist_ok=True)
    CHAT.write_text(json.dumps(state))
    return updates


def _chat(state: dict):
    if "chat_id" not in state:
        _updates(state)
    if "chat_id" not in state:
        raise SystemExit("Send any message to your Telegram bot first, so Hope knows where to write.")
    return state["chat_id"]


def _packages():
    for p in sorted(OUTBOX.glob("*.json")):
        yield p, json.loads(p.read_text(encoding="utf-8"))


def ask():
    state = _state()
    chat = _chat(state)
    for p, d in _packages():
        if "youtube_id" in d or "approval" in d or d.get("asked") or not p.with_suffix(".mp4").exists():
            continue
        text = f"New Short for 6 PM: {d['title']}\n\n{d['description'][:3000]}"
        buttons = {"inline_keyboard": [[{"text": "Approve", "callback_data": f"ok:{p.stem}"},
                                        {"text": "Skip", "callback_data": f"no:{p.stem}"}]]}
        _api("sendMessage", chat_id=chat, text=text, reply_markup=buttons)
        d["asked"] = True
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    print("Sent for approval")


def collect():
    state = _state()
    for u in _updates(state):
        q = u.get("callback_query")
        if not q or ":" not in q.get("data", ""):
            continue
        choice, stem = q["data"].split(":", 1)
        path = OUTBOX / f"{stem}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            d["approval"] = "ok" if choice == "ok" else "no"
            path.write_text(json.dumps(d, indent=2), encoding="utf-8")
        _api("answerCallbackQuery", callback_query_id=q["id"], text="Approved" if choice == "ok" else "Skipped")
    print("Approvals read")


def approved(package: dict) -> bool:
    """Whether video.py may post this package. Without Telegram set up, everything posts as before."""
    if not os.environ.get("TELEGRAM_TOKEN"):
        return True
    if os.environ.get("HOPE_APPROVAL", "approve") == "auto":
        return package.get("approval") != "no"
    return package.get("approval") == "ok"


def report():
    state = _state()
    spend = HERE / "runs" / "spend-report.md"
    links = [f"{d['title']}: https://youtu.be/{d['youtube_id']}" for _, d in _packages()
             if d.get("youtube_id") and not d.get("reported")]
    text = (spend.read_text(encoding="utf-8") if spend.exists() else "No spending report yet.") + \
        ("\n\nPosted today:\n" + "\n".join(links) if links else "")
    _api("sendMessage", chat_id=_chat(state), text=text[:4000])
    for p, d in _packages():
        if d.get("youtube_id") and not d.get("reported"):
            d["reported"] = True
            p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    print("Report sent")


if __name__ == "__main__":
    if not os.environ.get("TELEGRAM_TOKEN"):
        raise SystemExit("TELEGRAM_TOKEN not set; see the top of approve.py")
    {"ask": ask, "collect": collect, "report": report}[sys.argv[1]]()
