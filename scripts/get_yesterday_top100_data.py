#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取上一天ETHUSDT和ETHUSD各种数据类型的前100条记录
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append('/Users/pm/work_ai/binance_trading_system')

from data_downloader import BinanceDataDownloader
from data_reader import BinanceDataReader

def get_yesterday_date():
    """获取昨天的日期字符串"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')

def download_data_if_needed(downloader, market_type, data_type, symbol, date_str, interval=None):
    """如果需要的话下载数据"""
    try:
        print(f"正在检查并下载 {market_type} {symbol} {data_type} {interval or ''} 数据 ({date_str})...")
        downloader.download_data(
            market_type=market_type,
            data_type=data_type,
            symbol=symbol,
            start_date=date_str,
            end_date=date_str,
            interval=interval
        )
        print(f"✓ {market_type} {symbol} {data_type} {interval or ''} 数据下载完成")
        return True
    except Exception as e:
        print(f"✗ {market_type} {symbol} {data_type} {interval or ''} 数据下载失败: {e}")
        return False

def read_and_save_data(reader, market_type, data_type, symbol, date_str, output_dir, interval=None, limit=100):
    """读取数据并保存前N条记录到CSV"""
    try:
        print(f"正在读取 {market_type} {symbol} {data_type} {interval or ''} 数据...")
        
        # 读取数据
        df = reader.read_data(
            market_type=market_type,
            data_type=data_type,
            symbol=symbol,
            start_date=date_str,
            end_date=date_str,
            interval=interval
        )
        
        if df is None or df.empty:
            print(f"✗ 没有找到 {market_type} {symbol} {data_type} {interval or ''} 数据")
            return False
        
        # 获取前N条记录
        top_records = df.head(limit)
        
        # 生成文件名
        interval_suffix = f"_{interval}" if interval else ""
        filename = f"{symbol.lower()}_{market_type}_{data_type}{interval_suffix}_top{limit}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # 保存到CSV
        top_records.to_csv(filepath, index=False)
        
        print(f"✓ 已保存 {len(top_records)} 条记录到 {filename}")
        print(f"  数据预览 (前3行):")
        print(top_records.head(3).to_string(index=False))
        print(f"  数据预览 (后3行):")
        print(top_records.tail(3).to_string(index=False))
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 读取 {market_type} {symbol} {data_type} {interval or ''} 数据失败: {e}")
        return False

def main():
    print("=== 获取上一天ETHUSDT和ETHUSD数据 ===")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取昨天日期
    yesterday = get_yesterday_date()
    print(f"目标日期: {yesterday}")
    
    # 创建输出目录
    output_dir = "/Users/pm/work_ai/binance_trading_system/data/yesterday_top100_data"
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    print()
    
    # 初始化下载器和读取器
    downloader = BinanceDataDownloader()
    reader = BinanceDataReader()
    
    # 定义数据配置
    data_configs = [
        # ETHUSDT spot数据
        {"market_type": "spot", "symbol": "ETHUSDT", "data_type": "aggTrades"},
        {"market_type": "spot", "symbol": "ETHUSDT", "data_type": "klines", "interval": "1s"},
        {"market_type": "spot", "symbol": "ETHUSDT", "data_type": "klines", "interval": "1m"},
        {"market_type": "spot", "symbol": "ETHUSDT", "data_type": "klines", "interval": "1h"},
        {"market_type": "spot", "symbol": "ETHUSDT", "data_type": "trades"},
        
        # ETHUSDT um永续数据
        {"market_type": "um", "symbol": "ETHUSDT", "data_type": "aggTrades"},
        {"market_type": "um", "symbol": "ETHUSDT", "data_type": "trades"},
        
        # ETHUSD cm永续数据
        {"market_type": "cm", "symbol": "ETHUSD_PERP", "data_type": "aggTrades"},
        {"market_type": "cm", "symbol": "ETHUSD_PERP", "data_type": "trades"},
    ]
    
    successful_downloads = 0
    successful_reads = 0
    
    # 处理每个数据配置
    for i, config in enumerate(data_configs, 1):
        print(f"[{i}/{len(data_configs)}] 处理配置: {config}")
        
        # 下载数据
        download_success = download_data_if_needed(
            downloader=downloader,
            market_type=config["market_type"],
            data_type=config["data_type"],
            symbol=config["symbol"],
            date_str=yesterday,
            interval=config.get("interval")
        )
        
        if download_success:
            successful_downloads += 1
        
        # 读取并保存数据
        read_success = read_and_save_data(
            reader=reader,
            market_type=config["market_type"],
            data_type=config["data_type"],
            symbol=config["symbol"],
            date_str=yesterday,
            output_dir=output_dir,
            interval=config.get("interval"),
            limit=100
        )
        
        if read_success:
            successful_reads += 1
        
        print("-" * 80)
    
    print(f"\n=== 处理完成 ===")
    print(f"成功下载: {successful_downloads}/{len(data_configs)}")
    print(f"成功保存: {successful_reads}/{len(data_configs)}")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    main()