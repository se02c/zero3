import asyncio
from pyrogram import Client, filters
from strings import get_command
from strings.filters import command
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from YukkiMusic import (Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app)
from typing import Union
from pyrogram.types import InlineKeyboardButton

from config import GITHUB_REPO, SUPPORT_CHANNEL, SUPPORT_GROUP
from YukkiMusic import app
from config import BANNED_USERS, MUSIC_BOT_NAME

import re
import sys
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

BOT_USERNAME = getenv("BOT_USERNAME")


@app.on_message(
    command(["زيرو","سورس","السورس","source","يا سورس"])
    & ~filters.edited
)
async def khalid(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://t.me/XTIORY",
        caption=f"""╭──── • ◈ • ────╮\n么 [𝚂𝙾𝚄𝚁𝙲𝙴 𝚉𝙴𝚁𝙾](https://t.me/abogram) 𖠲\n么 [𝙰𝙺 𝚃𝙾 𝙼𝙴](https://t.me/abogram) 𖠲\n么 [Abdo Asil...🤍](https://t.me/ttccss) 𖠲\n╰──── • ◈ • ────╯\⍟ 𝚃𝙷𝙴 𝙱𝙴𝚂𝚃 𝚂𝙾𝚄𝚁𝙲𝙴 𝙾𝙽 𝚃𝙴𝙻𝙴𝙶𝚁𝙰𝙼""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Abdo Asil...🤍", url=f"https://t.me/ttccss"), 
                ],[
                    InlineKeyboardButton(
                        "• 𝙎𝙊𝙐𝙍𝘾𝙀 𝙕𝙀𝙍𝙊 •⚡️", url=f"https://t.me/XTIORY"),
                ],[
                    InlineKeyboardButton(
                        "اضغط لاضافه البوت لمجموعتك✅.", url=f"https://t.me/Rep0obot?startgroup=true"),
                ],

            ]

        ),

    )
