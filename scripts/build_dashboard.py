#!/usr/bin/env python3
"""Build a static dashboard (docs/site/index.html) from this repo's own GitHub
Issues. Runs inside the GitHub Action (post-on-approval.yml's sibling workflow,
build-dashboard.yml), server-side, so it can call the GitHub API freely -- a
browser page can't, which is the whole reason this isn't a client-side app.

Generic across every "project:<slug>" label, not just MapNet: add a project by
adding a config file, and its issues show up here automatically, grouped under
its own heading.

Usage: GH_TOKEN=... python3 scripts/build_dashboard.py
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

REPO = "devinvok/marketing-scout"


def gh_json(args: list[str]):
    out = subprocess.run(["gh"] + args, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def fetch_issues():
    return gh_json([
        "issue", "list", "--repo", REPO, "--state", "all", "--limit", "200",
        "--json", "number,title,body,labels,state,createdAt,closedAt,comments,url",
    ])


def status_of(issue: dict) -> tuple[str, str]:
    """(status_key, human label) for one issue."""
    label_names = {l["name"] for l in issue["labels"]}
    if issue["state"] == "OPEN":
        if "approved" in label_names:
            return "approved", "Approved — posting"
        return "pending", "Awaiting review"
    # closed
    comments = issue.get("comments") or []
    last_bodies = " ".join(c.get("body", "") for c in comments)
    if "Posted:" in last_bodies:
        return "posted", "Posted"
    if "Posting failed" in last_bodies:
        return "failed", "Posting failed"
    return "rejected", "Rejected (closed)"


def project_of(issue: dict) -> str:
    for l in issue["labels"]:
        if l["name"].startswith("project:"):
            return l["name"][len("project:"):]
    return "(unlabeled)"


def excerpt(body: str, n: int = 320) -> str:
    # Skip the parser-facing fenced blocks; show the first real prose paragraph.
    lines = []
    skipping = False
    for line in (body or "").splitlines():
        if line.strip().startswith("```"):
            skipping = not skipping
            continue
        if skipping:
            continue
        if line.strip().startswith("#") or line.strip().startswith("**No channel"):
            continue
        if line.strip():
            lines.append(line.strip())
        if sum(len(x) for x in lines) > n:
            break
    text = " ".join(lines)
    return (text[:n] + "…") if len(text) > n else text


STATUS_ORDER = ["pending", "approved", "failed", "posted", "rejected"]
STATUS_COLOR = {
    "pending": "#d97706", "approved": "#2563eb", "posted": "#16a34a",
    "failed": "#dc2626", "rejected": "#6b7280",
}


def render(issues: list[dict]) -> str:
    by_project: dict[str, list[dict]] = defaultdict(list)
    for iss in issues:
        by_project[project_of(iss)].append(iss)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>marketing-scout dashboard</title>
<style>
  :root {{ --bg:#0e1116; --card:#161b22; --fg:#e6edf3; --muted:#8b949e; --accent:#2dd4bf; }}
  @media (prefers-color-scheme: light) {{
    :root:not([data-theme="dark"]) {{ --bg:#f6f8fa; --card:#fff; --fg:#1f2328; --muted:#57606a; --accent:#0969da; }}
  }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font-family:-apple-system,Segoe UI,Inter,sans-serif;
          padding:32px 16px 64px; }}
  .wrap {{ max-width:880px; margin:0 auto; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .sub {{ color:var(--muted); font-size:14px; margin-bottom:28px; }}
  h2 {{ font-size:16px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted);
        margin:32px 0 12px; border-bottom:1px solid rgba(128,128,128,.25); padding-bottom:6px; }}
  .card {{ background:var(--card); border:1px solid rgba(128,128,128,.2); border-radius:10px;
           padding:16px 18px; margin-bottom:12px; }}
  .row {{ display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }}
  .title {{ font-weight:600; font-size:15px; }}
  .title a {{ color:inherit; text-decoration:none; }}
  .title a:hover {{ text-decoration:underline; }}
  .badge {{ font-size:11px; font-weight:700; padding:2px 9px; border-radius:999px; color:#fff;
            white-space:nowrap; }}
  .excerpt {{ color:var(--muted); font-size:13px; margin-top:8px; line-height:1.5; }}
  footer {{ color:var(--muted); font-size:12px; margin-top:40px; text-align:center; }}
  a.plain {{ color:var(--accent); }}
</style></head><body><div class="wrap">
<h1>marketing-scout</h1>
<div class="sub">Live from <a class="plain" href="https://github.com/{REPO}">{REPO}</a> — rebuilt on every issue change. Last build: {now}</div>
"""]

    for project, items in sorted(by_project.items()):
        parts.append(f"<h2>{html.escape(project)}</h2>")
        items.sort(key=lambda i: i["number"], reverse=True)
        for iss in items:
            status_key, status_label = status_of(iss)
            color = STATUS_COLOR[status_key]
            parts.append(f"""<div class="card">
  <div class="row">
    <div class="title"><a href="{iss['url']}" target="_blank" rel="noopener">#{iss['number']} {html.escape(iss['title'])}</a></div>
    <span class="badge" style="background:{color}">{html.escape(status_label)}</span>
  </div>
  <div class="excerpt">{html.escape(excerpt(iss.get('body', '')))}</div>
</div>""")
        if not items:
            parts.append('<div class="sub">Nothing yet.</div>')

    if not by_project:
        parts.append('<div class="sub">No issues yet — the weekly routine opens its first one Monday.</div>')

    parts.append(f"""
<footer>Approving happens on GitHub itself (the <code>approved</code> label) — this page is read-only,
built by <a class="plain" href="https://github.com/{REPO}/blob/main/.github/workflows/build-dashboard.yml">build-dashboard.yml</a>.</footer>
</div></body></html>""")
    return "\n".join(parts)


def main() -> int:
    try:
        issues = fetch_issues()
    except subprocess.CalledProcessError as e:
        print(f"Could not fetch issues: {e.stderr}", file=sys.stderr)
        return 1
    out_dir = "docs/site"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render(issues))
    print(f"Wrote {out_dir}/index.html from {len(issues)} issues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
