import os
import random

import vk_api
from dotenv import load_dotenv
from utils.dialogflow_api import detect_intent
from utils.telegram_notifications import format_exception, notify_admin
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.exceptions import ApiError


def print_message(event):
    message = event.object.message

    print("Новое сообщение:")
    if message["out"]:
        print("От меня для: ", message["peer_id"])
    else:
        print("Для меня от: ", message["from_id"])
    print("Текст:", message["text"])


def send_message(vk, peer_id, text):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=random.randint(1, 1000000000),
    )


def reply_from_dialogflow(event, vk):
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    message = event.object.message
    user_text = message["text"]
    session_id = str(message["from_id"])

    try:
        answer = detect_intent(project_id, session_id, user_text, "ru")
    except Exception as error:
        print(f"DialogFlow не ответил: {error}")
        notify_admin(format_exception("VK bot", error))
        send_message(vk, message["peer_id"], "DialogFlow не ответил. Посмотрите ошибку в терминале.")
        return

    if answer.intent.is_fallback:
        print("DialogFlow не понял вопрос. Просьба ответить оператору.")
        return

    send_message(vk, message["peer_id"], answer.fulfillment_text or "Я не знаю, что ответить")


def main():
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")

    if not token:
        raise RuntimeError("Добавьте VK_TOKEN в .env")
    if not group_id:
        raise RuntimeError("Добавьте VK_GROUP_ID в .env")
    if not project_id:
        raise RuntimeError("Добавьте DIALOGFLOW_PROJECT_ID в .env")

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    try:
        longpoll = VkBotLongPoll(vk_session, int(group_id))
    except ApiError as error:
        raise RuntimeError(f"VK API вернул ошибку: {error}")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print_message(event)
            if not event.object.message["out"]:
                reply_from_dialogflow(event, vk)


if __name__ == "__main__":
    load_dotenv()
    try:
        main()
    except Exception as error:
        notify_admin(format_exception("VK bot", error))
        raise
