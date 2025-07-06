import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from pyrogram import Client
from pyrogram.types import Message
from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis

async def download_user_dp(client: Client, message: Message, save_path: str) -> str:
    try:
        photos = await client.get_profile_photos(message.from_user.id, limit=1)
        if photos.total_count > 0:
            await client.download_media(photos[0].file_id, file_name=save_path)
            return save_path
    except Exception as e:
        print("DP Download Failed:", e)
    return None

def paste_dp_circle(bg: Image.Image, dp_path: str, x: int, y: int, size: int = 48):
    if os.path.exists(dp_path):
        dp = Image.open(dp_path).resize((size, size)).convert("RGBA")
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        bg.paste(dp, (x, y), mask)

async def get_thumb(client: Client, message: Message, videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_with_dp.png")
    if os.path.exists(cache_path):
        return cache_path

    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        results_data = await results.next()
        data = results_data["result"][0]
        title = re.sub(r"\W+", " ", data.get("title", "No Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except:
        title, thumbnail, duration, views = "No Title", YOUTUBE_IMG_URL, None, "Unknown Views"

    is_live = not duration or str(duration).lower() in {"", "live", "live now"}
    duration_text = "Live" if is_live else duration or "Unknown"

    # Download thumbnail
    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception as e:
        print("Thumbnail download error:", e)
        return None

    # Open and prepare background
    try:
        base = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")
    except:
        return None

    bg = ImageEnhance.Brightness(base.filter(ImageFilter.BoxBlur(10))).enhance(0.6)

    # Draw info panel
    draw = ImageDraw.Draw(bg)
    try:
        title_font = ImageFont.truetype("XQUEEN/assets/font2.ttf", 32)
        reg_font = ImageFont.truetype("XQUEEN/assets/font.ttf", 18)
    except:
        title_font = reg_font = ImageFont.load_default()

    panel_x, panel_y = 250, 120
    draw.rounded_rectangle((panel_x, panel_y, 1030, 600), 40, fill=(255,255,255,180))

    # Paste thumbnail with mask
    thumb = base.resize((500, 270))
    mask = Image.new("L", thumb.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 500, 270), 20, fill=255)
    bg.paste(thumb, (390, 150), mask)

    # Draw text
    draw.text((390, 440), trim_to_width(title, title_font, 480), font=title_font, fill="black")
    draw.text((390, 480), f"YouTube | {views}", font=reg_font, fill="black")
    draw.text((390, 510), "00:00", font=reg_font, fill="black")
    draw.text((800, 510), duration_text, font=reg_font, fill="red" if is_live else "black")

    # Draw red bar
    draw.line([(390, 500), (670, 500)], fill="red", width=6)
    draw.line([(670, 500), (870, 500)], fill="gray", width=5)
    draw.ellipse([(663, 493), (677, 507)], fill="red")

    # Paste user DP
    dp_path = os.path.join(CACHE_DIR, f"{message.from_user.id}_dp.jpg")
    await download_user_dp(client, message, dp_path)
    paste_dp_circle(bg, dp_path, 650, 470, 48)

    try:
        os.remove(thumb_path)
    except:
        pass

    bg.save(cache_path)
    return cache_path
