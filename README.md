# Hopeverse Media agents

Mr. Hope, the primary decision maker, makes YouTube Shorts for Hopeverse Media and directs his mini agents: Mr. Focus (the researcher, who finds the 5 best topics of the day, researches them and fact-checks scripts), Mr. Cast (character designer, keeps a recurring cast in `characters.md`), Mr. Pen (script writer), Mr. Cut (video editor), Mr. Spark (thumbnail and title), and Mr. Post (channel manager).

## Change what the agents do

Every agent's instructions are in `team.md`. Edit it on GitHub (open the file, click the pencil, then **Commit changes**). The daily run fetches the latest version before it starts, so nothing needs downloading.

## Run

1. `pip install -r requirements.txt`
2. Set your key: `$env:ANTHROPIC_API_KEY="..."` (PowerShell) or `export ANTHROPIC_API_KEY=...` (Mac/Linux)
3. `python agents.py "what Hope should do"`, or double-click `start_hope.bat` on Windows

Optional: with `PERPLEXITY_API_KEY` set (`setx PERPLEXITY_API_KEY pplx-...`), Mr. Focus searches with Perplexity Sonar first (about $0.006 a search, counted in the `HOPE_BUDGET` cap) and falls back to Claude's web search if it fails. Without the key nothing changes.

To run Hope automatically on Windows, double-click `schedule_hope.bat` once. It saves your key and creates two Task Scheduler tasks: at 16:00 Hope researches, writes and makes the Short (`hope_auto.bat`, which runs `video.py --no-upload`), and at 18:00 it is posted to YouTube and Instagram (`hope_auto.bat post`). Runs log to `runs/auto.log`. After every run `runs/spend-report.md` is updated (today, last 7 days, this month), and the 18:00 task opens it in Notepad. With `TELEGRAM_TOKEN` set (see the top of `approve.py`), the 4 PM run sends each new Short to Telegram with Approve and Skip buttons, the 6 PM run posts only approved Shorts (or everything except skipped ones with `HOPE_APPROVAL=auto`), then sends the spending report there instead of opening Notepad. Every hour `hope_auto.bat stats` runs `dashboard.py`, which collects YouTube and Instagram views, spend and agent work into `runs/dashboard.json` and pushes it to the `dashboard-data` branch for the Hopeverse HQ dashboard. Stop them with `schtasks /Delete /TN "Hope - research" /F` and `schtasks /Delete /TN "Hope - post" /F`.

Every run saves all helpers' outputs to `runs/`. Finished packages go to `outbox/` for you to review and upload by hand.

## Run in the cloud (no PC)

`.github/workflows/hope.yml` runs Hope on GitHub's servers: every day at 17:15 IST it researches, makes and posts the Short (`agents.py`, then `video.py`), and every hour it updates the dashboard. Keys go in the repo's **Settings > Secrets and variables > Actions**: `ANTHROPIC_API_KEY`, `PIXABAY_API_KEY`, `FAL_KEY`, `INSTAGRAM_TOKEN`, optional `PERPLEXITY_API_KEY`, and the YouTube files pasted as text: `YOUTUBE_CLIENT_SECRET` (client_secret.json), `YOUTUBE_TOKEN` (token.json), optional `YOUTUBE_TOKEN_HI` (token-hi.json). Hope's memory (outbox packages, `lessons.md`, `characters.md`, run logs) is kept on the `state` branch by `state.py`; videos and tokens are never saved there. To move from the PC, run `python state.py save` there once, then delete the Task Scheduler tasks so the Short isn't posted twice. Start a run by hand from the **Actions** tab > Hope > Run workflow.

## 100-day plan: 6 Shorts per channel, a new channel idea every day

The daily cloud run makes `SHORTS_PER_DAY` Shorts (default 6) for every channel in `channels.json` with platform `youtube` and status `live`, and the same number of series episodes when the series channel is connected. Mr. Hope reviews and rewrites `lessons.md` once, after the day's last Short. All runs stop once the day's spend reaches `DAILY_BUDGET` (default $20). Change both under **Settings > Secrets and variables > Actions > Variables**, no code edit needed.

YouTube's API allows about 6 uploads a day per Google Cloud project (10,000 quota units, 1,600 per upload), shared by every channel that uses the same `client_secret.json`. Uploads over the limit wait for the next run. Before connecting more channels, ask Google for more quota: Google Cloud Console > APIs & Services > YouTube Data API v3 > Quotas > the YouTube quota extension form (free; it takes a few days to weeks).

Every day `scout.py` also proposes one new channel for an audience the network doesn't reach yet, with a finished brand kit in the Signal style: name, handle, tagline, About text, keywords, first video ideas, profile picture, banner and watermark. They are saved in `ideas/<date>-<id>/` on the `state` branch, and the idea appears at the end of `runs/spend-report.md`. `python scout.py --demo` renders a sample kit locally.

