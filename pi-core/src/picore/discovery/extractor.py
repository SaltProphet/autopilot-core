"""
Deterministic extraction: raw items -> ProblemStatements with Evidence.
Fail-fast if heuristics cannot extract required fields.
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from ..models.core import ProblemStatement, Evidence, SourceRef

class Extractor:
    @staticmethod
    def extract_problems(raw_items: List[Dict[str, Any]]) -> List[ProblemStatement]:
        problems = []
        for item in raw_items:
            title = item.get("title") or item.get("story_title")
            text = item.get("text") or item.get("story_text") or ""
            url = item.get("url") or item.get("story_url") or ""
            object_id = str(item.get("objectID"))
            created_at = item.get("created_at")
            if not (title and object_id and created_at):
                continue  # skip incomplete
            # Heuristic: look for complaint/question/tooling gap in title/text
            if not Extractor.is_candidate(title, text):
                continue
            summary = Extractor.summarize(title, text)
            who_is_hurt = Extractor.extract_who(title, text)
            why_now = Extractor.extract_why(title, text)
            evidence = [Evidence(
                ref=SourceRef(
                    source_name="hn_algolia",
                    source_item_id=object_id,
                    source_url=url or f"https://news.ycombinator.com/item?id={object_id}",
                    retrieved_at=datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ),
                quote=title,
                signals={"title_length": len(title)},
                notes=None
            )]
            tags = ["hn"]
            score = 0.0  # To be set by ranker
            score_breakdown = {}
            problem_id = Extractor.stable_hash(title + text)
            problems.append(ProblemStatement(
                problem_id=problem_id,
                title=title,
                summary=summary,
                who_is_hurt=who_is_hurt,
                why_now=why_now,
                evidence=evidence,
                tags=tags,
                score=score,
                score_breakdown=score_breakdown
            ))
        if not problems:
            raise RuntimeError("No candidate problems extracted from raw items.")
        return problems

    @staticmethod
    def is_candidate(title: str, text: str) -> bool:
        # Simple heuristics: question, complaint, or tooling gap
        patterns = [r"\bhow do i\b", r"\bproblem\b", r"\bissue\b", r"\bcan't\b", r"\bneed\b", r"\bmissing\b", r"\btool\b", r"\bhelp\b", r"\bwhy\b", r"\bwhat's the best\b", r"\bworkflow\b"]
        combined = f"{title} {text}".lower()
        return any(re.search(p, combined) for p in patterns)

    @staticmethod
    def summarize(title: str, text: str) -> str:
        return title if title else text[:120]

    @staticmethod
    def extract_who(title: str, text: str) -> str:
        # Heuristic: look for "I", "we", "developers", etc.
        if "developer" in text.lower():
            return "Developers"
        if "user" in text.lower():
            return "Users"
        if "i " in text.lower() or " my " in text.lower():
            return "Individual user"
        return "Unknown"

    @staticmethod
    def extract_why(title: str, text: str) -> str:
        # Heuristic: look for urgency or recency
        if "now" in text.lower():
            return "Recent/urgent issue"
        if "today" in text.lower():
            return "Current relevance"
        return "Not specified"

    @staticmethod
    def stable_hash(s: str) -> str:
        import hashlib
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
