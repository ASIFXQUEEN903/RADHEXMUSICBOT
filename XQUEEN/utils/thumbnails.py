import os, re, aiohttp, aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL
from XQUEEN import app

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

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        search = VideosSearch(url, limit=1)
        results = (await search.next())["result"][0]

        title = re.sub(r"\W+", " ", results.get("title", "No Title")).title()
        duration = results.get("duration", "00:00")
        thumbnail_url = results["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/tmp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Load images
        raw_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        template = Image.open("XQUEEN/assets/thum.png").convert("RGBA")
        final_img = Image.new("RGBA", template.size, (0, 0, 0, 255))

        # Step 1: Blurred background
        bg = raw_thumb.resize(template.size).filter(ImageFilter.GaussianBlur(10))
        final_img.paste(bg, (0, 0))

        # Step 2: Crop square from center
        width, height = raw_thumb.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        thumb_crop = raw_thumb.crop((left, top, left + min_dim, top + min_dim))

        # Step 3: Resize to fill left side (square)
        left_img_size = 460  # size of the square image
        thumb_square = thumb_crop.resize((left_img_size, left_img_size))
        final_img.paste(thumb_square, (50, 150))  # Adjust as needed

        # Step 4: Paste overlay template (with icons/buttons etc.)
        final_img.paste(template, (0, 0), mask=template)

        # Step 5: Add text
        draw = ImageDraw.Draw(final_img)
        font_title = ImageFont.truetype("XQUEEN/assets/font.ttf", 45)
        font_tag = ImageFont.truetype("XQUEEN/assets/font2.ttf", 25)

        draw.text((600, 70), clear(title), fill="white", font=font_title)
        draw.text((600, 360), f"00:00 / {duration}", fill="white", font=font_tag)
        draw.text((600, 420), "XQUEEN SERVER", fill="white", font=font_tag)

        # Save and cleanup
        final_img.convert("RGB").save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] - {e}")
        return YOUTUBE_IMG_URL
