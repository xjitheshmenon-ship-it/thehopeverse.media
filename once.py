"""Put ÆTHER releases on Spotify etc. through ONCE (docs.once.app/rest-api). Needs the ONCE_TOKEN secret.
step=check: upload the files (free), print the price, store list and rules. Nothing is submitted or charged.
step=submit: same, then submit (debits credits: 2 per AI song). release=album|yaaru|steppu|all"""
import datetime, json, os, sys, urllib.request

API = "https://once.app/v1"
RAW = "https://raw.githubusercontent.com/" + os.environ.get("GITHUB_REPOSITORY", "xjitheshmenon-ship-it/thehopeverse.media") + "/main/"
CFG = json.load(open("release/aether.json", encoding="utf-8"))


def call(path, body=None):
    req = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(),
                                 method="GET" if body is None else "POST",
                                 headers={"Authorization": "Bearer " + os.environ["ONCE_TOKEN"].strip(),
                                          "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"{path} -> {e.code}: {e.read()[:2000].decode(errors='replace')}")


def upload(kind, repo_path):
    r = call("/files/from-url", {"type": kind, "url": RAW + repo_path, "file_name": repo_path.rsplit("/", 1)[1]})
    return r.get("fileUrl") or r.get("file_url") or r["url"]


def payload(rel, stores):
    a, w, year = CFG["artist"], CFG["writer"], str(datetime.date.today().year)
    line = {"pline_year": year, "pline_owner": a, "cline_year": year, "cline_owner": a}
    release = {"title": rel["title"], "primary_artist_name": a, "genre": rel["genre"], "label": a,
               "release_date": str(datetime.date.today() + datetime.timedelta(days=7)),
               "cover_art_file_url": upload("coverArt", rel["cover"]), "distribution_store_ids": stores,
               "contributors": [{"name": a, "role": "Producer"}], **line}
    if rel.get("sub_genre"):
        release["sub_genre"] = rel["sub_genre"]
    if rel.get("language"):
        release["audio_language"] = rel["language"]
    tracks = []
    for title, f in rel["tracks"]:
        t = {"title": title, "primary_artist_name": a, "audio_file_url": upload("audio", f"music/locked/{f}.mp3"),
             "explicit_flag": False, "track_type": "original", "contains_ai": True, "writers": [{"name": w}],
             "contributors": [{"name": a, "role": "Producer"}], **line}
        if rel.get("language"):
            t["language"] = rel["language"]
        tracks.append(t)
    return {"release": release, "tracks": tracks}


if __name__ == "__main__":
    step, which = os.environ.get("STEP", "check"), os.environ.get("RELEASE", "all")
    print("account:", json.dumps(call("/me"))[:300])
    print("credits:", json.dumps(call("/me/credits"))[:300])
    allstores = call("/distribution-stores")
    print("stores:", json.dumps(allstores)[:3000])
    items = allstores.get("stores", allstores) if isinstance(allstores, dict) else allstores
    stores = [s["id"] for s in items if isinstance(s, dict) and "content id" not in str(s.get("name", "")).lower()] or None
    print("rules:", json.dumps(call("/metadata-rules"))[:4000])
    for key in (CFG["releases"] if which == "all" else [which]):
        body = payload(CFG["releases"][key], stores)
        quote = call("/releases/quote", {"tracks": body["tracks"]})
        print(f"QUOTE {key}:", json.dumps(quote))
        if step == "submit" and not (quote.get("balance") or {}).get("covered"):
            sys.exit(f"not enough credits for {key}: buy them in ONCE first")
        if step == "submit":
            print(f"SUBMITTED {key}:", json.dumps(call("/releases", body))[:1000])
