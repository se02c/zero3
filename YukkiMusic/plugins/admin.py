import asyncio
import re

from time import time
from pyrogram.errors import FloodWait
from strings.filters import command
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChatPermissions,
    Message,
)

from YukkiMusic import BOT_ID, SUDOERS, app, log
from YukkiMusic.core.errors import capture_err
from YukkiMusic.core.keyboard import ikb
from YukkiMusic.utils.dbfunctions import (
    add_warn,
    get_warn,
    int_to_alpha,
    remove_warns,
    save_filter,
)
from YukkiMusic.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)

__MODULE__ = "Admin"
__HELP__ = """/ban - Ban A User
/dban - Delete the replied message banning its sender
/tban - Ban A User For Specific Time
/unban - Unban A User
/listban - Ban a user from groups listed in a message
/listunban - Unban a user from groups listed in a message
/warn - Warn A User
/dwarn - Delete the replied message warning its sender
/rmwarns - Remove All Warning of A User
/warns - Show Warning Of A User
/kick - Kick A User
/dkick - Delete the replied message kicking its sender
/purge - Purge Messages
/purge [n] - Purge "n" number of messages from replied message
/del - Delete Replied Message
/promote - Promote A Member
/fullpromote - Promote A Member With All Rights
/demote - Demote A Member
/pin - Pin A Message
/mute - Mute A User
/tmute - Mute A User For Specific Time
/unmute - Unmute A User
/ban_ghosts - Ban Deleted Accounts
/report | @admins | @admin - Report A Message To Admins.
/admincache - Reload admin list"""


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    try:
        member = await app.get_chat_member(chat_id, user_id)
    except Exception:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms


from YukkiMusic.core.permissions import adminsOnly

admins_in_chat = {}


async def list_admins(chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in app.iter_chat_members(
                chat_id, filter="administrators"
            )
        ],
    }
    return admins_in_chat[chat_id]["data"]


# Admin cache reload


@app.on_chat_member_updated()
async def admin_cache_func(_, cmu: ChatMemberUpdated):
    if cmu.old_chat_member and cmu.old_chat_member.promoted_by:
        admins_in_chat[cmu.chat.id] = {
            "last_updated_at": time(),
            "data": [
                member.user.id
                async for member in app.iter_chat_members(
                    cmu.chat.id, filter="administrators"
                )
            ],
        }
        log.info(f"Updated admin cache for {cmu.chat.id} [{cmu.chat.title}]")


# Purge Messages


@app.on_message(command("مسح") & ~filters.edited & ~filters.private)
@adminsOnly("can_delete_messages")
async def purgeFunc(_, message: Message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text("◍ برجاء الرد علي الرساله لحذفها √")

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.message_id + int(cmd[1])
        if purge_to > message.message_id:
            purge_to = message.message_id
    else:
        purge_to = message.message_id   

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
            repliedmsg.message_id,
            purge_to,
    ):
        message_ids.append(message_id)

        # Max message deletion limit is 100
        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,  # For both sides
            )

            # To delete more than 100 messages, start again
            message_ids = []

    # Delete if any messages left
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )


# Kick members


@app.on_message(
    command(["اطرده", "طرد"]) & ~filters.edited & ~filters.private
)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("◍ لا استطيع الوصول لايدي هذا العضو √")
    if user_id == BOT_ID:
        return await message.reply_text(
            "◍ لا استطيع طرد نفسي, استطيع المغادره اذا ارد √"
        )
    if user_id in SUDOERS:
        return await message.reply_text("◍ هل انت متأكد انك تريد طرد هذا المستخدم؟ ")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "◍ لا استطيع طرد الادمن انت تعرف القوانين √"
        )
    mention = (await app.get_users(user_id)).mention
    msg = f"""
**◍ تم طرد هذا العضو:** {mention}
**بواسطة:** {message.from_user.mention if message.from_user else 'Anon'}
**السبب:** {reason or 'No Reason Provided.'}"""
    if message.command[0][0] == "ا":
        await message.reply_to_message.delete()
    await message.chat.ban_member(user_id)
    await message.reply_text(msg)
    await asyncio.sleep(1)
    await message.chat.unban_member(user_id)


