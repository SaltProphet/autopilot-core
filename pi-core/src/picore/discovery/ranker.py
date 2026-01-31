"""
Score and rank problems with explicit breakdown. Select top 1 only.
Fail-fast if no problems or breakdown missing.
"""
from typing import List
from ..models.core import ProblemStatement

class Ranker:
    @staticmethod
    def score_and_rank(problems: List[ProblemStatement]) -> List[ProblemStatement]:
        if not problems:
            raise RuntimeError("No problems to rank.")
        scored = []
        for p in problems:
            breakdown = {
                "clarity": float(len(p.title) > 10),
                "specificity": float("how" in p.title.lower() or "why" in p.title.lower()),
                "actionability": float("tool" in p.title.lower()),
                "frequency_proxy": 1.0,  # All HN items = 1 for MVP
                "engagement_proxy": 1.0,  # Could use points/comments if present
            }
            score = sum(breakdown.values())
            p.score = score
            p.score_breakdown = breakdown
            scored.append(p)
        scored.sort(key=lambda p: p.score, reverse=True)
        if not scored or not scored[0].score_breakdown:
            raise RuntimeError("Ranking failed: no valid score breakdown.")
        return scored[:1]  # Only top 1 for MVP
