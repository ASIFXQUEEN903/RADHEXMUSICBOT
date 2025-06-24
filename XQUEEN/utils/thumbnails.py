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

        # Load base images
        raw_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        template = Image.open("XQUEEN/assets/thum.png").convert("RGBA")
        final_img = Image.new("RGBA", template.size, (0, 0, 0, 255))

        # Step 1: Blurred background
        bg = raw_thumb.resize(template.size).filter(ImageFilter.GaussianBlur(10))
        final_img.paste(bg, (0, 0))

        # Step 2: Dark overlay
        overlay = Image.new("RGBA", final_img.size, (0, 0, 0, 100))
        final_img = Image.alpha_composite(final_img, overlay)

        # Step 3: Crop center square from raw image
        width, height = raw_thumb.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        thumb_crop = raw_thumb.crop((left, top, left + min_dim, top + min_dim))

        # Step 4: Resize and place thumbnail
        left_img_size = 460  # Big enough to fill top-left empty region
        thumb_square = thumb_crop.resize((left_img_size, left_img_size))

        # Position for top-left region
        thumb_x = 80
        thumb_y = 40

        # Optional shadow behind image
        shadow = Image.new("RGBA", (left_img_size + 20, left_img_size + 20), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle((10, 10, left_img_size + 10, left_img_size + 10), fill=(0, 0, 0, 120))
        final_img.paste(shadow, (thumb_x - 10, thumb_y - 10), shadow)

        # Paste thumbnail
        final_img.paste(thumb_square, (thumb_x, thumb_y))

        # Step 5: Paste AirPods template overlay
        final_img.paste(template, (0, 0), mask=template)

        # Step 6: Draw text beside thumbnail
        draw = ImageDraw.Draw(final_img)
        font_title = ImageFont.truetype("XQUEEN/assets/font.ttf", 45)
        font_tag = ImageFont.truetype("XQUEEN/assets/font2.ttf", 25)

        text_x = thumb_x + left_img_size + 30
        draw.text((text_x, thumb_y + 10), clear(title), fill="white", font=font_title)
        draw.text((text_x, thumb_y + 80), f"00:00 / {duration}", fill="white", font=font_tag)
        draw.text((text_x, thumb_y + 130), "XQUEEN SERVER", fill="white", font=font_tag)

        # Step 7: Save and cleanup
        final_img.convert("RGB").save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] - {e}")
        return YOUTUBE_IMG_URL
