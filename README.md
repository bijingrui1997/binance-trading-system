# 币安量化交易系统 - 历史数据模块

这是一个基于币安API的量化交易系统的第一版，专注于历史数据的下载、存储和读取功能。

## 功能特性

### 🚀 核心功能
- **多数据类型支持**: K线数据(klines)、交易数据(trades)、聚合交易数据(aggTrades)
- **多市场支持**: 现货(spot)、USD-M期货(um)、COIN-M期货(cm)
- **灵活时间范围**: 支持指定开始和结束日期的数据下载
- **多交易对**: 支持批量下载多个交易对的数据
- **智能存储**: 自动组织文件结构，支持月度和日度数据
- **顺序读取**: 支持按时间顺序读取指定范围的历史数据
- **分块处理**: 支持大数据集的分块读取，节省内存

### 📊 数据类型
- **K线数据**: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
- **交易数据**: 完整的交易记录
- **聚合交易数据**: 聚合的交易数据

### 🛠 实用工具
- **数据信息查询**: 查看本地数据的统计信息
- **存储管理**: 查看存储使用情况
- **数据清理**: 清理过期的历史数据

## 安装说明

### 环境要求
- Python 3.8+
- 网络连接（用于下载数据）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 依赖包说明
- `requests`: HTTP请求库，用于数据下载
- `pandas`: 数据处理和分析
- `numpy`: 数值计算
- `python-dateutil`: 日期处理
- `tqdm`: 进度条显示
- `pytest`: 测试框架

## 快速开始

### 基础使用

```python
from historical_data_manager import HistoricalDataManager

# 初始化数据管理器
manager = HistoricalDataManager()

# 下载BTCUSDT的1小时K线数据
manager.download_data(
    symbols=["BTCUSDT"],
    market_type="spot",
    data_type="klines",
    interval="1h",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# 读取数据
df = manager.read_data(
    symbol="BTCUSDT",
    market_type="spot",
    data_type="klines",
    interval="1h",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(f"数据形状: {df.shape}")
print(df.head())
```

### 批量下载多个交易对

```python
# 下载多个交易对
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
manager.download_data(
    symbols=symbols,
    market_type="spot",
    data_type="klines",
    interval="4h",
    start_date="2024-01-01",
    end_date="2024-01-07"
)

# 读取每个交易对的数据
for symbol in symbols:
    df = manager.read_data(
        symbol=symbol,
        market_type="spot",
        data_type="klines",
        interval="4h",
        start_date="2024-01-01",
        end_date="2024-01-07"
    )
    print(f"{symbol}: {len(df)} 行数据")
```

### 分块读取大数据集

```python
# 分块读取，节省内存
chunk_generator = manager.read_data(
    symbol="BTCUSDT",
    market_type="spot",
    data_type="klines",
    interval="1m",
    start_date="2024-01-01",
    end_date="2024-01-31",
    chunk_size=10000  # 每块10000行
)

for chunk in chunk_generator:
    # 处理每个数据块
    print(f"处理 {len(chunk)} 行数据")
    # 在这里进行数据分析或处理
```

### 便捷方法

```python
# 自动检查本地数据，如果没有则下载
df = manager.download_and_read(
    symbol="ETHUSDT",
    market_type="spot",
    data_type="klines",
    interval="1h",
    start_date="2024-01-01",
    end_date="2024-01-07",
    force_download=False  # 如果本地有数据就不重新下载
)
```

## 数据结构

### K线数据字段
| 字段名 | 说明 |
|--------|------|
| open_time | 开盘时间 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
| close_time | 收盘时间 |
| quote_asset_volume | 成交额 |
| number_of_trades | 成交笔数 |
| taker_buy_base_asset_volume | 主动买入成交量 |
| taker_buy_quote_asset_volume | 主动买入成交额 |

## 数据接口说明

**注意：不同市场类型的数据结构存在差异，请根据具体市场类型使用对应的字段说明。**

### 聚合交易数据 (Aggregate Trades)

#### 现货市场 (SPOT) 和 U本位合约 (UM)
- `agg_trade_id`: 聚合交易ID
- `price`: 价格
- `quantity`: 数量
- `first_trade_id`: 第一个交易ID
- `last_trade_id`: 最后一个交易ID
- `transact_time`: 交易时间（微秒时间戳）
- `is_buyer_maker`: 是否为买方挂单
- `is_best_match`: 是否为最佳匹配（仅现货市场有此字段）

#### 币本位合约 (CM)
- `agg_trade_id`: 聚合交易ID
- `price`: 价格
- `quantity`: 数量
- `first_trade_id`: 第一个交易ID
- `last_trade_id`: 最后一个交易ID
- `transact_time`: 交易时间（毫秒时间戳）
- `is_buyer_maker`: 是否为买方挂单
- **注意：币本位合约没有 `is_best_match` 字段**

### 交易数据 (Trades)

