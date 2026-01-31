"""
Centralized configuration for pi-core.
- All paths, defaults, and environment overrides
- Deterministic HN query config
"""
import os
from pathlib import Path
from typing import Any

class Settings:
    # Root directories
    ROOT = Path(__file__).resolve().parent.parent.parent.parent
    DATA = ROOT / "data"
    RAW = DATA / "raw"
    DERIVED = DATA / "derived"
    RUNS = DATA / "runs"
    OUTPUTS = ROOT / "outputs"
    BUNDLES = OUTPUTS / "bundles"
    LOGS = ROOT / "logs"
    LOG_FILE = LOGS / "picore.log"

    # HN Algolia config (deterministic, bounded)
    HN_SOURCE_NAME = "hn_algolia"
    HN_QUERY = os.environ.get("PICORE_HN_QUERY", "python")
    HN_HITS_PER_PAGE = int(os.environ.get("PICORE_HN_HITS_PER_PAGE", 50))
    HN_TAGS = os.environ.get("PICORE_HN_TAGS", "story").split(",")
    HN_API_URL = "https://hn.algolia.com/api/v1/search_by_date"

    # Run config
    RUN_ID_FORMAT = "%Y%m%d-%H%M%S"
    KILL_FILE = RUNS / "KILL"
    LATEST_SYMLINK = RUNS / "latest"

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.DATA, cls.RAW, cls.DERIVED, cls.RUNS, cls.OUTPUTS, cls.BUNDLES, cls.LOGS]:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_env(cls, key: str, default: Any = None) -> Any:
        return os.environ.get(key, default)
