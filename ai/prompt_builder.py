# 提示词构建器 - 已整合到 data_aggregator.py 和 deepseek_client.py
# 此文件保留用于扩展自定义提示词

from typing import Dict

def build_system_prompt(risk_level: str = "conservative") -> str:
    """构建系统提示词"""
    base = """你是一个专业的虚拟货币交易分析师和量化交易员。你需要根据提供的数据分析市场并做出买入/卖出/持有决策。"""
    
    if risk_level == "aggressive":
        risk_rules = "你可以承受较高风险，仓位可以更大胆。"
    elif risk_level == "conservative":
        risk_rules = "你必须谨慎操作，把风险控制放在第一位。"
    else:
        risk_rules = "你需要在风险和收益之间取得平衡。"
    
    return f"{base}\n\n{risk_rules}\n\n你必须输出JSON格式的决策，不要输出其他内容。"


def build_user_prompt(data: Dict, risk_params: Dict) -> str:
    """构建用户提示词"""
    # 具体实现已整合到 DataAggregator.format_for_ai()
    pass

__all__ = ["build_system_prompt", "build_user_prompt"]
