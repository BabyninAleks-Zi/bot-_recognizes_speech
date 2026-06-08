import os
import sys
from pathlib import Path

import google.auth
from dotenv import load_dotenv
from google.auth.transport.requests import Request


DIALOGFLOW_SCOPE = "https://www.googleapis.com/auth/dialogflow"


def get_dialogflow_token():
    load_dotenv()
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_file:
        raise RuntimeError("Переменная GOOGLE_APPLICATION_CREDENTIALS не найдена в .env")

    credentials_path = Path(credentials_file).expanduser()
    if not credentials_path.is_absolute():
        credentials_path = Path.cwd() / credentials_path

    if not credentials_path.exists():
        raise RuntimeError(f"Файл с ключами не найден: {credentials_path}")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

    credentials, project_id = google.auth.default(scopes=[DIALOGFLOW_SCOPE])
    credentials.refresh(Request())

    return credentials.token, project_id


def main():
    try:
        token, project_id = get_dialogflow_token()
    except RuntimeError as error:
        sys.exit(str(error))

    if project_id:
        print(f"Project ID: {project_id}")
    print(token)


if __name__ == "__main__":
    main()

