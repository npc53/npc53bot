import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# توکن ربات خود را اینجا وارد کنید
TOKEN = "9241692260:AAFlYoIqnJFBpVmGIegUBa2zXW0Cztn5T1Q"

# منوی اصلی (دستور /start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Games", callback_data="menu_games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! به ربات دانلود بازی خوش آمدید. برای دیدن لیست بازی‌ها روی دکمه زیر کلیک کنید:", 
        reply_markup=reply_markup
    )

# مدیریت کلیک روی دکمه‌ها (منوی تو در تو)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # اگر کاربر روی منوی Games کلیک کرد
    if query.data == "menu_games":
        keyboard = [
            [InlineKeyboardButton("🔥 بازی اکشن (تست)", callback_data="download_game_1")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لیست بازی‌های موجود:", reply_markup=reply_markup)

    # اگر کاربر خواست برگردد صفحه اول
    elif query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("🎮 Games", callback_data="menu_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="به منوی اصلی برگشتید:", reply_markup=reply_markup)

    # اگر کاربر روی دانلود بازی اول کلیک کرد
    elif query.data == "download_game_1":
        chat_id = query.message.chat_id
        file_path = "game_sample.apk"  # مسیر یا نام فایل بازی شما
        
        # ساخت فایل تستی اگر وجود نداشته باشد
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("محتوای تستی فایل بازی...")

        try:
            await query.edit_message_text(text="در حال ارسال فایل بازی... لطفا منتظر بمانید.")
            
            # ارسال فایل به کاربر
            with open(file_path, "rb") as file:
                await context.bot.send_document(
                    chat_id=chat_id, 
                    document=file, 
                    caption="بازی شما ارسال شد."
                )
            
            # پیام موفقیت به کاربر
            await context.bot.send_message(chat_id=chat_id, text="✅ عملیات ارسال با موفقیت انجام شد.")

        except Exception as e:
            print(f"خطا در ارسال: {e}")
            await context.bot.send_message(chat_id=chat_id, text="❌ متأسفانه در ارسال فایل خطایی رخ داد.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("ربات روشن شد و آماده به کار است...")
    app.run_polling()

if __name__ == "__main__":
    main()