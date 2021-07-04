from telegram.ext import Updater, CallbackContext
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv
load_dotenv()
from strings import Strings

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
NOTIF_CHANNEL_ID = os.getenv("NOTIF_CHANNEL_ID")
ADMIN_IDS = os.getenv("ADMIN_IDS")
REDIS_DB_HOST = os.getenv("REDIS_DB_HOST")
REDIS_DB_PASSWORD = os.getenv("REDIS_DB_PASSWORD")
REDIS_DB_PORT = os.getenv("REDIS_DB_PORT")
REDIS_DB_NUMBER = os.getenv("REDIS_DB_NUMBER")

EXPIRE_DAYS = os.getenv("EXPIRE_DAYS")
EXPIRE_HOURS = os.getenv("EXPIRE_HOURS")
EXPIRE_MINS = os.getenv("EXPIRE_MINS")
EXPIRE_SECS = os.getenv("EXPIRE_SECS")
EXPIRE_USERS = os.getenv("EXPIRE_USERS")

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
import redis
r = redis.Redis(host=REDIS_DB_HOST, port=REDIS_DB_PORT, db=REDIS_DB_NUMBER, password = REDIS_DB_PASSWORD if (REDIS_DB_PASSWORD) else None)



import datetime, string
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Bot, ChatInviteLink
def inline_generate(update, context):
    query = update.inline_query.query
    results = list()
    user = context.bot.get_chat_member(GROUP_ID, update.inline_query.from_user.id)
    if (user.status == "administrator" or user.status == "creator"):
        if query.lower().strip() == 'link':
            timestamp = datetime.datetime.utcnow()
            add_seconds = datetime.timedelta(days=int(EXPIRE_DAYS), hours=int(EXPIRE_HOURS), minutes=int(EXPIRE_MINS), seconds=int(EXPIRE_SECS))
            time_in_future = timestamp + add_seconds
            invitelink = context.bot.create_chat_invite_link(chat_id = GROUP_ID, expire_date=time_in_future, member_limit=EXPIRE_USERS, timeout=None)
            markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton("Revoke", callback_data=f"{invitelink.invite_link}"),
                    ]])
            results = list()
            results.append(
                        InlineQueryResultArticle(
                        id=uuid4(),
                        title= Strings.INLINE_GENERATE_INVITE_LINK,
                        input_message_content=InputTextMessageContent(f"""{invitelink.invite_link}\n""", parse_mode='HTML', disable_web_page_preview=True),
                        description=f"Valid for {EXPIRE_USERS} user(s)\nExpires in {EXPIRE_DAYS} days, {EXPIRE_HOURS} hours, {EXPIRE_MINS} mins, {EXPIRE_SECS} seconds",
                        reply_markup = markup
                    )
            )
            r.incrby("total_inv", amount = 1)
            context.bot.send_message(chat_id = NOTIF_CHANNEL_ID, text = f"#GENERATE\nAdmin {update.inline_query.from_user.first_name} generated an expiring link - {invitelink.invite_link}", reply_markup = markup, disable_web_page_preview=True)
        context.bot.answer_inline_query(update.inline_query.id, results, cache_time = 1)
    else:
        results = list()
        results.append(
                    InlineQueryResultArticle(
                    id=uuid4(),
                    title=Strings.INLINE_UNAUTHORIZED,
                    input_message_content=InputTextMessageContent(Strings.INLINE_UNAUTHORIZED, parse_mode='HTML', disable_web_page_preview=True),
                    description='Unauthorized access',
                )
        )
        context.bot.answer_inline_query(update.inline_query.id, results, cache_time = 1)

from telegram.ext import InlineQueryHandler
inline_generate_handler = InlineQueryHandler(inline_generate)
dispatcher.add_handler(inline_generate_handler)



def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=Strings.GROUP_START_MESSAGE)
    if(not r.exists(f"{update.effective_chat.id}_inv")):
        r.mset({f"{update.effective_chat.id}_inv": "1"})
    if(not r.exists(f"total_started")):
        r.mset({f"total_started": "1"})
    else:
        r.incrby("total_started", amount = 1)
    if(not r.exists(f"total_inv")):    
        r.mset({f"total_inv": "1"})

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def resetlimit(update, context):
    user = context.bot.get_chat_member(GROUP_ID, update.effective_chat.id)
    if (user.status == "administrator" or user.status == "creator"):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Limit reset.")
        r.mset({f"{update.effective_chat.id}_inv": "1"})

