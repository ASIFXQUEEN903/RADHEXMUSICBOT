import os, re, aiohttp, aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL


def clear(text):
    result = ""
    for word in text.split():
        if len(result) + len(word) < 60:
            result += " " + word
    return result.strip()


async def get_thumb(videoid):
    output_path = f"cache/{videoid}.png"
    if os.path.exists(output_path):
        return output_path

    try:
        search = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        result = (await search.next())["result"][0]

        title = re.sub(r"\W+", " ", result.get("title", "No Title")).title()
        duration = result.get("duration", "00:00")
        thumb_url = result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/tmp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Load assets
        template = Image.open("XQUEEN/assets/thum.png").convert("RGBA")  # 1280x720
        yt_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        final = Image.new("RGBA", template.size)

        # Background blur
        bg = yt_thumb.resize((1280, 720)).filter(ImageFilter.GaussianBlur(12))
        final.paste(bg, (0, 0))

        # Circular crop inside ring
        crop_size = 390
        thumb = yt_thumb.resize((crop_size, crop_size))
        mask = Image.new("L", (crop_size, crop_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, crop_size, crop_size), fill=255)
        thumb.putalpha(mask)
        final.paste(thumb, (105, 165), mask=thumb)  # circle aligned

        # Paste UI overlay
        final.paste(template, (0, 0), mask=template)

        # Fonts
        font_title = ImageFont.truetype("XQUEEN/assets/font.ttf", 50)
        font_small = ImageFont.truetype("XQUEEN/assets/font2.ttf", 25)

        # Text elements
        draw = ImageDraw.Draw(final)
        draw.text((530, 20), clear(title), fill="white", font=font_title)                       # Title
        draw.text((530, 350), f"00:00 / {duration}", fill="white", font=font_small)             # Duration
        draw.text((1200, 690), "XQUEEN SERVER", fill="white", font=font_small, anchor="rd")     # Server Tag

        # Save final image
        final.convert("RGB").save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] {e}")
        return YOUTUBE_IMG_URL
