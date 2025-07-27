# 币安交易系统回测平台

一个功能完整的加密货币交易策略回测系统，支持多种技术指标策略和全过程可视化分析。

## 🚀 核心功能

### 回测引擎
- **完整的交易模拟**: 支持买入/卖出订单、持仓管理、资金管理
- **多种订单类型**: 市价单、限价单（未来扩展）
- **实时性能计算**: 收益率、夏普比率、最大回撤、波动率等
- **交易成本模拟**: 手续费、滑点等（可配置）

### 交易策略
- **移动平均线策略 (MA)**: 双均线交叉策略
- **RSI策略**: 基于相对强弱指数的超买超卖策略
- **布林带策略 (BB)**: 基于价格通道的突破策略
- **买入持有策略**: 基准对比策略
- **可扩展架构**: 轻松添加自定义策略

### 可视化分析
- **权益曲线图**: 资金变化趋势
- **价格走势与交易信号**: 买卖点标注
- **回撤分析图**: 风险评估
- **收益分布图**: 统计分析
- **交易分析图**: 交易行为分析
- **性能摘要报告**: 关键指标汇总

### Web界面
- **直观的策略配置**: 参数调整界面
- **实时回测执行**: 进度显示
- **交互式图表**: Plotly可视化
- **结果对比分析**: 多策略比较
- **报告导出**: 完整分析报告

## 📦 安装说明

### 1. 环境要求
- Python 3.8+
- 推荐使用虚拟环境

### 2. 安装依赖
```bash
# 克隆项目
git clone <repository-url>
cd binance_trading_system

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 特殊依赖说明

#### TA-Lib 安装
TA-Lib是技术指标计算库，安装可能需要额外步骤：

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

**Windows:**
```bash
# 下载预编译包
pip install TA-Lib
# 如果失败，从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载对应版本
```

**替代方案:**
如果TA-Lib安装困难，可以使用pandas-ta：
```bash
pip install pandas-ta
```
然后修改策略文件中的导入语句。

## 🎯 快速开始

### 1. 准备数据
确保有历史价格数据文件（CSV格式），包含以下列：
- `timestamp`: 时间戳
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

### 2. 命令行回测
```bash
# 基本回测
python run_backtest.py --symbol ETHUSDT --strategy ma

# 指定时间范围
python run_backtest.py --symbol ETHUSDT --strategy ma --start 2024-01-01 --end 2024-12-31

# 自定义策略参数
python run_backtest.py --symbol ETHUSDT --strategy ma --ma-short 5 --ma-long 20

# 使用指定数据文件
python run_backtest.py --symbol ETHUSDT --strategy rsi --data-file data/my_data.csv

# 查看所有选项
python run_backtest.py --help
```

### 3. Web界面
```bash
# 启动Web界面
streamlit run web_interface.py

# 浏览器访问 http://localhost:8501
```

### 4. 编程接口
```python
from run_backtest import BacktestRunner

# 创建回测运行器
runner = BacktestRunner()

# 运行回测
results = runner.run_backtest(
    symbol='ETHUSDT',
    strategy_name='ma',
    initial_capital=10000.0,
    strategy_params={
        'short_window': 5,
        'long_window': 20
    }
)

# 生成报告
saved_files = runner.generate_report('my_results')
```

## 📊 策略说明

### 移动平均线策略 (ma)
**原理**: 当短期均线上穿长期均线时买入，下穿时卖出

**参数**:
- `short_window`: 短期均线周期（默认5）
- `long_window`: 长期均线周期（默认20）

**适用场景**: 趋势明显的市场

### RSI策略 (rsi)
**原理**: 基于相对强弱指数判断超买超卖

**参数**:
- `period`: RSI计算周期（默认14）
- `oversold_threshold`: 超卖阈值（默认30）
- `overbought_threshold`: 超买阈值（默认70）

**适用场景**: 震荡市场

### 布林带策略 (bb)
**原理**: 价格触及布林带上轨时卖出，触及下轨时买入

**参数**:
- `period`: 移动平均周期（默认20）
- `std_dev`: 标准差倍数（默认2.0）

**适用场景**: 价格在通道内震荡的市场

### 买入持有策略 (buy_hold)
**原理**: 开始时买入并持有到结束

**参数**: 无

**适用场景**: 基准对比

## 📈 性能指标说明

### 收益指标
- **总收益率**: (最终权益 - 初始资金) / 初始资金 × 100%
- **年化收益率**: 按年化计算的收益率
- **累计收益**: 绝对收益金额

### 风险指标
- **最大回撤**: 从峰值到谷值的最大跌幅
- **波动率**: 收益率的标准差（年化）
- **夏普比率**: (年化收益率 - 无风险利率) / 年化波动率

### 交易指标
- **总交易次数**: 买入和卖出的总次数
- **胜率**: 盈利交易次数 / 总交易次数
- **平均持仓时间**: 每次交易的平均持续时间

## 🛠️ 自定义策略开发

### 1. 创建策略类
```python
from strategies import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=0.5):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # 实现你的策略逻辑
        # signals['signal'] = 1  # 买入信号
        # signals['signal'] = -1 # 卖出信号
        # signals['signal'] = 0  # 无信号
        
        return signals
