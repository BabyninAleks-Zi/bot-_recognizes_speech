import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError, PermissionDenied
from google.cloud import dialogflow_v2 as dialogflow


QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "questions.json"
REQUEST_TIMEOUT = 180


def get_existing_intent_names(project_id, intents_client):
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(
        request={"parent": parent},
        retry=None,
        timeout=REQUEST_TIMEOUT,
    )
    return {intent.display_name for intent in intents}


def create_intent(project_id, display_name, questions, answer, intents_client):
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for question in questions:
        part = dialogflow.Intent.TrainingPhrase.Part(text=question)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=[answer])
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = intents_client.create_intent(
        request={
            "parent": parent,
            "intent": intent,
        },
        retry=None,
        timeout=REQUEST_TIMEOUT,
    )
    print(f"Создали intent: {response.display_name}")


def main():
    load_dotenv()
    project_id = os.getenv("DIALOGFLOW_PROJECT_ID")

    if not project_id:
        sys.exit("Добавьте DIALOGFLOW_PROJECT_ID в .env")

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        intents = json.load(file)

    intents_client = dialogflow.IntentsClient()

    try:
        existing_intent_names = get_existing_intent_names(project_id, intents_client)
    except PermissionDenied:
        sys.exit(
            "Не хватает прав DialogFlow. "
            "Выдайте сервисному аккаунту роль Dialogflow Intent Admin."
        )
    except GoogleAPICallError as error:
        sys.exit(f"DialogFlow API вернул ошибку: {error}")

    for display_name, intent_data in intents.items():
        if display_name in existing_intent_names:
            print(f"Intent уже есть, пропускаем: {display_name}")
            continue

        try:
            create_intent(
                project_id,
                display_name,
                intent_data["questions"],
                intent_data["answer"],
                intents_client,
            )
        except PermissionDenied:
            sys.exit(
                "Не хватает прав DialogFlow. "
                "Выдайте сервисному аккаунту роль Dialogflow Intent Admin."
            )
        except GoogleAPICallError as error:
            print(f"Не удалось создать intent {display_name}: {error}")


if __name__ == "__main__":
    main()

