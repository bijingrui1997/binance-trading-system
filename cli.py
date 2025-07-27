#!/usr/bin/env python3
"""币安历史数据系统命令行工具"""
import argparse
import sys
from datetime import datetime, timedelta

from historical_data_manager import HistoricalDataManager
from config import KLINE_INTERVALS, MARKET_TYPES, DATA_TYPES


def download_command(args):
    """下载数据命令"""
    manager = HistoricalDataManager(args.data_dir)
    
    symbols = args.symbols.split(',') if args.symbols else ["BTCUSDT"]
    
    print(f"开始下载数据...")
    print(f"交易对: {symbols}")
    print(f"市场类型: {args.market_type}")
    print(f"数据类型: {args.data_type}")
    if args.data_type == "klines":
        print(f"K线间隔: {args.interval}")
    print(f"时间范围: {args.start_date} 到 {args.end_date}")
    print("-" * 50)
    
    try:
        downloaded_files = manager.download_data(
            symbols=symbols,
            market_type=args.market_type,
            data_type=args.data_type,
            interval=args.interval,
            start_date=args.start_date,
            end_date=args.end_date,
            download_monthly=not args.skip_monthly,
            download_daily=not args.skip_daily
        )
        
        print(f"\n下载完成！共下载 {len(downloaded_files)} 个文件")
        if args.verbose:
            for file_path in downloaded_files:
                print(f"  - {file_path}")
                
    except Exception as e:
        print(f"下载失败: {e}")
        sys.exit(1)


