import os
import sys

from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow


LANGUAGE_CODE = "ru"
SESSION_ID = "console-user"
REQUEST_TIMEOUT = 60


def detect_intent(
    project_id: str,
    session_id: str,
    text: str,
    language_code: str,
):
    session_client = dialogflow.SessionsClient(transport="rest")
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(
        text=text_input,
    )
    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input,
        },
        retry=None,
        timeout=REQUEST_TIMEOUT,
    )
    return response.query_result


def main() -> None:
    load_dotenv()

    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    if not project_id:
        sys.exit("Переменная DIALOGFLOW_PROJECT_ID не найдена в .env")

    if len(sys.argv) < 2:
        sys.exit('Запустите скрипт так: python detect_intent.py "Привет"')

    text = " ".join(sys.argv[1:])
    answer = detect_intent(project_id, SESSION_ID, text, LANGUAGE_CODE)

    print(f"Вы написали: {answer.query_text}")
    print(f"Intent: {answer.intent.display_name}")
    print(f"Confidence: {answer.intent_detection_confidence:.2f}")
    print(f"Ответ DialogFlow: {answer.fulfillment_text or '<пусто>'}")


if __name__ == "__main__":
    main()
