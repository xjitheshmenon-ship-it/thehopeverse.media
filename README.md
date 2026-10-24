# Hopeverse Media agents

Hope, the primary decision maker, runs Hopeverse Media's YouTube and Instagram channels and directs four helpers: a trend scout, a researcher, a creative, and a channel manager.

## Run

1. `pip install -r requirements.txt`
2. Set your key: `$env:ANTHROPIC_API_KEY="..."` (PowerShell) or `export ANTHROPIC_API_KEY=...` (Mac/Linux)
3. `python agents.py "what Hope should do"`, or double-click `start_hope.bat` on Windows

Every run saves all helpers' outputs to `runs/`. Finished packages go to `outbox/` for you to review and upload by hand.

## Channels

`channels.json` lists the channels. Hope proposes new ones as `needs_setup`; create them by hand (YouTube and Instagram don't allow automated channel creation), then set `status` to `live` and fill in `url`.
