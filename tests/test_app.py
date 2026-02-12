from pathlib import Path

from app import Task, add_task, load_tasks, mark_done, save_tasks


def test_add_task_assigns_incremental_ids() -> None:
    tasks = [Task(id=1, text="one"), Task(id=5, text="five")]
    created = add_task(tasks, "new")
    assert created.id == 6
    assert tasks[-1].text == "new"


def test_mark_done_returns_none_for_missing_task() -> None:
    tasks = [Task(id=1, text="one")]
    result = mark_done(tasks, 99)
    assert result is None


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "tasks.json"
    source = [Task(id=1, text="first"), Task(id=2, text="second", done=True)]
    save_tasks(source, db)

    loaded = load_tasks(db)
    assert loaded == source
