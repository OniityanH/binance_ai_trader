#!/usr/bin/env python3
"""
启动脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AITrader


if __name__ == "__main__":
    print("=" * 50)
    print("  Binance AI Trader 启动中...")
    print("=" * 50)
    
    trader = AITrader()
    trader.run()
