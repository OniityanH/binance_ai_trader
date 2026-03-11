# Binance AI Trader 项目架构

## 📐 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Binance AI Trader                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                     │
│  │  价格数据    │   │  鲸鱼动态    │   │   新闻数据   │                     │
│  │  模块        │   │   模块       │   │    模块      │                     │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                     │
│         │                  │                  │                              │
│         ▼                  ▼                  ▼                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                      数据聚合层 (Data Aggregator)                 │        │
│  │  - 统一数据格式                                                  │        │
│  │  - 数据清洗与验证                                                │        │
│  │  - 异常检测                                                      │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                    AI 决策层 (DeepSeek)                          │        │
│  │  - 构建提示词                                                     │        │
│  │  - 解析决策结果                                                  │        │
│  │  - 风险控制 (止损/止盈)                                          │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                    交易执行层 (Binance API)                      │        │
│  │  - 下单/平仓                                                     │        │
│  │  - 仓位管理                                                      │        │
│  │  - 风险检查                                                      │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 API 数据源设计

### 1. 价格数据模块

| 数据项 | API | 接口 | 备注 |
|--------|-----|------|------|
| 实时价格 | Binance | `GET /api/v3/ticker/24hr` | 免费，限频 |
| K线历史 | Binance | `GET /api/v3/klines` | 1m/5m/15m/1h/4h/1d |
| 订单簿 | Binance | `GET /api/v3/depth` | 深度数据 |
| 近期成交 | Binance | `GET /api/v3/trades` | 大户成交识别 |
| 资金费率 | Binance | `GET /api/v3/premiumIndex` | 多空情绪 |

**备选API (补充数据):**
- CoinGecko: `GET /coins/{id}/market_chart` (历史价格)
- CoinMarketCap: `GET v1/cryptocurrency/quotes/latest`

---

### 2. 鲸鱼动态模块

| 数据项 | API | 接口 | 备注 |
|--------|-----|------|------|
| 大额转账 | WhaleAlert | `GET /v1/transactions` | 免费有限额 |
| 交易所资金流向 | CryptoQuant | `GET /exchange/flow` | 需API Key |
| 链上巨鲸 | Glassnode | `GET /v1/metrics/entities` | 需API Key |
| 筹码分布 | IntoTheBlock | `GET /in_out_money` | 需API Key |

**备选方案 (免费):**
- On-chain data via free APIs (若上述需付费)
- Binance 大户持仓 (`GET /api/v3/ticker/holder`)

---

### 3. 新闻数据模块

| 数据项 | API | 接口 | 备注 |
|--------|-----|------|------|
| 币圈新闻 | CryptoPanic | `GET /api/v1/posts/` | 免费 |
| 新闻聚合 | CoinGecko | `GET /coins/{id}/market_data` | 带news字段 |
| 新闻 | CryptoCompare | `GET /news/` | 免费 |
| 新闻 | Bing News API | `GET /news/search` | 免费7天 |

**推荐组合:** CryptoCompare (主) + Bing News (补充)

---

### 4. AI 决策模块

| 项目 | 详情 |
|------|------|
| 模型 | DeepSeek Chat |
| 版本 | deepseek-chat |
| 调用方式 | OpenAI 兼容 API |

---

### 5. 交易执行模块

| 功能 | Binance API | 备注 |
|------|-------------|------|
| 市价单 | `POST /api/v3/order` (type=MARKET) | 快速成交 |
| 限价单 | `POST /api/v3/order` (type=LIMIT) | 更优价格 |
| 止盈止损 | `POST /api/v3/order` (type=STOP_LOSS_LIMIT) | 需参数 |
| 查询持仓 | `GET /api/v3/openOrders` | 当前仓位 |
| 撤单 | `DELETE /api/v3/order` | 取消挂单 |

**库:** `python-binance`

---

## 🔄 接口间数据传输格式

### 1. 价格数据 → 聚合层

```python
{
    "symbol": "BTCUSDT",
    "current_price": 67432.50,
    "price_change_24h": 2.34,
    "price_change_percent_24h": 3.61,
    "high_24h": 68000.00,
    "low_24h": 65000.00,
    "volume_24h": 1234567890.00,
    "klines": [
        {"time": 1234567890, "open": 67000, "high": 67500, "low": 66800, "close": 67432, "volume": 1234.5}
    ],
    "order_book": {
        "bids": [[67430, 1.5], [67429, 2.3]],
        "asks": [[67432, 0.8], [67433, 1.2]]
    }
}
```

### 2. 鲸鱼数据 → 聚合层

```python
{
    "whale_alerts": [
        {"time": 1234567890, "amount": 500, "from": "unknown", "to": "binance"}
    ],
    "exchange_flow": {
        "binance_inflow": 150000000,
        "binance_outflow": 120000000,
        "net_flow": 30000000
    },
    "holder_distribution": {
        "large_holders_percent": 45.2,
        "change_24h": 0.8
    }
}
```

### 3. 新闻数据 → 聚合层

```python
{
    "news": [
        {
            "title": "Bitcoin ETF inflows hit new high",
            "source": "CryptoCompare",
            "url": "https://...",
            "published_at": 1234567890,
            "sentiment": "positive"  # AI判断
        }
    ],
    "overall_sentiment": "bullish"  # 综合情绪
}
```

### 4. 聚合数据 → DeepSeek

```python
{
    "timestamp": 1234567890,
    "symbol": "BTCUSDT",
    "price_data": {...},
    "whale_data": {...},
    "news_data": {...},
    "portfolio": {
        "current_position": 0.0,  # 持仓数量
        "entry_price": 0.0,
        "unrealized_pnl": 0.0
    }
}
```

