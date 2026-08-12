# business.google

Ansible collection for interacting with Google Workspace (gsuite) services.

## Modules

- `gsheet_update` -- Update a Google Spreadsheet cell by row lookup.
- `gmail_search` -- Search Gmail messages with basic filters (to/from/subject/labels) and retrieve their contents.

## Requirements

- `google-api-python-client`
- `google-auth`

Install with:

```bash
pip install google-api-python-client google-auth
```

## Authentication

This collection uses two different Google authentication models depending on the module, because Gmail access requires a
specific mailbox owner's consent while Sheets access does not.

### `gsheet_update` -- service account

Authenticates using a Google service account. Provide credentials via one of:

- `credentials_path` module argument (path to a service account JSON key file)
- `credentials` module argument (service account JSON key as a dict, e.g. from Ansible Vault)
- `GOOGLE_SA_CRED_PATH` environment variable (path to a service account JSON key file)

The target spreadsheet is identified via the `gsheet_id` module argument or the `GOOGLE_SHEET_ID` environment variable.

### `gmail_search` -- OAuth2 installed-app credentials

Service accounts can't read a personal/Workspace Gmail mailbox without domain-wide delegation, so `gmail_search`
authenticates as a specific user via OAuth2 instead. Provide credentials via one of:

- `client_id` / `client_secret` / `refresh_token` module arguments (e.g. from Ansible Vault)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` environment variables -- this is the mechanism an
  AAP custom credential type should use to inject these values at job run time

The `refresh_token` must be obtained once via a human OAuth2 consent flow -- it cannot be generated automatically from
just the `client_id` and `client_secret`. Use the included helper script to do this:

```bash
pip install google-auth-oauthlib
python3 scripts/google_oauth_setup.py /path/to/client_id.json
```

This opens a browser for you to sign in and consent (requesting the `gmail.readonly` scope), then prints the
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` values to store in AAP. The `client_id.json` here
is an OAuth2 **installed-app** client downloaded from Google Cloud Console (APIs & Services > Credentials) -- see
`ansible_client_id.example.json` at the repo root for its shape -- not a service account key. The refresh token does
not expire unless revoked, so this only needs to be run once per Google account.
