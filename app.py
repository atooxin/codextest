#!/usr/bin/env python3
"""Mini CLI-приложение: простой трекер задач для терминала."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

DEFAULT_DB_PATH = Path(".codex_demo_tasks.json")


@dataclass
class Task:
    id: int
    text: str
    done: bool = False


def load_tasks(db_path: Path) -> List[Task]:
    if not db_path.exists():
        return []

    raw = json.loads(db_path.read_text(encoding="utf-8"))
    return [Task(**item) for item in raw]


def save_tasks(tasks: List[Task], db_path: Path) -> None:
    payload = [asdict(task) for task in tasks]
    db_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def add_task(tasks: List[Task], text: str) -> Task:
    next_id = max((task.id for task in tasks), default=0) + 1
    task = Task(id=next_id, text=text)
    tasks.append(task)
    return task


def mark_done(tasks: List[Task], task_id: int) -> Task | None:
    for task in tasks:
        if task.id == task_id:
            task.done = True
            return task
    return None


def format_task(task: Task) -> str:
    status = "✅" if task.done else "⬜"
    return f"{status} [{task.id}] {task.text}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python app.py",
        description="Тестовое CLI-приложение для Codex: трекер задач",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="путь до JSON-файла с задачами (по умолчанию: ./.codex_demo_tasks.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="добавить новую задачу")
    add_parser.add_argument("text", help="текст задачи")

    subparsers.add_parser("list", help="показать все задачи")

    done_parser = subparsers.add_parser("done", help="отметить задачу выполненной")
    done_parser.add_argument("task_id", type=int, help="ID задачи")

    subparsers.add_parser("stats", help="показать статистику")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    tasks = load_tasks(args.db)

    if args.command == "add":
        task = add_task(tasks, args.text)
        save_tasks(tasks, args.db)
        print(f"Добавлено: {format_task(task)}")
        return 0

    if args.command == "list":
        if not tasks:
            print("Список задач пуст. Добавь первую задачу командой add.")
            return 0
        for task in tasks:
            print(format_task(task))
        return 0

    if args.command == "done":
        task = mark_done(tasks, args.task_id)
        if task is None:
            print(f"Задача с ID={args.task_id} не найдена.")
            return 1
        save_tasks(tasks, args.db)
        print(f"Готово: {format_task(task)}")
        return 0

    if args.command == "stats":
        total = len(tasks)
        done = sum(task.done for task in tasks)
        pending = total - done
        print(f"Всего: {total} | Выполнено: {done} | В работе: {pending}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
