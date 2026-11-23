import json
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

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_URL = "https://t.me/nonplayercharacter53"
ADMIN_USER_ID = None  # در صورت نیاز آیدی عددی خودتان را اینجا بگذارید
STATS_CODE = "in25yearsyourfavouritegumwillcomebackinstyle"
DATA_FILE = "bot_data.json"

# هر عددی اینجا بگذارید، همیشه به تعداد کل کاربران اضافه می‌شود (حتی بعد از آپدیت)
BASE_USERS_OFFSET = 0


def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {"known_users": set(data.get("known_users", []))}
        except Exception as e:
            print(f"خطا در خواندن فایل داده: {e}")
    return {"known_users": set()}


def save_data(known_users: set) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"known_users": list(known_users)},
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception as e:
        print(f"خطا در ذخیره فایل داده: {e}")


state = load_data()
known_users = state["known_users"]


def get_total_users_count() -> int:
    try:
        env_extra = int(os.environ.get("EXTRA_USERS_COUNT", "0"))
    except ValueError:
        env_extra = 0
    return BASE_USERS_OFFSET + env_extra + len(known_users)


def track_user(update: Update) -> None:
    if update.effective_user:
        user_id = update.effective_user.id
        if user_id not in known_users:
            known_users.add(user_id)
            save_data(known_users)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass


def start_dummy_server() -> None:
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Games", callback_data="menu_games")]])


def games_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍌 my friend pedro", callback_data="download_my_friend_pedro")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")],
    ])


def get_start_text() -> str:
    return (
        f'سلام امیدوارم حالت خوب باشه. برای دیدن لیست روی دکمه زیر کلیک کن'
        f'(و اگر هم خاستی وارد <a href="{CHANNEL_URL}">چنل</a> شو):'
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    text = get_start_text()

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


async def get_my_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    if not update.message or not update.message.document:
        return

    user_id = update.effective_user.id
    if ADMIN_USER_ID is not None and user_id != ADMIN_USER_ID:
        return

    f_id = update.message.document.file_id
    print(f"\n---> NEW FILE ID: {f_id}\n")
    await update.message.reply_text(f"File ID اختصاصی این فایل:\n`{f_id}`", parse_mode="Markdown")


async def secret_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    if not update.message or not update.message.text:
        return

    if update.message.text.strip() == STATS_CODE:
        total_users = get_total_users_count()
        await update.message.reply_text(
            f"تعداد کل کاربرانی که از ربات استفاده کرده‌اند: {total_users}"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    query = update.callback_query
    if not query:
        return

    data = query.data

    if data == "menu_games":
        await query.answer()
        try:
            await query.edit_message_text(text="لیست بازی‌های موجود:", reply_markup=games_menu_keyboard())
        except Exception:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="لیست بازی‌های موجود:",
                reply_markup=games_menu_keyboard(),
            )

    elif data == "back_home":
        await query.answer()
        try:
            await query.edit_message_text(text="به منوی اصلی برگشتید:", reply_markup=main_menu_keyboard())
        except Exception:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="به منوی اصلی برگشتید:",
                reply_markup=main_menu_keyboard(),
            )

    elif data == "download_my_friend_pedro":
        await query.answer()
        chat_id = query.message.chat_id if query.message else update.effective_chat.id
        game_file_id = "BQACAgQAAxkBAAPMawFeM23VVg78J5uQdQFO5k8dA7kAAjMcAAJldPBT5N74a5PpSBs9BA"

        try:
            if query.message:
                await query.edit_message_text(
                    text="در حال ارسال فایل بازی My Friend Pedro... لطفا منتظر بمانید."
                )

            await context.bot.send_document(
                chat_id=chat_id,
                document=game_file_id,
                caption="بازی My Friend Pedro با موفقیت ارسال شد! 🍌🎮",
            )

            back_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]
            ])
            await context.bot.send_message(
                chat_id=chat_id, text="عملیات به پایان رسید.", reply_markup=back_markup
            )

        except Exception as e:
            print(f"خطا در ارسال: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ خطایی در ارسال فایل رخ داد. لطفاً مطمئن شوید File ID متعلق به همین ربات است.",
            )


def main():
    if not TOKEN:
        raise ValueError("متغیر محیطی BOT_TOKEN تنظیم نشده است.")

    start_dummy_server()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, get_my_file_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, secret_stats_handler))

    print("ربات روشن شد و آماده به کار است...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()