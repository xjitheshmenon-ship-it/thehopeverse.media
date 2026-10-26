"""Sign a YouTube channel in from GitHub, no PC needed: Actions > Connect a channel > Run workflow.

    Run 1 (signin_url empty): prints a Google sign-in link in the run's log. Open it on any phone or computer,
        sign in and pick the channel. The browser then shows a "can't connect to localhost" page: copy its whole
        address from the address bar.
    Run 2 (that address pasted as signin_url): saves the channel's sign-in, encrypted, on the state branch, then
        sets the channel's description, keywords, country and banner from its "branding" in channels.json.

    python connect.py <channel id> [signin_url]
    python connect.py <channel id> brand   -> set the description, keywords and banner again with the saved sign-in
"""
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

HERE = Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtube"]  # full access only to set up the channel's description and banner
TOKENS = HERE / "tokens"  # encrypted sign-ins, kept on the state branch; hope.yml unlocks them with TOKEN_KEY


def main(channel_id: str, signin_url: str = "") -> None:
    channel = next(c for c in json.loads((HERE / "channels.json").read_text(encoding="utf-8")) if c["id"] == channel_id)
    # The two runs are separate machines, so no PKCE verifier can be carried over; Google allows that for desktop apps.
    flow = Flow.from_client_secrets_file(str(HERE / "client_secret.json"), SCOPES, redirect_uri="http://localhost",
                                         autogenerate_code_verifier=False)
    if signin_url == "brand":  # the channel is signed in already: just refresh its About page and banner
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(HERE / channel.get("token", "token.json")))
        yt = build("youtube", "v3", credentials=creds)
        brand(yt, yt.channels().list(part="id", mine=True).execute()["items"][0]["id"], channel)
        return
    if not signin_url:
        url, _ = flow.authorization_url(access_type="offline", prompt="consent")
        print(f"\nOpen this link, sign in and pick the {channel['name']} channel:\n\n{url}\n\n"
              "Then copy the whole address of the page it lands on and run the workflow again with it as signin_url.")
        return
    code = urllib.parse.parse_qs(urllib.parse.urlparse(signin_url.strip()).query).get("code", [signin_url.strip()])[0]
    flow.fetch_token(code=code)
    creds = flow.credentials
    yt = build("youtube", "v3", credentials=creds)
    me = yt.channels().list(part="id,snippet", mine=True).execute()["items"][0]
    print(f"Signed in as the channel: {me['snippet']['title']} ({me['id']})")

    token = HERE / channel.get("token", "token.json")
    token.write_text(creds.to_json())
    TOKENS.mkdir(exist_ok=True)
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", "env:TOKEN_KEY",
                    "-in", str(token), "-out", str(TOKENS / f"{token.name}.enc")], check=True)
    print(f"Saved the sign-in for {channel['name']}; daily runs will now post there.")

    brand(yt, me["id"], channel)


def brand(yt, channel_yt_id: str, channel: dict) -> None:
    """The channel's description, keywords, country, banner and 'not made for kids', from channels.json.
    YouTube's API can't set the profile picture: upload brand/<name>-profile.png in Studio > Customisation."""
    branding = channel.get("branding")
    if not branding:
        return
    me = {"id": channel_yt_id}
    settings = {"channel": {"description": branding["description"], "keywords": branding["keywords"],
                            "country": branding.get("country", "IN"), "defaultLanguage": channel.get("lang", "en")}}
    if branding.get("banner"):
        banner = yt.channelBanners().insert(media_body=MediaFileUpload(str(HERE / branding["banner"]))).execute()
        settings["image"] = {"bannerExternalUrl": banner["url"]}
    yt.channels().update(part="brandingSettings", body={"id": me["id"], "brandingSettings": settings}).execute()
    yt.channels().update(part="status", body={"id": me["id"], "status": {"selfDeclaredMadeForKids": False}}).execute()
    print("Set the description, keywords, country, banner and 'not made for kids'.")


if __name__ == "__main__":
    main(*sys.argv[1:3])
