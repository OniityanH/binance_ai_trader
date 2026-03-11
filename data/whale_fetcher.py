from typing import Dict, List, Optional
import requests
from config.config import WHALEALERT_API_KEY, CRYPTOCOMPARE_API_KEY
from utils.logger import logger


class WhaleFetcher:
    """鲸鱼动态数据获取"""
    
    def __init__(self):
        self.whalealert_key = WHALEALERT_API_KEY
        self.cryptocompare_key = CRYPTOCOMPARE_API_KEY
    
    def get_whale_alerts(self, min_value: int = 1000000) -> List[Dict]:
        """获取大额转账 (WhaleAlert)"""
        try:
            if not self.whalealert_key:
                logger.warning("WhaleAlert API Key 未设置")
                return []
            
            url = "https://api.whalealert.com/v1/transactions"
            params = {
                "api_key": self.whalealert_key,
                "min_value": min_value,
                "limit": 10,
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                # 格式化更详细的信息
                formatted = []
                for tx in transactions:
                    formatted.append({
                        "time": tx.get("timestamp"),
                        "blockchain": tx.get("blockchain", ""),
                        "symbol": tx.get("symbol", ""),
                        "amount": tx.get("amount", 0),
                        "amount_usd": tx.get("amount_usd", 0),
                        "from": tx.get("from", ""),
                        "to": tx.get("to", ""),
                    })
                return formatted
            else:
                logger.error(f"WhaleAlert API错误: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取鲸鱼警告失败: {e}")
            return []
    
    def get_crypto_compare_news(self, categories: str = "BTC,ETH") -> List[Dict]:
        """获取CryptoCompare新闻"""
        try:
            if not self.cryptocompare_key:
                logger.warning("CryptoCompare API Key 未设置")
                return []
            
            url = "https://min-api.cryptocompare.com/data/v2/news/"
            params = {
                "lang": "EN",
                "categories": categories,
                "excludeCategories": "Sponsored",
                "limit": 20,
                "api_key": self.cryptocompare_key,
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "title": item.get("title"),
                        "body": item.get("body", "")[:200],
                        "source": item.get("source_info", {}).get("name"),
                        "url": item.get("url"),
                        "published_at": item.get("published_on"),
                        "categories": item.get("categories", ""),
                        "image_url": item.get("imageurl"),
                    }
                    for item in data.get("Data", [])
                ]
            else:
                logger.error(f"CryptoCompare API错误: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return []
    
    def analyze_sentiment(self, news: List[Dict]) -> str:
        """简单情绪分析 (基于关键词)"""
        if not news:
            return "neutral"
        
        bullish_keywords = ["bullish", "rise", "gain", "surge", "up", "growth", "ETF", "inflow", "adoption"]
        bearish_keywords = ["bearish", "fall", "drop", "crash", "down", "sell", "warning", "risk", "hack"]
        
        score = 0
        for item in news[:5]:  # 只分析前5条
            title = item.get("title", "").lower()
            body = item.get("body", "").lower()
            text = title + " " + body
            
            for kw in bullish_keywords:
                if kw in text:
                    score += 1
            for kw in bearish_keywords:
                if kw in text:
                    score -= 1
        
        if score > 0:
            return "bullish"
        elif score < 0:
            return "bearish"
        else:
            return "neutral"
    
    def get_all_data(self, symbol: str = "BTC") -> Dict:
        """获取所有鲸鱼数据"""
        # 简化: 只用CryptoCompare
        news = self.get_crypto_compare_news(categories=symbol.replace("USDT", ""))
        
        return {
            "whale_alerts": self.get_whale_alerts(),
            "news": news,
            "sentiment": self.analyze_sentiment(news),
            "news_summary": news[0].get("title", "无") if news else "无",
        }
