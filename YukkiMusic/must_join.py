from functools import wraps
from config.config import MUST_JOIN, CH_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant


CAPTION_BTN = InlineKeyboardMarkup(
            [[InlineKeyboardButton("اضـغط هنا للأشتـراك بالـقـنـاه✅", url="https://t.me/{MUST_JOIN}")]])

def must_join_channel(func):
    @wraps(func)
    async def sz_message(_, message):
        try:
            await message._client.get_chat_member(-{CH_ID}, message.from_user.id)
        except UserNotParticipant:
            return await message.reply_text(
            text="""
🗽يجب ان تشترك في قناة السورس⬇️\n [🔮𝐒𝐎𝐔𝐑𝐂𝐄 𝐕𝘼𝙈𝘽𝙄𝙍🔮](https://t.me/{MUST_JOIN})\n 🖥¦حتي تتمكن من استخدامي\n◍ اشترك ثم اضغط /play مره اخري√\n\nBy ||[ᯓ˹ 𝐕𝘼𝙈𝘽𝙄𝙍𖣥⃟⃟⃟⃟⃟🇵🇸فمـبــيرـ͢）⛧](https://t.me/XxlllllllllllllllllllllllllllxX)||
            """,
            reply_markup=CAPTION_BTN,
            disable_web_page_preview=True) 
        return await func(_, message)    
    return sz_message
