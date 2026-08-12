# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Ansible Support Analyzer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared Google authentication helpers for the business.google collection.

Centralizes service account credential resolution and loading so every
module in this collection authenticates the same way without duplicating
this logic.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE = True
except ImportError:
    # Left unbound on failure; safe because every module MUST call
    # check_google_deps() (which fail_json()/exits) before referencing these.
    Credentials = None
    build = None
    HttpError = None
    HAS_GOOGLE = False

GOOGLE_SA_CRED_ENV = "GOOGLE_SA_CRED_PATH"
GOOGLE_SHEET_ID_ENV = "GOOGLE_SHEET_ID"

#: Default OAuth scope granting read/write access to Google Sheets.
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

#: Shared argument_spec entries for modules that authenticate against Google.
#: Merge into a module's argument_spec, e.g.:
#:   argument_spec=dict(AUTH_ARGSPEC, **{"sheet": dict(type="str", ...)})
AUTH_ARGSPEC = dict(
    credentials_path=dict(type="path"),
    credentials=dict(type="dict", no_log=True),
    gsheet_id=dict(type="str", aliases=["spreadsheet_id"]),
)

#: Shared mutually_exclusive entries corresponding to AUTH_ARGSPEC.
AUTH_MUTUALLY_EXCLUSIVE = [["credentials_path", "credentials"]]


def check_google_deps(module):
    """Fail the module with a clear message if the Google client libs are missing."""
    if not HAS_GOOGLE:
        module.fail_json(
            msg=(
                "google-api-python-client and google-auth are required. "
                "Install with: pip install google-api-python-client google-auth"
            )
        )


def resolve_credentials_path(credentials_path):
    """Return explicit path or fall back to GOOGLE_SA_CRED_PATH."""
    if credentials_path:
        return credentials_path
    return os.environ.get(GOOGLE_SA_CRED_ENV)


def resolve_gsheet_id(gsheet_id):
    """Return explicit spreadsheet ID or fall back to GOOGLE_SHEET_ID."""
    if gsheet_id:
        return gsheet_id
    return os.environ.get(GOOGLE_SHEET_ID_ENV)


def load_credentials(credentials_path, credentials_dict, scopes=None):
    """Build Google service account credentials from a file path or dict."""
    scopes = scopes or SHEETS_SCOPES
    if credentials_path:
        if not os.path.isfile(credentials_path):
            raise ValueError(f"credentials file not found: {credentials_path}")
        return Credentials.from_service_account_file(credentials_path, scopes=scopes)
    return Credentials.from_service_account_info(credentials_dict, scopes=scopes)
