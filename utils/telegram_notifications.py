import os
import re
import traceback

from telegram import Bot


MAX_MESSAGE_LENGTH = 4000
TELEGRAM_TOKEN_PATTERN = re.compile(r"bot\d+:[A-Za-z0-9_-]+")


def format_exception(bot_name, error):
    traceback_text = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    traceback_text = TELEGRAM_TOKEN_PATTERN.sub("bot<hidden>", traceback_text)

    if len(traceback_text) > MAX_MESSAGE_LENGTH:
        traceback_text = "...\n" + traceback_text[-MAX_MESSAGE_LENGTH:]

    return f"{bot_name} упал с ошибкой:\n\n{traceback_text}"


def notify_admin(message):
    token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    if not token:
        print("Не отправили уведомление: добавьте TG_TOKEN в .env")
        return
    if not chat_id:
        print("Не отправили уведомление: добавьте TG_CHAT_ID в .env")
        return

    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message[:MAX_MESSAGE_LENGTH])
    except Exception as error:
        error_text = TELEGRAM_TOKEN_PATTERN.sub("bot<hidden>", str(error))
        print(f"Не удалось отправить уведомление в Telegram: {error_text}")
