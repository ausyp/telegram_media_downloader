---
name: pyrogram-telegram-bot-techniques
description: Pyrogram Telegram bot development techniques: parsing message links, custom session timeouts, avoiding black-screen video uploads, and removing ads from messages.Use when working with Pyrogram, parsing Telegram message links, uploading videos, or removing advertisement content from messages.
---

# Pyrogram Telegram Bot Development Techniques

## 1. Parsing Telegram Message Links

Extract chat_id, message_id, and topic_id from a Telegram link.

### Link data structure

```python
from dataclasses import dataclass
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse

@dataclass
class Link:
    """Telegram Link"""
    group_id: Union[str, int, None] = None
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    topic_id: Optional[int] = None
```

### Extracting link information

```python
def extract_info_from_link(link: str) -> Link:
    """Extract info from link"""
    if link in ("me", "self"):
        return Link(group_id=link)

    try:
        u = urlparse(link)
        paths = [p for p in u.path.split("/") if p]
        query = parse_qs(u.query)
    except ValueError:
        return Link()

    result = Link()

    if "comment" in query:
        result.group_id = paths[0]
        result.comment_id = int(query["comment"][0])
    elif len(paths) == 1 and paths[0] != "c":
        result.group_id = paths[0]
    elif len(paths) == 2:
        if paths[0] == "c":
            result.group_id = int(f"-100{paths[1]}")
        else:
            result.group_id = paths[0]
            result.post_id = int(paths[1])
    elif len(paths) == 3:
        if paths[0] == "c":
            result.group_id = int(f"-100{paths[1]}")
            result.post_id = int(paths[2])
        else:
            result.group_id = paths[0]
            result.topic_id = int(paths[1])
            result.post_id = int(paths[2])
    elif len(paths) == 4 and paths[0] == "c":
        result.group_id = int(f"-100{paths[1]}")
        result.topic_id = int(paths[2])
        result.post_id = int(paths[3])

    return result
```

### Parsing links and handling comments

```python
async def parse_link(client: pyrogram.Client, link_str: str):
    """Parse link - handles both regular messages and comments"""
    link = extract_info_from_link(link_str)
    if link.comment_id:
        # Comment links need the ID of the linked discussion group
        chat = await client.get_chat(link.group_id)
        if chat:
            return chat.linked_chat.id, link.comment_id, link.topic_id

    return link.group_id, link.post_id, link.topic_id
```

**Supported link formats:**
- `https://t.me/channel_name/123` - Public channel message
- `https://t.me/c/1234567890/123` - Private channel message (automatically converted to the -100 format)
- `https://t.me/channel_name/topic_id/123` - Topic message
- `https://t.me/channel_name/123?comment=456` - Comment message

---

## 2. Custom Session Timeout (HookSession/HookClient)

Subclass Pyrogram's Session and Client classes to customize the connection timeout.

```python
import pyrogram

class HookSession(pyrogram.session.Session):
    """Hook Session with custom timeout"""

    def start_timeout(self: pyrogram.session.Session, start_timeout: int):
        """Set the start timeout for the session."""
        self.START_TIMEOUT = start_timeout


class HookClient(pyrogram.Client):
    """Hook Client with custom session timeout"""

    START_TIME_OUT = 60  # Default 60 seconds

    def __init__(self, name: str, **kwargs):
        if "start_timeout" in kwargs:
            value = kwargs.get("start_timeout")
            if value:
                self.START_TIME_OUT = value
            kwargs.pop("start_timeout")
        super().__init__(name, **kwargs)

    async def connect(self) -> bool:
        if self.is_connected:
            raise ConnectionError("Client is already connected")

        await self.load_session()

        # Use the custom HookSession
        self.session = HookSession(
            self,
            await self.storage.dc_id(),
            await self.storage.auth_key(),
            await self.storage.test_mode(),
        )
        self.session.start_timeout(self.START_TIME_OUT)

        await self.session.start()
        self.is_connected = True
        return bool(await self.storage.user_id())

    async def start(self):
        is_authorized = await self.connect()
        try:
            if not is_authorized:
                await self.authorize()

            if not await self.storage.is_bot() and self.takeout:
                self.takeout_id = (
                    await self.invoke(
                        pyrogram.raw.functions.account.InitTakeoutSession()
                    )
                ).id

            await self.invoke(pyrogram.raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            self.me = await self.get_me()
            await self.initialize()
            return self
```

**Usage:**

```python
client = HookClient(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    start_timeout=120  # Custom timeout of 120 seconds
)
```

---

## 3. Avoiding Black-Screen Video Uploads

When uploading a video you must provide a thumbnail and the video attributes, otherwise the video may show as a black screen.

### Downloading the video thumbnail

