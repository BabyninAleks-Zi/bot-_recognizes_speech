import os
import random

import vk_api
from dotenv import load_dotenv
from utils.dialogflow_api import detect_intent
from utils.telegram_notifications import format_exception, notify_admin
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll


def send_message(vk, peer_id, text):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=random.randint(1, 1000000000),
    )


def reply_from_dialogflow(event, vk, project_id):
    message = event.object.message
    user_text = message["text"]
    session_id = f"vk-{message['from_id']}"
    answer = detect_intent(project_id, session_id, user_text, "ru")

    if answer.intent.is_fallback:
        return False

    send_message(vk, message["peer_id"], answer.fulfillment_text or "Я не знаю, что ответить")
    return True


def main():
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    notification_token = os.getenv("TG_TOKEN")
    admin_chat_id = os.getenv("TG_CHAT_ID")

    if not token:
        raise RuntimeError("Добавьте VK_TOKEN в .env")
    if not group_id:
        raise RuntimeError("Добавьте VK_GROUP_ID в .env")
    if not project_id:
        raise RuntimeError("Добавьте DIALOGFLOW_PROJECT_ID в .env")
    if not notification_token:
        raise RuntimeError("Добавьте TG_TOKEN в .env")
    if not admin_chat_id:
        raise RuntimeError("Добавьте TG_CHAT_ID в .env")

    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, int(group_id))

        for event in longpoll.listen():
            if event.type != VkBotEventType.MESSAGE_NEW:
                continue

            message = event.object.message
            direction = "От меня для" if message["out"] else "Для меня от"
            print(f"Новое сообщение:\n{direction}: {message['peer_id']}\nТекст: {message['text']}")

            if message["out"]:
                continue

            has_answer = reply_from_dialogflow(
                event,
                vk,
                project_id,
            )
            if not has_answer:
                print("DialogFlow не понял вопрос. Просьба ответить оператору.")

    except Exception as error:
        try:
            notify_admin(format_exception("VK bot", error), notification_token, admin_chat_id)
        except Exception:
            print("Не удалось отправить уведомление в Telegram.")
        raise


if __name__ == "__main__":
    main()
