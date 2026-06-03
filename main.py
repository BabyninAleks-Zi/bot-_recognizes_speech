import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Здравствуйте")


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")

    if not tg_token:
        raise RuntimeError("Переменная TG_TOKEN не найдена в .env")

    updater = Updater(token=tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