```python
import os
import time
import secrets
import asyncio

async def download_thumbnail(
    client: pyrogram.Client,
    temp_path: str,
    message: pyrogram.types.Message,
):
    """Downloads the thumbnail of a video message to a temporary file."""
    thumbnail_file = None
    if message.video.thumbs:
        thumbnail = message.video.thumbs[0] if message.video.thumbs else None
        unique_name = os.path.join(
            temp_path,
            "thumbnail",
            f"thumb-{int(time.time())}-{secrets.token_hex(8)}.jpg",
        )

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                thumbnail_file = await client.download_media(
                    thumbnail, file_name=unique_name
                )
                # Verify the file size
                if os.path.getsize(thumbnail_file) == thumbnail.file_size:
                    break

                raise ValueError(
                    f"Thumbnail file size mismatch: {os.path.getsize(thumbnail_file)}"
                    f" vs expected {thumbnail.file_size}"
                )
            except Exception as e:
                if attempt == max_attempts:
                    logger.exception(f"Failed to download thumbnail: {e}")
                else:
                    await asyncio.sleep(2)

    return thumbnail_file
```

### Uploading video with full attributes

```python
# Key point: thumb, width, height and duration must all be provided
thumbnail_file = await download_thumbnail(client, temp_save_path, message)

await message.reply_video(
    video_file_path,
    caption=caption,
    thumb=thumbnail_file,              # Thumbnail
    width=message.video.width,         # Video width
    height=message.video.height,       # Video height
    duration=message.video.duration,   # Video duration
    parse_mode=pyrogram.enums.ParseMode.HTML,
)
```

**Notes:**
- Without a thumbnail the video shows as a black screen
- Missing width/height breaks the video preview
- Remember to delete the temporary thumbnail file after uploading

---

## 4. Removing Ads from Messages

Analyze the message entities to extract or filter out ad content while keeping the original formatting.

### MessageProcessor class

```python
import pyrogram

def get_utf16_length(text: str) -> int:
    """Get UTF-16 length of text (Telegram uses UTF-16 for entity offsets)"""
    return len(text.encode('utf-16-le')) // 2

class MessageProcessor:
    """Helper class for processing message captions and entities."""

    def __init__(self, raw_message, filter_str):
        self.raw_message = raw_message
        self.raw_caption = raw_message.caption
        self.filter_str = filter_str
        self.raw_filter_str = pyrogram.parser.utils.add_surrogates(filter_str)
        self.raw_caption_str = pyrogram.parser.utils.add_surrogates(raw_message.caption)
        self.idx = self.raw_caption_str.find(self.raw_filter_str)
        self.start_offset = self.idx
        self.end_offset = self.idx + get_utf16_length(filter_str)
        self.filtered_entities = []

    def process_entities(self):
        """Process and filter message entities."""
        for entity in self.raw_message.caption_entities:
            cur_start_offset = entity.offset
            cur_end_offset = entity.offset + entity.length

            # Check whether the entity falls within the filtered range
            if (
                (cur_start_offset >= self.start_offset and cur_end_offset <= self.end_offset)
                or (cur_start_offset < self.start_offset and cur_end_offset > self.start_offset)
                or (cur_start_offset < self.end_offset and cur_end_offset > self.end_offset)
            ):
                self.filtered_entities.append(entity)

        self.filtered_entities.sort(key=lambda x: x.offset)

    def get_total_span(self):
        """Calculate the total span for text extraction."""
        if self.filtered_entities:
            first_entity = self.filtered_entities[0]
            last_entity = self.filtered_entities[-1]
            return (
                min(self.start_offset, first_entity.offset),
                max(self.end_offset, last_entity.offset + last_entity.length),
            )
        return (self.start_offset, self.end_offset)

    def extract_text(self, total_span):
        """Extract and process text with adjusted entity offsets."""
        text = self.raw_caption[total_span[0]:total_span[1]]
        for entity in self.filtered_entities:
            entity.offset -= total_span[0]
        return pyrogram.parser.Parser.unparse(text, self.filtered_entities, True)
```

### Handling ad replacement

```python
async def proc_replace_advertisement(message_link: str, filter_str: str):
    """Process and replace advertisement content in a message."""
    chat_id, message_id, _ = await parse_link(client, message_link)
    raw_message = await client.get_messages(chat_id, message_id)

    processor = MessageProcessor(raw_message, filter_str)
    processor.process_entities()
    total_span = processor.get_total_span()
    return processor.extract_text(total_span)
```

**How it works:**
1. Parse the message link to get the original message
2. Use filter_str to locate the text region to keep
3. Extract the entities in that region (links, bold, italics, etc.)
4. Reassemble the text, keeping the formatting but dropping the ad section

**Use cases:**
- Removing channel watermarks/ads when forwarding messages
- Keeping the original formatting (links, bold, italics, etc.)
- Adding to the filter list for batch processing

---

## Full Usage Example

```python
import pyrogram

# 1. Client with a custom timeout
client = HookClient(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    start_timeout=120
)

async def main():
    await client.start()

    # 2. Parse the message link
    link = "https://t.me/channel_name/123"
    chat_id, message_id, topic_id = await parse_link(client, link)

    # 3. Fetch the message and download the video
    message = await client.get_messages(chat_id, message_id)

    if message.video:
        # Download the thumbnail to avoid a black screen
        thumbnail = await download_thumbnail(client, "/tmp", message)

        await client.send_video(
            chat_id=destination_chat,
            video=video_path,
            thumb=thumbnail,
            width=message.video.width,
            height=message.video.height,
            duration=message.video.duration,
        )

    # 4. Remove ads
    if message.caption:
        clean_caption = await proc_replace_advertisement(
            link,
            "the part of the content you want"
        )
        print(clean_caption)

    await client.stop()
```
