import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# توکن ربات
TOKEN = "9241692260:AAFlYoIqnJFBpVmGIegUBa2zXW0Cztn5T1Q"

# آدرس کانال شما
CHANNEL_USERNAME = "@nonplayercharacter53"

# ذخیره کاربرانی که از جوین شدن صرف‌نظر کرده‌اند
users_declined = set()

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

    # دو دکمه کالبک برای اینکه با زدن هرکدام، پیام بسته شود
    keyboard = [
        [InlineKeyboardButton("حتما!!! (عضو شدم، بررسی کن)", callback_data="check_join")],
        [InlineKeyboardButton("نه", callback_data="refuse_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "دوست خوبم ببخشید ها ولی میشه لطفا این جا جوین بشی :("
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

# نمایش منوی اصلی به صورت پیام جدید (برای بستن پیام قبلی)
async def show_main_menu_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Games", callback_data="menu_games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "سلام! به ربات دانلود بازی خوش آمدید. برای دیدن لیست بازی‌ها روی دکمه زیر کلیک کنید:"
    
    chat_id = update.effective_chat.id
    # پاک کردن پیام قبلی جوین برای اینکه صفحه تمیز بماند
    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass
            
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# مدیریت کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    # اگر کاربر روی بررسی عضویت (حتما!!!) زد
    if query.data == "check_join":
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ["member", "administrator", "creator"]:
                await query.message.delete()
                await show_main_menu_new(update, context)
                return
            else:
                await query.answer("هنوز در کانال عضو نشده‌اید! لطفاً اول جوین شوید.", show_alert=True)
                # دکمه ورود مستقیم به کانال را به عنوان راهنما زیرش بگذاریم یا لینک بدهیم:
                return
        except Exception:
            # اگر نتوانست چک کند، برای اینکه کاربر معطل نشود اجازه عبور می‌دهیم و پیام را می‌بندیم
            await query.message.delete()
            await show_main_menu_new(update, context)
            return

    # اگر کاربر دکمه "نه" را زد
    elif query.data == "refuse_join":
        users_declined.add(user_id)
        try:
            await query.message.delete()
        except Exception:
            pass
        await show_main_menu_new(update, context)

    # منوی بازی‌ها
    elif query.data == "menu_games":
        keyboard = [
            [InlineKeyboardButton("🍌 my friend pedro", callback_data="download_my_friend_pedro")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="لیست بازی‌های موجود:", reply_markup=reply_markup)

    # بازگشت به صفحه اول
    elif query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("🎮 Games", callback_data="menu_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="به منوی اصلی برگشتید:", reply_markup=reply_markup)

    # ارسال فایل بازی My Friend Pedro با File ID صحیح
    elif query.data == "download_my_friend_pedro":
        chat_id = query.message.chat_id
        game_file_id = "BQACAgQAAxkBAAEkt4xq_imamNE6a-KG5UIEWAdpGFOetwACMxwAAmV08FPdC8i0vb6Gcz0E"
        
        try:
            await query.edit_message_text(text="در حال ارسال فایل بازی My Friend Pedro... لطفا منتظر بمانید.")
            
            # ارسال مستقیم فایل از طریق File ID
            await context.bot.send_document(
                chat_id=chat_id, 
                document=game_file_id, 
                caption="بازی My Friend Pedro با موفقیت ارسال شد! 🍌🎮"
            )
            
            keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_home")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="عملیات به پایان رسید.", reply_markup=reply_markup)

        except Exception as e:
            print(f"خطا در ارسال: {e}")
            await context.bot.send_message(
                chat_id=chat_id, 
                text="❌ خطایی در ارسال فایل رخ داد. لطفاً مطمئن شوید ربات دسترسی لازم را دارد."
            )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("ربات روشن شد و آماده به کار است...")
    app.run_polling()

if __name__ == "__main__":
    main()