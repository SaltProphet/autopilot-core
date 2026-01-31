"""
Hacker News Algolia adapter for pi-core.
Fetches bounded, deterministic results and persists raw snapshots.
"""
import requests
from pathlib import Path
from datetime import datetime
from ..config.settings import Settings
from .base import SourceAdapter

class HNAlgoliaAdapter(SourceAdapter):
    def fetch(self, query=None, hits_per_page=None, tags=None, out_path: Path = None):
        query = query or Settings.HN_QUERY
        hits_per_page = hits_per_page or Settings.HN_HITS_PER_PAGE
        tags = tags or Settings.HN_TAGS
        params = {
            "query": query,
            "tags": ",".join(tags),
            "hitsPerPage": hits_per_page,
            "numericFilters": "",
            "restrictSearchableAttributes": "",
            "typoTolerance": "false",
            "advancedSyntax": "true",
            "sort": "byDate"
        }
        resp = requests.get(Settings.HN_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        # Persist raw snapshot if out_path is given
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                for item in hits:
                    f.write(f"{item}\n")
        return hits
