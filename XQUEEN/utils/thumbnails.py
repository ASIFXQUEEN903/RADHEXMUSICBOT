import os, aiohttp, aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL


def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + " " + word if line else word
        if font.getlength(test_line) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
        if len(lines) == 2:  # Only 2 lines max
            break
    if line and len(lines) < 2:
        lines.append(line)
    return lines


async def get_thumb(videoid):
    output_path = f"cache/{videoid}.png"
    if os.path.exists(output_path):
        return output_path

    try:
        # Step 1: Get video details
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

        # Step 3: Load overlay and get size
        overlay_path = "XQUEEN/assets/thum.png"
        overlay = Image.open(overlay_path).convert("RGBA")
        width, height = overlay.size

        # Step 4: Blur background
        yt_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        bg = yt_thumb.resize((width, height)).filter(ImageFilter.GaussianBlur(4))

        # Step 5: Combine background and overlay
        final = Image.alpha_composite(bg.convert("RGBA"), overlay)

        # Step 6: Add title (blue, small, 2 lines max, right side)
        draw = ImageDraw.Draw(final)
        try:
            font = ImageFont.truetype("XQUEEN/assets/font.ttf", 22)
        except:
            font = ImageFont.load_default()

        # Wrap text (2 lines max)
        max_text_width = width - 450  # Space from right to left safe area
        wrapped_lines = wrap_text(title, font, max_text_width)

        # Draw lines (top-right, a little below top padding)
        text_x = width - 20
        text_y = 20
        line_spacing = 30
        for line in wrapped_lines:
            draw.text((text_x, text_y), line, font=font, fill="blue", anchor="ra")
            text_y += line_spacing

        # Step 7: Save final image
        final.save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] {e}")
        return YOUTUBE_IMG_URL
