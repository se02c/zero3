from functools import wraps
from config.config import MUST_JOIN
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

CAPTION_BTN = InlineKeyboardMarkup(
            [[InlineKeyboardButton("اضـغط هنا للأشتـراك بالـقـنـاه✅", url="https://t.me/{MUST_JOIN}")]])

def must_join_channel(func):
    @wraps(func)
    async def sz_message(_, bot: Client, msg: message):
        try:
            await bot.get_chat_member(MUST_JOIN, msg.from_user.id)
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await bot.get_chat(MUST_JOIN)
                link = chat_info.invite_link
        except UserNotParticipant:
            return await message.reply_text(
            text="""
🗽يجب ان تشترك في قناة السورس⬇️\n\n [⚙¦ قنــاة الســورس️](https://t.me/{MUST_JOIN})\n 🖥¦حتي تتمكن من استخدامي\n◍ اشترك ثم اضغط « /play والاغنيه» مره اخري√\n\n🌐¦ By ||[ᯓ˹ 𝐕𝘼𝙈𝘽𝙄𝙍𖣥⃟⃟⃟⃟⃟🇵🇸فمـبــيرـ͢）⛧](https://t.me/XxlllllllllllllllllllllllllllxX)||
            """,
            reply_markup=CAPTION_BTN,
            disable_web_page_preview=True) 
        return await func(_, message)    
    return sz_message
