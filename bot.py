
import os
import asyncio
import sys
from datetime import datetime, time
from zoneinfo import ZoneInfo

import jdatetime
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler
)

# تنظیمات ربات
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

TEHRAN = ZoneInfo("Asia/Tehran")

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر",
    "مرداد", "شهریور", "مهر", "آبان",
    "آذر", "دی", "بهمن", "اسفند"
]

WEEKDAYS = [
    "دوشنبه", "سه‌شنبه", "چهارشنبه",
    "پنجشنبه", "جمعه", "شنبه", "یکشنبه"
]


def fa(number):
    return str(number).translate(
        str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    )


def get_calendar_message():
    now = datetime.now(TEHRAN)

    solar = jdatetime.date.fromgregorian(
        date=now.date()
    )

    weekday = WEEKDAYS[now.weekday()]

    message = (
        "📅 تقویم روز\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🇮🇷 تاریخ شمسی:\n"
        f"{weekday} {fa(solar.day)} "
        f"{PERSIAN_MONTHS[solar.month - 1]} "
        f"{fa(solar.year)}\n\n"
        f"🌍 تاریخ میلادی:\n"
        f"{now.strftime('%A')} "
        f"{fa(now.day)} {now.strftime('%B')} "
        f"{fa(now.year)}\n\n"
        "✨ روز خوبی داشته باشید ❤️"
    )

    return message


# ارسال تاریخ به کانال
async def send_calendar(context: ContextTypes.DEFAULT_TYPE):
    message = get_calendar_message()

    await context.bot.send_message(
        chat_id=CHANNEL,
        text=message
    )

    print("Calendar sent successfully!")


# دستور آزمایشی /test
async def test_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await send_calendar(context)

    await update.message.reply_text(
        "✅ پیام تقویم با موفقیت به کانال ارسال شد."
    )


# نمایش تاریخ در چت خصوصی ربات
async def today(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        get_calendar_message()
    )


async def main():

    if not TOKEN or not CHANNEL:
        raise ValueError(
            "BOT_TOKEN یا CHANNEL_ID تنظیم نشده است."
        )

    app = Application.builder().token(TOKEN).build()

    # اجرای یک‌باره برای سرویس‌های زمان‌بندی ابری مثل GitHub Actions
    if "--send-once" in sys.argv:
        await app.initialize()
        try:
            await app.bot.send_message(
                chat_id=CHANNEL,
                text=get_calendar_message()
            )
            print("Calendar sent successfully!")
        finally:
            await app.shutdown()
        return

    # دستورات ربات
    app.add_handler(
        CommandHandler("test", test_calendar)
    )

    app.add_handler(
        CommandHandler("today", today)
    )

    # ارسال خودکار هر روز ساعت ۸ صبح تهران
    app.job_queue.run_daily(
        send_calendar,
        time=time(
            hour=8,
            minute=0,
            tzinfo=TEHRAN
        )
    )

    print("Calendar Bot is running!")
    print("Daily message scheduled for 08:00 Tehran time.")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    try:
        await asyncio.Event().wait()

    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
