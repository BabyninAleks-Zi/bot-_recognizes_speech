import os

import vk_api
from dotenv import load_dotenv
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


def main():
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")

    if not token:
        raise RuntimeError("Добавьте VK_TOKEN в .env")
    if not group_id:
        raise RuntimeError("Добавьте VK_GROUP_ID в .env")

    vk_session = vk_api.VkApi(token=token)
    try:
        longpoll = VkBotLongPoll(vk_session, int(group_id))
    except ApiError as error:
        raise RuntimeError(f"VK API вернул ошибку: {error}")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print_message(event)


if __name__ == "__main__":
    main()