### 5. DeepSeek 决策 → 交易执行

```python
{
    "decision": "BUY" | "SELL" | "HOLD",
    "confidence": 0.85,  # 信心度 0-1
    "amount": 0.01,       # 数量 (BTC)
    "price_limit": 67500, # 限价单价格 (可选)
    "stop_loss": 65000,   # 止损价格
    "take_profit": 70000, # 止盈价格
    "reason": "..."       # 决策理由
}
```

---

## 🧠 DeepSeek 提示词设计

### 系统提示词 (System Prompt)

```
你是一个专业的虚拟货币交易分析师和量化交易员。你需要根据提供的数据分析市场并做出买入/卖出/持有决策。

核心原则:
1. 永远把风险控制放在第一位
2. 只在高置信度时下单
3. 严格执行止损策略
4. 不追涨杀跌

你必须输出JSON格式的决策，不要输出其他内容。
```

### 用户提示词模板 (User Prompt)

```python
SYSTEM_PROMPT = """你是一个专业的虚拟货币交易分析师。你的任务是分析以下数据并做出交易决策。

## 当前持仓状态
- 当前持仓: {position} {symbol}
- 开仓价格: {entry_price}
- 当前盈亏: {unrealized_pnl}%
- 持仓时间: {holding_hours}小时

## 价格数据
- 当前价格: ${current_price}
- 24h涨跌: {price_change_percent}%
- 24h最高: ${high_24h}
- 24h最低: ${low_24h}
- 24h成交量: {volume_24h}

## K线技术分析 (最近{kline_count}根{kline_interval})
{kline_data}

## 订单簿分析
- 买方深度: {bid_depth}
- 卖方深度: {ask_depth}
- 买卖价差: {spread}

## 鲸鱼动态
- 大额转账: {whale_transfers}
- 交易所资金净流入: ${exchange_net_flow}
- 巨鲸持仓变化: {whale_holder_change}%

## 新闻情绪
- 最新新闻: {news_summary}
- 综合情绪: {sentiment} (bullish/neutral/bearish)

## 风控参数
- 最大单笔仓位: {max_position}%
- 最大止损: {max_stop_loss}%
- 风险偏好: {risk_level}

请根据以上数据输出你的交易决策。

输出格式 (JSON):
{{
    "decision": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0-1.0,
    "amount": 建议数量(若是BUY) 或 比例(若是SELL，如0.5表示50%仓位),
    "price_limit": 限价价格(可选，空字符串表示市价),
    "stop_loss": 止损价格(必须设置),
    "take_profit": 止盈价格(可选),
    "reason": "决策理由(20字以内)"
}}

重要提醒:
1. 如果当前有持仓，必须先考虑是否需要止损或止盈
2. 止损必须执行，不能抱有侥幸心理
3. confidence < 0.6 时必须 HOLD
4. 连续2次HOLD后才能再次考虑下单
"""

# 补充的风控规则提示
RISK_CONTROL_PROMPT = """
## 强制止损规则 (必须遵守)
- 当持仓亏损超过 {max_loss}% 时，必须无条件止损
- 当价格跌破关键支撑位时，触发止损
- 止盈可灵活，但止损必须坚决

## 止盈策略
- 建议使用移动止损: 当盈利达到 {profit_target}% 后，启动追踪止损
- 分批止盈: 50% @ {tp1}, 30% @ {tp2}, 20% @ {tp3}

## 禁止交易情形
- 重大新闻发布前后1小时内
- 交易所维护期间
- 波动率异常高时 (如单日涨跌幅>10%)
- 连续止损2次后，必须暂停交易1小时
"""
```

---

## 📁 项目文件结构

```
binance_AI_trader/
├── venv/                    # Python虚拟环境
├── config/
│   ├── __init__.py
│   ├── config.py           # API配置
│   └── risk_params.py      # 风控参数
├── data/
│   ├── __init__.py
│   ├── price_fetcher.py    # 价格数据获取
│   ├── whale_fetcher.py    # 鲸鱼数据获取
│   └── news_fetcher.py     # 新闻数据获取
├── aggregator/
│   ├── __init__.py
│   └── data_aggregator.py  # 数据聚合
├── ai/
│   ├── __init__.py
│   ├── deepseek_client.py  # DeepSeek调用
│   └── prompt_builder.py   # 提示词构建
├── trading/
│   ├── __init__.py
│   ├── binance_client.py   # Binance交易
│   ├── order_manager.py    # 订单管理
│   └── risk_manager.py    # 风控执行
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志
│   └── helpers.py         # 工具函数
├── main.py                # 主程序
├── run.py                 # 启动脚本
├── requirements.txt       # 依赖
└── .env                   # 环境变量
```

---

## ⚙️ 依赖包 (requirements.txt)

```
python-binance>=1.0.19
openai>=1.0.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
loguru>=0.7.0
aiohttp>=3.9.0
```

---

## 🔄 工作流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  定时触发   │────▶│  获取数据   │────▶│  数据聚合   │
│  (如5分钟)  │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  执行订单   │◀────│  AI决策     │◀────│  构建提示词 │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 🚨 风控要点

1. **最大仓位控制**: 单币种不超过总资金的20%
2. **止损纪律**: 亏损7%必须止损，不得犹豫
3. **止盈策略**: 盈利15%启动移动止损
4. **下单间隔**: 同一币种至少间隔5分钟
5. **异常处理**: 连续2次止损后暂停1小时
6. **日志记录**: 记录所有决策和执行结果
