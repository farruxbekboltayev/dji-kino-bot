import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")
    def log_message(self, *args):
        pass

def start_server():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()
    
import os
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 5702824058
LOG_CHANNEL = -1003453311549

# Kino olinadigan kanal
MOVIE_CHANNEL = "@DJI_kino"

# Majburiy obuna kanallari
SUB_CHANNELS = ["@tropisms", "@DJI_kino_kanal"]

# Kino kodi : kanal post ID
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
    "132": 27,
    "133": 24,
    "134": 25,
    "135": 29
}


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def add_user(user_id, first_name, last_name, username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (user_id, first_name, last_name, username)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, first_name, last_name, username))

    conn.commit()
    cur.close()
    conn.close()


def user_exists(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result is not None


def get_user_count():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()
    return count


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    username = update.effective_user.username

    if username:
        username_text = f"@{username}"
    else:
        username_text = "Username yo'q"

    if last_name:
        full_name = f"{first_name} {last_name}"
    else:
        full_name = first_name

    is_new_user = not user_exists(user_id)

    if is_new_user:
        add_user(user_id, first_name, last_name, username)

        try:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL,
                text=f"""Yangi foydalanuvchi 👤
Ismi: {full_name}
Username: {username_text}
ID: {user_id}"""
            )
        except Exception as e:
            print("LOG_CHANNEL ga user yuborishda xato:", e)

    await update.message.reply_text("🎬 Kino kodini yuboring:")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_user.id != ADMIN_ID:
        return

    count = get_user_count()

    await update.message.reply_text(
        f"Botdan foydalanganlar soni: {count} ta 👥"
    )


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


def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1-kanal 📢", url="https://t.me/tropisms")],
        [InlineKeyboardButton("2-kanal 📢", url="https://t.me/DJI_kino_kanal")],
        [InlineKeyboardButton("A'zo bo'ldim ✅", callback_data="check_sub")],
    ])


async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

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


async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    try:
        username = update.effective_user.username
        if username:
            username_text = f"@{username}"
        else:
            username_text = "Username yo'q"

        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=f"""Yangi so'rov 🎬
Ismi: {update.effective_user.first_name}
Username: {username_text}
ID: {user_id}

Yozgani: {code}"""
        )
    except Exception as e:
        print("So'rov logida xato:", e)

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
            print("Kino yuborishda xato:", e)
            await update.message.reply_text("⚠️ Kino topilmadi")
    else:
        await update.message.reply_text("❌ Bunday kod yo'q")


def main():
    if not TOKEN:
        raise ValueError("TOKEN topilmadi. Railway Variables ga TOKEN qo'shing.")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL topilmadi. Railway PostgreSQL ulang.")

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))

    print("Bot ishlayapti...")
    app.run_polling()


if __name__ == "__main__":
    main()
