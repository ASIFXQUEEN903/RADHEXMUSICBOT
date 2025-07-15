from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from XQUEEN import app


@app.on_message(filters.command("repo"))
async def help(client: Client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/ieqq3j.jpg",
        caption="""
𓆩🍁𓆪 𝐇𝐞𝐲 𝐁𝐚𝐛𝐲 💞

 𓆩 𝐐𝐔𝐄𝐄𝐍 𝐊𝐀 𝐎𝐅𝐅𝐈𝐂𝐀𝐋 𝐑𝐄𝐏𝐎 𓆪
𓆩 399 ᴘᴀʏᴍᴇɴᴛ ᴋᴀʀᴋᴇ @ASHLF903 ᴀꜱᴋ ꜰᴏʀ ʀᴇᴘᴏ 𓆪
        """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "𓆩⚡ 𝘼𝙎𝙆 𝙁𝙊𝙍 ⚡𓆪", url="https://t.me/ASHLF903"
                    )
                ]
            ]
        ),
    )


__MODULE__ = "Sᴏᴜʀᴄᴇ"
__HELP__ = """
## 🌀 Rᴇᴘᴏ Mᴏᴅᴜʟᴇ

➤ `/repo` – Get the stylish source code repo of this bot.
"""
