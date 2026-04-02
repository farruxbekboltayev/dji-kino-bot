from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import BadRequest

TOKEN = "8233016763:AAFvBHx4_NptrrwwEIABnrnu1KAWZHzgOCs"

# kino olinadigan kanal
MOVIE_CHANNEL = "@DJI_kino"

# majburiy obuna kanali
SUB_CHANNEL = "@tropisms"

# kod : post ID
movies = {
    "101": 3,
    "102": 5,
    "103": 6,
    "183": 7,
    "185": 8,
    "144": 10

}

# start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Kino kodini yuboring:"
    )

# a'zolikni tekshirish
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

# kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    # avval obuna tekshiriladi
    subscribed = await check_subscription(user_id, context)

    if not subscribed:

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📢 Kanalga a'zo bo'lish",
                url=f"https://t.me/{SUB_CHANNEL[1:]}"
            )]
        ])

        await update.message.reply_text(
            "❗ Avval kanalga a'zo bo'ling:",
            reply_markup=keyboard
        )
        return

    # kod tekshiriladi
    if code in movies:

        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=MOVIE_CHANNEL,
            message_id=movies[code]
        )

    else:
        await update.message.reply_text("❌ Bunday kod topilmadi")

# botni ishga tushirish
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))

print("Bot ishlayapti...")
app.run_polling()
