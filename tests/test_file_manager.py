from pathlib import Path

import pytest

from file_manager import copy_or_move, format_entry


def test_copy_or_move_copies_file(tmp_path: Path) -> None:
    src_dir = tmp_path / "left"
    dst_dir = tmp_path / "right"
    src_dir.mkdir()
    dst_dir.mkdir()
    source = src_dir / "a.txt"
    source.write_text("hello", encoding="utf-8")

    copied = copy_or_move(source, dst_dir)

    assert copied.read_text(encoding="utf-8") == "hello"
    assert source.exists()


def test_copy_or_move_moves_directory(tmp_path: Path) -> None:
    src_dir = tmp_path / "left"
    dst_dir = tmp_path / "right"
    src_dir.mkdir()
    dst_dir.mkdir()
    folder = src_dir / "folder"
    folder.mkdir()
    (folder / "x.txt").write_text("x", encoding="utf-8")

    moved = copy_or_move(folder, dst_dir, move=True)

    assert moved.is_dir()
    assert (moved / "x.txt").exists()
    assert not folder.exists()


def test_copy_or_move_raises_when_target_exists(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    dst_dir = tmp_path / "dest"
    src.write_text("x", encoding="utf-8")
    dst_dir.mkdir()
    (dst_dir / "a.txt").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        copy_or_move(src, dst_dir)


def test_format_entry_parent_marker() -> None:
    root = Path("/")
    assert format_entry(root) == "[..]"