from telegram.ext import CommandHandler
resetlimit_handler = CommandHandler('resetlimit', resetlimit)
dispatcher.add_handler(resetlimit_handler)

def revoke(update, context):
    user = context.bot.get_chat_member(GROUP_ID, update.effective_chat.id)
    if (user.status == "administrator" or user.status == "creator"):
        print(update.message.reply_to_message.text)
        context.bot.revoke_chat_invite_link(chat_id = GROUP_ID, invite_link = update.message.reply_to_message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Revoked the invite link.")
        context.bot.send_message(chat_id = NOTIF_CHANNEL_ID, text = f"#REVOKE\nAdmin {update.effective_chat.first_name} revoked {update.message.reply_to_message.text}", disable_web_page_preview=True)
        
        
from telegram.ext import CommandHandler
revoke_handler = CommandHandler('revoke', revoke)
dispatcher.add_handler(revoke_handler)

def stats(update, context):
    user = context.bot.get_chat_member(GROUP_ID, update.effective_chat.id)
    if (user.status == "administrator" or user.status == "creator"):
        total_started = int(r.get("total_started"))
        total_inv = int(r.get("total_inv"))
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Total Users: {total_started}\nTotal Invites Generated: {total_inv}")

from telegram.ext import CommandHandler
stats_handler = CommandHandler('stats', stats)
dispatcher.add_handler(stats_handler)


def direct_generate(update, context):
    # if context.args == null:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="send some text, you fool!") 
    if(r.get(f"{update.effective_chat.id}_inv") == b"1"):
        timestamp = datetime.datetime.utcnow()
        add_seconds = datetime.timedelta(days=int(EXPIRE_DAYS), hours=int(EXPIRE_HOURS), minutes=int(EXPIRE_MINS), seconds=int(EXPIRE_SECS))
        time_in_future = timestamp + add_seconds
        invitelink = context.bot.create_chat_invite_link(chat_id = GROUP_ID, expire_date=time_in_future, member_limit=EXPIRE_USERS, timeout=None)
        context.bot.send_message(chat_id=update.effective_chat.id, text=invitelink.invite_link)
        markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton("Revoke", callback_data=f"{invitelink.invite_link}"),
                    ]])
        chat = context.bot.get_chat(GROUP_ID, update.message.from_user.id)
        context.bot.send_message(chat_id = NOTIF_CHANNEL_ID, text = f"""#GENERATE
<b>User:</b> <a href="tg://user?id={update.effective_chat.id}">{update.effective_chat.first_name}</a> 
<b>ID:</b> <code>{update.effective_chat.id}</code>
<b>Generated:</b> <a href="{invitelink.invite_link}">Invite Link</a>
<b>Chat:</b> {chat.title}        
""", parse_mode = 'HTML', disable_web_page_preview=True, reply_markup = markup)
        r.mset({f"{update.effective_chat.id}_inv": "0"})
        r.incrby("total_inv", amount = 1)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=Strings.LIMIT_REACHED)

direct_generate_handler = CommandHandler('link', direct_generate)
dispatcher.add_handler(direct_generate_handler)

def revoke_inline(update: Update, _: CallbackContext):
    query = update.callback_query
    user = query.bot.get_chat_member(GROUP_ID, int(query.from_user.id))
    if (user.status == "administrator" or user.status == "creator"):
        query.bot.revoke_chat_invite_link(chat_id = GROUP_ID, invite_link = query.data)
        query.answer(text="Revoked the invite link.", show_alert = True)
        query.bot.send_message(chat_id = NOTIF_CHANNEL_ID, text = f"#REVOKE\nAdmin {query.from_user.first_name} revoked {query.data}", disable_web_page_preview=True)
    else:
        query.answer(Strings.INLINE_UNAUTHORIZED, show_alert = True)
    
from telegram.ext import CallbackQueryHandler
revoke_handler = CallbackQueryHandler(revoke_inline, pattern = '^http*')
dispatcher.add_handler(revoke_handler)

updater.start_polling()