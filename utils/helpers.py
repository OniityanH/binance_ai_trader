import json
from typing import Any, Dict, Optional


def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
    """解析DeepSeek返回的JSON响应"""
    try:
        # 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试提取JSON部分
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return None


def format_price(price: float) -> str:
    """格式化价格显示"""
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:,.4f}"
    else:
        return f"{price:,.8f}"


def calculate_percentage_change(old: float, new: float) -> float:
    """计算百分比变化"""
    if old == 0:
        return 0
    return ((new - old) / old) * 100


def get_symbol_precision(symbol: str) -> int:
    """获取交易对的价格精度"""
    if symbol.endswith("USDT"):
        return 2
    elif symbol.endswith("BUSD"):
        return 2
    else:
        return 4
