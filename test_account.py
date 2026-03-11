#!/usr/bin/env python3
"""测试脚本：获取账户信息"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading.binance_client import BinanceClient

def main():
    print("=" * 50)
    print("  账户信息查询")
    print("=" * 50)
    
    client = BinanceClient()
    if not client.client:
        print("❌ Binance 连接失败")
        return
    
    # 获取账户信息
    print("\n📊 账户余额:")
    print("-" * 30)
    try:
        account = client.client.get_account()
        for balance in account["balances"]:
            free = float(balance["free"])
            locked = float(balance["locked"])
            if free > 0 or locked > 0:
                print(f"  {balance['asset']:5s} | 可用: {free:>15.6f} | 冻结: {locked:>15.6f}")
    except Exception as e:
        print(f"获取余额失败: {e}")
    
    # 获取当前价格
    print("\n📈 当前价格:")
    print("-" * 30)
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
    for symbol in symbols:
        try:
            price = client.get_current_price(symbol)
            if price:
                print(f"  {symbol}: ${price:,.2f}")
        except Exception as e:
            print(f"  {symbol}: 获取失败")
    
    # 获取USDT余额
    print("\n💰 USDT 余额:")
    print("-" * 30)
    usdt_balance = client.get_balance("USDT")
    print(f"  USDT: ${usdt_balance:,.2f}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
