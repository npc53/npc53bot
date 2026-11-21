import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# بهتر است توکن را از Environment Variable بخوانید
TOKEN = os.environ.get("BOT_TOKEN", "9241692260:AAFlYoIqnJFBpVmGIegUBa2zXW0Cztn5T1Q")
CHANNEL_USERNAME = "@nonplayercharacter53"
ADMIN_USER_ID = None  # در صورت نیاز آیدی عددی خودتان را اینجا بگذارید (مثلاً 123456789)

users_declined = set()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass


def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in users_declined:
        await show_main_menu_new(update, context)
        return

    keyboard = [
        [InlineKeyboardButton("حتما!!!", callback_data="check_join")],
        [InlineKeyboardButton("نه", callback_data="refuse_join")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"میشه لطفا جوین شی؟ :("

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)


async def show_main_menu_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Games", callback_data="menu_games")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "سلام امیدوارم حالت خوب باشه. برای دیدن لیست روی دکمه زیر کلیک کن:"

    chat_id = update.effective_chat.id
    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass

    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


async def get_my_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return

    user_id = update.effective_user.id
    if ADMIN_USER_ID is not None and user_id != ADMIN_USER_ID:
        return

    f_id = update.message.document.file_id
    print(f"\n---> NEW FILE ID: {f_id}\n")
    await update.message.reply_text(f"File ID اختصاصی این فایل:\n`{f_id}`", parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "check_join":
        try:
            await query.message.delete()
        except Exception:
            pass
        await show_main_menu_new(update, context)

    elif query.data == "refuse_join":
        users_declined.add(user_id)
        try:
            await query.message.delete()
        except Exception:
            pass
        await show_main_menu_new(update, context)

    elif query.data == "menu_games":
        keyboard = [
            [InlineKeyboardButton("🍌 my friend pedro", callback_data="download_my_friend_pedro")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لیست بازی‌های موجود:", reply_markup=reply_markup)

    elif query.data == "back_home":
        keyboard = [[InlineKeyboardButton("🎮 Games", callback_data="menu_games")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="به منوی اصلی برگشتید:", reply_markup=reply_markup)

    elif query.data == "download_my_friend_pedro":
        chat_id = query.message.chat_id
        game_file_id = "BQACAgQAAxkBAAPMawFeM23VVg78J5uQdQFO5k8dA7kAAjMcAAJldPBT5N74a5PpSBs9BA"

        try:
            await query.edit_message_text(
                text="در حال ارسال فایل بازی My Friend Pedro... لطفا منتظر بمانید."
            )

            await context.bot.send_document(
                chat_id=chat_id,
                document=game_file_id,
                caption="بازی My Friend Pedro با موفقیت ارسال شد! 🍌🎮",
            )

            keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id, text="عملیات به پایان رسید.", reply_markup=reply_markup
            )

        except Exception as e:
            print(f"خطا در ارسال: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ خطایی در ارسال فایل رخ داد. لطفاً مطمئن شوید File ID متعلق به همین ربات است.",
            )


def main():
    start_dummy_server()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, get_my_file_id))

    print("ربات روشن شد و آماده به کار است...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()