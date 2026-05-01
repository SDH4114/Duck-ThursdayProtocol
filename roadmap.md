---

kanban-plugin: board

---

## Backlog

- [ ] Решить финальное имя ассистента: 
	**Thursday**
- [ ] Выбрать стиль голоса и поведения
- [ ] Описать список команд первой версии
- [ ] Определить путь к Obsidian vault и правила доступа
- [ ] Решить, какие папки файловой системы разрешены для чтения
- [ ] Решить, какие папки запрещены для записи
- [ ] Составить список приложений для запуска: VS Code, Obsidian, Terminal, Browser
- [ ] Продумать формат памяти о пользователе
- [ ] Подготовить формат журнала действий `actions.jsonl`
- [ ] Выбрать локальный STT: faster-whisper / whisper.cpp / Vosk
- [ ] Выбрать TTS: macOS say / Piper / ElevenLabs
- [ ] Выбрать wake word систему: hotkey first, потом openWakeWord или Porcupine
- [ ] Продумать формат task pack для OpenCode/Codex
- [ ] Продумать screen pipeline: screenshot → OCR → vision summary
- [ ] Подобрать визуальные референсы для интерфейса Jarvis-like dashboard


## MVP

- [ ] Создать Python-проект `thursday`
- [ ] Добавить `pyproject.toml`
- [ ] Добавить `app/main.py`
- [ ] Добавить загрузку `.env` и config
- [ ] Реализовать `CommandRouter`
- [ ] Реализовать простую классификацию команд по правилам
- [ ] Реализовать Telegram bot через `python-telegram-bot`
- [ ] Добавить whitelist Telegram user id
- [ ] Добавить команду `/start`
- [ ] Добавить команду `/status`
- [ ] Добавить команду `/help`
- [ ] Добавить tool `timers.py`
- [ ] Добавить команду “поставь таймер”
- [ ] Добавить tool `apps.py`
- [ ] Добавить команду “открой VS Code”
- [ ] Добавить tool `obsidian.py`
- [ ] Добавить поиск по Obsidian notes
- [ ] Добавить создание заметки в Obsidian
- [ ] Добавить tool `files.py`
- [ ] Добавить чтение файлов из разрешённых директорий
- [ ] Добавить `permissions.py`
- [ ] Разделить действия на low / medium / high risk
- [ ] Добавить подтверждение high-risk действий через Telegram
- [ ] Добавить `actions.jsonl`
- [ ] Логировать каждое действие
- [ ] Добавить voice output через macOS `say`
- [ ] Сделать первый полный сценарий: Telegram → команда → действие → ответ → log


## OpenCode Hook Bridge

- [ ] Сделать модуль `tools/opencode.py`
- [ ] Проверить доступность CLI OpenCode/Codex
- [ ] Добавить настройку пути к workspace
- [ ] Создать формат task pack
- [ ] Добавить команду “запусти задачу в OpenCode”
- [ ] Передавать задачу с контекстом проекта
- [ ] Сохранять stdout/stderr выполнения
- [ ] Делать краткий summary результата
- [ ] Отправлять summary в Telegram
- [ ] Сохранять результат в Obsidian journal
- [ ] Добавить режим dry-run
- [ ] Добавить подтверждение перед задачами, которые могут менять файлы
- [ ] Добавить список разрешённых проектов


## Voice

- [ ] Добавить hotkey activation
- [ ] Подключить microphone input
- [ ] Подключить faster-whisper
- [ ] Преобразовывать речь в текст
- [ ] Передавать распознанный текст в `CommandRouter`
- [ ] Добавить voice response
- [ ] Добавить wake word “Четверг”
- [ ] Добавить режим “слушать только после wake word”
- [ ] Добавить защиту от случайных команд
- [ ] Добавить команду “отмена”


## Screen

- [ ] Добавить screenshot tool
- [ ] Добавить команду “что на экране?”
- [ ] Добавить OCR через Tesseract или macOS Vision
- [ ] Извлекать текст с экрана
- [ ] Отправлять скриншот в Telegram
- [ ] Добавить vision-анализ через API или локальную модель
- [ ] Добавить распознавание ошибок на экране
- [ ] Добавить команду “объясни эту ошибку”
- [ ] Добавить режим “сделай скрин и отправь в OpenCode”


## Obsidian Memory

- [ ] Создать структуру `memory/profile.md`
- [ ] Создать `memory/preferences.md`
- [ ] Создать `memory/projects.md`
- [ ] Создать `memory/journal/`
- [ ] Добавить команду “запомни это”
- [ ] Добавить подтверждение перед записью фактов
- [ ] Добавить поиск по памяти
- [ ] Добавить ежедневный summary
- [ ] Добавить связь действий с проектами
- [ ] Добавить RAG по Obsidian


## Security

- [ ] Добавить permission config
- [ ] Запретить удаление файлов без подтверждения
- [ ] Запретить shell без подтверждения
- [ ] Запретить отправку приватных файлов наружу без подтверждения
- [ ] Добавить whitelist директорий
- [ ] Добавить blacklist директорий
- [ ] Добавить секреты только через `.env`
- [ ] Добавить Telegram user whitelist
- [ ] Добавить audit log
- [ ] Добавить emergency stop


## Later

- [ ] Добавить локальную LLM для простых команд
- [ ] Добавить dashboard UI
- [ ] Добавить system tray app
- [ ] Добавить планировщик ежедневных задач
- [ ] Добавить proactive reminders
- [ ] Добавить браузерные действия
- [ ] Добавить управление окнами
- [ ] Добавить плагины-навыки
- [ ] Добавить режим “coding assistant”
- [ ] Добавить режим “writer assistant”
- [ ] Добавить режим “game design assistant”




%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[false,false,false,false,false,false,false,false]}
```
%%