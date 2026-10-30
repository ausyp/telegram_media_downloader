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

# First run: wait for the one-time Telegram login, done from a console with
# `tmd-login`.
mkdir -p sessions
if [ ! -f sessions/.logged_in ]; then
    echo "============================================================"
    echo " Telegram login needed (first run only)."
    echo " In Portainer: Containers > telegram_media_downloader > Console,"
    echo " connect with /bin/sh, then run:  tmd-login"
    echo " Waiting for the login to finish..."
    echo "============================================================"
    while [ ! -f sessions/.logged_in ]; do
        sleep 3
    done
    echo "Login found, starting the downloader."
fi

exec python /app/media_downloader.py "$@"
