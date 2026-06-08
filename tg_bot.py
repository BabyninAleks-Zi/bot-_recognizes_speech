import os
import time

from dotenv import load_dotenv
from telegram.error import NetworkError, TimedOut
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from utils.dialogflow_api import detect_intent
from utils.telegram_notifications import format_exception, notify_admin


RECONNECT_DELAY = 60


def say_hi(update, context):
    update.message.reply_text("Здравствуйте")


def reply_from_dialogflow(update, context):
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    user_text = update.message.text
    session_id = str(update.effective_user.id)

    try:
        answer = detect_intent(project_id, session_id, user_text, "ru")
    except Exception as error:
        print(f"DialogFlow не ответил: {error}")
        notify_admin(format_exception("Telegram bot", error))
        update.message.reply_text("DialogFlow не ответил. Посмотрите ошибку в терминале.")
        return

    update.message.reply_text(answer.fulfillment_text or "Я не знаю, что ответить")


def handle_error(update, context):
    if context.error:
        notify_admin(format_exception("Telegram bot", context.error))


def run_bot():
    load_dotenv()
    token = os.getenv("TG_TOKEN")
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")

    if not token:
        raise RuntimeError("Добавьте TG_TOKEN в .env")
    if not project_id:
        raise RuntimeError("Добавьте DIALOGFLOW_PROJECT_ID в .env")

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", say_hi))
    dispatcher.add_handler(MessageHandler(Filters.text, reply_from_dialogflow))
    dispatcher.add_error_handler(handle_error)

    try:
        updater.start_polling()
        updater.idle()
    finally:
        updater.stop()


def main():
    while True:
        try:
            run_bot()
        except (NetworkError, TimedOut):
            print(f"Telegram API недоступен. Повтор через {RECONNECT_DELAY} секунд.")
            time.sleep(RECONNECT_DELAY)
        except Exception as error:
            notify_admin(format_exception("Telegram bot", error))
            raise


if __name__ == "__main__":
    main()
