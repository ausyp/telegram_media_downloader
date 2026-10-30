"""Create or update config.yaml from environment variables (used by the Docker image).

Only keys whose environment variable is set are written, so anything you edit
directly in config.yaml is kept unless an environment variable overrides it.
"""

import os
import sys

from ruamel import yaml

CONFIG_FILE = "config.yaml"

DEFAULT_CONFIG = {
    "api_id": "",
    "api_hash": "",
    "chat": [],
    "media_types": [
        "audio",
        "document",
        "photo",
        "video",
        "voice",
        "video_note",
        "animation",
    ],
    "file_formats": {"audio": ["all"], "document": ["all"], "video": ["all"]},
    "save_path": "/downloads",
    "file_path_prefix": ["chat_title", "media_datetime"],
    "file_name_prefix": ["message_id", "file_name"],
    "max_download_task": 5,
    "web_host": "0.0.0.0",
    "web_port": 5000,
    "language": "EN",
    "allowed_user_ids": ["me"],
    "ids_to_retry": [],
}


def _split(value: str) -> list:
    return [item.strip() for item in value.split(",") if item.strip()]


def _int_or_str(value: str):
    try:
        return int(value)
    except ValueError:
        return value


# (environment variable, config key, converter)
ENV_OVERRIDES = [
    ("API_ID", "api_id", _int_or_str),
    ("API_HASH", "api_hash", str),
    ("BOT_TOKEN", "bot_token", str),
    ("ALLOWED_USER_IDS", "allowed_user_ids", _split),
    ("WEB_LOGIN_SECRET", "web_login_secret", str),
    ("MAX_DOWNLOAD_TASK", "max_download_task", int),
    ("MEDIA_TYPES", "media_types", _split),
    ("FILE_NAME_PREFIX", "file_name_prefix", _split),
    ("SAVE_PATH", "save_path", str),
    ("LANGUAGE", "language", str),
    ("LOG_LEVEL", "log_level", str),
]


def main():
    """Entry point"""
    _yaml = yaml.YAML()

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = _yaml.load(f.read()) or {}
        print(f"Using existing {os.path.abspath(CONFIG_FILE)}")
    else:
        config = dict(DEFAULT_CONFIG)
        print(f"Creating {os.path.abspath(CONFIG_FILE)} from defaults")

    for env_name, key, convert in ENV_OVERRIDES:
        value = os.environ.get(env_name, "").strip()
        if value:
            config[key] = convert(value)

    chat_ids = os.environ.get("CHAT_IDS", "").strip()
    if chat_ids:
        existing = {str(item.get("chat_id")): item for item in config.get("chat") or []}
        config["chat"] = [
            existing.get(
                chat_id, {"chat_id": _int_or_str(chat_id), "last_read_message_id": 0}
            )
            for chat_id in _split(chat_ids)
        ]

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        _yaml.dump(config, f)

    if not config.get("api_id") or not config.get("api_hash"):
        print(
            "ERROR: API_ID and API_HASH are required. Get them from "
            "https://my.telegram.org/apps and set them as environment variables "
            "(or in config.yaml in the data volume).",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
