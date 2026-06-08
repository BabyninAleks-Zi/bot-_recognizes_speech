import os
import sys

from dotenv import load_dotenv

from utils.dialogflow_api import detect_intent


LANGUAGE_CODE = "ru"
SESSION_ID = "console-user"


def main():
    load_dotenv()

    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    if not project_id:
        sys.exit("Переменная DIALOGFLOW_PROJECT_ID не найдена в .env")

    if len(sys.argv) < 2:
        sys.exit('Запустите скрипт так: python -m utils.detect_intent "Привет"')

    text = " ".join(sys.argv[1:])
    answer = detect_intent(project_id, SESSION_ID, text, LANGUAGE_CODE)

    print(f"Вы написали: {answer.query_text}")
    print(f"Intent: {answer.intent.display_name}")
    print(f"Confidence: {answer.intent_detection_confidence:.2f}")
    print(f"Ответ DialogFlow: {answer.fulfillment_text or '<пусто>'}")


if __name__ == "__main__":
    main()