## Channels

`channels.json` lists the channels. Hope proposes new ones as `needs_setup`; create them by hand (YouTube and Instagram don't allow automated channel creation), then set `status` to `live` and fill in `url`.

## Videos and YouTube upload

`python video.py` turns every outbox package without a video into an `.mp4` next to it (free Edge AI voice, captions, real stock footage from Pixabay when `PIXABAY_API_KEY` is set, else photo-real fal.ai images when `FAL_KEY` is set), then uploads YouTube packages as **public** videos. The daily run does this automatically after the agents finish.

One-time YouTube setup:

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable **YouTube Data API v3**.
2. Under **Google Auth Platform**, set up the consent screen (External), add yourself as a test user, then set publishing status to **In production** so the sign-in doesn't expire every 7 days.
3. Create an **OAuth client ID** of type **Desktop app**, download its JSON, and save it next to `agents.py` as `client_secret.json`.
4. Run `python video.py` once by hand and sign in with the Google account that owns the channel. After that it's automatic.

Videos uploaded by an unaudited Google Cloud project stay private. To be able to publish them, submit YouTube's API audit form for the project.

## Hindi dub channel

Every new Short is also remade in Hindi for the **Hopeverse Hindi** channel (`yt-hopeverse-hi` in `channels.json`): Claude adapts the script into natural spoken Hindi, the `hi-IN-MadhurNeural` voice reads it, and the captions use Windows' Nirmala UI font. It reuses the English video's footage, so each dub costs one small Claude call. Dubs go only to their own YouTube channel, never to Instagram or Facebook.

Setup, once: create the channel in YouTube (same Google account, **Create a channel** under Switch account), then run `python video.py --connect hi` and pick that channel when you sign in. Nothing is dubbed until `token-hi.json` exists. For Spanish later, copy the Hindi entry in `channels.json` with `lang` `es`, `language` `Spanish`, voice `es-MX-JorgeNeural` and token `token-es.json`.

## Hindi micro web series channel

`series.py` writes one episode a day of an original Hindi micro web series for **Kissa (किस्सा)** (`yt-kissa` in `channels.json`, name chosen by Hope). The stories are inspired by popular Korean drama tropes but set in India and never copy a real show, so the channel can be monetised. The story so far (premise, cast with looks and voices, a summary of every episode) is kept in `series.json` on the `state` branch, so each episode continues the last; delete it to start a new season. Instructions and the season idea are under **Mr. Pen (series)** in `team.md`. Each character gets one fixed face (a reference photo in `hosts/`, like Arjun and Meera) and a Hindi voice; episodes run 60 to 90 seconds, end on a cliffhanger and post only to this channel. About $0.70 an episode (Claude plus fal.ai images and music).

Setup, once, no PC needed: create the channel in YouTube (same Google account, **Create a channel** under Switch account). Then on GitHub open **Actions > Hope > Run workflow**, pick job `connect` and channel `yt-kissa`, and run it. Open the sign-in link from the run's log on any phone or computer, sign in and pick Kissa; the browser ends on a "can't connect to localhost" page, so copy that page's whole address. Run the workflow again with that address in `signin_url`. `connect.py` saves the sign-in encrypted (with the `YOUTUBE_CLIENT_SECRET` secret as the key) in `tokens/` on the `state` branch, and sets the channel's description, keywords, country, banner and "not made for kids" from `branding` in `channels.json`. Only the profile picture (`brand/kissa-profile.png`) must be uploaded by hand in YouTube Studio, because YouTube's API can't set it. The same `connect` job works for the Hindi dub channel and for Hopeverse Media when a sign-in expires.

## How Mr. Hope learns

After every run, Mr. Hope reviews the day: cost, what was made, and (once YouTube is connected) each Short's views, likes and comments. He rewrites `lessons.md` with his strategy, business goals and a section of lessons for each agent; every agent automatically follows its own section on the next run. Delete `lessons.md` to make him start fresh. Each run's cost is logged in `runs/history.jsonl`.

## Instagram Reels

Once you make a video **public** on YouTube, the next `python video.py` also posts it to Instagram as a Reel (Instagram has no private drafts, so YouTube is the review step). It needs `INSTAGRAM_TOKEN` (Instagram Login, no Facebook Page): a token for the Instagram professional account from a Meta app's "API setup with Instagram login" page, with `instagram_business_basic` and `instagram_business_content_publish`. It lasts 60 days. The video is handed to Instagram through a temporary public link on fal.ai storage, so `FAL_KEY` is needed too.
