import os
import sys
from pathlib import Path

import google.auth
from dotenv import load_dotenv
from google.auth.transport.requests import Request


DIALOGFLOW_SCOPE = "https://www.googleapis.com/auth/dialogflow"


def get_credentials_path(credentials_file):
    credentials_path = Path(credentials_file).expanduser()
    if not credentials_path.is_absolute():
        credentials_path = Path.cwd() / credentials_path

    if not credentials_path.exists():
        raise RuntimeError(f"Файл с ключами не найден: {credentials_path}")

    return credentials_path


def get_dialogflow_token(credentials_path):
    credentials, project_id = google.auth.load_credentials_from_file(
        str(credentials_path),
        scopes=[DIALOGFLOW_SCOPE],
    )
    credentials.refresh(Request())

    return credentials.token, project_id


def main():
    load_dotenv()
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_file:
        sys.exit("Переменная GOOGLE_APPLICATION_CREDENTIALS не найдена в .env")

    try:
        credentials_path = get_credentials_path(credentials_file)
        token, project_id = get_dialogflow_token(credentials_path)
    except RuntimeError as error:
        sys.exit(str(error))

    if project_id:
        print(f"Project ID: {project_id}")
    print(token)


if __name__ == "__main__":
    main()
