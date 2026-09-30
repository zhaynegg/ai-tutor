# Bilim Al — AI tutor

## Локальный запуск (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env  # только если .env ещё нет
python -m uvicorn main:app --reload
```

Повторный запуск: `./start.sh`. Проверки: `.venv/bin/python -m unittest discover -s tests -v`.

Откройте http://localhost:8000. Для AI нужен GROQ_API_KEY. Для регистрации нужна почта: локально можно использовать SMTP, на Render — RESEND_API_KEY и MAIL_FROM. У Resend адрес отправителя должен быть разрешён; тестовый отправитель обычно ограничен адресом владельца аккаунта.

SQLite создаётся автоматически в папке проекта. Копия начинается с новой базой: старые пользователи не перенесены. Курсы создаются при первом запуске.

## Render

Загрузите проект в свой GitHub-репозиторий. Создайте Blueprint из render.yaml либо Web Service с командами:

- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`

Переменные: DATABASE_URL (PostgreSQL), SECRET_KEY (случайная длинная строка; Blueprint создаёт автоматически), GROQ_API_KEY, RESEND_API_KEY, MAIL_FROM.

Blueprint создаёт только бесплатный Web Service. PostgreSQL подключается отдельно через DATABASE_URL: используйте постоянную базу Render или внешнего провайдера. Бесплатная база Render истекает через 30 дней. Без PostgreSQL приложение на Render намеренно не запускается, чтобы не терять аккаунты в SQLite.

Почта отправляется через HTTPS Resend, поскольку бесплатный Render блокирует SMTP. Секреты и локальная база исключены из Git.

Выполнение произвольного Python-кода отключено по умолчанию: subprocess не является безопасной песочницей. AI-проверка остаётся доступной. Для доверенного локального использования можно задать ENABLE_CODE_EXECUTION=true; на публичном сайте нужен отдельный изолированный исполнитель.

`migrate.py` из исходного проекта удаляет курсы, уроки и прогресс; не запускайте его для обычного деплоя.

## Выбор модели Groq

По умолчанию используется `openai/gpt-oss-120b`. Можно выбрать другую доступную текстовую модель через `GROQ_MODEL`. В Render задайте `GROQ_MODEL=openai/gpt-oss-120b`, если ранее было настроено старое значение. Доступ зависит от аккаунта/проекта Groq. Недоступная модель возвращает HTTP 503 с объяснением, лимит — HTTP 429.
