import os, aiohttp, aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL


async def get_thumb(videoid):
    output_path = f"cache/{videoid}.png"
    if os.path.exists(output_path):
        return output_path

    try:
        # Step 1: Get thumbnail URL & title
        search = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        result = (await search.next())["result"][0]
        thumb_url = result["thumbnails"][0]["url"].split("?")[0]
        title = result.get("title", "No Title")

        # Step 2: Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/tmp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Step 3: Load overlay template
        overlay_path = "XQUEEN/assets/thum.png"
        overlay = Image.open(overlay_path).convert("RGBA")
        width, height = overlay.size

        # Step 4: Load thumbnail and blur it
        yt_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        bg = yt_thumb.resize((width, height)).filter(ImageFilter.GaussianBlur(4))

        # Step 5: Combine blurred background with overlay
        final = Image.alpha_composite(bg.convert("RGBA"), overlay)

        # Step 6: Draw video title on the image (top-right side)
        draw = ImageDraw.Draw(final)
        try:
            font = ImageFont.truetype("XQUEEN/assets/font.ttf", 28)
        except:
            font = ImageFont.load_default()

        # Text wrapping (max length control)
        if len(title) > 55:
            title = title[:52] + "..."

        # Draw title at top-right with padding
        text_x = width - 20
        text_y = 15
        draw.text((text_x, text_y), title, font=font, fill="white", anchor="ra")  # right aligned

        # Step 7: Save final output
        final.save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] {e}")
        return YOUTUBE_IMG_URL
