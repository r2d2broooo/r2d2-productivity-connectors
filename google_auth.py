#!/usr/bin/env python3
"""One-time Google OAuth helper — mints a refresh token for Google Tasks sync.

Run this ONCE on the desktop (it opens a browser). Prereqs in Google Cloud:
  1. Create / pick a project at https://console.cloud.google.com
  2. APIs & Services -> Library -> enable "Google Tasks API"
  3. APIs & Services -> Credentials -> Create credentials -> OAuth client ID
     -> Application type: "Desktop app". Copy the Client ID + Client secret.
  4. OAuth consent screen -> add your own Gmail as a Test user.

Then run:
    python3 scripts/google_auth.py
Paste the Client ID + secret when prompted, approve in the browser, and this
prints the three lines to append to your .env:
    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_REFRESH_TOKEN=...

Stdlib only — no google client libraries.
"""
import http.server
import json
import secrets
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/tasks"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
PORT = 8731  # loopback redirect port


class _Handler(http.server.BaseHTTPRequestHandler):
    code = None
    state = None

    def do_GET(self):
        q = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(q)
        _Handler.code = (params.get("code") or [None])[0]
        got_state = (params.get("state") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        ok = _Handler.code and got_state == _Handler.state
        msg = "Authorized. You can close this tab and return to the terminal." if ok \
            else "Authorization failed — check the terminal."
        self.wfile.write(f"<html><body><h2>{msg}</h2></body></html>".encode())

    def log_message(self, *a):
        pass


def main():
    client_id = input("Google Client ID: ").strip()
    client_secret = input("Google Client secret: ").strip()
    redirect_uri = f"http://localhost:{PORT}/"
    state = secrets.token_urlsafe(16)
    _Handler.state = state

    auth = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",        # force a refresh_token every time
        "state": state,
    })
    print("\nOpening browser for Google sign-in...")
    print("If it doesn't open, paste this URL:\n", auth, "\n")
    try:
        webbrowser.open(auth)
    except Exception:
        pass

    srv = http.server.HTTPServer(("localhost", PORT), _Handler)
    srv.handle_request()  # serve exactly one redirect
    if not _Handler.code:
        print("No authorization code received. Aborting.")
        return

    body = urllib.parse.urlencode({
        "code": _Handler.code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as r:
        tok = json.loads(r.read().decode())

    refresh = tok.get("refresh_token")
    if not refresh:
        print("No refresh_token returned. Re-run (the consent prompt is required).")
        print("Raw response:", tok)
        return

    print("\n" + "=" * 60)
    print("SUCCESS — append these lines to your .env files:")
    print("=" * 60)
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={refresh}")
    print("=" * 60)


if __name__ == "__main__":
    main()
