#!/usr/bin/env python3
"""Submit one self-text post to a subreddit via Reddit's OAuth API.

argv[1] = subreddit (no r/ prefix), argv[2] = title, argv[3] = body (or body on
stdin if argv[3] is omitted). Needs a Reddit "script" app (reddit.com/prefs/apps,
type: script) and a one-time authorization to get a refresh token -- see
docs/ONBOARDING.md for the exact steps. Secrets:

  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REFRESH_TOKEN, REDDIT_USER_AGENT

Prints the posted thread's URL on success. Exits non-zero with a plain message on
any failure; does not retry.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
SUBMIT_URL = "https://oauth.reddit.com/api/submit"


def get_access_token(client_id: str, client_secret: str, refresh_token: str, user_agent: str) -> str:
    body = urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh_token}).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST", headers={"User-Agent": user_agent})
    auth = f"{client_id}:{client_secret}".encode()
    import base64
    req.add_header("Authorization", "Basic " + base64.b64encode(auth).decode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: post_to_reddit.py <subreddit> <title> [body]", file=sys.stderr)
        return 1
    subreddit, title = sys.argv[1], sys.argv[2]
    body = sys.argv[3] if len(sys.argv) > 3 else sys.stdin.read()
    missing = [k for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_REFRESH_TOKEN", "REDDIT_USER_AGENT") if not os.environ.get(k)]
    if missing:
        print(f"Missing secrets: {', '.join(missing)}. Nothing posted.", file=sys.stderr)
        return 1
    try:
        token = get_access_token(os.environ["REDDIT_CLIENT_ID"], os.environ["REDDIT_CLIENT_SECRET"],
                                  os.environ["REDDIT_REFRESH_TOKEN"], os.environ["REDDIT_USER_AGENT"])
    except Exception as e:
        print(f"Reddit auth failed: {e}", file=sys.stderr)
        return 1
    form = urllib.parse.urlencode({
        "sr": subreddit, "kind": "self", "title": title, "text": body, "api_type": "json",
    }).encode()
    req = urllib.request.Request(SUBMIT_URL, data=form, method="POST", headers={
        "Authorization": f"bearer {token}",
        "User-Agent": os.environ["REDDIT_USER_AGENT"],
        "Content-Type": "application/x-www-form-urlencoded",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"Reddit API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return 1
    errors = data.get("json", {}).get("errors", [])
    if errors:
        print(f"Reddit rejected the post: {errors}", file=sys.stderr)
        return 1
    url = data.get("json", {}).get("data", {}).get("url")
    if not url:
        print(f"Unexpected response, no url: {data}", file=sys.stderr)
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
