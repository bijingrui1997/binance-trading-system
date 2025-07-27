#!/usr/bin/env python3
"""币安历史数据系统快速开始脚本"""
import os
from datetime import datetime, timedelta

from historical_data_manager import HistoricalDataManager


def quick_start_demo():
    """快速开始演示"""
    print("=" * 60)
    print("币安历史数据系统 - 快速开始演示")
    print("=" * 60)
    
    # 初始化管理器
    manager = HistoricalDataManager()
    
    # 设置演示参数
    symbol = "BTCUSDT"
    start_date = "2024-01-01"
    end_date = "2024-01-03"
    
    print(f"\n1. 下载 {symbol} 的1小时K线数据")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print("-" * 40)
    
    try:
        # 下载数据
        downloaded_files = manager.download_data(
            symbols=[symbol],
            data_type="klines",
            interval="1h",
            start_date=start_date,
            end_date=end_date
        )
        print(f"✓ 下载完成，共 {len(downloaded_files)} 个文件")
        
        # 读取数据
        print(f"\n2. 读取下载的数据")
        print("-" * 40)
        
        df = manager.read_data(
            symbol=symbol,
            data_type="klines",
            interval="1h",
            start_date=start_date,
            end_date=end_date
        )
        
        if not df.empty:
            print(f"✓ 数据读取成功")
            print(f"  数据形状: {df.shape}")
            print(f"  时间范围: {df.iloc[0, 0]} 到 {df.iloc[-1, 0]}")
            print(f"  最高价: {df['high'].max():.2f}")
            print(f"  最低价: {df['low'].min():.2f}")
            print(f"  平均成交量: {df['volume'].mean():.2f}")
            
            print(f"\n  前5行数据:")
            print(df[['open_time', 'open', 'high', 'low', 'close', 'volume']].head())
        else:
            print("✗ 未找到数据")
        
        # 查看数据信息
        print(f"\n3. 查看数据信息")
        print("-" * 40)
        
        info = manager.get_data_info(
            symbol=symbol,
            data_type="klines",
            interval="1h"
        )
        
        print(f"✓ 数据信息:")
        print(f"  交易对: {info['symbol']}")
        print(f"  数据类型: {info['data_type']}")
        print(f"  K线间隔: {info['interval']}")
        print(f"  文件数量: {info['files_count']}")
        print(f"  时间范围: {info['date_range']}")
        
        # 存储统计
        print(f"\n4. 存储统计信息")
        print("-" * 40)
        
        stats = manager.get_storage_stats()
        print(f"✓ 存储统计:")
        print(f"  数据目录: {stats['data_directory']}")
        print(f"  总大小: {stats['total_size_mb']:.2f} MB")
        print(f"  总文件数: {stats['total_files']}")
        
        # 本地交易对
        local_symbols = manager.get_local_symbols("spot", "klines")
        print(f"  本地K线交易对: {len(local_symbols)} 个")
        if local_symbols:
            print(f"  交易对列表: {', '.join(local_symbols[:5])}{'...' if len(local_symbols) > 5 else ''}")
        
        print(f"\n5. 演示完成！")
        print("=" * 60)
        print("\n接下来你可以:")
        print("• 使用 python cli.py --help 查看命令行工具")
        print("• 使用 python example_usage.py 查看更多示例")
        print("• 查看 README.md 了解详细文档")
        print("• 修改配置文件 config.py 自定义设置")
        
    except Exception as e:
        print(f"✗ 演示过程中出错: {e}")
        print("\n请检查:")
        print("• 网络连接是否正常")
        print("• 是否安装了所有依赖包")
        print("• 数据目录是否有写入权限")


def interactive_demo():
    """交互式演示"""
    print("=" * 60)
    print("币安历史数据系统 - 交互式演示")
    print("=" * 60)
    
    manager = HistoricalDataManager()
    
    while True:
        print("\n请选择操作:")
        print("1. 下载数据")
        print("2. 读取数据")
        print("3. 查看信息")
        print("4. 存储统计")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            # 下载数据
            symbol = input("请输入交易对 (默认: BTCUSDT): ").strip() or "BTCUSDT"
            interval = input("请输入K线间隔 (默认: 1h): ").strip() or "1h"
            
            # 默认下载最近3天的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            print(f"\n下载 {symbol} 的 {interval} K线数据 ({start_date} 到 {end_date})...")
            
            try:
                downloaded_files = manager.download_data(
                    symbols=[symbol],
                    data_type="klines",
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date
                )
                print(f"✓ 下载完成，共 {len(downloaded_files)} 个文件")
            except Exception as e:
                print(f"✗ 下载失败: {e}")
        
        elif choice == '2':
            # 读取数据
            symbol = input("请输入交易对 (默认: BTCUSDT): ").strip() or "BTCUSDT"
            interval = input("请输入K线间隔 (默认: 1h): ").strip() or "1h"
            
            # 默认读取最近1天的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            print(f"\n读取 {symbol} 的 {interval} K线数据 ({start_date} 到 {end_date})...")
            
            try:
                df = manager.read_data(
                    symbol=symbol,
                    data_type="klines",
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not df.empty:
                    print(f"✓ 数据读取成功")
                    print(f"  数据形状: {df.shape}")
                    print(f"  时间范围: {df.iloc[0, 0]} 到 {df.iloc[-1, 0]}")
                    print(f"  最高价: {df['high'].max():.2f}")
                    print(f"  最低价: {df['low'].min():.2f}")
                    
                    show_data = input("是否显示前5行数据? (y/N): ").strip().lower()
                    if show_data == 'y':
                        print(df[['open_time', 'open', 'high', 'low', 'close', 'volume']].head())
                else:
                    print("✗ 未找到数据")
            except Exception as e:
                print(f"✗ 读取失败: {e}")
        
        elif choice == '3':
            # 查看信息
            symbol = input("请输入交易对 (默认: BTCUSDT): ").strip() or "BTCUSDT"
            interval = input("请输入K线间隔 (默认: 1h): ").strip() or "1h"
            
            try:
                info = manager.get_data_info(
                    symbol=symbol,
                    data_type="klines",
                    interval=interval
                )
                
                print(f"\n✓ {symbol} 数据信息:")
                print(f"  数据类型: {info['data_type']}")
                print(f"  K线间隔: {info['interval']}")
                print(f"  文件数量: {info['files_count']}")
                print(f"  时间范围: {info['date_range']}")
            except Exception as e:
                print(f"✗ 查询失败: {e}")
        
        elif choice == '4':
            # 存储统计
            try:
                stats = manager.get_storage_stats()
                print(f"\n✓ 存储统计信息:")
                print(f"  数据目录: {stats['data_directory']}")
                print(f"  总大小: {stats['total_size_mb']:.2f} MB")
                print(f"  总文件数: {stats['total_files']}")
                
                for market_type, market_stats in stats['market_types'].items():
                    print(f"  {market_type}: {market_stats['file_count']} 文件, {market_stats['size_mb']:.2f} MB")
                
                # 显示本地交易对
                local_symbols = manager.get_local_symbols("spot", "klines")
                if local_symbols:
                    print(f"  本地K线交易对: {len(local_symbols)} 个")
                    print(f"  交易对: {', '.join(local_symbols[:10])}{'...' if len(local_symbols) > 10 else ''}")
            except Exception as e:
                print(f"✗ 查询失败: {e}")
        
        elif choice == '5':
            print("\n感谢使用币安历史数据系统！")
            break
        
        else:
            print("\n无效选择，请重新输入")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_demo()
    else:
        quick_start_demo()


if __name__ == '__main__':
    main()