# Ban members


@app.on_message(
    command(["حظر", "احظره", "حظرلمده"])
    & ~filters.edited
    & ~filters.private
)
@adminsOnly("can_restrict_members")
async def banFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text("◍ لا استطيع الوصول لايدي هذا العضو √")
    if user_id == BOT_ID:
        return await message.reply_text(
            "◍ لا استطيع حظر نفسي, استطيع المغادره اذا ارد √"
        )
    if user_id in SUDOERS:
        return await message.reply_text(
            "◍ لا استطيع حظر نفسي, استطيع المغادره اذا ارد √"
        )
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "◍ لا استطيع طرد الادمن انت تعرف القوانين √"
        )

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )

    msg = (
        f"**◍ تم حظر هذا العضو:** {mention}\n"
        f"**بواسطه:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0][0] == "ا":
        await message.reply_to_message.delete()
    if message.command[0] == "حظرلمده":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"**◍ تم حظره لمدة:** {time_value}\n"
        if temp_reason:
            msg += f"**السبب:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                await message.reply_text(msg)
            else:
                await message.reply_text("◍ لا تسطيع وضع المده اكثر من 99 √")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**السبب:** {reason}"
    await message.chat.ban_member(user_id)
    await message.reply_text(msg)


# Unban members


@app.on_message(command("الغاءحظر") & ~filters.edited & ~filters.private)
@adminsOnly("can_restrict_members")
async def unban_func(_, message: Message):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text("◍ لاتستطيع الغاء حظر القناه √")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await message.reply_text(
            "◍ قم بكتابه يوزر الامر مع يوزر العضو او بالرد علي رساله للعضو لالغاء حظره √"
        )
    await message.chat.unban_member(user)
    umention = (await app.get_users(user)).mention
    await message.reply_text(f"Unbanned! {umention}")


# Ban users listed in a message


@app.on_message(
    SUDOERS & command("المحظورين") & ~filters.edited & ~filters.private
)
async def list_ban_(c, message: Message):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text(
            "◍ قم بإعطاء ايدي ويوزر الشخص مع رابط الرساله وسبب قايمه الحظر √"
        )
    if (
        len(msglink_reason.split(" ")) == 1
    ):  # message link included with the reason
        return await message.reply_text(
            "◍ يجب ان تعطي سبب لقايمة المحظورين"
        )
    # seperate messge link from reason
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", messagelink
    ):  # validate link
        return await message.reply_text("◍ عفوا قمت بإعطاء رابط رساله خطأ √")

    if userid == BOT_ID:
        return await message.reply_text("◍ لا استطيع حظر نفسي √")
    if userid in SUDOERS:
        return await message.reply_text(
            "◍ هل انت متأكد من انك تريد حظر هذا الشخص √"
        )
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(
        "`حظر المستخدم من مجموعات متعددة.\
         هذا قد يستغرق بعض الوقت`"
    )
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall("@\w+", msgtext)
    except:
        return await m.edit_text("◍ لا استطيع الوصول ليوزر الجروب")
    count = 0
    for username in gusernames:
        try:
            await app.ban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention

    msg = f"""
**◍ قايمة المحظورين:** {mention}
**المحظورين:** `{userid}`
**الادمن:** {message.from_user.mention}
**الجروبات المتفاعله:** `{count}`
**السبب:** {reason}
"""
    await m.edit_text(msg)


# Unban users listed in a message


@app.on_message(
    SUDOERS & command("الملغاه") & ~filters.edited & ~filters.private
)
async def list_unban_(c, message: Message):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text(
            "◍ قم بإعطاء ايدي ويوزر الشخص مع رابط الرساله وسبب قايمه الملغاه √"
        )

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", msglink
    ):  # validate link
        return await message.reply_text("◍ رابط الرساله خطأ √")

    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(
        "`الغاء حظر هذا المستخدم من الجروبات المتعدده. \
         ربما يأخد بعض الوقت`"
    )
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall("@\w+", msgtext)
    except:
        return await m.edit_text("◍ لا استطيع الوصول ليوزر المجموعه √")
    count = 0
    for username in gusernames:
        try:
            await app.unban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention
    msg = f"""
**قايمة الملغي حظرهم:** {mention}
**الملغي حظرهم:** `{userid}`
**الادمن:** {message.from_user.mention}
**الجروبات المتفاعله:** `{count}`
"""
    await m.edit_text(msg)


