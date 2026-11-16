"""Which YouTube channels are still up (owner, 16 Nov 2026, after two were removed). Read-only, free (a few quota
units). Uses the Instinct sign-in to read public data: a removed channel or video simply isn't returned.
    python tools/channel_check.py   (run by check.yml)"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HANDLES = ["@HopeverseMedia", "@Instinct.natureFR", "@TheSankalpDesk", "@PoochoSawaal", "@theaetherscore"]
IDS = ["UChBAj1iJyHZCOVAMbz7Re1A"]  # Instinct Japan
VIDEOS = "kUEa8YP5eEM rQPOCx8wY6c gqqVe-Ubm48 1GMi6HZVxvI 1muEoV3OaIw 3G1ZdxpPNng 3iJYU9wAlXA 5Vqw3XPKfrk 7CVtKzS0j5o 7EnQAJ7VphA 7iUZ0O9eVpQ 8ZFsuu0XldM 96ZU280OHk0 A8NYdCOxLiU BIDMOnJSl8c CRZ5MjxLdNU EVS2-Mxz8DA HOFe0M8BN88 IeUiMtPnM5I K2nPuRFeJfw KkQeednJ8es O1eFyMh2bf4 Q6UZoTneaNY R2WckuM7jPY S6FOIE6m9KI StOh_A23DgE U2pXKi-dAM4 Wnhg4vb5fDU X7fZUVCDwMA YG_j8JRtXrI _uLPkFmKuGc b4VUeg2yTlQ c7AzOqWq4Co cEdDRufOdDk cGBmFQEIpSs cehcP966t1c e13gmAPlb-4 eQfs4mjkLPk eg6BapdWt4s hrpBLFh5SFo j5yHF-7wCNA msQN1i2NsxA nHLGxkOXUOA nScf1bbmKYc qNt8yZVSvuo rT2fSUy9hWs vbZbftf2VCg yqDe-uhQQLA ".split()  # Hopeverse's 3 Shorts, then ÆTHER uploads

yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(Path("token-instinct.json"))))
for h in HANDLES:
    items = yt.channels().list(part="snippet,statistics,status", forHandle=h).execute().get("items", [])
    print(h, "UP" if items else "NOT FOUND (removed?)", items[0]["statistics"] if items else "")
for i in IDS:
    items = yt.channels().list(part="snippet,statistics", id=i).execute().get("items", [])
    print(i, "UP" if items else "NOT FOUND (removed?)", items[0]["snippet"]["title"] if items else "")
for k in range(0, len(VIDEOS), 50):
    found = {v["id"]: v for v in yt.videos().list(part="snippet,status", id=",".join(VIDEOS[k:k + 50])).execute().get("items", [])}
    for v in VIDEOS[k:k + 50]:
        x = found.get(v)
        print(v, f"{x['snippet']['channelTitle']} | {x['status']['privacyStatus']} | {x['snippet']['title'][:60]}" if x else "GONE")
