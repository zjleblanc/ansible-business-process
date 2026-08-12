# Changelog

## 2026-08-12 — Limit account activity summaries to the last 3 months

### Added
- `business.google.recent_tasks` filter plugin to keep only Salesforce tasks whose date falls within the last N months (default 3).

### Changed
- Account dashboard updates now summarize and write only tasks from the last 3 months; when none remain, columns F and G are set to `{}` and the AI call is skipped.
- Annotated parser loop state in `parse_sf_tasks` so Pylint no longer flags `current_account` as unsubscriptable.

---

## 2026-08-12 — Require gsheet and gmail vars for account dashboard playbook

### Changed
- `pb_update_account_tasks.yml` now asserts required AI, Gmail, and Google Sheets variables up front (with inline example values) instead of defaulting sheet/range settings in the playbook `vars` section.
- Updated `vault.yml` to supply the required playbook variables for local runs.
- Ignored `*.log` files in `.gitignore`.

---

## 2026-08-12 — Migrate parse_sf_tasks filter from business.custom to business.google

### Changed
- Moved `parse_sf_tasks` filter plugin from `business.custom` to `business.google` — the FQCN is now `business.google.parse_sf_tasks`.
- `parse_sf_tasks` now returns a dict (with an `accounts` key) instead of a plain list, adding `total_tasks`, `total_opps`, and `total_accounts` summary counts at the root, account, and opportunity levels.
- Updated `gmail_tasks_report.yml` playbook to use the new FQCN.
- Moved `beautifulsoup4` dependency under the `business.google` group in `requirements.txt`.

### Removed
- Removed the `business.custom` collection (its only content was `parse_sf_tasks`).

---

## 2026-08-12 — Support OAuth2 credentials in gsheet_update alongside service accounts

### Added
- `SHEETS_COMBINED_ARGSPEC` and `SHEETS_COMBINED_MUTUALLY_EXCLUSIVE` in `business.google`'s `module_utils/auth.py`, merging the service-account and OAuth2 argument specs and enforcing that only one credential type is provided at a time.

### Changed
- `gsheet_update` now authenticates with either a Google service account (`credentials_path`/`credentials`) or an OAuth2 installed-app client (`client_id`/`client_secret`/`refresh_token`), so the same OAuth2 client already used by `gmail_search` can also update Sheets.
- `scripts/google_oauth_setup.py` now requests both the `gmail.readonly` and `spreadsheets` scopes by default, so a single refresh token works for both `gmail_search` and `gsheet_update`.
- Updated the `business.google` collection README to document the dual authentication options for `gsheet_update` and note that existing Gmail-only refresh tokens must be regenerated to also cover Sheets.
