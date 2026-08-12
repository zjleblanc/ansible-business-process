# business.google

Ansible collection for interacting with Google Workspace (gsuite) services.

## Modules

- `gsheet_update` -- Update a Google Spreadsheet cell by row lookup.

## Requirements

- `google-api-python-client`
- `google-auth`

Install with:

```bash
pip install google-api-python-client google-auth
```

## Authentication

Modules in this collection authenticate using a Google service account. Provide credentials via one of:

- `credentials_path` module argument (path to a service account JSON key file)
- `credentials` module argument (service account JSON key as a dict, e.g. from Ansible Vault)
- `GOOGLE_SA_CRED_PATH` environment variable (path to a service account JSON key file)

The target spreadsheet is identified via the `gsheet_id` module argument or the `GOOGLE_SHEET_ID` environment variable.
