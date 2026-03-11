from typing import Dict, Optional
from data.price_fetcher import PriceFetcher
from data.whale_fetcher import WhaleFetcher
from trading.binance_client import BinanceClient
from utils.logger import logger


class DataAggregator:
    """数据聚合器"""
    
    def __init__(self):
        self.price_fetcher = PriceFetcher()
        self.whale_fetcher = WhaleFetcher()
        self.binance_client = BinanceClient()
        logger.info("数据聚合器初始化完成")
    
    def aggregate(self, symbol: str, portfolio: Optional[Dict] = None) -> Dict:
        """聚合所有数据"""
        portfolio = portfolio or {
            "current_position": 0.0,
            "entry_price": 0.0,
            "unrealized_pnl": 0.0,
            "holding_hours": 0,
        }
        
        logger.info(f"开始聚合 {symbol} 数据...")
        
        # 价格数据
        price_data = self.price_fetcher.get_all_data(symbol)
        
        # 鲸鱼/新闻数据
        whale_data = self.whale_fetcher.get_all_data(symbol.replace("USDT", ""))
        
        # 账户余额
        usdt_balance = self.binance_client.get_balance("USDT")
        
        # 聚合
        aggregated = {
            "symbol": symbol,
            "timestamp": int(price_data["ticker"]["current_price"] if price_data.get("ticker") else 0),
            "price_data": price_data,
            "whale_data": whale_data,
            "portfolio": portfolio,
            "account_balance": usdt_balance,
        }
        
        logger.info(f"{symbol} 数据聚合完成")
        return aggregated
    
    def format_for_ai(self, data: Dict) -> str:
        """格式化数据为AI提示词 (每小时决策版)"""
        from datetime import datetime
        
        price_data = data.get("price_data", {})
        whale_data = data.get("whale_data", {})
        portfolio = data.get("portfolio", {})
        
        ticker = price_data.get("ticker", {})
        klines_1h = price_data.get("klines_1h", [])
        klines_15m = price_data.get("klines_15m", [])
        order_book = price_data.get("order_book", {})
        premium = price_data.get("premium_index", {})
        
        symbol = data.get("symbol", "")
        
        # 格式化1小时K线 (最近6根)
        kline_1h_text = ""
        if klines_1h:
            for k in klines_1h[-6:]:
                time_str = datetime.fromtimestamp(k['time']).strftime("%H:%M")
                direction = "上涨" if k['close'] >= k['open'] else "下跌"
                kline_1h_text += f"- {time_str}: {k['open']} → {k['close']} ({direction})\n"
        
        # 格式化15分钟K线 (最近4根)
        kline_15m_text = ""
        if klines_15m:
            for k in klines_15m[-4:]:
                time_str = datetime.fromtimestamp(k['time']).strftime("%H:%M")
                kline_15m_text += f"- {time_str}: {k['open']} → {k['close']}\n"
        
        # 格式化新闻
        news_list = whale_data.get("news", [])
        news_text = ""
        if news_list:
            for i, news in enumerate(news_list[:3], 1):
                news_text += f"{i}. {news.get('title', '无')}\n"
        else:
            news_text = "无最新新闻"
        
        # 格式化大额转账
        whale_alerts = whale_data.get("whale_alerts", [])
        whale_text = ""
        if whale_alerts:
            from datetime import datetime
            for i, alert in enumerate(whale_alerts[:5], 1):  # 最多显示5笔
                time_str = datetime.fromtimestamp(alert.get("time", 0)).strftime("%H:%M") if alert.get("time") else "未知"
                amount_usd = alert.get("amount_usd", 0)
                symbol = alert.get("symbol", "")
                whale_text += f"{i}. {time_str} | {symbol} | ${amount_usd:,.0f}\n"
        else:
            whale_text = "无大额转账"
        
        # 账户余额
        account_balance = data.get("account_balance", 0)
        
        prompt = f"""## 交易对
{symbol}

## 账户资金
- USDT可用余额: ${account_balance:,.2f}

## 持仓状态
- 当前持仓: {portfolio.get('current_position', 0)} {symbol}
- 开仓价格: ${portfolio.get('entry_price', 0)}
- 当前盈亏: {portfolio.get('unrealized_pnl', 0)}%
- 持仓时间: {portfolio.get('holding_hours', 0)}小时

## 价格数据
- 当前价格: ${ticker.get('current_price', 0)}
- 24h涨跌: {ticker.get('price_change_percent', 0)}%
- 24h最高: ${ticker.get('high_24h', 0)}
- 24h最低: ${ticker.get('low_24h', 0)}
- 24h成交量: ${ticker.get('quote_volume_24h', 0):,.0f}

## 技术分析

### 1小时K线 (最近6根)
{kline_1h_text}

### 15分钟K线 (最近4根)
{kline_15m_text}

### 订单簿
- 买方深度: ${order_book.get('bid_depth', 0):,.0f} USDT
- 卖方深度: ${order_book.get('ask_depth', 0):,.0f} USDT
- 买卖价差: ${order_book.get('spread', 0)}

### 资金费率
- 当前费率: {premium.get('funding_rate', 0) * 100}%

## 链上/鲸鱼数据 (大额转账)
{whale_text}

## 综合情绪: {whale_data.get('sentiment', 'neutral')}

## 新闻 (最近3条)
{news_text}

## 风控参数
- 最大止损: 7%
- 止盈目标: 15%
- 风险偏好: 保守

请根据以上数据做出交易决策。输出JSON格式: {{"decision": "BUY"|"SELL"|"HOLD", "confidence": 0.0-1.0, "amount": 数量, "stop_loss": 止损价, "take_profit": 止盈价, "reason": "理由"}}
"""
        return prompt
