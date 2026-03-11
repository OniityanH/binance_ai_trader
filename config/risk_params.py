# 风控参数

# 仓位管理
MAX_POSITION_PERCENT = 20  # 单币种最大仓位占比 (%)
MIN_ORDER_AMOUNT = 10       # 最小下单金额 (USDT)

# 止损止盈
DEFAULT_STOP_LOSS_PERCENT = 7   # 默认止损比例 (%)
DEFAULT_TAKE_PROFIT_PERCENT = 15 # 默认止盈比例 (%)
TRAILING_STOP_START = 10         # 移动止损启动盈利门槛 (%)
TRAILING_STOP_PERCENT = 5        # 移动止损回调比例 (%)

# 交易限制
MIN_CONFIDENCE = 0.6        # 最小信心度
MAX_CONSECUTIVE_LOSS = 2    # 最大连续止损次数
COOLDOWN_AFTER_LOSS = 60    # 止损后冷却时间 (分钟)
MIN_ORDER_INTERVAL = 5      # 同一币种最小下单间隔 (分钟)

# 禁止交易情形
MAX_PRICE_CHANGE_24H = 10   # 24h涨跌超过此比例禁止交易 (%)
