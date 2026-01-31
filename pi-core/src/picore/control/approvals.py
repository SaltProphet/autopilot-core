"""
Approval gating and ApprovalRecord persistence for pi-core.
Blocks generation/packaging unless approved.
"""
import json
from pathlib import Path
from datetime import datetime
from ..models.core import ApprovalRecord

class ApprovalManager:
    @staticmethod
    def approval_file(run_folder: Path) -> Path:
        return run_folder / "approval_record.json"

    @staticmethod
    def is_approved(run_folder: Path) -> bool:
        file = ApprovalManager.approval_file(run_folder)
        if not file.exists():
            return False
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            ApprovalRecord.parse_obj(data)  # Validate
            return True
        except Exception:
            return False

    @staticmethod
    def write_approval(run_folder: Path, run_id: str, approved_by: str, note: str = None):
        record = ApprovalRecord(
            run_id=run_id,
            approved_at=datetime.utcnow(),
            approved_by=approved_by,
            note=note
        )
        file = ApprovalManager.approval_file(run_folder)
        with file.open("w", encoding="utf-8") as f:
            f.write(record.json(indent=2, sort_keys=True, ensure_ascii=False))

    @staticmethod
    def require_approved(run_folder: Path):
        if not ApprovalManager.is_approved(run_folder):
            raise SystemExit("Approval required: run is blocked until explicitly approved.")
