
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
	"""
	Abstract base class for all data connectors.
	"""
	@abstractmethod
	def fetch(self, **kwargs) -> List[Dict[str, Any]]:
		"""
		Fetch raw items from the data source.
		Returns a list of dicts.
		"""
		pass

