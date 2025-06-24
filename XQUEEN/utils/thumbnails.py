import os, aiohttp, aiofiles
from PIL import Image, ImageFilter
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL


async def get_thumb(videoid):
    output_path = f"cache/{videoid}.png"
    if os.path.exists(output_path):
        return output_path

    try:
        # Step 1: Get thumbnail URL from YouTube
        search = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        result = (await search.next())["result"][0]
        thumb_url = result["thumbnails"][0]["url"].split("?")[0]

        # Step 2: Download YouTube thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/tmp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Step 3: Load thum.png (overlay) and get its size
        overlay_path = "XQUEEN/assets/thum.png"
        overlay = Image.open(overlay_path).convert("RGBA")
        width, height = overlay.size

        # Step 4: Open downloaded YouTube thumb and make blurred bg
        yt_thumb = Image.open(f"cache/tmp_{videoid}.png").convert("RGB")
        bg = yt_thumb.resize((width, height)).filter(ImageFilter.GaussianBlur(4))

        # Step 5: Combine blurred background and overlay
        final = Image.alpha_composite(bg.convert("RGBA"), overlay)

        # Step 6: Save final result
        final.save(output_path)
        os.remove(f"cache/tmp_{videoid}.png")
        return output_path

    except Exception as e:
        print(f"[THUMB ERROR] {e}")
        return YOUTUBE_IMG_URL
