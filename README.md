# Hopeverse Media agents

Mr. Hope, the primary decision maker, makes YouTube Shorts for Hopeverse Media and directs his mini agents: Mr. Focus (the researcher, who finds the 5 best topics of the day, researches them and fact-checks scripts), Mr. Cast (character designer, keeps a recurring cast in `characters.md`), Mr. Pen (script writer), Mr. Cut (video editor), Mr. Spark (thumbnail and title), and Mr. Post (channel manager).

## Change what the agents do

Every agent's instructions are in `team.md`. Edit it on GitHub (open the file, click the pencil, then **Commit changes**). The daily run fetches the latest version before it starts, so nothing needs downloading.

## Run

1. `pip install -r requirements.txt`
2. Set your key: `$env:ANTHROPIC_API_KEY="..."` (PowerShell) or `export ANTHROPIC_API_KEY=...` (Mac/Linux)
3. `python agents.py "what Hope should do"`, or double-click `start_hope.bat` on Windows

To run Hope automatically once a day (9:00) on Windows, double-click `schedule_hope.bat` once. It saves your key and creates a Task Scheduler task; scheduled runs log to `runs/auto.log`. Stop it with `schtasks /Delete /TN "Hope - Hopeverse Media" /F`.

Every run saves all helpers' outputs to `runs/`. Finished packages go to `outbox/` for you to review and upload by hand.

## Channels

`channels.json` lists the channels. Hope proposes new ones as `needs_setup`; create them by hand (YouTube and Instagram don't allow automated channel creation), then set `status` to `live` and fill in `url`.

## Videos and YouTube upload

`python video.py` turns every outbox package without a video into an `.mp4` next to it (free Edge AI voice, captions, real stock footage from Pixabay when `PIXABAY_API_KEY` is set, else photo-real fal.ai images when `FAL_KEY` is set), then uploads YouTube packages as **private** videos. The daily run does this automatically after the agents finish.

One-time YouTube setup:

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable **YouTube Data API v3**.
2. Under **Google Auth Platform**, set up the consent screen (External), add yourself as a test user, then set publishing status to **In production** so the sign-in doesn't expire every 7 days.
3. Create an **OAuth client ID** of type **Desktop app**, download its JSON, and save it next to `agents.py` as `client_secret.json`.
4. Run `python video.py` once by hand and sign in with the Google account that owns the channel. After that it's automatic.

Videos uploaded by an unaudited Google Cloud project stay private. To be able to publish them, submit YouTube's API audit form for the project.

## How Mr. Hope learns

After every run, Mr. Hope reviews the day: cost, what was made, and (once YouTube is connected) each Short's views, likes and comments. He rewrites `lessons.md` with his strategy, business goals and a section of lessons for each agent; every agent automatically follows its own section on the next run. Delete `lessons.md` to make him start fresh. Each run's cost is logged in `runs/history.jsonl`.

## Instagram Reels

Once you make a video **public** on YouTube, the next `python video.py` also posts it to Instagram as a Reel (Instagram has no private drafts, so YouTube is the review step). It needs `INSTAGRAM_TOKEN`: a Facebook Login token with `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement` and `business_management`, for a Facebook Page linked to the Instagram professional account. Make one in the Graph API Explorer and extend it to 60 days in the Access Token Debugger.
