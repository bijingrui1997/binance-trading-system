#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测系统主运行脚本 - 币安交易系统

功能:
- 加载历史数据
- 配置交易策略
- 运行回测
- 生成可视化报告
- 性能分析

使用示例:
    python run_backtest.py --symbol ETHUSDT --strategy ma --start 2024-01-01 --end 2024-12-31
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import json
from typing import Dict, List, Optional

# 导入自定义模块
from backtest_engine import BacktestEngine, Portfolio
from strategies import StrategyFactory
from visualizer import BacktestVisualizer

class BacktestRunner:
    """回测运行器"""
    
    def __init__(self):
        self.engine = BacktestEngine()
        self.visualizer = BacktestVisualizer()
        self.results = {}
    
    def load_data_from_csv(self, file_path: str) -> pd.DataFrame:
        """从CSV文件加载数据"""
        try:
            df = pd.read_csv(file_path)
            
            # 检查必要的列
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # 尝试映射常见的列名
                column_mapping = {
                    'open_time': 'timestamp',
                    'time': 'timestamp',
                    'datetime': 'timestamp'
                }
                
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns and new_name in missing_columns:
                        df = df.rename(columns={old_name: new_name})
                        missing_columns.remove(new_name)
                
                if missing_columns:
                    raise ValueError(f"缺少必要的列: {missing_columns}")
            
            # 转换时间戳
            if df['timestamp'].dtype == 'object':
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            elif df['timestamp'].dtype in ['int64', 'float64']:
                # 假设是毫秒时间戳
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 确保数据类型正确
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 删除无效数据
            df = df.dropna()
            
            # 按时间排序
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            print(f"成功加载数据: {len(df)} 条记录")
            print(f"时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
            
            return df
            
        except Exception as e:
            print(f"加载数据失败: {e}")
            return pd.DataFrame()
    
    def find_data_file(self, symbol: str, data_dir: str = "data") -> Optional[str]:
        """查找数据文件"""
        # 可能的文件名模式
        patterns = [
            f"{symbol.lower()}_spot_klines_1h_top100.csv",
            f"{symbol.lower()}_spot_klines_1m_top100.csv",
            f"{symbol.lower()}_spot_klines_1s_top100.csv",
            f"{symbol.lower()}_klines.csv",
            f"{symbol.upper()}_klines.csv",
            f"{symbol.lower()}.csv",
            f"{symbol.upper()}.csv"
        ]
        
        # 搜索目录
        search_dirs = [
            data_dir,
            os.path.join(data_dir, "yesterday_top100_data"),
            os.path.join(data_dir, "historical"),
            "."
        ]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            for pattern in patterns:
                file_path = os.path.join(search_dir, pattern)
                if os.path.exists(file_path):
                    print(f"找到数据文件: {file_path}")
                    return file_path
        
        return None
    
    def run_backtest(self, symbol: str, strategy_name: str, 
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    initial_capital: float = 10000.0, data_file: Optional[str] = None,
                    strategy_params: Optional[Dict] = None) -> Dict:
        """运行回测"""
        
        print(f"\n=== 开始回测 ===")
        print(f"交易对: {symbol}")
        print(f"策略: {strategy_name}")
        print(f"初始资金: ${initial_capital:,.2f}")
        
        # 1. 加载数据
        if data_file and os.path.exists(data_file):
            data = self.load_data_from_csv(data_file)
        else:
            data_file = self.find_data_file(symbol)
            if not data_file:
                raise FileNotFoundError(f"未找到 {symbol} 的数据文件")
            data = self.load_data_from_csv(data_file)
        
        if data.empty:
            raise ValueError("数据为空")
        
        # 2. 过滤时间范围
        if start_date:
            start_dt = pd.to_datetime(start_date)
            data = data[data['timestamp'] >= start_dt]
        
        if end_date:
            end_dt = pd.to_datetime(end_date)
            data = data[data['timestamp'] <= end_dt]
        
        if data.empty:
            raise ValueError("指定时间范围内无数据")
        
        print(f"回测时间范围: {data['timestamp'].min()} 到 {data['timestamp'].max()}")
        print(f"数据点数量: {len(data)}")
        
        # 3. 创建策略
        strategy_params = strategy_params or {}
        strategy = StrategyFactory.create_strategy(strategy_name, **strategy_params)
        
        if not strategy:
            raise ValueError(f"未知策略: {strategy_name}")
        
        print(f"策略参数: {strategy_params}")
        
        # 4. 运行回测
        self.engine.load_data(data)
        self.engine.set_strategy(strategy)
        
        print("\n开始执行回测...")
        results = self.engine.run_backtest(initial_capital)
        
        # 5. 添加额外信息
        results.update({
            'symbol': symbol,
            'strategy_name': strategy_name,
            'strategy_params': strategy_params,
            'data_file': data_file,
            'backtest_period': {
                'start': data['timestamp'].min().isoformat(),
                'end': data['timestamp'].max().isoformat(),
                'days': (data['timestamp'].max() - data['timestamp'].min()).days
            }
        })
        
        self.results = results
        
        # 6. 打印结果摘要
        self.print_results_summary(results)
        
        return results
    
    def print_results_summary(self, results: Dict):
        """打印结果摘要"""
        print(f"\n=== 回测结果摘要 ===")
        print(f"总收益率: {results.get('total_return', 0):.2f}%")
        print(f"年化收益率: {results.get('annualized_return', 0):.2f}%")
        print(f"最大回撤: {results.get('max_drawdown', 0):.2f}%")
        print(f"夏普比率: {results.get('sharpe_ratio', 0):.3f}")
        print(f"波动率: {results.get('volatility', 0):.2f}%")
        print(f"总交易次数: {results.get('total_trades', 0)}")
        print(f"胜率: {results.get('win_rate', 0):.1f}%")
        
        if 'portfolio' in results:
            portfolio = results['portfolio']
            print(f"最终资金: ${portfolio.cash:.2f}")
            print(f"持仓市值: ${portfolio.market_value:.2f}")
            print(f"总权益: ${portfolio.total_equity:.2f}")
    
    def generate_report(self, output_dir: str = "backtest_results") -> Dict[str, str]:
        """生成可视化报告"""
        if not self.results:
            raise ValueError("请先运行回测")
        
        print(f"\n生成可视化报告到: {output_dir}")
        
        # 重新加载价格数据用于可视化
        data_file = self.results.get('data_file')
        if data_file and os.path.exists(data_file):
            price_data = self.load_data_from_csv(data_file)
        else:
            price_data = pd.DataFrame()
        
        # 生成所有图表
        saved_files = self.visualizer.generate_full_report(
            self.results, price_data, output_dir
        )
        
        # 保存结果JSON
        results_file = os.path.join(output_dir, 'backtest_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            # 转换不可序列化的对象
            serializable_results = self.results.copy()
            if 'portfolio' in serializable_results:
                del serializable_results['portfolio']  # Portfolio对象不可序列化
            
            json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)
        
        saved_files['results_json'] = results_file
        
        print("报告生成完成:")
        for name, path in saved_files.items():
            print(f"  {name}: {path}")
        
        return saved_files

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='币安交易系统回测工具')
    
    parser.add_argument('--symbol', type=str, default='ETHUSDT', 
                       help='交易对符号 (默认: ETHUSDT)')
    parser.add_argument('--strategy', type=str, default='ma', 
                       choices=['ma', 'rsi', 'bb', 'buy_hold'],
                       help='交易策略 (默认: ma)')
    parser.add_argument('--start', type=str, 
                       help='开始日期 (格式: YYYY-MM-DD)')
    parser.add_argument('--end', type=str, 
                       help='结束日期 (格式: YYYY-MM-DD)')
    parser.add_argument('--capital', type=float, default=10000.0,
                       help='初始资金 (默认: 10000)')
    parser.add_argument('--data-file', type=str,
                       help='数据文件路径')
    parser.add_argument('--output-dir', type=str, default='backtest_results',
                       help='输出目录 (默认: backtest_results)')
    
    # 策略参数
    parser.add_argument('--ma-short', type=int, default=5,
                       help='MA策略短期均线周期 (默认: 5)')
    parser.add_argument('--ma-long', type=int, default=20,
                       help='MA策略长期均线周期 (默认: 20)')
    parser.add_argument('--rsi-period', type=int, default=14,
                       help='RSI策略周期 (默认: 14)')
    parser.add_argument('--rsi-oversold', type=float, default=30,
                       help='RSI超卖阈值 (默认: 30)')
    parser.add_argument('--rsi-overbought', type=float, default=70,
                       help='RSI超买阈值 (默认: 70)')
    parser.add_argument('--bb-period', type=int, default=20,
                       help='布林带周期 (默认: 20)')
    parser.add_argument('--bb-std', type=float, default=2.0,
                       help='布林带标准差倍数 (默认: 2.0)')
    
    args = parser.parse_args()
    
    # 构建策略参数
    strategy_params = {}
    if args.strategy == 'ma':
        strategy_params = {
            'short_window': args.ma_short,
            'long_window': args.ma_long
        }
    elif args.strategy == 'rsi':
        strategy_params = {
            'period': args.rsi_period,
            'oversold_threshold': args.rsi_oversold,
            'overbought_threshold': args.rsi_overbought
        }
    elif args.strategy == 'bb':
        strategy_params = {
            'period': args.bb_period,
            'std_dev': args.bb_std
        }
    
    try:
        # 创建回测运行器
        runner = BacktestRunner()
        
        # 运行回测
        results = runner.run_backtest(
            symbol=args.symbol,
            strategy_name=args.strategy,
            start_date=args.start,
            end_date=args.end,
            initial_capital=args.capital,
            data_file=args.data_file,
            strategy_params=strategy_params
        )
        
        # 生成报告
        saved_files = runner.generate_report(args.output_dir)
        
        print(f"\n=== 回测完成 ===")
        print(f"查看详细报告: {args.output_dir}/")
        
    except Exception as e:
        print(f"回测失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()