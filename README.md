# marketing-scout

A config-driven agent crew that scouts how AI engines talk about an open-source
project, drafts growth actions, and only ever publishes after a human approves —
one GitHub label click, from GitHub's own app.

Built first for [MapNet](https://github.com/devinvok/MapNet); designed from the
start to run for any project that drops in a config file.

## The loop

**Scout → Analyst → Fixer → Publisher → Outreach → Reporter**, once a week, per
configured project:

- **Scout** asks AI engines the questions a real user would ask, and checks whether
  and how the project comes up against named competitors.
- **Analyst** compares the project's own facts against what the engines actually
  recommend, and finds the concrete gap.
- **Fixer** can commit small, honest fixes directly to the project's own repo
  (README wording, GitHub Topics, a social preview image) — never to anyone else's.
- **Publisher** drafts one new piece of content a week, always from a new angle,
  always sourced only from the project's own facts files.
- **Outreach** finds newsletters, directories, and awesome-lists the project isn't
  on yet, and can prepare (never open) a pull request to a third-party list.
- **Reporter** opens one GitHub Issue per proposed public action and logs the run.

## The one hard rule

No agent in this system ever posts, comments, votes, signs up, or sends anything on
an external platform under the project owner's identity, or fakes engagement in any
form. It never invents a number. The only things it does on its own are: commit to
the project's own repo, prepare (not open) a third-party PR branch, and open an
Issue *in this repo* describing a proposed action. **Publishing only happens after
a human adds the `approved` label to that issue** — see
[`.github/workflows/post-on-approval.yml`](.github/workflows/post-on-approval.yml).
This is not a soft preference; it's enforced by what the automation is actually
capable of doing, not just told not to do.

## How approval works

1. The weekly routine opens an Issue like "Post to X: what we tried that didn't
   work", with the draft text in a fenced block.
2. You read it — on GitHub, in the GitHub mobile app, wherever — and either close
   it (reject) or add the `approved` label.
3. That label is the *only* trigger that runs
   [`post-on-approval.yml`](.github/workflows/post-on-approval.yml), which posts
   through the platform's own official API using secrets stored in this repo's
   settings, never in any file, log, or client-side code.
4. The workflow comments the published URL back on the issue and closes it.

Hacker News has no posting API at all, by design on their end — those drafts stay
issues you submit yourself; the system never pretends otherwise.

## Onboarding a new project

See [`docs/ONBOARDING.md`](docs/ONBOARDING.md). In short: add `configs/<slug>.json`
(schema in [`configs/SCHEMA.md`](configs/SCHEMA.md)), add the repo secrets for
whichever channels you want enabled, point a scheduled routine at this repo. No
other code changes.

## License

MIT — see [LICENSE](LICENSE).
