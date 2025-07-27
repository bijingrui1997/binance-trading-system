"""币安历史数据系统使用示例"""
import pandas as pd
from datetime import datetime, timedelta

from historical_data_manager import HistoricalDataManager
from config import DEFAULT_CONFIG


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 初始化数据管理器
    manager = HistoricalDataManager()
    
    # 下载BTCUSDT的1小时K线数据
    print("\n1. 下载BTCUSDT的1小时K线数据...")
    downloaded_files = manager.download_data(
        symbols=["BTCUSDT"],
        market_type="spot",
        data_type="klines",
        interval="1h",
        start_date="2024-01-01",
        end_date="2024-01-31",
        download_monthly=True,
        download_daily=False  # 只下载月度数据以节省时间
    )
    
    print(f"下载完成，共 {len(downloaded_files)} 个文件")
    
    # 读取数据
    print("\n2. 读取BTCUSDT数据...")
    df = manager.read_data(
        symbol="BTCUSDT",
        market_type="spot",
        data_type="klines",
        interval="1h",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    
    if not df.empty:
        print(f"数据形状: {df.shape}")
        print(f"时间范围: {df['open_time'].min()} 到 {df['open_time'].max()}")
        print("\n前5行数据:")
        print(df.head())
        
        # 简单的数据分析
        print("\n3. 简单数据分析:")
        print(f"最高价: {df['high'].max():.2f}")
        print(f"最低价: {df['low'].min():.2f}")
        print(f"平均成交量: {df['volume'].mean():.2f}")
    else:
        print("未读取到数据")


def example_multiple_symbols():
    """多交易对下载示例"""
    print("\n=== 多交易对下载示例 ===")
    
    manager = HistoricalDataManager()
    
    # 下载多个交易对的数据
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    print(f"\n下载多个交易对数据: {symbols}")
    
    downloaded_files = manager.download_data(
        symbols=symbols,
        market_type="spot",
        data_type="klines",
        interval="4h",
        start_date="2024-01-01",
        end_date="2024-01-07",
        download_monthly=False,
        download_daily=True
    )
    
    print(f"下载完成，共 {len(downloaded_files)} 个文件")
    
    # 读取每个交易对的数据
    for symbol in symbols:
        print(f"\n读取 {symbol} 数据...")
        df = manager.read_data(
            symbol=symbol,
            market_type="spot",
            data_type="klines",
            interval="4h",
            start_date="2024-01-01",
            end_date="2024-01-07"
        )
        
        if not df.empty:
            print(f"{symbol} 数据行数: {len(df)}")
            print(f"价格范围: {df['low'].min():.2f} - {df['high'].max():.2f}")
        else:
            print(f"{symbol} 无数据")


def example_chunk_reading():
    """分块读取示例"""
    print("\n=== 分块读取示例 ===")
    
    manager = HistoricalDataManager()
    
    # 先确保有数据
    manager.download_data(
        symbols=["ETHUSDT"],
        market_type="spot",
        data_type="klines",
        interval="1m",
        start_date="2024-01-01",
        end_date="2024-01-03",
        download_monthly=False,
        download_daily=True
    )
    
    print("\n分块读取ETHUSDT数据...")
    chunk_generator = manager.read_data(
        symbol="ETHUSDT",
        market_type="spot",
        data_type="klines",
        interval="1m",
        start_date="2024-01-01",
        end_date="2024-01-03",
        chunk_size=1000  # 每块1000行
    )
    
    chunk_count = 0
    total_rows = 0
    
    for chunk in chunk_generator:
        chunk_count += 1
        total_rows += len(chunk)
        print(f"处理第 {chunk_count} 块，包含 {len(chunk)} 行数据")
        
        # 这里可以对每个块进行处理
        # 例如：计算技术指标、存储到数据库等
        
        if chunk_count >= 3:  # 只处理前3块作为示例
            break
    
    print(f"总共处理了 {chunk_count} 块，{total_rows} 行数据")


def example_data_info():
    """数据信息查询示例"""
    print("\n=== 数据信息查询示例 ===")
    
    manager = HistoricalDataManager()
    
    # 获取本地交易对列表
    print("\n本地可用的交易对:")
    local_symbols = manager.get_local_symbols(market_type="spot", data_type="klines")
    print(local_symbols[:10])  # 显示前10个
    
    # 获取特定交易对的数据信息
    if local_symbols:
        symbol = local_symbols[0]
        print(f"\n{symbol} 数据信息:")
        info = manager.get_data_info(
            symbol=symbol,
            market_type="spot",
            data_type="klines",
            interval="1h"
        )
        
        for key, value in info.items():
            print(f"{key}: {value}")
    
    # 获取存储统计信息
    print("\n存储统计信息:")
    stats = manager.get_storage_stats()
    print(f"数据目录: {stats['data_directory']}")
    print(f"总大小: {stats['total_size_mb']} MB")
    print(f"总文件数: {stats['total_files']}")
    
    for market_type, market_stats in stats['market_types'].items():
        print(f"{market_type}: {market_stats['file_count']} 文件, {market_stats['size_mb']} MB")


def example_download_and_read():
    """下载并读取的便捷方法示例"""
    print("\n=== 下载并读取便捷方法示例 ===")
    
    manager = HistoricalDataManager()
    
    # 使用便捷方法，自动检查本地数据并下载
    print("\n使用便捷方法获取ADAUSDT数据...")
    df = manager.download_and_read(
        symbol="ADAUSDT",
        market_type="spot",
        data_type="klines",
        interval="1h",
        start_date="2024-01-01",
        end_date="2024-01-07",
        force_download=False  # 如果本地有数据就不重新下载
    )
    
    if not df.empty:
        print(f"获取到 {len(df)} 行数据")
        print("\n数据概览:")
        print(df.describe())
    else:
        print("未获取到数据")


def example_different_data_types():
    """不同数据类型示例"""
    print("\n=== 不同数据类型示例 ===")
    
    manager = HistoricalDataManager()
    
    # 下载交易数据
    print("\n下载BTCUSDT交易数据...")
    manager.download_data(
        symbols=["BTCUSDT"],
        market_type="spot",
        data_type="trades",
        start_date="2024-01-01",
        end_date="2024-01-01",  # 只下载一天的数据
        download_monthly=False,
        download_daily=True
    )
    
    # 读取交易数据
    trades_df = manager.read_data(
        symbol="BTCUSDT",
        market_type="spot",
        data_type="trades",
        start_date="2024-01-01",
        end_date="2024-01-01"
    )
    
    if not trades_df.empty:
        print(f"交易数据行数: {len(trades_df)}")
        print("\n交易数据前5行:")
        print(trades_df.head())
    
    # 下载聚合交易数据
    print("\n下载BTCUSDT聚合交易数据...")
    manager.download_data(
        symbols=["BTCUSDT"],
        market_type="spot",
        data_type="aggTrades",
        start_date="2024-01-01",
        end_date="2024-01-01",
        download_monthly=False,
        download_daily=True
    )
    
    # 读取聚合交易数据
    agg_trades_df = manager.read_data(
        symbol="BTCUSDT",
        market_type="spot",
        data_type="aggTrades",
        start_date="2024-01-01",
        end_date="2024-01-01"
    )
    
    if not agg_trades_df.empty:
        print(f"聚合交易数据行数: {len(agg_trades_df)}")
        print("\n聚合交易数据前5行:")
        print(agg_trades_df.head())


def main():
    """主函数"""
    print("币安历史数据系统使用示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_multiple_symbols()
        example_chunk_reading()
        example_data_info()
        example_download_and_read()
        example_different_data_types()
        
        print("\n=== 所有示例运行完成 ===")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()