#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成回测引擎演示脚本

展示如何使用集成回测引擎进行自动数据下载和回测
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_backtest_engine import IntegratedBacktestEngine
from strategies import MovingAverageStrategy, RSIStrategy
from datetime import datetime, timedelta

def demo_basic_backtest():
    """演示基础回测功能"""
    print("\n" + "="*60)
    print("🚀 基础集成回测演示")
    print("="*60)
    
    # 创建集成引擎
    engine = IntegratedBacktestEngine(initial_capital=10000.0)
    
    # 创建移动平均策略
    strategy = MovingAverageStrategy(short_window=5, long_window=20, position_size=1000)
    
    # 设置回测参数
    symbol = "BTCUSDT"
    start_date = "2025-06-01"
    end_date = "2025-06-30"
    
    print(f"📊 回测参数:")
    print(f"   交易对: {symbol}")
    print(f"   策略: {strategy.name}")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print(f"   初始资金: ${engine.portfolio.initial_capital:,.2f}")
    
    # 运行回测
    results = engine.run_backtest_with_auto_download(
        symbol=symbol,
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=10000.0
    )
    
    if results:
        print(f"\n📈 回测结果:")
        print(f"   总收益率: {results.get('total_return', 0):.2%}")
        print(f"   最终资金: ${results.get('final_equity', 0):,.2f}")
        print(f"   交易次数: {results.get('total_trades', 0)}")
        print(f"   最大回撤: {results.get('max_drawdown', 0):.2%}")
    else:
        print("❌ 回测失败")
    
    return results

def demo_streaming_backtest():
    """演示流式回测功能"""
    print("\n" + "="*60)
    print("🌊 流式回测演示")
    print("="*60)
    
    # 创建集成引擎
    engine = IntegratedBacktestEngine(initial_capital=5000.0)
    
    # 创建RSI策略
    strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70, position_size=500)
    
    # 设置回测参数
    symbol = "ETHUSDT"
    start_date = "2025-07-01"
    end_date = "2025-07-31"
    
    print(f"📊 流式回测参数:")
    print(f"   交易对: {symbol}")
    print(f"   策略: {strategy.name}")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print(f"   初始资金: ${engine.portfolio.initial_capital:,.2f}")
    print(f"   分块大小: 1000 条记录")
    
    # 运行流式回测
    results = engine.run_streaming_backtest(
        symbol=symbol,
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        chunk_size=1000
    )
    
    if results:
        print(f"\n📈 流式回测结果:")
        print(f"   总收益率: {results.get('total_return', 0):.2%}")
        print(f"   最终资金: ${results.get('final_equity', 0):,.2f}")
        print(f"   交易次数: {results.get('total_trades', 0)}")
    else:
        print("❌ 流式回测失败")
    
    return results

def demo_data_download():
    """演示数据下载功能"""
    print("\n" + "="*60)
    print("📥 数据下载演示")
    print("="*60)
    
    # 创建集成引擎
    engine = IntegratedBacktestEngine()
    
    # 测试数据下载
    symbols = ["ADAUSDT", "DOTUSDT"]
    
    for symbol in symbols:
        print(f"\n📊 下载 {symbol} 数据...")
        
        # 设置较小的时间范围以确保数据存在
        start_date = "2025-07-25"
        end_date = "2025-07-26"
        
        data = engine.load_data_with_auto_download(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval="1h"
        )
        
        if data is not None and not data.empty:
            print(f"✅ {symbol} 数据下载成功: {len(data)} 条记录")
            print(f"   时间范围: {data.index[0]} 到 {data.index[-1]}")
            print(f"   价格范围: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
        else:
            print(f"❌ {symbol} 数据下载失败")

def demo_multi_strategy_comparison():
    """演示多策略对比"""
    print("\n" + "="*60)
    print("🔄 多策略对比演示")
    print("="*60)
    
    # 创建不同的策略
    strategies = {
        "MA_5_20": MovingAverageStrategy(short_window=5, long_window=20, position_size=1000),
        "MA_10_30": MovingAverageStrategy(short_window=10, long_window=30, position_size=1000),
        "RSI_14": RSIStrategy(rsi_period=14, oversold=30, overbought=70, position_size=1000)
    }
    
    symbol = "BNBUSDT"
    start_date = "2025-07-20"
    end_date = "2025-07-26"
    
    print(f"📊 策略对比参数:")
    print(f"   交易对: {symbol}")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print(f"   策略数量: {len(strategies)}")
    
    results = {}
    
    for strategy_name, strategy in strategies.items():
        print(f"\n🔄 测试策略: {strategy_name}")
        
        # 为每个策略创建独立的引擎
        engine = IntegratedBacktestEngine(initial_capital=5000.0)
        
        result = engine.run_backtest_with_auto_download(
            symbol=symbol,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=5000.0
        )
        
        if result:
            results[strategy_name] = result
            print(f"   ✅ 收益率: {result.get('total_return', 0):.2%}")
        else:
            print(f"   ❌ 测试失败")
    
    # 显示对比结果
    if results:
        print(f"\n📊 策略对比结果:")
        print(f"{'策略名称':<15} {'收益率':<10} {'交易次数':<8} {'最终资金':<12}")
        print("-" * 50)
        
        for name, result in results.items():
            return_rate = result.get('total_return', 0)
            trades = result.get('total_trades', 0)
            final_equity = result.get('final_equity', 0)
            print(f"{name:<15} {return_rate:>8.2%} {trades:>8} ${final_equity:>10,.2f}")
        
        # 找出最佳策略
        best_strategy = max(results.items(), key=lambda x: x[1].get('total_return', 0))
        print(f"\n🏆 最佳策略: {best_strategy[0]} (收益率: {best_strategy[1].get('total_return', 0):.2%})")

def main():
    """主函数"""
    print("🎯 集成回测引擎演示程序")
    print("本程序将演示集成回测引擎的各种功能")
    
    try:
        # 1. 基础回测演示
        demo_basic_backtest()
        
        # 2. 流式回测演示
        demo_streaming_backtest()
        
        # 3. 数据下载演示
        demo_data_download()
        
        # 4. 多策略对比演示
        demo_multi_strategy_comparison()
        
        print("\n" + "="*60)
        print("🎉 所有演示完成！")
        print("="*60)
        print("\n💡 提示:")
        print("   - 集成引擎会自动下载缺失的数据")
        print("   - 支持流式处理大量数据")
        print("   - 可以对比不同策略的表现")
        print("   - 数据会缓存到本地，下次使用更快")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()