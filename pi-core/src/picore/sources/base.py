"""
SourceAdapter protocol/interface for pi-core sources.
"""
from typing import List, Any
from abc import ABC, abstractmethod

class SourceAdapter(ABC):
    @abstractmethod
    def fetch(self, **kwargs) -> List[Any]:
        """Fetch items from the source. Must be deterministic and bounded."""
        pass
