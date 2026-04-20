from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8233016763:AAFvBHx4_NptrrwwEIABnrnu1KAWZHzgOCs"
ADMIN_ID =5702824058
LOG_CHANNEL = -1003453311549

# kino olinadigan kanal
MOVIE_CHANNEL = "@DJI_kino"

# majburiy obuna kanallari
SUB_CHANNELS = ["@tropisms", "@DJI_kino_kanal"]

# kod : kanal post ID
movies = {
    "101": 3,
    "102": 5,
    "103": 6,
    "183": 7,
    "185": 8,
    "144": 10,
    "611": 11,
    "108": 12,
    "128": 13,
    "129": 14,
    "385": 15,
    "932": 16,
    "237": 17,
    "131": 18,
    "124": 19,
    "125": 20,
    "126": 21,
    "127": 22,
    "130": 23,
    "132": 24
}

users = set()

# start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in users:
        users.add(user_id)

        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name
        username = update.effective_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "Username yo'q"

        if last_name:
            full_name = f"{first_name} {last_name}"
        else:
            full_name = first_name

        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=f"""Yangi foydalanuvchi 👤
Ismi: {full_name}
Username: {username_text}
ID: {user_id}"""
        )

    await update.message.reply_text("🎬 Kino kodini yuboring:")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        f"Botdan foydalanganlar soni: {len(users)} ta 👥"
    )

# a'zolikni tekshirish
async def check_subscription(user_id, context):

    for channel in SUB_CHANNELS:

        try:

            member = await context.bot.get_chat_member(channel, user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except Exception as e:

            print(f"{channel} tekshirishda xato:", e)

            return False

    return True


# tugmalar
def join_keyboard():

    keyboard = InlineKeyboardMarkup([

        [InlineKeyboardButton("1-kanal 📢", url="https://t.me/tropisms")],

        [InlineKeyboardButton("2-kanal 📢", url="https://t.me/DJI_kino_kanal")],

        [InlineKeyboardButton("A'zo bo'ldim ✅", callback_data="check_sub")]

    ])

    return keyboard


# tugma bosilganda
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    subscribed = await check_subscription(user_id, context)

    if subscribed:

        await query.edit_message_text("✅ Rahmat! Endi kino kodini yuboring:")

    else:

        await query.edit_message_text(

            "❗ Avval kanallarga a'zo bo'ling:",

            reply_markup=join_keyboard()

        )


# kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id


        if username:
            username_text = f"@{username}"
        else:
            username_text = "Username yo'q"

        if last_name:
            full_name = f"{first_name} {last_name}"
        else:
            full_name = first_name

        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=f"""Yangi foydalanuvchi 👤
Ismi: {full_name}
Username: {username_text}
ID: {user_id}"""
        )

    code = update.message.text.strip()

    subscribed = await check_subscription(user_id, context)

    if not subscribed:
        await update.message.reply_text(
            "❗ Kinoni olish uchun kanallarga a'zo bo'ling:",
            reply_markup=join_keyboard()
        )
        return

    if code in movies:
        try:
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=MOVIE_CHANNEL,
                message_id=movies[code]
            )
        except Exception as e:
            print("kino yuborishda xato:", e)
            await update.message.reply_text("⚠️ Kino topilmadi")
    else:
        await update.message.reply_text("❌ Bunday kod yo'q")

    
# ishga tushirish
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("stats", stats))

app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))


print("Bot ishlayapti...")

app.run_polling()
