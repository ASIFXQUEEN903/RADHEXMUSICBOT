from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS
from XQUEEN import app, YouTube
from XQUEEN.utils import time_to_seconds
from XQUEEN.utils.stream.stream import stream
import config


@app.on_message(filters.command("903play") & filters.group & ~BANNED_USERS)
async def auto_play_903_links(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🎧 Please send a YouTube playlist link after `/903play`.")

    url = message.text.strip().split(None, 1)[1]

    if "youtube.com/playlist" not in url and "youtu.be" not in url:
        return await message.reply_text("❌ Invalid YouTube playlist link.")

    status = await message.reply_text("📥 Fetching playlist info...")
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    try:
        playlist_links = await YouTube.playlist(
            url,
            config.PLAYLIST_FETCH_LIMIT,
            user_id,
        )
    except Exception as e:
        return await status.edit_text(f"❌ Failed to fetch playlist:\n`{str(e)}`")

    if not playlist_links or len(playlist_links) == 0:
        return await status.edit_text("⚠️ Playlist is empty or could not be fetched.")

    for idx, link in enumerate(playlist_links, start=1):
        try:
            details, track_id = await YouTube.track(link)
            title = details["title"]
            thumb = details["thumb"]
            duration = details["duration_min"]
            duration_sec = time_to_seconds(duration)

            if duration_sec > config.DURATION_LIMIT:
                await message.reply_text(
                    f"⚠️ Skipping '{title}' — exceeds {config.DURATION_LIMIT_MIN} minutes limit."
                )
                continue

            await stream(
                _=None,
                message=status,
                user_id=user_id,
                details=details,
                chat_id=chat_id,
                name=user_name,
                original_chat_id=chat_id,
                streamtype="youtube",
                video=False,
                forceplay=False,
            )

            await status.edit_text(f"▶️ Playing {idx}/{len(playlist_links)}: {title}")
        except Exception as err:
            await message.reply_text(f"⚠️ Error playing track {idx}: `{str(err)}`")

    await status.edit_text("✅ All playlist songs processed.")
