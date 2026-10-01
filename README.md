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

Откройте http://localhost:8000. Для AI нужен GROQ_API_KEY. Для регистрации нужна почта. Рекомендуемая настройка на Render — EmailJS с подключённым Gmail: EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID и EMAILJS_PUBLIC_KEY. Альтернативы — Brevo или Resend через HTTPS, а локально доступен SMTP. Тестовый отправитель Resend ограничен адресом владельца аккаунта.

SQLite создаётся автоматически в папке проекта. Копия начинается с новой базой: старые пользователи не перенесены. Встроенная программа включает 12 курсов и 54 урока: основы Python, условия и циклы, функции, коллекции, файлы и JSON, обработку ошибок, стандартную библиотеку, ООП, алгоритмы, продвинутый Python, SQLite и практические проекты. В разделе практики доступны 40 тем, сгруппированных по разделам.

При запуске обновление программы автоматически добавляет недостающие курсы и уроки в существующую базу, сохраняя идентификаторы уроков, аккаунты, прогресс и правки преподавателя. Обновление отмечается в таблице `curriculum_updates` и выполняется один раз: последующие удаления через админку не отменяются при перезапуске. Для применения на Render разверните обновлённый код и перезапустите приложение; запускать `migrate.py` не нужно.

## Render

Загрузите проект в свой GitHub-репозиторий. Создайте Blueprint из render.yaml либо Web Service с командами:

- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`

Переменные: DATABASE_URL (PostgreSQL), SECRET_KEY (случайная длинная строка; Blueprint создаёт автоматически), GROQ_API_KEY и три настройки EmailJS, перечисленные ниже. render.yaml запрашивает эти обязательные настройки; дополнительные почтовые ключи можно добавить вручную в Render → Environment.

Blueprint создаёт только бесплатный Web Service. PostgreSQL подключается отдельно через DATABASE_URL: используйте постоянную базу Render или внешнего провайдера. Бесплатная база Render истекает через 30 дней. Без PostgreSQL приложение на Render намеренно не запускается, чтобы не терять аккаунты в SQLite.

Почта отправляется через HTTPS EmailJS, Brevo или Resend, поскольку бесплатный Render блокирует SMTP. Порядок выбора: EmailJS → Brevo → Resend → локальный SMTP. Если задана хотя бы одна настройка EMAILJS_*, приложение выбирает EmailJS и требует все три обязательных значения; неполная настройка не переключает отправку на старый сервис. Ошибка выбранного сервиса возвращает ошибку регистрации; автоматического переключения между сервисами нет. Секреты и локальная база исключены из Git.

### EmailJS + Gmail: подключение к Render

Один шаблон обслуживает регистрацию и восстановление пароля. Код генерируется и проверяется на сервере. Адрес получателя берётся из регистрации или запроса восстановления; вручную добавлять каждого пользователя в EmailJS не нужно.

1. В EmailJS → Email Services добавьте Gmail, подключите аккаунт и отправьте тестовое письмо. Скопируйте Service ID: [настройка сервиса](https://www.emailjs.com/docs/tutorial/adding-email-service/).
2. В Email Templates создайте один шаблон. Заполните поля:

   | Поле EmailJS | Значение |
   | --- | --- |
   | To Email | `{{to_email}}` |
   | Subject | `{{subject}}` |
   | From Name | `Bilim Al` |
   | From Email | Включите использование адреса по умолчанию из подключённого Gmail |
   | Reply-To | Подключённый адрес Gmail или пустое поле |
   | CC / BCC | Пустые поля |

   В редактор HTML вставьте содержимое `templates/email/emailjs_code.html`. Используйте двойные фигурные скобки: EmailJS экранирует значения сам. Сохраните шаблон и скопируйте Template ID: [поля шаблона](https://www.emailjs.com/docs/tutorial/creating-email-template/), [переменные](https://www.emailjs.com/docs/user-guide/dynamic-variables-templates/).
3. В разделе Account скопируйте Public Key. В Account → Security включите **Allow API requests from non-browser applications**: Python-сервер на Render отправляет запросы без браузера. Если включена авторизация приватным ключом, скопируйте также Private Key: [официальная инструкция для серверных запросов](https://github.com/emailjs-com/emailjs-nodejs).
4. Отправьте обновлённые файлы в ветку GitHub, подключённую к вашему Render Web Service. В Render → ваш сервис → Environment добавьте:

   | Переменная Render | Откуда взять значение |
   | --- | --- |
   | EMAILJS_SERVICE_ID | EmailJS → Email Services → ваш Gmail-сервис |
   | EMAILJS_TEMPLATE_ID | EmailJS → Email Templates → созданный шаблон |
   | EMAILJS_PUBLIC_KEY | EmailJS → Account → Public Key |
   | EMAILJS_PRIVATE_KEY | Необязательно; нужен, если включена авторизация приватным ключом |

   Для EmailJS поле MAIL_FROM не требуется: отправителем служит подключённый Gmail. Старые значения Brevo/Resend не мешают, когда все настройки EmailJS заполнены. DATABASE_URL, SECRET_KEY и GROQ_API_KEY продолжают использоваться.
5. Сохраните переменные с **Save, rebuild, and deploy**. Если новый код ещё не развернулся, выберите **Manual Deploy → Deploy latest commit**. Эти изменения должны присутствовать в подключённой ветке: [переменные Render](https://render.com/docs/configure-environment-variables), [развёртывание](https://render.com/docs/deploys).
6. Проверьте регистрацию с доступным другим адресом, подтвердите код из письма и проверьте восстановление пароля. Для теста шаблона в EmailJS передайте `to_email`, `subject`, `username`, `code`, `title`, `message`, `expires_minutes`.

Логи ошибок показывают почтовый хост и HTTP-статус без ключей и кодов. Если видите `provider=api.emailjs.com status=403`, проверьте доступ для серверных запросов, ключи и настройки Security в EmailJS. Статус 429 может означать ограничение запросов или квоты; проверьте историю EmailJS. Бесплатный тариф включает 200 запросов в месяц, API ограничен одним запросом в секунду: [тарифы](https://www.emailjs.com/pricing/), [API](https://www.emailjs.com/docs/rest-api/send/).

### Коды подтверждения без своего домена через Brevo

1. Создайте аккаунт Brevo. В разделе отправителей добавьте свою почту (например, Gmail), имя `Bilim Al` и подтвердите адрес кодом из письма: [инструкция Brevo](https://help.brevo.com/hc/en-us/articles/208836149-Create-a-new-sender-From-name-and-From-email).
2. Убедитесь, что транзакционная отправка активна. Если она отключена, запросите активацию у поддержки Brevo: [проверка активации](https://help.brevo.com/hc/en-us/articles/115000188150-Troubleshooting-Issues-with-Brevo-SMTP).
3. Создайте API-ключ Brevo (не SMTP-ключ). В Render → Environment задайте `BREVO_API_KEY` и `MAIL_FROM=Bilim Al <your-address@gmail.com>`, подставив именно подтверждённый адрес. Ключ храните только в переменных окружения.
4. Разверните обновлённый код и перезапустите сервис с новыми переменными. Проверьте регистрацию с другим адресом получателя и статус отправки в транзакционных логах Brevo.

Brevo временно заменяет адрес отправителя на свой совместимый адрес при использовании бесплатной почты. Это позволяет начать без своего домена, но сервис рекомендует собственный подтверждённый домен для постоянной работы: [правила замены отправителя](https://help.brevo.com/hc/en-us/articles/14925263522578-Comply-with-Gmail-Yahoo-and-Microsoft-s-requirements-for-email-senders). Бесплатный тариф ограничен 300 отправками в день; лишние транзакционные письма могут попасть в очередь, а коды приложения действуют 15 минут: [лимиты Brevo](https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan).

Для Resend используйте `RESEND_API_KEY` и `MAIL_FROM` на собственном подтверждённом домене. Адрес `onboarding@resend.dev` подходит только для отправки на почту владельца аккаунта.

Выполнение произвольного Python-кода отключено по умолчанию: subprocess не является безопасной песочницей. AI-проверка остаётся доступной. Для доверенного локального использования можно задать ENABLE_CODE_EXECUTION=true; на публичном сайте нужен отдельный изолированный исполнитель.

`migrate.py` из исходного проекта удаляет курсы, уроки и прогресс; не запускайте его для обычного деплоя.

## Выбор модели Groq

По умолчанию используется `openai/gpt-oss-120b`. Можно выбрать другую доступную текстовую модель через `GROQ_MODEL`. В Render задайте `GROQ_MODEL=openai/gpt-oss-120b`, если ранее было настроено старое значение. Доступ зависит от аккаунта/проекта Groq. Недоступная модель возвращает HTTP 503 с объяснением, лимит — HTTP 429.
