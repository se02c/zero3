import asyncio
from pyrogram import Client, filters
from strings import get_command
from strings.filters import command
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from YukkiMusic import (Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app)


@app.on_message(
     command(["المطور","سيزر","المبرمج"])
    & ~filters.edited
)
async def khalid(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://t.me/XxlllllllllllllllllllllllllllxX",
        caption=f"""◍ الزرار الاول: قناه السورس \n◍ الزرار الثاني: هو مبرمج السورس\n√""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                InlineKeyboardButton(
                    "• 𝙎𝙊𝙐𝙍𝘾𝙀 𝙕𝙀𝙍𝙊 •⚡️", url=f"https://t.me/abogram"
                ),
                ],
                [
                    InlineKeyboardButton(
                        "Abdo Asil...🤍", url=f"https://t.me/ttccss"),
                ],
            ]
        ),
    )
