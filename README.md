# Codex Demo CLI App

Небольшое тестовое приложение, которое можно запускать из терминала: **трекер задач** на Python.

## Требования

- Python 3.10+

## Быстрый старт

```bash
python app.py add "Проверить, что Codex в терминале запускается"
python app.py add "Сделать коммит"
python app.py list
python app.py done 1
python app.py stats
```

По умолчанию задачи сохраняются в файл `.codex_demo_tasks.json` в текущей директории.

## Использование отдельной базы

```bash
python app.py --db /tmp/my_tasks.json add "Тест с другой базой"
python app.py --db /tmp/my_tasks.json list
```

## Тесты

```bash
python -m pytest -q
```
