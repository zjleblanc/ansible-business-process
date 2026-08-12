# Changelog

## 2026-08-12 — Support OAuth2 credentials in gsheet_update alongside service accounts

### Added
- `SHEETS_COMBINED_ARGSPEC` and `SHEETS_COMBINED_MUTUALLY_EXCLUSIVE` in `business.google`'s `module_utils/auth.py`, merging the service-account and OAuth2 argument specs and enforcing that only one credential type is provided at a time.

### Changed
- `gsheet_update` now authenticates with either a Google service account (`credentials_path`/`credentials`) or an OAuth2 installed-app client (`client_id`/`client_secret`/`refresh_token`), so the same OAuth2 client already used by `gmail_search` can also update Sheets.
- `scripts/google_oauth_setup.py` now requests both the `gmail.readonly` and `spreadsheets` scopes by default, so a single refresh token works for both `gmail_search` and `gsheet_update`.
- Updated the `business.google` collection README to document the dual authentication options for `gsheet_update` and note that existing Gmail-only refresh tokens must be regenerated to also cover Sheets.
