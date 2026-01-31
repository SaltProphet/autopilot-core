
import requests
from typing import List, Dict, Any
from .base import BaseConnector

class RedditConnector(BaseConnector):
	"""
	Minimal Reddit connector for demo: fetches posts from a subreddit (read-only, no auth).
	"""
	BASE_URL = "https://www.reddit.com"

	def fetch(self, subreddit: str = "all", limit: int = 20) -> List[Dict[str, Any]]:
		headers = {"User-Agent": "pi-core-demo/0.1"}
		url = f"{self.BASE_URL}/r/{subreddit}/hot.json?limit={limit}"
		resp = requests.get(url, headers=headers, timeout=10)
		if resp.status_code != 200:
			raise RuntimeError(f"Reddit API error: {resp.status_code}")
		data = resp.json()
		posts = []
		for child in data.get("data", {}).get("children", []):
			post = child.get("data", {})
			posts.append({
				"title": post.get("title"),
				"text": post.get("selftext", ""),
				"url": post.get("url"),
				"objectID": str(post.get("id")),
				"created_at": post.get("created_utc"),
				"subreddit": post.get("subreddit"),
				"permalink": post.get("permalink"),
				"author": post.get("author"),
				"num_comments": post.get("num_comments"),
				"score": post.get("score"),
			})
		return posts

