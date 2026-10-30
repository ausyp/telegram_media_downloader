
<h1 align="center">Telegram Media Downloader</h1>

<p align="center">
<a href="https://deepwiki.com/tangyoha/telegram_media_downloader"><img alt="DeepWiki" src="https://img.shields.io/badge/DeepWiki-Documentation-blue"></a>
<a href="https://github.com/tangyoha/telegram_media_downloader/actions"><img alt="Unittest" src="https://github.com/tangyoha/telegram_media_downloader/workflows/Unittest/badge.svg"></a>
<a href="https://codecov.io/gh/tangyoha/telegram_media_downloader"><img alt="Coverage Status" src="https://codecov.io/gh/tangyoha/telegram_media_downloader/branch/master/graph/badge.svg"></a>
<a href="https://github.com/tangyoha/telegram_media_downloader/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/python/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/tangyoha/telegram_media_downloader/releases">
<img alt="Code style: black" src="https://img.shields.io/github/v/release/tangyoha/telegram_media_downloader?display_name=tag"></a>
</p>

<h3 align="center">
  <a href="https://github.com/tangyoha/telegram_media_downloader/discussions/categories/ideas">Feature request</a>
  <span> · </span>
  <a href="https://github.com/tangyoha/telegram_media_downloader/issues">Report a bug</a>
  <span> · </span>
  Support: <a href="https://github.com/tangyoha/telegram_media_downloader/discussions">Discussions</a>
  <span> & </span>
  <a href="https://t.me/TeegramMediaDownload">Telegram Community</a>
</h3>

## Overview

