# Target AI API

FastAPI приложение для взаимодействия с ChatGPT API.

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/target-ai.git
cd target-ai
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
.\venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` из примера:
```bash
copy .env.example .env  # для Windows
cp .env.example .env    # для Linux/Mac
```

5. Отредактируйте `.env` файл, добавив свой API ключ OpenAI.

## Запуск

```bash
uvicorn app.main:app --reload
```

API будет доступен по адресу: http://localhost:8000

## API Endpoints

### POST /chat

Отправка сообщения в ChatGPT.

Headers:
- X-API-Key: ваш API ключ OpenAI

Request body:
```json
{
    "message": "Ваше сообщение"
}
```

Response:
```json
{
    "message": "Ответ от ChatGPT"
}
```

## Документация API

После запуска сервера, документация API доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
