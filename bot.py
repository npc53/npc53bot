import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات
TOKEN = "9241692260:AAFlYoIqnJFBpVmGIegUBa2zXW0Cztn5T1Q"

# آدرس کانال شما
CHANNEL_USERNAME = "@nonplayercharacter53"

# ذخیره کاربرانی که از جوین شدن صرف‌نظر کرده‌اند
users_declined = set()


# سرور HTTP کوچک برای راضی نگه‌داشتن پورت Web Service در Render
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


# دستور /start (بررسی عضویت کانال)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in users_declined:
        await show_main_menu_new(update, context)
        return

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await show_main_menu_new(update, context)
            return
    except Exception:
        pass

    keyboard = [
        [InlineKeyboardButton("حتما!!! (عضو شدم، بررسی کن)", callback_data="check_join")],
        [InlineKeyboardButton("نه", callback_data="refuse_join")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "دوست خوبم ببخشید ها ولی میشه لطفا این جا جوین بشی :("
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)


# نمایش منوی اصلی به صورت پیام جدید (برای بستن پیام قبلی)
async def show_main_menu_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Games", callback_data="menu_games")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "سلام! به ربات دانلود بازی خوش آمدید. برای دیدن لیست بازی‌ها روی دکمه زیر کلیک کنید:"

    chat_id = update.effective_chat.id
    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass

    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


# ابزار کمکی: دریافت File ID هر فایلی که خودتان به ربات بفرستید
async def get_my_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.document:
        f_id = update.message.document.file_id
        print(f"\n---> NEW FILE ID: {f_id}\n")
        await update.message.reply_text(f"File ID اختصاصی این فایل:\n`{f_id}`", parse_mode="Markdown")


# مدیریت کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "check_join":
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ["member", "administrator", "creator"]:
                await query.message.delete()
                await show_main_menu_new(update, context)
                return
            else:
                await query.answer("هنوز در کانال عضو نشده‌اید! لطفاً اول جوین شوید.", show_alert=True)
                return
        except Exception:
            await query.message.delete()
            await show_main_menu_new(update, context)
            return

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
        game_file_id = "BQACAgQAAxkBAAEkt4xq_imamNE6a-KG5UIEWAdpGFOetwACMxwAAmV08FPdC8i0vb6Gcz0E"

        try:
            await query.edit_message_text(text="در حال ارسال فایل بازی My Friend Pedro... لطفا منتظر بمانید.")

            await context.bot.send_document(
                chat_id=chat_id,
                document=game_file_id,
                caption="بازی My Friend Pedro با موفقیت ارسال شد! 🍌🎮",
            )

            keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="عملیات به پایان رسید.", reply_markup=reply_markup)

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
    app.run_polling()


if __name__ == "__main__":
    main()