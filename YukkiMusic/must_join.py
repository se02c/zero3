from config.config import MUST_JOIN
from YukkiMusic import app
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden


@app.on_message(filters.incoming & filters.group & ~filters.edited)
async def must_join_channel(bot: Client, msg: Message):
    if not MUST_JOIN:  # Not compulsory
        return
    try:
        try:
            await bot.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await bot.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"🗽يجب ان تشترك في قناة السورس⬇️\n [🔮𝐒𝐎𝐔𝐑𝐂𝐄 𝐕𝘼𝙈𝘽𝙄𝙍🔮]({link})\n 🖥¦حتي تتمكن من استخدامي\n◍ اشترك ثم اضغط /play مره اخري√\n\nBy ||[ᯓ˹ 𝐕𝘼𝙈𝘽𝙄𝙍𖣥⃟⃟⃟⃟⃟🇵🇸فمـبــيرـ͢）⛧](https://t.me/XxlllllllllllllllllllllllllllxX)||",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("اضـغط هنا للأشتـراك بالـقـنـاه✅", url=link)]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"انا لست ادمن في قناه/جروب اشتراك الاجباري: {MUST_JOIN} !")
