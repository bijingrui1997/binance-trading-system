# 集成回测引擎使用指南

## 概述

集成回测引擎 (`IntegratedBacktestEngine`) 是对原有回测系统的增强版本，它集成了数据下载和管理功能，能够在回测过程中自动下载缺失的数据，支持流式处理大量数据。

## 主要特性

### 🚀 自动数据下载
- 回测时自动检测数据是否存在
- 缺失数据时自动从币安下载
- 支持月度和日度数据下载
- 智能缓存，避免重复下载

### 🌊 流式处理
- 支持大数据集的分块处理
- 边下载边回测，提高效率
- 内存友好，适合长期回测

### 📊 多策略支持
- 兼容所有现有策略
- 支持多策略对比
- 支持多标的组合回测

## 快速开始

### 基础使用

```python
from integrated_backtest_engine import IntegratedBacktestEngine
from strategies import MovingAverageStrategy

# 创建集成引擎
engine = IntegratedBacktestEngine(initial_capital=10000.0)

# 创建策略
strategy = MovingAverageStrategy(short_window=5, long_window=20)

# 运行回测（会自动下载数据）
results = engine.run_backtest_with_auto_download(
    symbol="BTCUSDT",
    strategy=strategy,
    start_date="2025-06-01",
    end_date="2025-06-30",
    initial_capital=10000.0
)

if results:
    print(f"总收益率: {results['total_return']:.2%}")
    print(f"最终资金: ${results['final_equity']:,.2f}")
```

### 流式回测

```python
# 流式回测适合处理大量数据
results = engine.run_streaming_backtest(
    symbol="ETHUSDT",
    strategy=strategy,
    start_date="2025-01-01",
    end_date="2025-12-31",
    chunk_size=1000  # 每次处理1000条记录
)
```

### 多策略对比

```python
strategies = {
    "MA_5_20": MovingAverageStrategy(5, 20),
    "MA_10_30": MovingAverageStrategy(10, 30),
    "RSI_14": RSIStrategy(14)
}

results = {}
for name, strategy in strategies.items():
    engine = IntegratedBacktestEngine(initial_capital=5000.0)
    result = engine.run_backtest_with_auto_download(
        symbol="BTCUSDT",
        strategy=strategy,
        start_date="2025-06-01",
        end_date="2025-06-30",
        initial_capital=5000.0
    )
    results[name] = result

# 对比结果
for name, result in results.items():
    if result:
        print(f"{name}: {result['total_return']:.2%}")
```

## API 参考

### IntegratedBacktestEngine

#### 构造函数
```python
IntegratedBacktestEngine(initial_capital=10000.0, commission=0.001)
```

**参数:**
- `initial_capital`: 初始资金
- `commission`: 手续费率

#### 主要方法

##### run_backtest_with_auto_download
```python
run_backtest_with_auto_download(
    symbol: str,
    strategy: BaseStrategy,
    start_date: str,
    end_date: str,
    initial_capital: float,
    interval: str = '1h',
    market_type: str = 'spot'
) -> Optional[Dict[str, Any]]
```

运行带自动数据下载的回测。

**参数:**
- `symbol`: 交易对（如 "BTCUSDT"）
- `strategy`: 交易策略实例
- `start_date`: 开始日期（"YYYY-MM-DD"）
- `end_date`: 结束日期（"YYYY-MM-DD"）
- `initial_capital`: 初始资金
- `interval`: 时间间隔（'1m', '5m', '1h', '1d' 等）
- `market_type`: 市场类型（'spot', 'um', 'cm'）

**返回:**
- 回测结果字典或 None（失败时）

##### run_streaming_backtest
```python
run_streaming_backtest(
    symbol: str,
    strategy: BaseStrategy,
    start_date: str,
    end_date: str,
    chunk_size: int = 1000,
    interval: str = '1h',
    market_type: str = 'spot'
) -> Optional[Dict[str, Any]]
```

运行流式回测，适合大数据集。

**参数:**
- `chunk_size`: 每次处理的记录数
- 其他参数同 `run_backtest_with_auto_download`

##### load_data_with_auto_download
```python
load_data_with_auto_download(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = '1h',
    market_type: str = 'spot'
) -> Optional[pd.DataFrame]
```

加载数据，如果本地不存在则自动下载。

##### run_multi_symbol_backtest
```python
run_multi_symbol_backtest(
    symbols: List[str],
    strategy: BaseStrategy,
    start_date: str,
    end_date: str,
    weights: Optional[Dict[str, float]] = None,
    interval: str = '1h',
    market_type: str = 'spot'
) -> Optional[Dict[str, Any]]
```

运行多标的组合回测。

**参数:**
- `symbols`: 交易对列表
- `weights`: 权重分配字典（可选，默认等权重）

## 使用示例

### 示例1：基础回测

```python
#!/usr/bin/env python3
from integrated_backtest_engine import IntegratedBacktestEngine
from strategies import MovingAverageStrategy

def basic_backtest_example():
    # 创建引擎和策略
    engine = IntegratedBacktestEngine(initial_capital=10000.0)
    strategy = MovingAverageStrategy(short_window=5, long_window=20, position_size=1000)
    
    # 运行回测
    results = engine.run_backtest_with_auto_download(
        symbol="BTCUSDT",
        strategy=strategy,
        start_date="2025-06-01",
        end_date="2025-06-30",
        initial_capital=10000.0
    )
    
    if results:
        print(f"总收益率: {results['total_return']:.2%}")
        print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
        print(f"交易次数: {results['total_trades']}")
        print(f"最终资金: ${results['final_equity']:,.2f}")
    else:
        print("回测失败")

if __name__ == "__main__":
    basic_backtest_example()
```

