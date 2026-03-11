from typing import Dict, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config.config import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.logger import logger
from utils.helpers import get_symbol_precision


class BinanceClient:
    """Binance 交易客户端"""
    
    def __init__(self):
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
            # 测试连接
            self.client.get_account()
            logger.info("Binance交易客户端初始化成功")
        except Exception as e:
            logger.error(f"Binance客户端初始化失败: {e}")
            self.client = None
    
    def get_balance(self, asset: str = "USDT") -> float:
        """获取余额"""
        try:
            if not self.client:
                return 0
            account = self.client.get_account()
            for balance in account["balances"]:
                if balance["asset"] == asset:
                    return float(balance["free"])
            return 0
        except Exception as e:
            logger.error(f"获取{asset}余额失败: {e}")
            return 0
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """获取当前持仓"""
        try:
            if not self.client:
                return None
            # 获取当前挂单
            open_orders = self.client.get_open_orders(symbol=symbol)
            if open_orders:
                return {"has_position": True, "orders": open_orders}
            
            # 获取24小时交易记录判断是否有持仓
            trades = self.client.get_my_trades(symbol=symbol, limit=1)
            if trades:
                last_trade = trades[0]
                return {
                    "has_position": True,
                    "last_trade_price": float(last_trade["price"]),
                    "last_trade_qty": float(last_trade["qty"]),
                    "is_buyer": last_trade["isBuyer"],
                }
            return {"has_position": False}
        except Exception as e:
            logger.error(f"获取{symbol}持仓失败: {e}")
            return None
    
    def market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """市价单"""
        try:
            if not self.client:
                return None
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            logger.info(f"市价单下单成功: {side} {quantity} {symbol}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Binance API错误: {e}")
            return None
        except Exception as e:
            logger.error(f"下单失败: {e}")
            return None
    
    def limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        """限价单"""
        try:
            if not self.client:
                return None
            precision = get_symbol_precision(symbol)
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=f"{price:.{precision}f}"
            )
            logger.info(f"限价单下单成功: {side} {quantity} {symbol} @ {price}")
            return order
        except Exception as e:
            logger.error(f"限价单下单失败: {e}")
            return None
    
    def stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Optional[Dict]:
        """止损单"""
        try:
            if not self.client:
                return None
            precision = get_symbol_precision(symbol)
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=quantity,
                stopPrice=f"{stop_price:.{precision}f}",
                price=f"{stop_price:.{precision}f}"
            )
            logger.info(f"止损单下单成功: {side} {quantity} {symbol} @ {stop_price}")
            return order
        except Exception as e:
            logger.error(f"止损单下单失败: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """撤单"""
        try:
            if not self.client:
                return False
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"撤单成功: {symbol} {order_id}")
            return True
        except Exception as e:
            logger.error(f"撤单失败: {e}")
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """获取当前价格"""
        try:
            if not self.client:
                return None
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker["price"])
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return None
