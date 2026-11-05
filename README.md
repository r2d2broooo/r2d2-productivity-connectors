# R2D2 Productivity Connectors

Small explicit-action helpers for sending an email through SMTP and transferring note-shaped records to Google Tasks. They are separated from trading and agent orchestration so an application can reuse the account connectors without importing the larger workspace.

The modules do not schedule work or carry account credentials. A caller decides when an external action is authorized.

## Components

### SMTP email

`email_client.py` creates a plain-text message and sends it through an SSL SMTP connection. It exposes an asynchronous `send_email(to, subject, body)` function that runs the blocking SMTP work in a thread.

Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` and `SMTP_PASSWORD` locally. `SMTP_FROM` is optional and defaults to the configured user. This is an outgoing-mail helper; the repository does not implement an IMAP inbox reader, spam processing or mailbox synchronization.

### Google Tasks

`gtasks_sync.py` uses the official Google Tasks API through standard-library HTTP/JSON utilities. It can find or create the configured task list and add note records while skipping existing title/body pairs. Input records have `title` and `content` fields.

The connector uses `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` and `GOOGLE_REFRESH_TOKEN`, obtains short-lived access tokens and caches those tokens in memory. The supplied `google_auth.py` is a separate interactive setup helper for obtaining the required local OAuth credentials.

## Setup and safe inspection

The connector runtime uses the Python standard library. Read [USAGE.md](USAGE.md) and the module docstrings for account-specific prerequisites.

```bash
python3 check.py
```

Importing the helper modules or running source checks does not send a message or change tasks. Calling `send_email`, `sync_notes` or the interactive authorization helper does have external effects. Test with an account and content you deliberately choose, and keep credentials in an untracked local environment or secret store.

## Data and limits

No addresses, mail content, OAuth records, task exports, passwords or account tokens are included. The Google connector maps notes to Tasks; it is not an unofficial Google Keep client or a complete two-way task-sync system. Its duplicate detection is based on the normalized title/body pair and does not reconcile arbitrary edits in both directions.

Checks cover the source, not actual mail delivery, account permissions or Google authentication. Provider policies and server requirements can differ. The larger agent workflow may invoke these functions only as an explicitly requested action; this standalone repository adds no background sending.

## Privacy, provenance and updates

This repository is a sanitized source export. No provider credentials, personal contact information, configured IP addresses, private conversations or runtime databases are included. Example hostnames and local environment variables are intentional. Keep newly generated account data and captures outside version control.

A source manifest records exported files. Local adaptations and third-party material retain their own provenance/notices; public visibility does not apply a new blanket license to every file. Related repositories and the manual update process are listed in the [workspace catalogue](https://github.com/r2d2broooo/r2d2-workspace-catalog).

Updates are made only on explicit request. Cloning does not enable an automatic sync, scheduled publication or Git push.
