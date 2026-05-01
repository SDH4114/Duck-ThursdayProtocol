# Telegram + OpenCode Bridge

Этот MVP делает простой цикл:

```text
Telegram message -> whitelist -> CommandRouter -> OpenCodeBridge -> Telegram reply -> actions.jsonl
```

Ты пишешь в Telegram задачу, бот запускает OpenCode/Codex в `~/aiwork/thusday` и отправляет результат обратно в Telegram.

Все runtime-данные тоже лежат в `~/aiwork/thusday`:

- `~/aiwork/thusday/AGENT.md` — личность, правила и ограничения ассистента.
- `~/aiwork/thusday/sessions/` — markdown-сессии Telegram-диалогов.
- `~/aiwork/thusday/logs/actions.jsonl` — audit log.
- `~/aiwork/thusday/` — workspace, где запускается OpenCode/Codex.

## 1. Создать Telegram bot

1. Открой Telegram.
2. Найди `@BotFather`.
3. Отправь `/newbot`.
4. Задай имя и username бота.
5. Сохрани токен из BotFather.

Токен нельзя коммитить в git.

## 2. Узнать свой Telegram user id

Самый простой способ:

1. Напиши `@userinfobot` в Telegram.
2. Скопируй свой numeric ID.
3. Добавь его в `.env` как `TELEGRAM_ALLOWED_USER_IDS`.

Можно указать несколько ID через запятую:

```env
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

## 3. Установить проект

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 4. Создать `.env`

Скопируй `.env.example` в `.env` и заполни значения:

```env
TELEGRAM_BOT_TOKEN=токен_от_BotFather
TELEGRAM_ALLOWED_USER_IDS=твой_telegram_id

THURSDAY_HOME=/Users/aminmammadov/aiwork/thusday
THURSDAY_ALLOWED_READ_DIRS=/Users/aminmammadov/aiwork/thusday:/Users/aminmammadov/aiwork/data-obsidian/projects/Thursday:/Users/aminmammadov/giti/Duck-ThursdayProtocol

OPENCODE_COMMAND=opencode run
OPENCODE_AGENT=build
OPENCODE_WORKSPACE=/Users/aminmammadov/aiwork/thusday
OPENCODE_TIMEOUT_SECONDS=300
OPENCODE_MAX_OUTPUT_CHARS=3500
OPENCODE_ENABLED=true
```

Если `OPENCODE_WORKSPACE` не указать, программа будет использовать `THURSDAY_HOME`.

`THURSDAY_ALLOWED_READ_DIRS` задаёт папки, откуда бот может читать файлы. Разделитель — двоеточие `:`.

`OPENCODE_AGENT=build` можно не указывать, если в `~/aiwork/thusday/opencode.json` уже стоит:

```json
"default_agent": "build"
```

Thursday Core читает этот файл и передаёт `--agent build` в `opencode run`.

Для Telegram нужен non-interactive режим. Для OpenCode это `opencode run`:

```env
OPENCODE_COMMAND=opencode run
```

Не ставь просто `opencode`: это запускает TUI и бот может получить пустой ответ.

Для Codex можно использовать:

```env
OPENCODE_COMMAND=codex exec
```

Но на этой машине `codex exec` сейчас возвращает ошибку версии CLI для модели `gpt-5.5`, поэтому рабочий вариант здесь — `opencode run`.

## 5. Запустить бота

```bash
source .venv/bin/activate
thursday
```

Альтернатива:

```bash
python -m thursday.app.main
```

## 6. Проверить в Telegram

Напиши боту:

```text
/start
```

Потом:

```text
/status
```

Потом обычную задачу:

```text
Напиши короткий README для этого проекта
```

Бот должен отправить текст в OpenCode/Codex и вернуть ответ в Telegram.

## 7. Команды памяти и файлов

Прочитать диалог за дату:

```text
о чем мы говорили 30.04.2026
```

Также работает формат:

```text
о чем мы говорили 2026-04-30
```

Прочитать файл:

```text
прочитай файл /Users/aminmammadov/aiwork/thusday/AGENT.md
```

Прочитать текстовые файлы в папке:

```text
прочитай файлы в директории /Users/aminmammadov/aiwork/data-obsidian/projects/Thursday
```

Если путь вне `THURSDAY_ALLOWED_READ_DIRS`, бот откажет.

Прочитать сайт:

```text
прочитай сайт https://example.com
```

Найти информацию в интернете:

```text
найди в интернете latest opencode documentation
```

Удаление файлов заблокировано. Команды вроде `удали`, `delete`, `rm` не передаются в OpenCode.

Блокируются также `remove`, `unlink`, `rmdir`, `shutil.rmtree`, `send2trash`, `очисти`, `стереть`, `снеси`.

## Как это работает внутри

Основные файлы:

- `thursday/app/main.py` — собирает приложение.
- `thursday/app/config.py` — читает `.env`.
- `thursday/app/agent_profile.py` — создаёт `~/aiwork/thusday/AGENT.md`.
- `thursday/app/permissions.py` — проверяет Telegram whitelist.
- `thursday/app/router.py` — решает, что делать с сообщением.
- `thursday/interfaces/telegram_bot.py` — Telegram polling bot.
- `thursday/tools/files.py` — безопасно читает файлы только из разрешённых папок.
- `thursday/tools/web.py` — читает публичные web-страницы и делает простой web search.
- `thursday/tools/opencode.py` — запускает OpenCode/Codex CLI.
- `thursday/app/action_log.py` — пишет audit log.
- `thursday/app/session_store.py` — сохраняет Telegram-диалоги в markdown-сессии.

Логи действий пишутся сюда:

```text
~/aiwork/thusday/logs/actions.jsonl
```

Диалоги Telegram пишутся сюда:

```text
~/aiwork/thusday/sessions/telegram-<chat_id>-YYYY-MM-DD.md
```

Файл личности ассистента создаётся автоматически при запуске:

```text
~/aiwork/thusday/AGENT.md
```

## Важная безопасность

- `.env` уже игнорируется git через `.gitignore`.
- В Telegram отвечает только пользователям из `TELEGRAM_ALLOWED_USER_IDS`.
- Сейчас любая разрешённая Telegram-команда уходит в OpenCode/Codex.
- Не добавляй чужие ID в whitelist.
- Не запускай bridge на чувствительных workspace без понимания, что OpenCode/Codex может менять файлы.

## Следующий шаг

После проверки Telegram bridge стоит добавить режимы:

- `observe` — OpenCode только анализирует.
- `edit` — OpenCode может менять файлы.
- `confirm` — перед изменениями бот спрашивает подтверждение в Telegram.

Это нужно до подключения shell/tools с высокими правами.
