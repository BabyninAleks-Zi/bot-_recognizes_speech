import os
import re
import traceback

from telegram import Bot


MAX_MESSAGE_LENGTH = 4000
TELEGRAM_TOKEN_PATTERN = re.compile(r"bot\d+:[A-Za-z0-9_-]+")


def hide_secrets(text):
    return TELEGRAM_TOKEN_PATTERN.sub("bot<hidden>", text)


def get_telegram_bot():
    token = os.getenv("TG_TOKEN")

    if not token:
        raise RuntimeError("Добавьте TG_TOKEN в .env")

    return Bot(token=token)


def format_exception(bot_name, error):
    traceback_text = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    traceback_text = hide_secrets(traceback_text)

    if len(traceback_text) > MAX_MESSAGE_LENGTH:
        traceback_text = "...\n" + traceback_text[-MAX_MESSAGE_LENGTH:]

    return f"{bot_name} упал с ошибкой:\n\n{traceback_text}"


def notify_admin(message):
    chat_id = os.getenv("TG_CHAT_ID")

    if not chat_id:
        print("Не отправили уведомление: добавьте TG_CHAT_ID в .env")
        return

    try:
        bot = get_telegram_bot()
        bot.send_message(chat_id=chat_id, text=message[:MAX_MESSAGE_LENGTH])
    except Exception as error:
        print(f"Не удалось отправить уведомление в Telegram: {hide_secrets(str(error))}")
