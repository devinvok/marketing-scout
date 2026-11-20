# Onboarding a new project

## 1. Add a config file

Copy `configs/mapnet.json` to `configs/<your-slug>.json` and edit every field —
see [`configs/SCHEMA.md`](../configs/SCHEMA.md) for what each one means. Leave
every channel `"enabled": false` until step 2 is done for that channel.

## 2. Turn on a channel (optional, per project)

### X
1. developer.x.com → create a Developer App (the free tier covers this: write-only,
   up to 1,500 posts/month).
2. In the app's "Keys and tokens" tab, set permissions to **Read and Write** *before*
   generating the access token, or it will be read-only.
3. Add these as **repo secrets** (Settings → Secrets and variables → Actions) on
   *this* repo: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`.
4. Add `X_HANDLE` as a repo **variable** (not secret) — just your @handle, used to
   build the result URL.
5. Flip `channels.x.enabled` to `true` in your config.

### Reddit
1. reddit.com/prefs/apps → create app, type **script**.
2. Follow Reddit's OAuth "installed app" flow once, by hand, to get a refresh
   token with `submit` scope — this is a one-time step; the refresh token doesn't
   expire from use. (Reddit's own developer docs walk through this; look for
   "OAuth2 quick start" in their API wiki.)
3. Add repo secrets: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_REFRESH_TOKEN`.
4. Add a `REDDIT_USER_AGENT` repo variable — Reddit requires a descriptive one,
   e.g. `marketing-scout/0.1 by u/yourusername`.
5. Flip `channels.reddit.enabled` to `true`.

### Hacker News
Not available. HN has no public submission API — only a read-only one. Drafts for
HN always stay issues the owner submits by hand; this is a permanent limitation on
HN's end, not something a future version of this project can change.

### More AI engines for the Scout (optional)
`engines: ["claude"]` needs nothing extra. To add others:
- OpenAI: `OPENAI_API_KEY` repo secret, add `"openai"` to the config's `engines`.
- Gemini: `GEMINI_API_KEY`, add `"gemini"`.
- Perplexity: `PERPLEXITY_API_KEY` (no free tier), add `"perplexity"`.

The weekly routine skips any engine whose secret is missing and says so in its
report, rather than silently running with fewer engines than you asked for.

## 3. Point a scheduled routine at this repo

The routine prompt (kept in the scheduler, not in this repo, since it's the same
prompt for every project — only the config differs) needs: the project's repo
cloned as its working directory, and `devinvok/marketing-scout`'s `configs/<slug>.json`
fetched at the start of each run via `gh api repos/devinvok/marketing-scout/contents/configs/<slug>.json`.
See the MapNet routine for a working example of this prompt shape.

## 4. Watch the first run

Check this repo's Issues, filtered to `project:<slug>` label, after the first
scheduled run. Approve or close each one. That's the whole ongoing workflow.
