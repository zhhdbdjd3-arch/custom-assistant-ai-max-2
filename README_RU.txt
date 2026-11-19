CUSTOM ASSISTANT AI MAX — СЕРВЕР

В ЭТОМ АРХИВЕ ФАЙЛЫ СЕРВЕРА, А НЕ APK.

1. Загрузи ВСЕ файлы из архива в корень нового GitHub-репозитория.
   В корне должны лежать main.py, requirements.txt и render.yaml.
2. В Render выбери этот репозиторий.
3. Runtime: Python 3.
4. Build Command: pip install -r requirements.txt
5. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
6. После успешного запуска скопируй адрес сервиса Render.
7. В приложении Custom Assistant AI MAX в поле «Адрес сервера API»
   укажи адрес Render с окончанием /api

Параметры Kilo уже заданы в render.yaml:
AI_BASE_URL=https://ai-gateway.kilo.ai/api/v1
AI_MODEL=nvidia/nemotron-3.5-super-vl:free

ПРИМЕЧАНИЕ:
Доступность бесплатной модели и лимиты определяет Kilo и они могут меняться.
Ключ API в APK не добавляй. Если Kilo потребует ключ, добавь его только
в Render → Environment.
