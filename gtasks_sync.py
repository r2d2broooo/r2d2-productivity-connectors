"""Sync dashboard notes -> Google Tasks (official API, no third-party deps).

Personal Gmail has no official Google Keep API, so the closest faithful target
is Google Tasks: a task carries a title + a notes body, which maps 1:1 onto a
dashboard note, and it's a fully official OAuth surface (no account-lock risk
like the unofficial Keep route).

Auth is the OAuth 2.0 "installed app" flow. Run scripts/google_auth.py once on a
machine with a browser to mint a refresh token, then put these in .env:
    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_REFRESH_TOKEN=...

Everything here is stdlib (urllib/json) on purpose — self-hosted, minimal-dep.
"""
import json
import os
import time
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://tasks.googleapis.com/tasks/v1"
SCOPE = "https://www.googleapis.com/auth/tasks"
LIST_TITLE = "Dashboard Notes"
NOTES_MAX = 8000  # Google Tasks 'notes' field cap is ~8KB

_token_cache = {"access": None, "exp": 0.0}


class GTasksError(RuntimeError):
    pass


def configured() -> bool:
    return all(os.environ.get(k) for k in
               ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"))


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def _access_token() -> str:
    if _token_cache["access"] and time.time() < _token_cache["exp"] - 60:
        return _token_cache["access"]
    if not configured():
        raise GTasksError("Google not configured — set GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN in .env")
    try:
        tok = _post_form(TOKEN_URL, {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        })
    except urllib.error.HTTPError as e:
        raise GTasksError(f"token refresh failed ({e.code}) — re-run google_auth.py: {e.read()[:200]!r}")
    _token_cache["access"] = tok["access_token"]
    _token_cache["exp"] = time.time() + int(tok.get("expires_in", 3600))
    return _token_cache["access"]


def _api(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}


def _ensure_list() -> str:
    """Return the id of the 'Dashboard Notes' task list, creating it if missing."""
    res = _api("GET", "/users/@me/lists", params={"maxResults": 100})
    for item in res.get("items", []):
        if item.get("title") == LIST_TITLE:
            return item["id"]
    created = _api("POST", "/users/@me/lists", body={"title": LIST_TITLE})
    return created["id"]


def _existing_keys(list_id: str) -> set:
    """(title, notes) pairs already present, so we never push a duplicate."""
    keys, page = set(), None
    while True:
        params = {"maxResults": 100, "showHidden": True, "showCompleted": True}
        if page:
            params["pageToken"] = page
        res = _api("GET", f"/lists/{list_id}/tasks", params=params)
        for t in res.get("items", []):
            keys.add(((t.get("title") or "").strip().lower(),
                      (t.get("notes") or "").strip()))
        page = res.get("nextPageToken")
        if not page:
            break
    return keys


def sync_notes(notes: list[dict]) -> dict:
    """Push each dashboard note to Google Tasks once. Dedup is by (title, body):
    a note already in the list (or repeated in the input) is skipped.

    `notes` items use the chat_log.get_notes() shape: {title, content, ...}.
    Returns {added, skipped, total, list}.
    """
    list_id = _ensure_list()
    seen = _existing_keys(list_id)
    added = skipped = 0
    for n in notes:
        title = (n.get("title") or "").strip()
        content = (n.get("content") or "").strip()[:NOTES_MAX]
        if not title and not content:
            continue
        if not title:  # derive a title from the first line of the body
            title = content.splitlines()[0][:80] if content else "(untitled)"
        key = (title.strip().lower(), content)
        if key in seen:
            skipped += 1
            continue
        _api("POST", f"/lists/{list_id}/tasks", body={"title": title, "notes": content})
        seen.add(key)
        added += 1
    return {"added": added, "skipped": skipped, "total": len(notes), "list": LIST_TITLE}
