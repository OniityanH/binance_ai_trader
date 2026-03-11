import time
from datetime import datetime
from aggregator.data_aggregator import DataAggregator
from ai.deepseek_client import DeepSeekClient
from trading.order_manager import OrderManager
from trading.risk_manager import RiskManager
from config.config import TRADING_SYMBOLS, TRADING_INTERVAL
from utils.logger import logger


# 每小时执行的秒数
HOURLY_INTERVAL = 3600


class AITrader:
    """AI交易主程序 (每小时决策版)"""
    
    def __init__(self):
        self.aggregator = DataAggregator()
        self.ai_client = DeepSeekClient()
        self.order_manager = OrderManager()
        self.risk_manager = RiskManager()
        logger.info("AI Trader 初始化完成")
        logger.info(f"交易币种: {TRADING_SYMBOLS}")
        logger.info(f"执行间隔: {TRADING_INTERVAL}")
    
    def trade_single_symbol(self, symbol: str):
        """交易单个币种"""
        logger.info(f"=== 开始分析 {symbol} ===")
        
        # 获取持仓信息
        position = self.risk_manager.get_position(symbol)
        portfolio = {}
        if position:
            portfolio = {
                "current_position": position["quantity"],
                "entry_price": position["entry_price"],
                "holding_hours": (datetime.now() - position["entry_time"]).total_seconds() / 3600,
            }
        
        # 1. 获取并聚合数据
        data = self.aggregator.aggregate(symbol, portfolio)
        
        # 2. 格式化数据为AI提示词
        prompt = self.aggregator.format_for_ai(data)
        
        # 3. 获取当前价格
        current_price = data["price_data"]["ticker"]["current_price"] if data["price_data"].get("ticker") else 0
        if not current_price:
            logger.error(f"无法获取 {symbol} 价格，跳过")
            return
        
        # 4. AI决策
        decision = self.ai_client.make_decision(prompt)
        if not decision:
            logger.error("AI决策失败")
            return
        
        # 5. 风控验证
        decision = self.ai_client.validate_decision(decision, current_price)
        
        # 6. 检查风控
        if not self.risk_manager.check_can_trade():
            logger.warning("风控检查不通过，暂停交易")
            return
        
        # 7. 执行订单
        success = self.order_manager.execute_order(decision, symbol, current_price)
        
        # 8. 更新风控状态
        if success:
            if decision.get("decision") == "BUY":
                # 更新持仓
                amount = decision.get("amount", 100)
                quantity = amount / current_price
                self.risk_manager.update_position(symbol, current_price, quantity)
                self.risk_manager.record_profit()
            elif decision.get("decision") == "SELL":
                self.risk_manager.remove_position(symbol)
                self.risk_manager.record_profit()
        else:
            # 如果执行失败且是止损场景
            if decision.get("decision") == "SELL":
                self.risk_manager.record_loss()
        
        logger.info(f"=== {symbol} 交易完成 ===\n")
    
    def run(self):
        """主循环"""
        logger.info(f"开始交易循环，监控: {TRADING_SYMBOLS}")
        
        while True:
            try:
                for symbol in TRADING_SYMBOLS:
                    self.trade_single_symbol(symbol)
                    time.sleep(1)  # 避免API限流
                
                # 等待下次执行 (每小时)
                logger.info(f"等待 1 小时后再次执行...")
                time.sleep(HOURLY_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("用户中断，退出交易")
                break
            except Exception as e:
                logger.error(f"交易循环异常: {e}")
                time.sleep(60)  # 异常后等待1分钟
    
    def _interval_to_seconds(self, interval: str) -> int:
        """将间隔转换为秒"""
        mapping = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
        }
        return mapping.get(interval, 300)


if __name__ == "__main__":
    trader = AITrader()
    trader.run()
