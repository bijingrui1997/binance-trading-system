#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测系统使用示例 - 币安交易系统

这个脚本演示了如何使用回测系统进行策略测试
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# 导入回测模块
from run_backtest import BacktestRunner

def example_simple_backtest():
    """简单回测示例"""
    print("=== 简单回测示例 ===")
    
    # 创建回测运行器
    runner = BacktestRunner()
    
    try:
        # 运行回测
        results = runner.run_backtest(
            symbol='ETHUSDT',
            strategy_name='ma',  # 移动平均线策略
            initial_capital=10000.0,
            strategy_params={
                'short_window': 5,
                'long_window': 20
            }
        )
        
        # 生成报告
        saved_files = runner.generate_report('example_results')
        
        print("\n回测完成！查看结果:")
        for name, path in saved_files.items():
            print(f"  {name}: {path}")
            
    except Exception as e:
        print(f"回测失败: {e}")

def example_strategy_comparison():
    """策略对比示例"""
    print("\n=== 策略对比示例 ===")
    
    strategies = [
        ('ma', {'short_window': 5, 'long_window': 20}),
        ('rsi', {'period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70}),
        ('bb', {'period': 20, 'std_dev': 2.0}),
        ('buy_hold', {})
    ]
    
    results_comparison = []
    
    for strategy_name, params in strategies:
        print(f"\n测试策略: {strategy_name}")
        
        try:
            runner = BacktestRunner()
            results = runner.run_backtest(
                symbol='ETHUSDT',
                strategy_name=strategy_name,
                initial_capital=10000.0,
                strategy_params=params
            )
            
            # 收集关键指标
            strategy_result = {
                'strategy': strategy_name,
                'total_return': results.get('total_return', 0),
                'max_drawdown': results.get('max_drawdown', 0),
                'sharpe_ratio': results.get('sharpe_ratio', 0),
                'total_trades': results.get('total_trades', 0),
                'win_rate': results.get('win_rate', 0)
            }
            
            results_comparison.append(strategy_result)
            
        except Exception as e:
            print(f"策略 {strategy_name} 测试失败: {e}")
    
    # 显示对比结果
    if results_comparison:
        print("\n=== 策略对比结果 ===")
        comparison_df = pd.DataFrame(results_comparison)
        print(comparison_df.to_string(index=False, float_format='%.2f'))
        
        # 找出最佳策略
        best_return = comparison_df.loc[comparison_df['total_return'].idxmax()]
        best_sharpe = comparison_df.loc[comparison_df['sharpe_ratio'].idxmax()]
        
        print(f"\n最佳收益策略: {best_return['strategy']} ({best_return['total_return']:.2f}%)")
        print(f"最佳夏普比率策略: {best_sharpe['strategy']} ({best_sharpe['sharpe_ratio']:.3f})")

def example_parameter_optimization():
    """参数优化示例"""
    print("\n=== 参数优化示例 ===")
    
    # 测试不同的移动平均线参数组合
    short_windows = [3, 5, 7, 10]
    long_windows = [15, 20, 25, 30]
    
    best_result = None
    best_params = None
    best_return = -float('inf')
    
    print("测试移动平均线参数组合...")
    
    for short in short_windows:
        for long in long_windows:
            if short >= long:
                continue
                
            try:
                runner = BacktestRunner()
                results = runner.run_backtest(
                    symbol='ETHUSDT',
                    strategy_name='ma',
                    initial_capital=10000.0,
                    strategy_params={
                        'short_window': short,
                        'long_window': long
                    }
                )
                
                total_return = results.get('total_return', 0)
                
                print(f"MA({short},{long}): {total_return:.2f}%")
                
                if total_return > best_return:
                    best_return = total_return
                    best_params = (short, long)
                    best_result = results
                    
            except Exception as e:
                print(f"MA({short},{long}) 测试失败: {e}")
    
    if best_result:
        print(f"\n最佳参数组合: MA({best_params[0]},{best_params[1]})")
        print(f"最佳收益率: {best_return:.2f}%")
        print(f"夏普比率: {best_result.get('sharpe_ratio', 0):.3f}")
        print(f"最大回撤: {best_result.get('max_drawdown', 0):.2f}%")

def example_custom_data():
    """自定义数据示例"""
    print("\n=== 自定义数据示例 ===")
    
    # 生成模拟数据
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='1H')
    np.random.seed(42)
    
    # 生成随机价格数据（模拟真实价格走势）
    price = 3000  # 初始价格
    prices = []
    
    for _ in range(len(dates)):
        # 随机游走模型
        change = np.random.normal(0, 0.02)  # 2%的标准差
        price *= (1 + change)
        prices.append(price)
    
    # 创建OHLCV数据
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.uniform(100, 1000, len(dates))
    })
    
    # 保存到临时文件
    temp_file = 'temp_custom_data.csv'
    data.to_csv(temp_file, index=False)
    
    try:
        # 使用自定义数据运行回测
        runner = BacktestRunner()
        results = runner.run_backtest(
            symbol='CUSTOM',
            strategy_name='ma',
            initial_capital=10000.0,
            data_file=temp_file,
            strategy_params={
                'short_window': 24,  # 24小时
                'long_window': 168   # 7天
            }
        )
        
        print(f"自定义数据回测完成")
        print(f"数据点数量: {len(data)}")
        print(f"总收益率: {results.get('total_return', 0):.2f}%")
        
        # 生成报告
        runner.generate_report('custom_data_results')
        
    except Exception as e:
        print(f"自定义数据回测失败: {e}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """主函数"""
    print("币安交易系统回测示例")
    print("=" * 50)
    
    # 检查数据文件是否存在
    data_dir = "data/yesterday_top100_data"
    if not os.path.exists(data_dir):
        print(f"警告: 数据目录 {data_dir} 不存在")
        print("请先运行数据下载脚本获取历史数据")
        print("或者查看 example_custom_data() 了解如何使用自定义数据")
        print()
    
    try:
        # 运行示例
        example_simple_backtest()
        example_strategy_comparison()
        example_parameter_optimization()
        example_custom_data()
        
        print("\n=== 所有示例完成 ===")
        print("\n提示:")
        print("1. 查看生成的报告文件了解详细结果")
        print("2. 运行 'streamlit run web_interface.py' 启动Web界面")
        print("3. 使用 'python run_backtest.py --help' 查看命令行选项")
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行失败: {e}")

if __name__ == '__main__':
    main()