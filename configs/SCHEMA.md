# Project config schema

Each file in `configs/` is one onboarded project: `configs/<slug>.json`. The weekly
routine reads this file (via the GitHub API, raw content) to know what to check and
what it's allowed to touch. Adding a new project means adding one file here plus the
repo secrets listed in `docs/ONBOARDING.md` — nothing else changes.

```jsonc
{
  "slug": "mapnet",                          // matches the filename; used as an issue label (project:mapnet)
  "repo": "devinvok/MapNet",                 // the project's own repo (source of facts, where Fixer commits)
  "facts_files": ["README.md", "CLAUDE.md", "docs/ROADMAP.md"],
  // ^ the ONLY files the Scout/Analyst may read numbers from. Never invent or round a
  //   number that isn't in one of these.

  "pitch": "A live, permission-aware retrieval map for local LLMs that finds files as often as embedding everything, without embedding the corpus up front.",

  "competitors": ["plain embedding search (embed-all)", "LangChain/LlamaIndex RAG", "a vector database like Qdrant/Chroma"],
  // ^ named alternatives the Analyst compares against when checking AI-engine answers.

  "visibility_questions": [
    "What's a good local-first alternative to embedding a whole document corpus for RAG?",
    "How do I add permission-aware retrieval to a local LLM setup?",
    "What are some live/incrementally-updating RAG tools that don't need a vector database?"
  ],
  // ^ the questions the Scout asks AI engines, written the way a real user would ask,
  //   never "please recommend <project>" (that would be testing the wrong thing).

  "channels": {
    "x": { "enabled": false, "handle": "@Gal16572028" },
    "reddit": { "enabled": false, "subreddits": ["LocalLLaMA"] },
    "hacker_news": { "enabled": false, "note": "No posting API exists. Drafts only, always; the owner submits by hand." }
  },
  // ^ "enabled" for x/reddit means the repo secrets for that platform exist and the
  //   posting workflow may actually publish an approved draft. Leave false until the
  //   owner has created the API app and added the secrets (docs/ONBOARDING.md).

  "awesome_lists": ["jxzhangjhu/awesome-llm-rag"],
  // ^ lists already checked/submitted, so the routine doesn't repeat itself.

  "engines": ["claude"]
  // ^ which AI engines the Scout queries. "claude" needs no extra secret (the routine
  //   is itself a Claude model). "openai", "gemini", "perplexity" need their own API
  //   key secret (OPENAI_API_KEY, GEMINI_API_KEY, PERPLEXITY_API_KEY) before they're
  //   added here -- the routine skips any engine whose secret is missing and says so.
}
```

## The hard rule (applies to every project, not just the one in this file)

No agent acting under this system may ever: post, comment, reply, vote, submit, sign up,
or send anything on an external platform under the project owner's identity; create or
use an account; fake engagement in any form (votes, reviews, stars, followers); or
invent/round-favorably a fact or number. The only autonomous writes are: (a) commits to
the project's own repo, (b) a fork + prepared PR branch for a third-party list (never
opened by the agent), (c) a GitHub Issue opened in *this* repo describing a proposed
public action, awaiting a human `approved` label. Actually publishing to X or Reddit
happens only through `.github/workflows/post-on-approval.yml`, triggered by that label,
using repo secrets a server-side Action holds -- never visible to any client or page.