def read_command(args):
    """读取数据命令"""
    manager = HistoricalDataManager(args.data_dir)
    
    print(f"读取 {args.symbol} 数据...")
    print(f"市场类型: {args.market_type}")
    print(f"数据类型: {args.data_type}")
    if args.data_type == "klines":
        print(f"K线间隔: {args.interval}")
    print(f"时间范围: {args.start_date} 到 {args.end_date}")
    print("-" * 50)
    
    try:
        df = manager.read_data(
            symbol=args.symbol,
            market_type=args.market_type,
            data_type=args.data_type,
            interval=args.interval,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if df.empty:
            print("未找到数据")
            return
        
        print(f"数据形状: {df.shape}")
        print(f"时间范围: {df.iloc[0, 0]} 到 {df.iloc[-1, 0]}")
        
        if args.data_type == "klines":
            print(f"最高价: {df['high'].max():.2f}")
            print(f"最低价: {df['low'].min():.2f}")
            print(f"平均成交量: {df['volume'].mean():.2f}")
        
        if args.head > 0:
            print(f"\n前 {args.head} 行数据:")
            print(df.head(args.head))
        
        if args.output:
            df.to_csv(args.output, index=False)
            print(f"\n数据已保存到: {args.output}")
            
    except Exception as e:
        print(f"读取失败: {e}")
        sys.exit(1)


def info_command(args):
    """信息查询命令"""
    manager = HistoricalDataManager(args.data_dir)
    
    if args.symbol:
        # 查询特定交易对信息
        print(f"查询 {args.symbol} 数据信息...")
        info = manager.get_data_info(
            symbol=args.symbol,
            market_type=args.market_type,
            data_type=args.data_type,
            interval=args.interval
        )
        
        print(f"交易对: {info['symbol']}")
        print(f"市场类型: {info['market_type']}")
        print(f"数据类型: {info['data_type']}")
        if info['interval']:
            print(f"K线间隔: {info['interval']}")
        print(f"文件数量: {info['files_count']}")
        print(f"时间范围: {info['date_range']}")
        
        if args.verbose and info['files']:
            print("\n文件列表:")
            for file_name in info['files']:
                print(f"  - {file_name}")
    else:
        # 查询存储统计信息
        print("存储统计信息:")
        stats = manager.get_storage_stats()
        
        print(f"数据目录: {stats['data_directory']}")
        print(f"总大小: {stats['total_size_mb']:.2f} MB")
        print(f"总文件数: {stats['total_files']}")
        
        for market_type, market_stats in stats['market_types'].items():
            print(f"{market_type}: {market_stats['file_count']} 文件, {market_stats['size_mb']:.2f} MB")
        
        # 显示本地交易对
        print("\n本地交易对:")
        for market_type in MARKET_TYPES:
            for data_type in DATA_TYPES:
                symbols = manager.get_local_symbols(market_type, data_type)
                if symbols:
                    print(f"{market_type}/{data_type}: {len(symbols)} 个交易对")
                    if args.verbose:
                        print(f"  {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")


def cleanup_command(args):
    """清理数据命令"""
    manager = HistoricalDataManager(args.data_dir)
    
    print(f"清理 {args.days} 天前的数据...")
    
    if not args.force:
        confirm = input("确认要删除旧数据吗？(y/N): ")
        if confirm.lower() != 'y':
            print("取消操作")
            return
    
    try:
        deleted_count = manager.cleanup_old_data(args.days)
        print(f"清理完成，删除了 {deleted_count} 个文件")
    except Exception as e:
        print(f"清理失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="币安历史数据系统命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 下载BTCUSDT的1小时K线数据
  python cli.py download -s BTCUSDT -i 1h --start-date 2024-01-01 --end-date 2024-01-31
  
  # 下载多个交易对的数据
  python cli.py download -s BTCUSDT,ETHUSDT,BNBUSDT -i 4h --start-date 2024-01-01
  
  # 读取数据并显示统计信息
  python cli.py read -s BTCUSDT -i 1h --start-date 2024-01-01 --end-date 2024-01-31
  
  # 查看存储统计信息
  python cli.py info
  
  # 查看特定交易对信息
  python cli.py info -s BTCUSDT -d klines -i 1h
  
  # 清理30天前的数据
  python cli.py cleanup --days 30
"""
    )
    
    # 全局参数
    parser.add_argument('--data-dir', default=None, help='数据存储目录')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载历史数据')
    download_parser.add_argument('-s', '--symbols', default='BTCUSDT', 
                               help='交易对，多个用逗号分隔 (默认: BTCUSDT)')
    download_parser.add_argument('-m', '--market-type', choices=MARKET_TYPES, 
                               default='spot', help='市场类型 (默认: spot)')
    download_parser.add_argument('-d', '--data-type', choices=DATA_TYPES, 
                               default='klines', help='数据类型 (默认: klines)')
    download_parser.add_argument('-i', '--interval', choices=KLINE_INTERVALS, 
                               default='1h', help='K线间隔 (默认: 1h)')
    download_parser.add_argument('--start-date', 
                               default=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                               help='开始日期 YYYY-MM-DD (默认: 30天前)')
    download_parser.add_argument('--end-date', 
                               default=datetime.now().strftime('%Y-%m-%d'),
                               help='结束日期 YYYY-MM-DD (默认: 今天)')
    download_parser.add_argument('--skip-monthly', action='store_true', 
                               help='跳过月度数据下载')
    download_parser.add_argument('--skip-daily', action='store_true', 
                               help='跳过日度数据下载')
    
    # 读取命令
    read_parser = subparsers.add_parser('read', help='读取历史数据')
    read_parser.add_argument('-s', '--symbol', required=True, help='交易对')
    read_parser.add_argument('-m', '--market-type', choices=MARKET_TYPES, 
                           default='spot', help='市场类型 (默认: spot)')
    read_parser.add_argument('-d', '--data-type', choices=DATA_TYPES, 
                           default='klines', help='数据类型 (默认: klines)')
    read_parser.add_argument('-i', '--interval', choices=KLINE_INTERVALS, 
                           default='1h', help='K线间隔 (默认: 1h)')
    read_parser.add_argument('--start-date', 
                           default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                           help='开始日期 YYYY-MM-DD (默认: 7天前)')
    read_parser.add_argument('--end-date', 
                           default=datetime.now().strftime('%Y-%m-%d'),
                           help='结束日期 YYYY-MM-DD (默认: 今天)')
    read_parser.add_argument('--head', type=int, default=5, 
                           help='显示前N行数据 (默认: 5, 0表示不显示)')
    read_parser.add_argument('-o', '--output', help='输出CSV文件路径')
    
    # 信息命令
    info_parser = subparsers.add_parser('info', help='查询数据信息')
    info_parser.add_argument('-s', '--symbol', help='交易对 (不指定则显示存储统计)')
    info_parser.add_argument('-m', '--market-type', choices=MARKET_TYPES, 
                           default='spot', help='市场类型 (默认: spot)')
    info_parser.add_argument('-d', '--data-type', choices=DATA_TYPES, 
                           default='klines', help='数据类型 (默认: klines)')
    info_parser.add_argument('-i', '--interval', choices=KLINE_INTERVALS, 
                           default='1h', help='K线间隔 (默认: 1h)')
    
    # 清理命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧数据')
    cleanup_parser.add_argument('--days', type=int, default=30, 
                              help='保留天数 (默认: 30)')
    cleanup_parser.add_argument('--force', action='store_true', 
                              help='强制删除，不询问确认')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    try:
        if args.command == 'download':
            download_command(args)
        elif args.command == 'read':
            read_command(args)
        elif args.command == 'info':
            info_command(args)
        elif args.command == 'cleanup':
            cleanup_command(args)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()