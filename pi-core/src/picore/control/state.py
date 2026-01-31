"""
RunState atomic load/save and per-run folder handling.
"""
import json
from pathlib import Path
from typing import Any
from ..models.core import RunState

class StateManager:
    @staticmethod
    def load(path: Path) -> RunState:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return RunState.parse_obj(data)

    @staticmethod
    def save(state: RunState, path: Path) -> None:
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            f.write(state.json(indent=2, sort_keys=True, ensure_ascii=False))
        tmp_path.replace(path)

    @staticmethod
    def ensure_run_folder(run_id: str, base: Path) -> Path:
        run_folder = base / run_id
        run_folder.mkdir(parents=True, exist_ok=True)
        return run_folder
