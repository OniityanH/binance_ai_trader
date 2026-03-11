# API 配置
import os
from dotenv import load_dotenv

load_dotenv()

# Binance API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# WhaleAlert API
WHALEALERT_API_KEY = os.getenv("WHALEALERT_API_KEY", "")

# CryptoCompare API
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")

# 交易参数 - 限制为6种主流币
TRADING_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT", 
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]
TRADING_INTERVAL = "1h"  # 每小时执行一次
