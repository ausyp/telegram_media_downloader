#!/bin/sh
set -e

# All runtime state (config.yaml, data.yaml, bot.yaml, sessions, logs, temp files)
# lives in /data so a single volume keeps it across container updates.
DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR" "${SAVE_PATH:-/downloads}"
cd "$DATA_DIR"

# The app looks for rclone at ./rclone/rclone by default.
if [ ! -e rclone/rclone ]; then
    mkdir -p rclone
    ln -s /usr/bin/rclone rclone/rclone
fi

touch data.yaml
python /app/docker/init_config.py

exec python /app/media_downloader.py "$@"
