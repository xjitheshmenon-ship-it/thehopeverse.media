"""What is left on each paid service, so a run never goes dry without warning.

    python credits.py    -> print the table

fal.ai, HeyGen and ElevenLabs report their balance over their APIs. Anthropic and Perplexity have no balance API
for a normal key, so their rows show the logged spend instead. dashboard.py shows the table and the 5 PM report
(agents.spend_report) warns when something is low.
"""
import json
import os
import urllib.request

# Below these, the row turns "low": about a day of normal use.
LOW = {"fal.ai": 5.0, "HeyGen": 20.0, "ElevenLabs": 20000}


def _get(url: str, **headers) -> dict:
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30))


def _row(service: str, left, unit: str, note: str, low: float = None) -> dict:
    status = "unknown" if left is None else "empty" if left <= 0 else "low" if low is not None and left < low else "ok"
    return {"service": service, "left": left, "unit": unit, "status": status, "note": note}


def check() -> list:
    rows = []
    key = os.environ.get("FAL_KEY", "").strip()
    try:
        bal = _get("https://api.fal.ai/v1/account/billing?expand=credits", Authorization=f"Key {key}")["credits"]
        rows.append(_row("fal.ai", round(bal["current_balance"], 2), bal.get("currency", "USD").lower(),
                         "Images, Kling clips, music, Instagram uploads", LOW["fal.ai"]))
    except Exception as e:  # e.g. a key without billing:usage:read
        rows.append(_row("fal.ai", None, "usd", f"Couldn't read the balance ({e}); needs a key with billing read access"))
    key = os.environ.get("HEYGEN_API_KEY", "").strip()
    try:
        q = _get("https://api.heygen.com/v2/user/remaining_quota", **{"x-api-key": key})["data"]
        rows.append(_row("HeyGen", round(q["remaining_quota"] / 60, 1), "credits",
                         "Talking hosts; Kling on fal.ai takes over when it runs out", LOW["HeyGen"]))
    except Exception as e:
        rows.append(_row("HeyGen", None, "credits", f"Couldn't read the balance ({e})"))
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    try:
        s = _get("https://api.elevenlabs.io/v1/user/subscription", **{"xi-api-key": key})
        rows.append(_row("ElevenLabs", s["character_limit"] - s["character_count"], "characters",
                         f"Voices; free Edge voices take over when it runs out. Plan: {s.get('tier', '?')}",
                         LOW["ElevenLabs"]))
    except Exception as e:  # a restricted key needs "User: read" permission
        rows.append(_row("ElevenLabs", None, "characters", f"Couldn't read the balance ({e}); needs User read permission"))
    for service, note in [("Anthropic", "No balance API: see console.anthropic.com > Billing. Spend is logged per run"),
                          ("Perplexity", "No balance API: see perplexity.ai/account/api. About $0.006 a search")]:
        rows.append(_row(service, None, "usd", note))
    return rows


def warnings(rows: list) -> list:
    return [f"{r['service']} is {r['status']}: {r['left']} {r['unit']} left" for r in rows if r["status"] in ("low", "empty")]


if __name__ == "__main__":
    for r in check():
        print(f"{r['service']:<11} {r['status']:<8} {r['left']} {r['unit']}  {r['note']}")
    assert _row("x", 0, "usd", "", 5)["status"] == "empty" and _row("x", 3, "usd", "", 5)["status"] == "low" \
        and _row("x", 9, "usd", "", 5)["status"] == "ok" and _row("x", None, "usd", "")["status"] == "unknown"
