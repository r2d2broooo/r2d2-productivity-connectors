# Optional account connectors

Read module docstrings for environment variable names and APIs. Configure SMTP/IMAP
or Google OAuth yourself. No credentials, access tokens or account data are included.
Run each helper from its own environment and choose local credential storage paths.
These source modules expose explicit functions; importing/checking them does not
send email or edit tasks. Actual delivery, authentication and permissions were not
tested during the source backup. No background sync is enabled by this repository.