#### 现货市场 (SPOT) 和 U本位合约 (UM)
- `id`: 交易ID
- `price`: 价格
- `qty`: 数量
- `quote_qty`: 计价货币数量
- `time`: 交易时间（微秒时间戳）
- `is_buyer_maker`: 是否为买方挂单
- `is_best_match`: 是否为最佳匹配（仅现货市场有此字段）

#### 币本位合约 (CM)
- `id`: 交易ID
- `price`: 价格
- `qty`: 数量（张数）
- `base_qty`: 基础货币数量
- `time`: 交易时间（毫秒时间戳）
- `is_buyer_maker`: 是否为买方挂单
- **注意：币本位合约使用 `base_qty` 而非 `quote_qty`，且没有 `is_best_match` 字段**

### K线数据 (Klines)

#### 现货市场 (SPOT)
- `open_time`: 开盘时间（微秒时间戳）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `close_time`: 收盘时间（微秒时间戳）
- `quote_volume`: 计价货币成交量
- `count`: 成交笔数
- `taker_buy_volume`: 主动买入成交量
- `taker_buy_quote_volume`: 主动买入计价货币成交量
- `ignore`: 忽略字段

#### U本位合约 (UM) 和 币本位合约 (CM)
- `open_time`: 开盘时间（毫秒时间戳）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `close_time`: 收盘时间（毫秒时间戳）
- `quote_volume`: 计价货币成交量
- `count`: 成交笔数
- `taker_buy_volume`: 主动买入成交量
- `taker_buy_quote_volume`: 主动买入计价货币成交量
- `ignore`: 忽略字段

**时间戳说明：**
- 现货市场使用微秒时间戳（16位数字）
- 合约市场使用毫秒时间戳（13位数字）

## 文件结构

```
binance_trading_system/
├── config.py                    # 配置文件
├── data_downloader.py           # 数据下载器
├── data_reader.py               # 数据读取器
├── historical_data_manager.py   # 历史数据管理器
├── example_usage.py             # 使用示例
├── test_system.py               # 测试文件
├── requirements.txt             # 依赖包
├── README.md                    # 说明文档
└── data/                        # 数据存储目录
    ├── spot/                    # 现货数据
    │   ├── monthly/             # 月度数据
    │   │   ├── klines/
    │   │   ├── trades/
    │   │   └── aggTrades/
    │   └── daily/               # 日度数据
    │       ├── klines/
    │       ├── trades/
    │       └── aggTrades/
    ├── um/                      # USD-M期货数据
    └── cm/                      # COIN-M期货数据
```

## 高级功能

### 数据信息查询

```python
# 获取数据信息
info = manager.get_data_info(
    symbol="BTCUSDT",
    market_type="spot",
    data_type="klines",
    interval="1h"
)
print(info)

# 获取本地交易对列表
local_symbols = manager.get_local_symbols("spot", "klines")
print(f"本地交易对: {local_symbols}")

# 获取存储统计
stats = manager.get_storage_stats()
print(f"总大小: {stats['total_size_mb']} MB")
print(f"总文件数: {stats['total_files']}")
```

### 数据清理

```python
# 清理30天前的数据
deleted_count = manager.cleanup_old_data(days_to_keep=30)
print(f"删除了 {deleted_count} 个文件")
```

## 运行示例

```bash
# 运行使用示例
python example_usage.py

# 运行测试
python test_system.py
```

## 配置说明

可以通过修改 `config.py` 文件来自定义配置：

```python
# 修改默认配置
DEFAULT_CONFIG = {
    "data_directory": "/path/to/your/data",  # 自定义数据目录
    "market_type": "spot",
    "data_type": "klines",
    "interval": "1h",
    "start_date": "2020-01-01",
    "symbols": ["BTCUSDT", "ETHUSDT"],
    # ... 其他配置
}
```

## 注意事项

1. **网络要求**: 数据下载需要稳定的网络连接
2. **存储空间**: 历史数据文件较大，请确保有足够的存储空间
3. **下载限制**: 币安对数据下载有一定的频率限制，建议合理安排下载任务
4. **数据完整性**: 某些历史数据可能不完整或缺失，系统会自动跳过无效文件

## 错误处理

系统包含完善的错误处理机制：
- 网络错误时会自动重试
- 文件损坏时会跳过并继续处理
- 参数错误时会给出明确的错误信息

## 性能优化建议

1. **批量下载**: 一次下载多个交易对比单独下载更高效
2. **分块读取**: 对于大数据集使用分块读取避免内存溢出
3. **本地缓存**: 充分利用本地已下载的数据，避免重复下载
4. **并行处理**: 可以考虑使用多线程或多进程来加速数据处理

## 后续版本规划

- [ ] 实时数据接口
- [ ] 技术指标计算
- [ ] 数据可视化
- [ ] 策略回测框架
- [ ] 风险管理模块
- [ ] 实盘交易接口

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证。