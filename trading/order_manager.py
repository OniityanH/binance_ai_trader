from typing import Dict, Optional
from datetime import datetime, timedelta
from .binance_client import BinanceClient
from config.risk_params import MIN_ORDER_INTERVAL
from utils.logger import logger


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.binance = BinanceClient()
        self.last_order_time: Dict[str, datetime] = {}  # symbol -> last order time
    
    def can_order(self, symbol: str) -> bool:
        """检查是否可以下单"""
        now = datetime.now()
        if symbol in self.last_order_time:
            elapsed = (now - self.last_order_time[symbol]).total_seconds() / 60
            if elapsed < MIN_ORDER_INTERVAL:
                logger.warning(f"{symbol} 下单间隔不足，还需 {MIN_ORDER_INTERVAL - elapsed:.1f} 分钟")
                return False
        return True
    
    def record_order(self, symbol: str):
        """记录下单时间"""
        self.last_order_time[symbol] = datetime.now()
    
    def execute_buy(self, symbol: str, amount: float, price_limit: float = None) -> bool:
        """执行买入"""
        if not self.can_order(symbol):
            return False
        
        # 获取当前价格
        current_price = self.binance.get_current_price(symbol)
        if not current_price:
            logger.error("无法获取当前价格")
            return False
        
        # 计算数量 (USDT / 价格)
        balance = self.binance.get_balance("USDT")
        if balance < amount:
            logger.error(f"USDT余额不足: {balance} < {amount}")
            return False
        
        quantity = amount / current_price
        # 保留合理精度
        quantity = round(quantity, 5)
        
        if price_limit:
            order = self.binance.limit_order(symbol, "BUY", quantity, price_limit)
        else:
            order = self.binance.market_order(symbol, "BUY", quantity)
        
        if order:
            self.record_order(symbol)
            logger.info(f"买入成功: {symbol} {quantity} @ {current_price}")
            return True
        
        return False
    
    def execute_sell(self, symbol: str, percent: float = 1.0, price_limit: float = None) -> bool:
        """执行卖出"""
        if not self.can_order(symbol):
            return False
        
        # 这里简化处理，实际需要查询持仓
        # 暂时返回False，因为获取持仓逻辑较复杂
        logger.warning("卖出功能需要完善持仓查询逻辑")
        return False
    
    def execute_order(self, decision: Dict, symbol: str, current_price: float) -> bool:
        """执行AI决策"""
        decision_type = decision.get("decision", "HOLD")
        
        if decision_type == "HOLD":
            logger.info("AI决策: 持有")
            return True
        
        if decision_type == "BUY":
            amount = decision.get("amount", 100)  # 默认100 USDT
            price_limit = decision.get("price_limit")
            if price_limit:
                price_limit = float(price_limit)
            return self.execute_buy(symbol, amount, price_limit)
        
        if decision_type == "SELL":
            percent = decision.get("amount", 1.0)
            price_limit = decision.get("price_limit")
            if price_limit:
                price_limit = float(price_limit)
            return self.execute_sell(symbol, percent, price_limit)
        
        return False
