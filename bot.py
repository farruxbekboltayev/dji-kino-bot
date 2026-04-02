from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8233016763:AAFvBHx4_NptrrwwEIABnrnu1KAWZHzgOCs"

# kino olinadigan kanal
MOVIE_CHANNEL = "@DJI_kino"

# majburiy obuna kanallari
SUB_CHANNELS = ["@tropisms", "@DJI_kino_kanal"]

# kod : post ID
movies = {
    "101": 3,
    "102": 5,
    "103": 6,
    "183": 7,
    "185": 8,
    "144": 10,
    "611": 11
}

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Kino kodini yuboring:")

# obuna tekshirish
async def check_subscription(user_id, context):

    for channel in SUB_CHANNELS:

        member = await context.bot.get_chat_member(channel, user_id)

        if member.status not in ["member", "administrator", "creator"]:
            return False

    return True

# tugma bosilganda qayta tekshiradi
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user_id = query.from_user.id

    subscribed = await check_subscription(user_id, context)

    if subscribed:
        await query.answer("Rahmat! Endi kod yuboring ✅")
        await query.edit_message_text("🎬 Kino kodini yuboring:")
    else:
        await query.answer("Hali ham obuna bo'lmadingiz ❌")

# kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    subscribed = await check_subscription(user_id, context)

    if not subscribed:

        keyboard = InlineKeyboardMarkup([

            [InlineKeyboardButton("1-kanal 📢", url="https://t.me/tropisms")],

            [InlineKeyboardButton("2-kanal 📢", url="https://t.me/DJI_kino_kanal")],

            [InlineKeyboardButton("A'zo bo'ldim ✅", callback_data="check_sub")]

        ])

        await update.message.reply_text(

            "❗ Kinoni olish uchun quyidagi kanallarga a'zo bo'ling:",

            reply_markup=keyboard

        )

        return

    if code in movies:

        await context.bot.copy_message(

            chat_id=update.effective_chat.id,

            from_chat_id=MOVIE_CHANNEL,

            message_id=movies[code]

        )

    else:

        await update.message.reply_text("❌ Bunday kod topilmadi")

# ishga tushirish
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))

app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub"))

print("Bot ishlayapti...")

app.run_polling()
