from typing import Dict, List, Optional
from binance.client import Client
from config.config import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.logger import logger


class PriceFetcher:
    """价格数据获取"""
    
    def __init__(self):
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
            logger.info("Binance客户端初始化成功")
        except Exception as e:
            logger.error(f"Binance客户端初始化失败: {e}")
            self.client = None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取24小时行情"""
        try:
            if not self.client:
                return None
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                "symbol": ticker["symbol"],
                "current_price": float(ticker["lastPrice"]),
                "price_change": float(ticker["priceChange"]),
                "price_change_percent": float(ticker["priceChangePercent"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"]),
                "volume_24h": float(ticker["volume"]),
                "quote_volume_24h": float(ticker["quoteVolume"]),
            }
        except Exception as e:
            logger.error(f"获取{symbol}行情失败: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 50) -> List[Dict]:
        """获取K线数据"""
        try:
            if not self.client:
                return []
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return [
                {
                    "time": k[0] // 1000,
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                }
                for k in klines
            ]
        except Exception as e:
            logger.error(f"获取{symbol}K线失败: {e}")
            return []
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """获取订单簿"""
        try:
            if not self.client:
                return {}
            depth = self.client.get_order_book(symbol=symbol, limit=limit)
            bids = [[float(p), float(q)] for p, q in depth["bids"]]
            asks = [[float(p), float(q)] for p, q in depth["asks"]]
            bid_depth = sum(q for _, q in bids)
            ask_depth = sum(q for _, q in asks)
            return {
                "bids": bids,
                "asks": asks,
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "spread": asks[0][0] - bids[0][0] if asks and bids else 0,
            }
        except Exception as e:
            logger.error(f"获取{symbol}订单簿失败: {e}")
            return {}
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """获取近期成交"""
        try:
            if not self.client:
                return []
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            return [
                {
                    "time": t["time"] // 1000,
                    "price": float(t["price"]),
                    "qty": float(t["qty"]),
                    "isBuyerMaker": t["isBuyerMaker"],
                }
                for t in trades
            ]
        except Exception as e:
            logger.error(f"获取{symbol}近期成交失败: {e}")
            return []
    
    def get_premium_index(self, symbol: str) -> Optional[Dict]:
        """获取资金费率"""
        try:
            if not self.client:
                return None
            premium = self.client.get_premium_index(symbol=symbol)
            return {
                "mark_price": float(premium["markPrice"]),
                "index_price": float(premium["indexPrice"]),
                "funding_rate": float(premium["lastFundingRate"]),
                "next_funding_time": premium["nextFundingTime"],
            }
        except Exception as e:
            logger.error(f"获取{symbol}资金费率失败: {e}")
            return None
    
    def get_all_data(self, symbol: str) -> Dict:
        """获取所有价格数据 (每小时决策版)"""
        data = {
            "ticker": self.get_ticker(symbol),
            # 1小时K线: 最近24根 = 24小时
            "klines_1h": self.get_klines(symbol, "1h", 24),
            # 1天K线: 最近7天
            "klines_1d": self.get_klines(symbol, "1d", 7),
            "order_book": self.get_order_book(symbol),
            "premium_index": self.get_premium_index(symbol),
        }
        return data
