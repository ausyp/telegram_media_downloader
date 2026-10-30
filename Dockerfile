FROM python:3.11.9-alpine AS build

WORKDIR /app

# Build deps for pip packages that need compilation
RUN apk add --no-cache --virtual .build-deps gcc musl-dev

# Install python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install rclone (runtime binary)
RUN apk add --no-cache rclone


FROM python:3.11.9-alpine AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    SAVE_PATH=/downloads

# Copy installed deps from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# rclone for optional cloud uploads (linked into the data dir by the entrypoint)
COPY --from=build /usr/bin/rclone /usr/bin/rclone

# Lets the TZ environment variable set the timezone
RUN apk add --no-cache tzdata

# Copy app source code
COPY . /app

# `tmd-login` command for the one-time Telegram login from a container console
RUN printf '#!/bin/sh\nexec python /app/docker/login.py "$@"\n' > /usr/local/bin/tmd-login \
    && chmod +x /usr/local/bin/tmd-login

VOLUME ["/data", "/downloads"]
EXPOSE 5000

ENTRYPOINT ["/bin/sh", "/app/docker/entrypoint.sh"]
