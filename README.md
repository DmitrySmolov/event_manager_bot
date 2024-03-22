# event_manager_bot
Проект с двумя ботами на aiogram3 и бэкендом на Django REST Framework и базой данных PostgreSQL.
Один бот регистрирует мероприятие, второй - подтверждает или отклоняет его.

## Требования

- Python 3.12
- PostgreSQL

## Технологии

- aiogram 3.4
- Django 5.0
- djangorestframework 3.15

## Установка

Клонируйте репозиторий
```
git clone https://github.com/DmitrySmolov/event_manager_bot.git
```
Создайте и активируйте виртуальное окружение. Установите зависимости:
```
pip install -r requirements.txt
```
Создайте файл .env в корне проекта со следующими переменными:
```
SECRET_KEY=<ключ для бэкенда Джанго>
DB_NAME=<имя базы данных Postges куда будут сохраняться таблицы БД>
POSTGRES_USER=<имя пользователя для БД>
POSTGRES_PASSWORD=<пароль для БД>
DB_HOST=localhost
DB_PORT=5432
EVENT_REGISTRATOR_BOT_TOKEN=<токен бота, сохраняющего мероприятия>
API_URL_BASE=http://localhost:8000/api/
EVENT_ENDPOINT=events/
EVENT_STATUS_ENDPOINT=events/{event_id}/status/
EVENT_STATUS_UPDATER_BOT_TOKEN=<токен бота, для подтверждения или отклонения>
ADMIN_CHAT_ID=<telegram id администратора, который будет прринимать решения по мероприятиям>
EVENT_WHOOK_FULL_URL=http://localhost:8081/db_event/
STATUS_WHOOK_FULL_URL=http://localhost:8080/db_status/
```

## Запуск
Запуск локально с трёх терминалов.<br>
Бэкенд:
```
python backend/manage.py runserver
```
Бот-регистратор:
```
python bots/event_registrator_bot/main.py
```
Бот, изменяющий статусы:
```
python bots/event_status_updater_bot/main.py
```

## Использование
Меню бота-регистратора:
- /start Для начала заполнения формы
- /cancel Для прекращения в любой момент<br>
Меню бота для изменения статуса:
- /start Для начала работы<br>
ВАЖНО: для того, чтобы бот мог отправлять оповещения администратору, администратор должен первым начать взаимодействие с ботом через команду Старт. Так уж устроен Telegram API.