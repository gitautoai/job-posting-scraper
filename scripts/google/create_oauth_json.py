# pylint: disable=broad-exception-raised

import os

from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
def create_oauth_json():
    """Create google-oauth.json from environment variable"""
    oauth_json = os.getenv("GOOGLE_OAUTH_JSON")
    if not oauth_json:
        raise Exception("GOOGLE_OAUTH_JSON environment variable is not set")

    with open("google-oauth.json", "w", encoding="utf-8") as f:
        f.write(oauth_json)
    print("Created google-oauth.json from environment variable")
