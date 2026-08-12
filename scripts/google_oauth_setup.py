#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Zachary LeBlanc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""One-time helper to obtain a Gmail OAuth2 refresh token.

The gmail_search module authenticates using an OAuth2 installed-app client
(client_id/client_secret) plus a refresh_token. Google's OAuth2 flow
requires a human to consent in a browser, so that step cannot happen inside
an Ansible module -- it must be done once, out-of-band, using this script.

Usage:
    pip install google-auth-oauthlib
    python3 scripts/google_oauth_setup.py /path/to/client_id.json

    # or, with a non-default scope / local server port:
    python3 scripts/google_oauth_setup.py client_id.json \\
        --scopes https://www.googleapis.com/auth/gmail.readonly \\
        --port 8080

This opens a browser for you to sign in and consent, then prints the
client_id, client_secret, and refresh_token to store in your AAP custom
credential type (or as GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET /
GOOGLE_REFRESH_TOKEN environment variables / Ansible Vault values).

The client_id.json is the "installed app" OAuth client downloaded from the
Google Cloud Console (APIs & Services > Credentials), NOT a service account
key -- see ansible_client_id.example.json at the repo root for its shape.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import argparse
import json
import sys

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Obtain a Gmail OAuth2 refresh token via a one-time browser consent flow."
    )
    parser.add_argument(
        "client_secret_file",
        help="Path to the OAuth2 installed-app client_id JSON file downloaded from Google Cloud Console.",
    )
    parser.add_argument(
        "--scopes",
        nargs="+",
        default=DEFAULT_SCOPES,
        help=f"OAuth2 scopes to request (default: {DEFAULT_SCOPES[0]}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Local port for the OAuth2 redirect callback (default: automatically choose a free port).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print(
            "google-auth-oauthlib is required for this setup script.\n"
            "Install with: pip install google-auth-oauthlib",
            file=sys.stderr,
        )
        return 1

    try:
        with open(args.client_secret_file, encoding="utf-8") as handle:
            client_config = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Failed to read client_secret_file: {exc}", file=sys.stderr)
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret_file, scopes=args.scopes)
    print("Opening a browser to sign in and consent. If it doesn't open automatically, "
          "visit the printed URL manually.\n")
    credentials = flow.run_local_server(port=args.port)

    client_section = client_config.get("installed") or client_config.get("web") or {}
    client_id = client_section.get("client_id", credentials.client_id)
    client_secret = client_section.get("client_secret", credentials.client_secret)

    print("\nOAuth2 consent complete. Store these values in your AAP custom credential type\n"
          "(or as environment variables / Vault-encrypted module arguments):\n")
    print(f"  GOOGLE_CLIENT_ID={client_id}")
    print(f"  GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"  GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
    print("\nThe refresh_token does not expire unless revoked, so this flow only needs to run once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
