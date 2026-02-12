#!/usr/bin/env python3
"""Two-pane terminal file manager inspired by Total Commander."""

from __future__ import annotations

import curses
import shutil
import stat
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class PaneState:
    path: Path
    cursor: int = 0
    entries: list[Path] = field(default_factory=list)

    def refresh(self) -> None:
        self.path = self.path.expanduser().resolve()
        items = list(self.path.iterdir())
        self.entries = sorted(items, key=lambda p: (p.is_file(), p.name.lower()))
        self.entries.insert(0, self.path.parent)
        if self.cursor >= len(self.entries):
            self.cursor = max(0, len(self.entries) - 1)

    def selected(self) -> Path:
        if not self.entries:
            return self.path
        return self.entries[self.cursor]


def format_entry(path: Path) -> str:
    if path == path.parent:
        return "[..]"

    name = path.name + ("/" if path.is_dir() else "")
    try:
        info = path.stat()
        if path.is_dir():
            size = "<DIR>"
        else:
            size = f"{info.st_size:>8}"
        mtime = datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M")
        mode = stat.filemode(info.st_mode)
    except OSError:
        size = "?"
        mtime = "?"
        mode = "??????????"
    return f"{mode} {size:>8} {mtime} {name}"


def copy_or_move(src: Path, dst_dir: Path, move: bool = False) -> Path:
    dst = dst_dir / src.name
    if dst.exists():
        raise FileExistsError(f"Destination already exists: {dst}")

    if move:
        shutil.move(str(src), str(dst))
    elif src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return dst


class FileManager:
    def __init__(self, left: Path, right: Path) -> None:
        self.panes = [PaneState(left), PaneState(right)]
        self.active = 0
        self.status = "Tab переключает панель | Enter открыть | F5 копировать | F6 переместить | F8 удалить | q выход"

    def other_index(self) -> int:
        return 1 - self.active

    def refresh(self) -> None:
        for pane in self.panes:
            pane.refresh()

    def prompt(self, stdscr: curses.window, text: str) -> str:
        h, w = stdscr.getmaxyx()
        curses.echo()
        stdscr.addnstr(h - 1, 0, " " * (w - 1), w - 1)
        stdscr.addnstr(h - 1, 0, text, w - 1)
        stdscr.refresh()
        value = stdscr.getstr(h - 1, min(len(text), w - 2), w - len(text) - 2)
        curses.noecho()
        return value.decode("utf-8", errors="ignore").strip()

    def open_entry(self, entry: Path) -> None:
        if entry.is_dir():
            self.panes[self.active].path = entry.resolve()
            self.panes[self.active].cursor = 0
            return

        cmd = ["xdg-open", str(entry)]
        try:
            subprocess.Popen(cmd)
            self.status = f"Открывается: {entry.name}"
        except Exception as exc:  # noqa: BLE001
            self.status = f"Не удалось открыть: {exc}"

    def delete_entry(self, entry: Path) -> None:
        if entry == entry.parent:
            self.status = "Нельзя удалить родительскую ссылку"
            return
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink(missing_ok=True)
        self.status = f"Удалено: {entry.name}"

    def rename_entry(self, stdscr: curses.window, entry: Path) -> None:
        if entry == entry.parent:
            self.status = "Нечего переименовывать"
            return
        new_name = self.prompt(stdscr, f"Rename {entry.name} -> ")
        if not new_name:
            self.status = "Переименование отменено"
            return
        target = entry.with_name(new_name)
        entry.rename(target)
        self.status = f"Переименовано в {new_name}"

    def make_dir(self, stdscr: curses.window) -> None:
        name = self.prompt(stdscr, "Create dir: ")
        if not name:
            self.status = "Создание каталога отменено"
            return
        target = self.panes[self.active].path / name
        target.mkdir(parents=False, exist_ok=False)
        self.status = f"Создан каталог: {name}"

    def draw_pane(self, stdscr: curses.window, pane: PaneState, x: int, width: int, active: bool) -> None:
        h, _ = stdscr.getmaxyx()
        title = f" {pane.path} "
        border_attr = curses.A_BOLD if active else curses.A_DIM
        stdscr.addnstr(0, x, title.ljust(width), width, border_attr)

        max_lines = h - 2
        start = 0
        if pane.cursor >= max_lines:
            start = pane.cursor - max_lines + 1

        visible = pane.entries[start : start + max_lines]
        for i, entry in enumerate(visible):
            y = i + 1
            idx = i + start
            text = format_entry(entry)
            attr = curses.A_REVERSE if (active and idx == pane.cursor) else curses.A_NORMAL
            stdscr.addnstr(y, x, text.ljust(width), width, attr)

        for y in range(len(visible) + 1, h - 1):
            stdscr.addnstr(y, x, " " * width, width)

    def run(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.keypad(True)
        self.refresh()

        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            mid = w // 2

            self.draw_pane(stdscr, self.panes[0], 0, mid, self.active == 0)
            self.draw_pane(stdscr, self.panes[1], mid, w - mid, self.active == 1)
            stdscr.addnstr(h - 1, 0, self.status.ljust(w - 1), w - 1, curses.A_STANDOUT)
            stdscr.refresh()

            key = stdscr.getch()
            pane = self.panes[self.active]
            entry = pane.selected()

            try:
                if key in (ord("q"), 27):
                    return
                if key == 9:  # Tab
                    self.active = self.other_index()
                elif key in (curses.KEY_UP, ord("k")):
                    pane.cursor = max(0, pane.cursor - 1)
                elif key in (curses.KEY_DOWN, ord("j")):
                    pane.cursor = min(len(pane.entries) - 1, pane.cursor + 1)
                elif key in (10, 13):
                    self.open_entry(entry)
                elif key in (curses.KEY_F5, ord("5")):
                    target = copy_or_move(entry, self.panes[self.other_index()].path, move=False)
                    self.status = f"Скопировано: {target.name}"
                elif key in (curses.KEY_F6, ord("6")):
                    target = copy_or_move(entry, self.panes[self.other_index()].path, move=True)
                    self.status = f"Перемещено: {target.name}"
                elif key in (curses.KEY_F8, ord("8")):
                    self.delete_entry(entry)
                elif key == curses.KEY_F7:
                    self.make_dir(stdscr)
                elif key == curses.KEY_F2:
                    self.rename_entry(stdscr, entry)
                elif key == ord("r"):
                    self.refresh()
                    self.status = "Обновлено"
            except Exception as exc:  # noqa: BLE001
                self.status = f"Ошибка: {exc}"

            self.refresh()


def main() -> int:
    manager = FileManager(Path.cwd(), Path.home())
    curses.wrapper(manager.run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
