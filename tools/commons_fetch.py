"""Download freely licensed files from Wikimedia Commons (the session sandbox can't reach Commons; Actions can).

python tools/commons_fetch.py OUT_DIR "Category:A" "Category:B" "File:x.webm" ...
Keeps only CC BY / CC0 / public-domain files (no share-alike, no non-free), images as 1920 px thumbs,
videos as originals, and writes OUT_DIR/credits.json with author, licence and source page for each.
"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "HopeverseMediaBot/1.0 (https://github.com/xjitheshmenon-ship-it/thehopeverse.media)"}


def get(url):
    for i in range(8):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except urllib.error.HTTPError as e:  # Commons throttles bots with 429: wait as asked, then go on
            if i == 7 or e.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 15 * (i + 1))
        except OSError:
            if i == 7:
                raise
            time.sleep(5 * (i + 1))


def api(**p):
    p.update(format="json", formatversion=2)
    return json.loads(get(API + "?" + urllib.parse.urlencode(p)))


def free(lic):
    lic = lic.lower().strip()
    if re.search(r"\b(sa|nc|nd)\b", lic.replace("-", " ")):
        return False
    return lic.startswith(("cc by", "cc0", "public domain")) or lic == "pd"


def titles(source):
    if source.startswith("File:"):
        return [source]
    out, cont = [], {}
    while True:
        r = api(action="query", list="categorymembers", cmtitle=source, cmtype="file", cmlimit=500, **cont)
        out += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" not in r:
            return out
        cont = {"cmcontinue": r["continue"]["cmcontinue"]}


def main(out, sources):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    credits, seen = [], set()
    for src in sources:
        for t in titles(src):
            if t in seen:
                continue
            seen.add(t)
            info = api(action="query", titles=t, prop="imageinfo", iiprop="url|extmetadata|mime|size",
                       iiurlwidth=1920)["query"]["pages"][0]["imageinfo"][0]
            meta = {k: v.get("value", "") for k, v in info["extmetadata"].items()}
            lic = re.sub("<[^>]+>", "", meta.get("LicenseShortName", "")).strip()
            if not free(lic):
                print("skip (licence)", lic, t)
                continue
            video = info["mime"].startswith(("video", "application/ogg"))
            url = info["url"] if video else info.get("thumburl", info["url"])
            name = re.sub(r"[^A-Za-z0-9._-]+", "_", t[5:])
            if not video:
                name = Path(name).stem + Path(urllib.parse.urlparse(url).path).suffix
            try:
                (out / name).write_bytes(get(url))
            except Exception as e:  # one stubborn file must not lose the rest
                print("skip (download)", e, t)
                continue
            credits.append({"file": name, "title": t, "page": info["descriptionurl"], "licence": lic,
                            "licence_url": meta.get("LicenseUrl", ""),
                            "author": re.sub("<[^>]+>", "", meta.get("Artist", "")).strip(),
                            "description": re.sub("<[^>]+>", "", meta.get("ImageDescription", "")).strip()[:300]})
            print("ok", lic, name)
            time.sleep(1.5)
    (out / "credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1))
    print(len(credits), "files")


if __name__ == "__main__":
    assert free("CC BY 4.0") and free("CC BY 3.0") and free("CC0") and free("Public domain")
    assert not free("CC BY-SA 4.0") and not free("CC BY-NC 2.0") and not free("")
    main(sys.argv[1], sys.argv[2:])