### 示例2：流式回测

```python
def streaming_backtest_example():
    engine = IntegratedBacktestEngine(initial_capital=5000.0)
    strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)
    
    # 流式回测，适合长期数据
    results = engine.run_streaming_backtest(
        symbol="ETHUSDT",
        strategy=strategy,
        start_date="2025-01-01",
        end_date="2025-12-31",
        chunk_size=1000
    )
    
    if results:
        print(f"流式回测完成，收益率: {results['total_return']:.2%}")
```

### 示例3：多标的回测

```python
def multi_symbol_backtest_example():
    engine = IntegratedBacktestEngine(initial_capital=20000.0)
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    
    # 多标的回测
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    weights = {"BTCUSDT": 0.5, "ETHUSDT": 0.3, "BNBUSDT": 0.2}
    
    results = engine.run_multi_symbol_backtest(
        symbols=symbols,
        strategy=strategy,
        start_date="2025-06-01",
        end_date="2025-06-30",
        weights=weights
    )
    
    if results:
        print(f"组合收益率: {results['total_return']:.2%}")
        print(f"加权收益率: {results['weighted_return']:.2%}")
        
        # 显示各标的表现
        for symbol, result in results['symbol_results'].items():
            print(f"{symbol}: {result['total_return']:.2%}")
```

## 数据管理

### 数据存储结构

```
data/
├── spot/
│   ├── monthly/
│   │   └── klines/
│   │       └── BTCUSDT/
│   │           └── 1h/
│   │               ├── BTCUSDT-1h-2025-06.zip
│   │               └── BTCUSDT-1h-2025-07.zip
│   └── daily/
│       └── klines/
│           └── BTCUSDT/
│               └── 1h/
│                   ├── BTCUSDT-1h-2025-06-01.zip
│                   └── BTCUSDT-1h-2025-06-02.zip
└── um/  # 合约数据
    └── ...
```

### 数据下载策略

1. **优先级**: 月度数据 > 日度数据
2. **缓存**: 已下载的数据会缓存到本地
3. **增量**: 只下载缺失的数据
4. **容错**: 下载失败时会尝试其他数据源

## 性能优化

### 内存优化
- 使用流式处理减少内存占用
- 分块读取大文件
- 及时释放不需要的数据

### 速度优化
- 并行下载多个文件
- 智能缓存避免重复下载
- 预处理数据格式

### 网络优化
- 断点续传支持
- 重试机制
- 压缩传输

## 故障排除

### 常见问题

#### 1. 数据下载失败
```
❌ 下载失败: 404 Client Error
```

**解决方案:**
- 检查交易对名称是否正确
- 确认日期范围是否有效
- 尝试使用更早的日期

#### 2. 内存不足
```
❌ MemoryError: Unable to allocate array
```

**解决方案:**
- 使用流式回测 (`run_streaming_backtest`)
- 减小 `chunk_size` 参数
- 缩短回测时间范围

#### 3. 策略错误
```
❌ 策略执行失败
```

**解决方案:**
- 检查策略参数是否合理
- 确认数据格式是否正确
- 查看详细错误日志

### 调试技巧

1. **启用详细日志**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查数据质量**
```python
data = engine.load_data_with_auto_download("BTCUSDT", "2025-06-01", "2025-06-30")
print(data.info())
print(data.describe())
```

3. **监控下载进度**
```python
progress = engine.get_download_progress("BTCUSDT")
print(f"下载进度: {progress}")
```

## 最佳实践

### 1. 数据管理
- 定期清理旧数据
- 备份重要的回测结果
- 使用版本控制管理策略代码

### 2. 策略开发
- 先在小数据集上测试
- 使用参数优化找到最佳配置
- 进行样本外测试验证

### 3. 性能监控
- 监控内存使用情况
- 记录回测执行时间
- 定期检查数据完整性

### 4. 风险管理
- 设置合理的止损点
- 控制单次交易规模
- 分散投资降低风险

## 扩展功能

### 自定义数据源

可以扩展 `IntegratedBacktestEngine` 来支持其他数据源：

```python
class CustomIntegratedEngine(IntegratedBacktestEngine):
    def __init__(self, custom_downloader, **kwargs):
        super().__init__(**kwargs)
        self.downloader = custom_downloader
    
    def load_custom_data(self, source, **params):
        # 实现自定义数据加载逻辑
        pass
```

### 高级策略

集成引擎支持所有高级策略功能：

```python
class AdvancedStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Advanced")
        self.ml_model = load_model()  # 机器学习模型
    
    def generate_signal(self, current_data, index, full_data):
        # 使用机器学习预测
        features = self.extract_features(current_data)
        prediction = self.ml_model.predict(features)
        return self.convert_to_signal(prediction)
```

## 总结

集成回测引擎提供了一个完整的解决方案，从数据获取到策略回测，再到结果分析。它的主要优势包括：

- **自动化**: 无需手动下载数据
- **高效**: 支持流式处理和并行计算
- **灵活**: 兼容各种策略和数据源
- **可靠**: 完善的错误处理和恢复机制

通过合理使用这些功能，可以大大提高量化交易策略的开发和验证效率。