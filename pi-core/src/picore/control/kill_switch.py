"""
Kill switch logic for pi-core.
Checks for the presence of the kill file before and after every step.
"""
from pathlib import Path
from ..config.settings import Settings

class KillSwitch:
    @staticmethod
    def check_kill() -> bool:
        """Returns True if kill file exists, else False."""
        return Settings.KILL_FILE.exists()

    @staticmethod
    def require_alive():
        if KillSwitch.check_kill():
            raise SystemExit("KILL switch engaged: data/runs/KILL file present. Aborting run.")
