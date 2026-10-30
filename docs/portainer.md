# Installing with Portainer

The Docker image is built automatically by GitHub Actions and published to
`ghcr.io/ausyp/telegram_media_downloader` for `amd64` and `arm64` hosts.

## 1. Get your Telegram credentials

1. **API ID and API hash:** log in at <https://my.telegram.org/apps> and create an app.
2. **Bot token (optional, for bot mode):** message [@BotFather](https://t.me/BotFather),
   send `/newbot`, and copy the token. Anything you send or forward to this bot is
   downloaded.

## 2. Create the stack

In Portainer go to **Stacks > Add stack** and give it a name such as `telegram-downloader`.

Choose one of these build methods:

- **Repository:** repository URL `https://github.com/ausyp/telegram_media_downloader`,
  reference `refs/heads/master`, compose path `docker-compose.yml`. Portainer can then
  redeploy automatically when the repo changes.
- **Web editor:** paste the contents of [`docker-compose.yml`](../docker-compose.yml).

Under **Environment variables** add:

| Variable            | Required | Description                                                                 |
| ------------------- | -------- | --------------------------------------------------------------------------- |
| `API_ID`            | Yes      | From my.telegram.org                                                        |
| `API_HASH`          | Yes      | From my.telegram.org                                                        |
| `BOT_TOKEN`         | No       | Bot token from @BotFather                                                   |
| `ALLOWED_USER_IDS`  | No       | Comma separated user ids or usernames allowed to use the bot. Default `me`  |
| `WEB_LOGIN_SECRET`  | No       | Password for the web UI. Strongly recommended if the port is reachable     |
| `MAX_DOWNLOAD_TASK` | No       | Number of simultaneous downloads. Default `5`                               |
| `DOWNLOAD_PATH`     | No       | Host folder for downloads, e.g. `/mnt/media/telegram`. Default: a volume    |
| `CHAT_IDS`          | No       | Comma separated chat ids to download in full on start                      |
| `WEB_PORT`          | No       | Host port for the web UI. Default `5000`                                    |
| `TZ`                | No       | Timezone, e.g. `America/New_York`. Default `UTC`                            |

Click **Deploy the stack**.

## 3. Log in to Telegram (first run only)

The downloader uses your own Telegram account, so it needs a one-time login.

1. Open **Containers > telegram_media_downloader > Attach** and click **Connect**.
2. Press Enter if you don't see a prompt yet. When asked
   `Enter phone number or bot token`, type your phone number with country code
   (for example `+15551234567`) and confirm with `y`.
3. Enter the login code Telegram sends you (and your 2FA password if you have one).
4. Once you see `Successfully started`, close the console with the **Disconnect** button.
   Don't press Ctrl+C, which would stop the container.

The login is saved in the `tmd_data` volume, so restarts and image updates don't
need it again.

## 4. Use it

- **Web UI:** `http://YOUR_HOST:5000`
- **Bot:** send `/help` to your bot, or just send/forward it any photo, video or file.

## Updating

Pull the latest image and redeploy: in **Stacks > telegram-downloader** click
**Update the stack** with **Re-pull image and redeploy** turned on.

## Advanced configuration

On first start the container creates `/data/config.yaml` from the environment
variables above. Every option from the main [README](../README.md#configuration)
can be set there, e.g. filters, file name patterns or rclone uploads. Edit it through
a container console (`vi /data/config.yaml`) or the volume on the host, then restart
the container. Environment variables that are set always override the matching key
in `config.yaml`.

## Notes

- The data volume contains your logged-in Telegram session. Treat it like a password
  and don't share backups of it.
- If the image pull fails with `denied`, the GHCR package is private. Make it public
  under your GitHub profile > **Packages > telegram_media_downloader > Package settings**,
  or add a GHCR registry with a personal access token in Portainer's **Registries**.
