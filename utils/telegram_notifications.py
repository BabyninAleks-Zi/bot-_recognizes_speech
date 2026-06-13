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


def notify_admin(message, token, chat_id):
    if not token:
        raise RuntimeError("Добавьте TG_TOKEN в .env")
    if not chat_id:
        raise RuntimeError("Добавьте TG_CHAT_ID в .env")

    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message[:MAX_MESSAGE_LENGTH])
