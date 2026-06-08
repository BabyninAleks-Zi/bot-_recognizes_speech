# Боты поддержки с DialogFlow

Проект с ботами поддержки для Telegram и ВКонтакте. Боты принимают сообщения пользователей, отправляют текст в DialogFlow ES, распознают намерение пользователя и отвечают заранее подготовленной фразой.

VK-бот дополнительно умеет уступать место оператору: если DialogFlow не понял вопрос и вернул fallback intent, бот молчит и не мешает живой техподдержке.

## Демо

- Telegram: [@Incredible_space_bot](https://t.me/Incredible_space_bot)
- ВКонтакте: [vk.com/club235528518](https://vk.com/club235528518)

## Что такое DialogFlow

DialogFlow ES — это сервис Google Cloud для создания разговорных интерфейсов. В этом проекте он работает как "мозг" ботов:

- тренировочные фразы показывают, как пользователь может сформулировать вопрос;
- intent описывает, что пользователь имеет в виду;
- ответ intent-а содержит фразу, которую бот отправит пользователю.

Например, фразы "Как устроиться к вам на работу?", "Как работать у вас?" и "Хочу работать у вас" могут вести к одному intent-у с одним ответом про трудоустройство.

## Возможности

- Telegram-бот отвечает на `/start`.
- Telegram-бот отвечает на обычные сообщения через DialogFlow.
- VK-бот слушает сообщения группы через Long Poll API.
- VK-бот отвечает пользователям фразами из DialogFlow.
- VK-бот молчит при fallback intent, чтобы оператор поддержки мог ответить сам.
- Скрипт обучения создаёт intents в DialogFlow из `questions.json`.
- Есть отдельные консольные скрипты для проверки DialogFlow и Google OAuth-токена.

Локальные скриншоты и демо-файлы можно складывать в `assets/`; эта папка добавлена в `.gitignore`.

## Структура проекта

```text
.
├── tg_bot.py                # Telegram-бот
├── vk_bot.py                # VK-бот для группы
├── questions.json           # FAQ-вопросы и ответы для обучения DialogFlow
├── utils/
│   ├── __init__.py
│   ├── dialogflow_api.py        # Общие функции DialogFlow
│   ├── detect_intent.py         # Проверка ответа DialogFlow из консоли
│   ├── learn_dialogflow.py      # Создание intents в DialogFlow из questions.json
│   └── get_dialogflow_token.py  # Получение Google OAuth access token
├── requirements.txt
└── README.md
```

## Требования

- Python 3.10+
- токен Telegram-бота;
- токен группы ВКонтакте;
- id группы ВКонтакте;
- Google Cloud проект с включённым DialogFlow ES;
- JSON-файл ключей сервисного аккаунта Google.

Основные зависимости:

- `python-telegram-bot==13.10`
- `google-cloud-dialogflow`
- `vk_api`
- `python-dotenv`

## Установка

Склонируйте репозиторий и перейдите в папку проекта:

```bash
cd "bot _recognizes_speech"
```

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его:

```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
TG_TOKEN=your_telegram_bot_token
TG_CHAT_ID=your_telegram_chat_id_for_error_notifications
VK_TOKEN=your_vk_group_token
VK_GROUP_ID=your_vk_group_id
DIALOGFLOW_PROJECT_ID=your_google_cloud_project_id
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```

Файл ключей сервисного аккаунта Google положите в корень проекта под именем:

```text
credentials.json
```

Не публикуйте `.env` и `credentials.json`.

`TG_CHAT_ID` нужен для уведомлений об ошибках. Бот сможет писать в этот чат только если пользователь уже запускал его в Telegram.

## Настройка DialogFlow

1. Включите DialogFlow API в Google Cloud проекте.
2. Создайте или выберите сервисный аккаунт.
3. Скачайте JSON-ключ сервисного аккаунта.
4. Положите ключ в корень проекта как `credentials.json`.
5. Выдайте сервисному аккаунту роли:

```text
Dialogflow API Client
Dialogflow Intent Admin
```

`Dialogflow API Client` нужен для распознавания сообщений.

`Dialogflow Intent Admin` нужен только для запуска `utils.learn_dialogflow`.

Проверьте доступ к DialogFlow:

```bash
python -m utils.detect_intent "Привет"
```

Скрипт должен вывести распознанный intent и ответ DialogFlow.

## Обучение DialogFlow

`utils.learn_dialogflow` читает `questions.json` и создаёт intents в DialogFlow:

```bash
python -m utils.learn_dialogflow
```

Запускайте этот скрипт только когда нужно загрузить или обновить intents. Не запускайте его при каждом старте ботов.

Если intent с таким именем уже есть в DialogFlow, скрипт пропустит его.

## Запуск Telegram-бота

```bash
python tg_bot.py
```

Поведение:

- команда `/start` отвечает `Здравствуйте`;
- обычные сообщения отправляются в DialogFlow;
- пользователь получает ответ DialogFlow в Telegram.

## Настройка группы ВКонтакте

В настройках группы включите:

- сообщения сообщества;
- Long Poll API;
- события сообщений для Long Poll API.

Токен группы должен иметь доступ к сообщениям.

## Запуск VK-бота

```bash
python vk_bot.py
```

Поведение:

- входящие сообщения группы печатаются в терминал;
- текст пользователя отправляется в DialogFlow;
- если DialogFlow нашёл подходящий intent, бот отвечает в VK;
- если DialogFlow вернул fallback intent, бот молчит и ждёт ответа оператора.

## Деплой и мониторинг

На сервере удобно запускать ботов через `systemd`:

```text
bot-recognizes-speech-tg.service
bot-recognizes-speech-vk.service
```

Оба сервиса должны быть включены в автозапуск и иметь `Restart=always`. Тогда после перезагрузки сервера или падения процесса бот поднимется снова.

Проверка:

```bash
systemctl status bot-recognizes-speech-tg.service
systemctl status bot-recognizes-speech-vk.service
```

Логи:

```bash
journalctl -u bot-recognizes-speech-tg.service -f
journalctl -u bot-recognizes-speech-vk.service -f
```

Если бот упадёт с необработанной ошибкой или не сможет получить ответ от DialogFlow, он отправит traceback в Telegram-чат из `TG_CHAT_ID`. Токены Telegram в traceback скрываются перед отправкой.

## Получение DialogFlow OAuth-токена

Этот скрипт необязателен для работы ботов. Он нужен только для проверки, что Google credentials настроены правильно:

```bash
python -m utils.get_dialogflow_token
```

Токен временный. Не сохраняйте и не публикуйте его.
