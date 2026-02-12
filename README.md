# Terminal File Manager (Total Commander style)

This repository now includes a dual-pane file manager for terminal usage, inspired by Total Commander.

## Run

```bash
python3 file_manager.py
```

## Key bindings

- `Tab` — switch active pane
- `↑/↓` or `k/j` — move cursor
- `Enter` — open directory / launch file with `xdg-open`
- `F5` (or `5`) — copy selected item to the opposite pane
- `F6` (or `6`) — move selected item to the opposite pane
- `F7` — create directory
- `F8` (or `8`) — delete selected item
- `F2` — rename selected item
- `r` — refresh panes
- `q` / `Esc` — quit

## Notes

- Left pane starts from the current working directory.
- Right pane starts from your home directory.
- On very small terminals, some columns may be truncated.