> **Running it with Docker or Portainer?** Follow [Docker / Portainer setup](#docker--portainer-setup).

> Support two default running

* The robot is running, and the command `download` or `forward` is issued from the robot

* Download as a one-time download tool

### UI

#### Web page

> After running, open a browser and visit `localhost:5000`
> If it is a remote machine, you need to configure web_host: 0.0.0.0


<img alt="Code style: black" style="width:100%; high:60%;" src="./screenshot/web_ui.gif"/>

### Robot

> Need to configure bot_token, please refer to [Documentation](https://github.com/tangyoha/telegram_media_downloader/wiki/How-to-Download-Using-Robots)

<img alt="Code style: black" style="width:60%; high:30%; " src="./screenshot/bot.gif"/>

### Support

| Category             | Support                                          |
| -------------------- | ------------------------------------------------ |
| Language             | `Python 3.7` and above                           |
| Download media types | audio, document, photo, video, video_note, voice |

### Version release plan

* [v2.2.0](https://github.com/tangyoha/telegram_media_downloader/issues/2)

## Installation

For *nix os distributions with `make` availability

```sh
git clone https://github.com/tangyoha/telegram_media_downloader.git
cd telegram_media_downloader
make install
```

For Windows which doesn't have `make` inbuilt

```sh
git clone https://github.com/tangyoha/telegram_media_downloader.git
cd telegram_media_downloader
pip3 install -r requirements.txt
```

## Docker / Portainer setup

Setup takes about 15 minutes. At the end you have a Telegram bot that saves everything you send it to a folder on your server, plus a web dashboard on port 5000.

The image `ghcr.io/ausyp/telegram_media_downloader:latest` is public and built for amd64 and arm64 (works on a Raspberry Pi 4/5 or Synology too), so Portainer needs no registry login.

### 1. Get your API ID and API hash

1. Open [my.telegram.org/apps](https://my.telegram.org/apps) and log in with your phone number. The code arrives in the Telegram app, not by SMS.
2. Fill in the "Create new application" form. Any title and short name work, for example `MediaDownloader` and `mediadl`. Platform can be "Other".
3. Copy **App api_id** (a number) and **App api_hash** (a 32-character string). Keep the hash private.

### 2. Create your bot

1. In Telegram, open [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Pick a display name, then a username ending in `bot`, for example `my_media_dl_bot`.
3. Copy the token BotFather sends (like `7012345678:AAH...`). This is your `BOT_TOKEN`.

Only your own account can use the bot by default. To allow others, list their user ids or `@usernames` in `ALLOWED_USER_IDS`.

### 3. Deploy the stack in Portainer

1. Go to **Stacks > Add stack** and name it `telegram-downloader`.
2. Under **Build method**, choose **Repository**:
    - Repository URL: `https://github.com/ausyp/telegram_media_downloader`
    - Repository reference: `refs/heads/master`
    - Compose path: `docker-compose.yml` (the default)
3. Under **Environment variables**, click **Load variables from .env file** and pick a filled-in copy of [`stack.env.example`](./stack.env.example), or switch to **Advanced mode** and paste:

    ```
    API_ID=12345678
    API_HASH=0123456789abcdef0123456789abcdef
    BOT_TOKEN=7012345678:AAH-your-token
    WEB_LOGIN_SECRET=choose-a-password
    DOWNLOAD_PATH=/mnt/media/telegram
    MAX_DOWNLOAD_TASK=5
    TZ=America/New_York
    ```

4. Click **Deploy the stack**.

| Variable | Required | What it does | Default |
| --- | --- | --- | --- |
| `API_ID` | Yes | From step 1 | none |
| `API_HASH` | Yes | From step 1 | none |
| `BOT_TOKEN` | For the bot | From step 2 | none |
| `WEB_LOGIN_SECRET` | Recommended | Password for the web UI | no password |
| `DOWNLOAD_PATH` | Recommended | Host folder where files are saved | a Docker volume |
| `ALLOWED_USER_IDS` | No | Comma-separated user ids or @usernames allowed to use the bot | `me` (your account) |
| `MAX_DOWNLOAD_TASK` | No | Files downloaded at the same time | 5 |
| `CHAT_IDS` | No | Chats to download in full on every start | none |
| `WEB_PORT` | No | Host port for the web UI | 5000 |
| `TZ` | No | Timezone used for dated folders | UTC |

### 4. Log in to Telegram (first run only)

Until you log in, the container log says `Telegram login needed` and waits. The login is then saved in the `tmd_data` volume and survives restarts and updates.

1. Go to **Containers > telegram_media_downloader > Console**, keep `/bin/sh`, and click **Connect**.
2. Run `tmd-login`.
3. Enter your phone number with country code (for example `+15551234567`) and confirm with `y`.
4. Enter the code Telegram sends to your Telegram app, then your two-step verification password if you use one.
5. When it says `Logged in as ...`, click **Disconnect**. The downloader starts by itself within a few seconds.

Over SSH, steps 1 to 4 are just `docker exec -it telegram_media_downloader tmd-login`.

### 5. Use it

**The bot.** Open your bot in Telegram and send `/start`.

| You send the bot | What happens |
| --- | --- |
| Any photo, video, audio, voice note or file, or a forward of one | Downloaded right away |
| A message link like `https://t.me/somechannel/123` | That one message is downloaded |
| `/download https://t.me/somechannel 1 0` | Every message in the chat, from message 1 to the latest (0 = latest) |
| `/download https://t.me/somechannel 100 200` | Messages 100 to 200 only |
| `/forward` | Copies messages from one chat to another; send it alone to see the format |
| `/listen_forward` | Keeps forwarding new messages from one chat to another |
| `/get_info` | Shows the bot's status and settings |
| `/stop` | Stops a running download or forward task |
| `/help` | Lists every command |

For a private channel or group, use the link of any message in it; your account must be a member.

**The web UI.** Open `http://YOUR-SERVER-IP:5000` and log in with `WEB_LOGIN_SECRET`. It shows downloads in progress with their speed, and finished downloads with their paths.

**Your files** land in `DOWNLOAD_PATH`, sorted as `<chat name>/<year_month>/<message id> - <file name>`.

### Optional extras

- **Download whole chats automatically:** set `CHAT_IDS` to a comma-separated list such as `-1001234567890,-1009876543210`. Each start downloads new messages in those chats and remembers where it stopped. Get an id by forwarding a message from the chat to [@username_to_id_bot](https://t.me/username_to_id_bot).
- **Advanced settings:** the container writes `/data/config.yaml` on first start. Edit it from the Console (`vi /data/config.yaml`) for filters, file name patterns, file types or rclone uploads (see [Configuration](#configuration)), then restart the container. Environment variables always override the matching line.
- **Updating:** in **Stacks > telegram-downloader**, turn on **Re-pull image and redeploy** and click **Update the stack**. Your login and settings are kept.

### Troubleshooting

- **The bot ignores you:** your account isn't in `ALLOWED_USER_IDS`, or the step 4 login isn't done.
- **`API_ID and API_HASH are required` in the logs:** the environment variables didn't reach the container. Recheck step 3 and redeploy.
- **`stat .../docker-compose.yml: no such file`:** the compose path in the stack doesn't match. Use `docker-compose.yml`.
- **Some files are skipped:** check `media_types` and `file_formats` in `/data/config.yaml`.
- **Can't reach the web UI:** open port 5000 (or your `WEB_PORT`) on the server firewall.

**Security:** the `tmd_data` volume holds a logged-in Telegram session, so treat backups of it like a password. Keep the web UI on your home network or behind a VPN.

### Docker compose without Portainer

```sh
mkdir -p ~/telegram_media_downloader && cd ~/telegram_media_downloader
wget https://raw.githubusercontent.com/ausyp/telegram_media_downloader/master/docker-compose.yml
wget -O .env https://raw.githubusercontent.com/ausyp/telegram_media_downloader/master/stack.env.example
nano .env   # fill in your values
docker compose up -d
docker exec -it telegram_media_downloader tmd-login   # first run only
```

Upgrade with `docker compose pull && docker compose up -d`.

## Upgrade installation

```sh
cd telegram_media_downloader
pip3 install -r requirements.txt
```

## Configuration

All the configurations are  passed to the Telegram Media Downloader via `config.yaml` file.

**Getting your API Keys:**
The very first step requires you to obtain a valid Telegram API key (API id/hash pair):

1. Visit  [https://my.telegram.org/apps](https://my.telegram.org/apps)  and log in with your Telegram Account.
2. Fill out the form to register a new Telegram application.
3. Done! The API key consists of two parts:  **api_id**  and  **api_hash**.

**Getting chat id:**

**1. Using web telegram:**

1. Open <https://web.telegram.org/?legacy=1#/im>

2. Now go to the chat/channel and you will see the URL as something like
   - `https://web.telegram.org/?legacy=1#/im?p=u853521067_2449618633394` here `853521067` is the chat id.
   - `https://web.telegram.org/?legacy=1#/im?p=@somename` here `somename` is the chat id.
   - `https://web.telegram.org/?legacy=1#/im?p=s1301254321_6925449697188775560` here take `1301254321` and add `-100` to the start of the id => `-1001301254321`.
   - `https://web.telegram.org/?legacy=1#/im?p=c1301254321_6925449697188775560` here take `1301254321` and add `-100` to the start of the id => `-1001301254321`.

**2. Using bot:**

1. Use [@username_to_id_bot](https://t.me/username_to_id_bot) to get the chat_id of
    - almost any telegram user: send username to the bot or just forward their message to the bot
    - any chat: send chat username or copy and send its joinchat link to the bot
    - public or private channel: same as chats, just copy and send to the bot
    - id of any telegram bot

### config.yaml

```yaml
api_hash: your_api_hash
api_id: your_api_id
chat:
- chat_id: telegram_chat_id
  last_read_message_id: 0
  download_filter: message_date >= 2022-12-01 00:00:00 and message_date <= 2023-01-17 00:00:00
- chat_id: telegram_chat_id_2
  last_read_message_id: 0
# note we remove ids_to_retry to data.yaml
ids_to_retry: []
media_types:
- audio
- document
- photo
- video
- voice
- animation #gif
file_formats:
  audio:
  - all
  document:
  - pdf
  - epub
  video:
  - mp4
save_path: D:\telegram_media_downloader
file_path_prefix:
- chat_title
- media_datetime
upload_drive:
  # required
  enable_upload_file: true
  # required
  remote_dir: drive:/telegram
  # required
  upload_adapter: rclone
  # option,when config upload_adapter rclone then this config are required
  rclone_path: D:\rclone\rclone.exe
  # option
  before_upload_file_zip: True
  # option
  after_upload_file_delete: True
hide_file_name: true
file_name_prefix:
- message_id
- file_name
file_name_prefix_split: ' - '
max_download_task: 5
web_host: 127.0.0.1
web_port: 5000
language: EN
web_login_secret: 123
allowed_user_ids:
- 'me'
date_format: '%Y_%m'
enable_download_txt: false
```

- **api_hash**  - The api_hash you got from telegram apps
- **api_id** - The api_id you got from telegram apps
- **bot_token** - Your bot token
- **chat** - Chat list
  - `chat_id` -  The id of the chat/channel you want to download media. Which you get from the above-mentioned steps.
  - `download_filter` - Download filter, see [How to use Filter](https://github.com/tangyoha/telegram_media_downloader/wiki/How-to-use-Filter)
  - `last_read_message_id` - If it is the first time you are going to read the channel let it be `0` or if you have already used this script to download media it will have some numbers which are auto-updated after the scripts successful execution. Don't change it.
  - `ids_to_retry` - `Leave it as it is.` This is used by the downloader script to keep track of all skipped downloads so that it can be downloaded during the next execution of the script.
- **media_types** - Type of media to download, you can update which type of media you want to download it can be one or any of the available types.
- **file_formats** - File types to download for supported media types which are `audio`, `document` and `video`. Default format is `all`, downloads all files.
- **save_path** - The root directory where you want to store downloaded files.
- **file_path_prefix** - Store file subfolders, the order of the list is not fixed, can be randomly combined.
  - `chat_title`      - Channel or group title, it will be chat id if not exist title.
  - `media_datetime`  - Media date.
  - `media_type`      - Media type, also see `media_types`.
- **upload_drive** - You can upload file to cloud drive.
  - `enable_upload_file` - Enable upload file, default `false`.
  - `remote_dir` - Where you upload, like `drive_id/drive_name`.
  - `upload_adapter` - Upload file adapter, which can be `rclone`, `aligo`. If it is `rclone`, it supports all `rclone` servers that support uploading. If it is `aligo`, it supports uploading `Ali cloud disk`.
  - `rclone_path` - RClone exe path, see [How to use rclone](https://github.com/tangyoha/telegram_media_downloader/wiki/Rclone)
  - `before_upload_file_zip` - Zip file before upload, default `false`.
  - `after_upload_file_delete` - Delete file after upload success, default `false`.
- **file_name_prefix** - Custom file name, use the same as **file_path_prefix**
  - `message_id` - Message id
  - `file_name` - File name (may be empty)
  - `caption` - The title of the message (may be empty)
- **file_name_prefix_split** - Custom file name prefix symbol, the default is `-`
- **max_download_task** - The maximum number of task download tasks, the default is 5.
- **hide_file_name** - Whether to hide the web interface file name, default `false`
- **web_host** - Web host
- **web_port** - Web port
- **language** - Application language, the default is English (`EN`), optional `ZH`(Chinese),`RU`,`UA`
- **web_login_secret** - Web page login password, if not configured, no login is required to access the web page
- **log_level** - see `logging._nameToLevel`.
- **forward_limit** - Limit the number of forwards per minute, the default is 33, please do not modify this parameter by default.
- **allowed_user_ids** - Who is allowed to use the robot? The default login account can be used. Please add single quotes to the name with @.
- **date_format** Support custom configuration of media_datetime format in file_path_prefix.see [python-datetime](https://docs.python.org/3/library/datetime.html)
- **enable_download_txt** Enable download txt file, default `false`

## Execution

```sh
python3 media_downloader.py
```

All downloaded media will be stored at the root of `save_path`.
The specific location reference is as follows:

The complete directory of video download is: `save_path`/`chat_title`/`media_datetime`/`media_type`.
The order of the list is not fixed and can be randomly combined.
If the configuration is empty, all files are saved under `save_path`.

## Proxy

`socks4, socks5, http` proxies are supported in this project currently. To use it, add the following to the bottom of your `config.yaml` file

```yaml
proxy:
  scheme: socks5
  hostname: 127.0.0.1
  port: 1234
  username: your_username(delete the line if none)
  password: your_password(delete the line if none)
```

If your proxy doesn’t require authorization you can omit username and password. Then the proxy will automatically be enabled.

## Contributing

### Contributing Guidelines

Read through our [contributing guidelines](https://github.com/tangyoha/telegram_media_downloader/blob/master/CONTRIBUTING.md) to learn about our submission process, coding rules and more.

### Want to Help?

Want to file a bug, contribute some code, or improve documentation? Excellent! Read up on our guidelines for [contributing](https://github.com/tangyoha/telegram_media_downloader/blob/master/CONTRIBUTING.md).

### Code of Conduct

Help us keep Telegram Media Downloader open and inclusive. Please read and follow our [Code of Conduct](https://github.com/tangyoha/telegram_media_downloader/blob/master/CODE_OF_CONDUCT.md).


### Sponsor

[PayPal](https://paypal.me/tangyoha?country.x=C2&locale.x=zh_XC)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tangyoha/telegram_media_downloader&type=Date)](https://star-history.com/#tangyoha/telegram_media_downloader&Date)
