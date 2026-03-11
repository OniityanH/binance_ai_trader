from typing import Dict, List
from .whale_fetcher import WhaleFetcher

# 新闻获取复用 WhaleFetcher
NewsFetcher = WhaleFetcher

__all__ = ["NewsFetcher"]
