from typing import Dict, Optional
from openai import OpenAI
from config.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from config.risk_params import MIN_CONFIDENCE
from utils.logger import logger
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """你是一个专业的虚拟货币交易分析师和量化交易员。你需要根据提供的数据分析市场并做出买入/卖出/持有决策。

核心原则:
1. 永远把风险控制放在第一位
2. 只在高置信度时下单
3. 严格执行止损策略
4. 不追涨杀跌

你必须输出JSON格式的决策，不要输出其他内容。
"""

DECISION_JSON_TEMPLATE = """
输出格式 (JSON):
{
    "decision": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0-1.0,
    "amount": 建议数量(若是BUY) 或 比例(若是SELL，如0.5表示50%仓位),
    "price_limit": 限价价格(可选，空字符串表示市价),
    "stop_loss": 止损价格(必须设置),
    "take_profit": 止盈价格(可选),
    "reason": "决策理由(20字以内)"
}

重要提醒:
1. 如果当前有持仓，必须先考虑是否需要止损或止盈
2. 止损必须执行，不能抱有侥幸心理
3. confidence < 0.6 时必须 HOLD
4. 连续2次HOLD后才能再次考虑下单
"""


class DeepSeekClient:
    """DeepSeek AI 客户端"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.model = DEEPSEEK_MODEL
        logger.info(f"DeepSeek客户端初始化完成，使用模型: {self.model}")
    
    def make_decision(self, market_data: str) -> Optional[Dict]:
        """让AI做出交易决策"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": market_data + DECISION_JSON_TEMPLATE}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            content = response.choices[0].message.content
            logger.debug(f"AI原始响应: {content}")
            
            # 解析JSON
            decision = parse_json_response(content)
            if decision:
                logger.info(f"AI决策: {decision.get('decision')}, 信心度: {decision.get('confidence')}")
                return decision
            else:
                logger.error("AI响应解析失败")
                return None
                
        except Exception as e:
            logger.error(f"AI决策失败: {e}")
            return None
    
    def validate_decision(self, decision: Dict, current_price: float) -> Dict:
        """验证和修正决策"""
        if not decision:
            return {"decision": "HOLD", "confidence": 0, "reason": "AI解析失败"}
        
        # 置信度检查
        if decision.get("confidence", 0) < MIN_CONFIDENCE:
            decision["decision"] = "HOLD"
            decision["reason"] = f"信心度不足({decision.get('confidence')})"
            logger.info("信心度不足，强制HOLD")
        
        # 止损价格检查
        if decision.get("decision") in ["BUY", "SELL"]:
            if not decision.get("stop_loss"):
                decision["stop_loss"] = current_price * 0.93  # 默认7%止损
                logger.warning("未设置止损，使用默认7%")
        
        return decision
