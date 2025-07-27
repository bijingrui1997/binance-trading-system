#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成回测引擎测试脚本
测试自动数据下载和流式回测功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_backtest_engine import IntegratedBacktestEngine
from strategies import StrategyFactory
from datetime import datetime, timedelta
import pandas as pd

def test_integrated_engine():
    """测试集成引擎功能"""
    print("=" * 60)
    print("🚀 集成回测引擎测试")
    print("=" * 60)
    
    # 创建集成引擎
    engine = IntegratedBacktestEngine(initial_capital=100000)
    
    # 创建策略
    strategy = StrategyFactory.create_strategy('moving_average', short_window=10, long_window=30)
    
    # 设置测试参数
    symbol = 'BTCUSDT'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 测试最近30天
    
    print(f"📊 测试参数:")
    print(f"   交易对: {symbol}")
    print(f"   开始日期: {start_date.strftime('%Y-%m-%d')}")
    print(f"   结束日期: {end_date.strftime('%Y-%m-%d')}")
    print(f"   策略: 移动平均线 (10/30)")
    print(f"   初始资金: $100,000")
    print()
    
    try:
        # 运行集成回测
        print("🔄 开始集成回测（自动下载数据）...")
        results = engine.run_backtest_with_auto_download(
            symbol=symbol,
            strategy=strategy,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='1h',
            market_type='spot'
        )
        
        if results:
            print("\n✅ 回测完成！")
            print("\n📈 回测结果:")
            print(f"   总收益率: {results.get('total_return', 0):.2%}")
            print(f"   年化收益率: {results.get('annualized_return', 0):.2%}")
            print(f"   最大回撤: {results.get('max_drawdown', 0):.2%}")
            print(f"   夏普比率: {results.get('sharpe_ratio', 0):.4f}")
            print(f"   总交易次数: {results.get('total_trades', 0)}")
            print(f"   胜率: {results.get('win_rate', 0):.1%}")
            
            # 显示资金曲线信息
            equity_curve = results.get('equity_curve', [])
            if equity_curve:
                print(f"\n💰 资金变化:")
                print(f"   初始资金: ${equity_curve[0].get('total_equity', 0):,.2f}")
                print(f"   最终资金: ${equity_curve[-1].get('total_equity', 0):,.2f}")
                print(f"   数据点数: {len(equity_curve)}")
        else:
            print("❌ 回测失败，未返回结果")
            
    except Exception as e:
        print(f"❌ 回测过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_data_download_only():
    """测试仅数据下载功能"""
    print("\n" + "=" * 60)
    print("📥 数据下载测试")
    print("=" * 60)
    
    engine = IntegratedBacktestEngine()
    
    # 测试数据下载
    symbol = 'ETHUSDT'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # 测试最近7天
    
    print(f"📊 下载参数:")
    print(f"   交易对: {symbol}")
    print(f"   开始日期: {start_date.strftime('%Y-%m-%d')}")
    print(f"   结束日期: {end_date.strftime('%Y-%m-%d')}")
    print(f"   时间间隔: 1h")
    print()
    
    try:
        print("🔄 开始下载数据...")
        data = engine.load_data_with_auto_download(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='1h',
            market_type='spot'
        )
        
        if data is not None and not data.empty:
            print("\n✅ 数据下载成功！")
            print(f"\n📊 数据信息:")
            print(f"   数据行数: {len(data)}")
            print(f"   时间范围: {data.index[0]} 到 {data.index[-1]}")
            print(f"   列名: {list(data.columns)}")
            print(f"\n📈 价格范围:")
            print(f"   最高价: ${data['high'].max():.2f}")
            print(f"   最低价: ${data['low'].min():.2f}")
            print(f"   开盘价: ${data['open'].iloc[0]:.2f}")
            print(f"   收盘价: ${data['close'].iloc[-1]:.2f}")
        else:
            print("❌ 数据下载失败或数据为空")
            
    except Exception as e:
        print(f"❌ 数据下载过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 集成回测引擎功能测试")
    print("测试自动数据下载和流式回测功能\n")
    
    # 测试1: 完整的集成回测
    test_integrated_engine()
    
    # 测试2: 仅数据下载
    test_data_download_only()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)