# Delete messages


@app.on_message(command("حذف") & ~filters.edited & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("◍ قم بالرد علي الرساله لحذفها √")
    await message.reply_to_message.delete()
    await message.delete()


# Promote Members


@app.on_message(
    command(["رفع/مشرف", "مشرف/كامل"])
    & ~filters.edited
    & ~filters.private
)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message: Message):
    user_id = await extract_user(message)
    umention = (await app.get_users(user_id)).mention
    if not user_id:
        return await message.reply_text("◍ لا استطيع ايجاد ايدي المستخدم √")
    bot = await app.get_chat_member(message.chat.id, BOT_ID)
    if user_id == BOT_ID:
        return await message.reply_text("◍ لا استطيع رفع نفسي مشرف √")
    if not bot.can_promote_members:
        return await message.reply_text("◍ عفوا لا املك صلاحيات كامله √")
    if message.command[0][0] == "م":
        await message.chat.promote_member(
            user_id=user_id,
            can_change_info=bot.can_change_info,
            can_invite_users=bot.can_invite_users,
            can_delete_messages=bot.can_delete_messages,
            can_restrict_members=bot.can_restrict_members,
            can_pin_messages=bot.can_pin_messages,
            can_promote_members=bot.can_promote_members,
            can_manage_chat=bot.can_manage_chat,
            can_manage_voice_chats=bot.can_manage_voice_chats,
        )
        return await message.reply_text(f"◍ تم رفعه مشرف كامل √ {umention}")

    await message.chat.promote_member(
        user_id=user_id,
        can_change_info=False,
        can_invite_users=bot.can_invite_users,
        can_delete_messages=bot.can_delete_messages,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_chat=bot.can_manage_chat,
        can_manage_voice_chats=bot.can_manage_voice_chats,
    )
    await message.reply_text(f"◍ تم رفعه مشرف بنجاح √ {umention}")


# Demote Member


