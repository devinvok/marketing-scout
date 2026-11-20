# Architecture

```
 ┌─────────────────────┐        reads config          ┌──────────────────────┐
 │ scheduled routine     │ ───────────────────────────▶ │ configs/<slug>.json  │
 │ (weekly, per project)│                               │  (this repo)         │
 └──────────┬───────────┘                               └──────────────────────┘
            │ Scout + Analyst + Fixer + Publisher + Outreach
            │  - reads the project's own facts_files only
            │  - commits safe fixes to the PROJECT's own repo
            │  - forks a third-party awesome-list, prepares (never opens) a PR
            ▼
 ┌──────────────────────┐
 │ opens a GitHub Issue  │   one per proposed public action, label project:<slug>
 │ in THIS repo          │   draft text in fenced ```channel / ```text blocks
 └──────────┬───────────┘
            │ human reviews on GitHub / GitHub mobile app
            │ adds label "approved", or closes to reject
            ▼
 ┌──────────────────────────────┐
 │ .github/workflows/            │  the ONLY thing that ever calls a platform's API
 │   post-on-approval.yml        │  secrets live here only, never in a client,
 └──────────┬────────────────────┘  a log, or a page
            │
            ▼
   X API / Reddit API (official, OAuth, same mechanism Buffer/Hootsuite use)
            │
            ▼
   comments the published URL back on the issue, closes it
```

## Why issues-and-actions instead of a custom web app

A bespoke dashboard was the first design considered. It fails for a structural
reason, not a cosmetic one: a page a person opens in a browser cannot safely hold
API secrets (anything in client-side code is readable via dev tools by anyone with
the link), and a sandboxed page also can't freely call arbitrary external APIs to
sync state on its own. GitHub Issues already is a reviewable, mobile-friendly,
notification-driven inbox, and GitHub Actions already is a secure, secret-holding,
server-side executor triggered by repo events. Using them directly removes an
entire category of security design this project would otherwise have to solve
itself, and it's also what makes a project "join" this system by just adding a
config file and some repo secrets, instead of deploying anything.

## Why the Scout's AI-visibility check is approximate for the Claude engine

Asking "would Claude recommend this project" from inside an agent that already
knows the project's repo is not a blind test — the model already has the context
in its window. The honest caveat, stated in every run's report: the Claude-engine
score is a self-evaluated approximation, not a clean signal. A genuinely blind
check needs a fresh API call with no prior context, which is exactly what the
`openai`/`gemini`/`perplexity` engines give you (a separate API key means a
separate, context-free call) — adding one of those is the way to get a real
signal, not just another data point.