```

### 2. 注册策略
```python
# 在strategies.py的StrategyFactory中添加
class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_name: str, **kwargs):
        if strategy_name == 'my_custom':
            return MyCustomStrategy(**kwargs)
        # ... 其他策略
```

### 3. 使用自定义策略
```python
results = runner.run_backtest(
    symbol='ETHUSDT',
    strategy_name='my_custom',
    strategy_params={
        'param1': 15,
        'param2': 0.3
    }
)
```

## 📁 项目结构

```
binance_trading_system/
├── backtest_engine.py      # 回测引擎核心
├── strategies.py           # 交易策略实现
├── visualizer.py          # 可视化模块
├── run_backtest.py        # 命令行接口
├── web_interface.py       # Web界面
├── example_backtest.py    # 使用示例
├── data_downloader.py     # 数据下载器
├── requirements.txt       # 依赖包列表
├── README_BACKTEST.md     # 回测系统文档
└── data/                  # 数据目录
    └── yesterday_top100_data/
        ├── ethusdt_spot_klines_1h_top100.csv
        └── ...
```

## 🔧 配置说明

### 回测参数
- `initial_capital`: 初始资金（默认10000 USD）
- `commission`: 手续费率（默认0.1%）
- `slippage`: 滑点（默认0.05%）

### 数据格式
CSV文件必须包含以下列（列名可以映射）：
```
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,3000.0,3010.0,2990.0,3005.0,1000.0
```

支持的时间戳格式：
- ISO格式: `2024-01-01 00:00:00`
- Unix时间戳: `1704067200000` (毫秒)
- 其他pandas可解析的格式

## 📊 示例用法

### 运行示例脚本
```bash
python example_backtest.py
```

示例包括：
1. **简单回测**: 基本的策略测试
2. **策略对比**: 多个策略的性能比较
3. **参数优化**: 寻找最佳参数组合
4. **自定义数据**: 使用模拟数据进行测试

### Web界面功能
1. **策略配置**: 在侧边栏选择策略和参数
2. **回测执行**: 点击按钮开始回测
3. **结果分析**: 查看详细的图表和指标
4. **报告导出**: 生成完整的分析报告

## 🚨 注意事项

### 数据质量
- 确保数据完整性，避免缺失值
- 检查时间戳的连续性
- 验证价格数据的合理性（high >= low等）

### 回测局限性
- **前瞻偏差**: 避免使用未来数据
- **生存偏差**: 考虑退市或停牌的影响
- **市场冲击**: 大额交易的价格影响
- **流动性**: 实际交易中的流动性限制

### 性能优化
- 大数据集可能需要较长计算时间
- 考虑使用数据采样进行快速测试
- 并行化多策略比较（未来版本）

## 🔮 未来计划

### v2.0 功能
- [ ] 多资产组合回测
- [ ] 期货和衍生品支持
- [ ] 实时数据接入
- [ ] 机器学习策略框架
- [ ] 风险管理模块

### v2.1 功能
- [ ] 策略优化算法
- [ ] 回测结果数据库存储
- [ ] API接口
- [ ] 云端部署支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd binance_trading_system

# 安装开发依赖
pip install -r requirements.txt
pip install -e .

# 运行测试
pytest tests/
```

### 代码规范
- 遵循PEP 8代码风格
- 添加类型提示
- 编写单元测试
- 更新文档

## 📄 许可证

MIT License - 详见LICENSE文件

## 📞 支持

如有问题或建议，请：
1. 查看文档和示例
2. 搜索已有的Issue
3. 创建新的Issue描述问题
4. 参与讨论和改进

---

**免责声明**: 本系统仅用于教育和研究目的。实际交易存在风险，请谨慎投资。