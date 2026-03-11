from typing import Dict, Optional
from datetime import datetime, timedelta
from config.risk_params import (
    MAX_CONSECUTIVE_LOSS,
    COOLDOWN_AFTER_LOSS,
    DEFAULT_STOP_LOSS_PERCENT,
    DEFAULT_TAKE_PROFIT_PERCENT,
)
from utils.logger import logger


class RiskManager:
    """风控管理器"""
    
    def __init__(self):
        self.consecutive_losses = 0
        self.last_loss_time: Optional[datetime] = None
        self.positions: Dict[str, Dict] = {}  # symbol -> position info
    
    def check_can_trade(self) -> bool:
        """检查是否可以交易"""
        # 检查冷却期
        if self.last_loss_time:
            elapsed = (datetime.now() - self.last_loss_time).total_seconds() / 60
            if elapsed < COOLDOWN_AFTER_LOSS:
                logger.warning(f"冷却期中，还需 {COOLDOWN_AFTER_LOSS - elapsed:.1f} 分钟")
                return False
        
        # 检查连续亏损
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSS:
            logger.warning(f"连续亏损 {self.consecutive_losses} 次，暂停交易")
            return False
        
        return True
    
    def record_loss(self):
        """记录亏损"""
        self.consecutive_losses += 1
        self.last_loss_time = datetime.now()
        logger.warning(f"连续亏损次数: {self.consecutive_losses}")
    
    def record_profit(self):
        """记录盈利"""
        if self.consecutive_losses > 0:
            self.consecutive_losses = 0
            logger.info("盈利重置连续亏损计数")
    
    def calculate_stop_loss(self, entry_price: float, direction: str = "long") -> float:
        """计算止损价格"""
        if direction == "long":
            return entry_price * (1 - DEFAULT_STOP_LOSS_PERCENT / 100)
        else:
            return entry_price * (1 + DEFAULT_STOP_LOSS_PERCENT / 100)
    
    def calculate_take_profit(self, entry_price: float, direction: str = "long") -> float:
        """计算止盈价格"""
        if direction == "long":
            return entry_price * (1 + DEFAULT_TAKE_PROFIT_PERCENT / 100)
        else:
            return entry_price * (1 - DEFAULT_TAKE_PROFIT_PERCENT / 100)
    
    def should_stop_loss(self, current_price: float, entry_price: float, direction: str = "long") -> bool:
        """是否应该止损"""
        if direction == "long":
            loss_percent = (entry_price - current_price) / entry_price * 100
        else:
            loss_percent = (current_price - entry_price) / entry_price * 100
        
        if loss_percent >= DEFAULT_STOP_LOSS_PERCENT:
            logger.warning(f"触发止损: 亏损 {loss_percent:.2f}%")
            return True
        return False
    
    def should_take_profit(self, current_price: float, entry_price: float, direction: str = "long") -> bool:
        """是否应该止盈"""
        if direction == "long":
            profit_percent = (current_price - entry_price) / entry_price * 100
        else:
            profit_percent = (entry_price - current_price) / entry_price * 100
        
        if profit_percent >= DEFAULT_TAKE_PROFIT_PERCENT:
            logger.info(f"触发止盈: 盈利 {profit_percent:.2f}%")
            return True
        return False
    
    def update_position(self, symbol: str, entry_price: float, quantity: float):
        """更新持仓信息"""
        self.positions[symbol] = {
            "entry_price": entry_price,
            "quantity": quantity,
            "entry_time": datetime.now(),
        }
        logger.info(f"更新持仓: {symbol} @ {entry_price} x {quantity}")
    
    def remove_position(self, symbol: str):
        """移除持仓"""
        if symbol in self.positions:
            del self.positions[symbol]
            logger.info(f"清除持仓: {symbol}")
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """获取持仓信息"""
        return self.positions.get(symbol)
