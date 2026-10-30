"""One-time Telegram login for the Docker image.

Run it from a container console with `tmd-login`. It signs in your account,
saves the session in the data volume and lets the downloader start.
"""

import os
import sys

import pyrogram
from ruamel import yaml

DATA_DIR = os.environ.get("DATA_DIR", "/data")
SESSION_DIR = os.path.join(DATA_DIR, "sessions")
SESSION_NAME = "media_downloader"
LOGGED_IN_MARKER = os.path.join(SESSION_DIR, ".logged_in")


def main():
    """Entry point"""
    with open(os.path.join(DATA_DIR, "config.yaml"), encoding="utf-8") as f:
        config = yaml.YAML().load(f.read()) or {}

    if not config.get("api_id") or not config.get("api_hash"):
        sys.exit("API_ID and API_HASH are missing. Set them on the stack first.")

    os.makedirs(SESSION_DIR, exist_ok=True)

    # A session left behind by an unfinished login can't be used, so start clean.
    session_file = os.path.join(SESSION_DIR, f"{SESSION_NAME}.session")
    if not os.path.exists(LOGGED_IN_MARKER) and os.path.exists(session_file):
        os.remove(session_file)

    client = pyrogram.Client(
        SESSION_NAME,
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        proxy=config.get("proxy"),
        workdir=SESSION_DIR,
        no_updates=True,
    )
    with client:
        me = client.get_me()
        print(f"\nLogged in as {me.first_name} (id {me.id}).")

    with open(LOGGED_IN_MARKER, "w", encoding="utf-8") as f:
        f.write(str(me.id))
    print("Done. The downloader will start within a few seconds.")


if __name__ == "__main__":
    main()