@app.on_message(command("مميز") & ~filters.edited & ~filters.private)
@adminsOnly("can_promote_members")
async def demote(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("◍ لا استطيع ايجاد ايدي المستخدم √")
    if user_id == BOT_ID:
        return await message.reply_text("◍ لا استطيع رفع نفسي مميز √")
    if user_id in SUDOERS:
        return await message.reply_text(
            "◍ هل انت متأكد من انك تريد رفع هذا الشخص √"
        )
    await message.chat.promote_member(
        user_id=user_id,
        can_change_info=False,
        can_invite_users=False,
        can_delete_messages=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
        can_manage_chat=False,
        can_manage_voice_chats=False,
    )
    umention = (await app.get_users(user_id)).mention
    await message.reply_text(f"◍ تم رفعه مميز بنجاح √ {umention}")


# Pin Messages


@app.on_message(
    command(["تنظيف", "unpin"]) & ~filters.edited & ~filters.private
)
@adminsOnly("can_pin_messages")
async def pin(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to pin/unpin it.")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await message.reply_text(
            f"**Unpinned [this]({r.link}) message.**",
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=True)
    await message.reply(
        f"**Pinned [this]({r.link}) message.**",
        disable_web_page_preview=True,
    )
    msg = "Please check the pinned message: ~ " + f"[Check, {r.link}]"
    filter_ = dict(type="text", data=msg)
    await save_filter(message.chat.id, "~pinned", filter_)


# Mute members


@app.on_message(
    command(["كتم", "اكتمه"]) & ~filters.edited & ~filters.private
)
@adminsOnly("can_restrict_members")
async def mute(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("◍ لا استطيع ايجاد ايدي المستخدم √")
    if user_id == BOT_ID:
        return await message.reply_text("◍ لا استطيع كتم نفسي √.")
    if user_id in SUDOERS:
        return await message.reply_text(
            "◍ هل انت متأكد من انك تريد كتم هذا الشخص √!"
        )
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "◍ لا استطيع كتم الادمن انت تعرف القوانين √"
        )
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨   الغاء كتمه   🚨": f"unmute_{user_id}"})
    msg = (
        f"**◍ تم كتم هذا العضو:** {mention}\n"
        f"**بواسطة:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0] == "اكتمه":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"**◍ تم كتمه لمده:** {time_value}\n"
        if temp_reason:
            msg += f"**السبب:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text("◍ لاتسطيع كتمه اكثر من 99")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**السبب:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    await message.reply_text(msg, reply_markup=keyboard)


# Unmute members


@app.on_message(command("الغاءكتم") & ~filters.edited & ~filters.private)
@adminsOnly("can_restrict_members")
async def unmute(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("◍ لا استطيع ايجاد ايدي المستخدم √")
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    await message.reply_text(f"◍ تم الغاء كتمه بنجاح √ {umention}")


# Ban deleted accounts


@app.on_message(
    command("ban_ghosts")
    & ~filters.private
    & ~filters.edited
)
@adminsOnly("can_restrict_members")
async def ban_deleted_accounts(_, message: Message):
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    m = await message.reply("Finding ghosts...")

    async for i in app.iter_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
            except Exception:
                pass
            banned_users += 1
        await m.edit(f"Banned {banned_users} Deleted Accounts")
    else:
        await m.edit("There are no deleted accounts in this chat")


@app.on_message(
    filters.command(["warn", "dwarn"]) & ~filters.edited & ~filters.private
)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == BOT_ID:
        return await message.reply_text(
            "I can't warn myself, i can leave if you want."
        )
    if user_id in SUDOERS:
        return await message.reply_text(
            "You Wanna Warn The Elevated One?, RECONSIDER!"
        )
    if user_id in (await list_admins(chat_id)):
        return await message.reply_text(
            "I can't warn an admin, You know the rules, so do i."
        )
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  Remove Warn  🚨": f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(
            f"Number of warns of {mention} exceeded, BANNED!"
        )
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
**Warned User:** {mention}
**Warned By:** {message.from_user.mention if message.from_user else 'Anon'}
**Reason:** {reason or 'No Reason Provided.'}
**Warns:** {warns + 1}/3"""
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n"
            + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("User has no warnings.")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__Warn removed by {from_user.mention}__"
    await cq.message.edit(text)


# Rmwarns


@app.on_message(
    filters.command("rmwarns") & ~filters.edited & ~filters.private
)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a message to remove a user's warnings."
        )
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"{mention} have no warnings.")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"Removed warnings of {mention}.")


# Warns


@app.on_message(filters.command("warns") & ~filters.edited & ~filters.private)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(f"{mention} has no warnings.")
    return await message.reply_text(f"{mention} has {warns}/3 warnings.")


# Report


@app.on_message(
    (
            filters.command("report")
            | filters.command(["admins", "admin"], prefixes="@")
    )
    & ~filters.edited
    & ~filters.private
)
@capture_err
async def report_user(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a message to report that user."
        )

    reply = message.reply_to_message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if reply_id == user_id:
        return await message.reply_text("Why are you reporting yourself ?")

    list_of_admins = await list_admins(message.chat.id)
    linked_chat = (await app.get_chat(message.chat.id)).linked_chat
    if linked_chat is not None:
        if reply_id in list_of_admins or reply_id == message.chat.id or reply_id == linked_chat.id:
            return await message.reply_text(
                "Do you know that the user you are replying is an admin ?"
            )
    else:
        if reply_id in list_of_admins or reply_id == message.chat.id:
            return await message.reply_text(
                "Do you know that the user you are replying is an admin ?"
            )

    user_mention = reply.from_user.mention if reply.from_user else reply.sender_chat.title
    text = f"Reported {user_mention} to admins!"
    admin_data = await app.get_chat_members(
        chat_id=message.chat.id, filter="administrators"
    )  # will it giv floods ?
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            # return bots or deleted admins
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"

    await message.reply_to_message.reply_text(text)
