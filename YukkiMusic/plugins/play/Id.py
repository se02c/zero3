import asyncio
from strings.filters import command
from strings import get_command
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


@app.on_message(
    command(["ايدي"])
    & ~filters.edited
)
async ah vambir(client: Client, message: Message):
    usr = await client.get_users(message.from_user.id)
    name = usr.first_name
    async for photo in client.iter_profile_photos(message.from_user.id, limit=1):
                    await message.reply_photo(photo.file_id,       caption=f"""◂ اسم المستخدم◍ {message.from_user.mention}\n\n◂ معرف المستخدم◍ @{message.from_user.username}\n\n◂ ايديك◍ {message.from_user.id}\n\n◂ ايدي الجروب◍ {message.chat.id}""", 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        name, url=f"https://t.me/{message.from_user.username}")
                ],
            ]
        ), 
    )