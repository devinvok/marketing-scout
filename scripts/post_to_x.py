#!/usr/bin/env python3
"""Post one tweet via X API v2, user-context OAuth 1.0a.

Reads text from argv[1] (or stdin if no argv). Needs four secrets as environment
variables, from an X Developer App with OAuth 1.0a user-context write access
(developer.x.com -> your app -> Keys and tokens -> regenerate "Access Token and
Secret" with Read and Write permissions set first):

  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET

Prints the posted tweet's URL on success, on its own line, and nothing else to
stdout (so a workflow can capture it directly). Any problem exits non-zero with a
plain-English message on stderr; never retries silently and never falls back to a
different auth method.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid

API_URL = "https://api.twitter.com/2/tweets"


def oauth1_header(method: str, url: str, api_key: str, api_secret: str, token: str, token_secret: str) -> str:
    params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }
    base = "&".join(
        urllib.parse.quote(x, safe="")
        for x in (method.upper(), url, "&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in sorted(params.items())))
    )
    signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    signature = hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    import base64
    params["oauth_signature"] = base64.b64encode(signature).decode()
    return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(params.items()))


def main() -> int:
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    text = text.strip()
    if not text:
        print("No text given to post.", file=sys.stderr)
        return 1
    missing = [k for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET") if not os.environ.get(k)]
    if missing:
        print(f"Missing secrets: {', '.join(missing)}. Nothing posted.", file=sys.stderr)
        return 1
    header = oauth1_header(
        "POST", API_URL,
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"],
    )
    body = json.dumps({"text": text}).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST",
                                  headers={"Authorization": header, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"X API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return 1
    tweet_id = data.get("data", {}).get("id")
    if not tweet_id:
        print(f"Unexpected response, no tweet id: {data}", file=sys.stderr)
        return 1
    handle = os.environ.get("X_HANDLE", "i").lstrip("@")
    print(f"https://x.com/{handle}/status/{tweet_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
