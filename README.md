# r2d2-productivity-connectors

Small email and Google Tasks helpers with explicit authentication and no background sending.

Keep personal productivity connectors independent of market analysis and agent orchestration.

## Features

- SMTP/IMAP helper source
- Google Tasks API integration
- Local Google OAuth setup helper
- Credentials stay local

## Use

python3 check.py; read USAGE.md before configuring accounts. External sending or account writes require an explicit task.

Run `python3 check.py` for read-only source checks. These checks are not a claim
that external accounts, market feeds, hardware or a deployed service are configured.

## Snapshot and updates

Created on 2026-11-05 from the local R2D2 workspaces. This is a private source
snapshot; the original local workspaces remain the working copies. The catalogue
repo records every source and omission. Updates happen only on explicit operator
request; there is no automatic sync, push, hook or publishing timer.

Credentials, private chats/memory, live paper books, game saves, models, caches,
virtual environments and proprietary application binaries are not included.
Use a separate environment for this repo. Read USAGE.md/SETUP.md or the original
README where present. Existing integrations are documented rather than silently
starting account actions.
