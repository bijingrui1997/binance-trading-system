#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合ETH数据获取脚本
获取ETHUSDT和ETHUSD在不同市场的各种数据类型
包括昨天和上个月的数据，每种获取前20条记录
"""

import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_downloader import BinanceDataDownloader
from data_reader import BinanceDataReader
from config import get_market_path_prefix

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_date_strings():
    """获取昨天和上个月的日期字符串"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    last_month = today - relativedelta(months=1)
    
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    last_month_str = last_month.strftime('%Y-%m')
    
    logger.info(f"当前时间: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"昨天日期: {yesterday_str}")
    logger.info(f"上个月: {last_month_str}")
    
    return yesterday_str, last_month_str

def download_data_if_needed(downloader, symbol, market_type, data_type, date_str, interval=None, is_monthly=False):
    """如果需要则下载数据"""
    try:
        # 使用通用的download_data方法
        if is_monthly:
            # 月度数据：从月初到月末
            start_date = date_str + '-01'
            end_date = date_str + '-28'  # 保守的月末日期
            downloader.download_data(
                symbols=[symbol],
                market_type=market_type,
                data_type=data_type,
                interval=interval or '1h',
                start_date=start_date,
                end_date=end_date,
                download_monthly=True,
                download_daily=False
            )
        else:
            # 日度数据
            downloader.download_data(
                symbols=[symbol],
                market_type=market_type,
                data_type=data_type,
                interval=interval or '1h',
                start_date=date_str,
                end_date=date_str,
                download_monthly=False,
                download_daily=True
            )
        return True
    except Exception as e:
        logger.warning(f"下载数据失败 {symbol} {market_type} {data_type}: {e}")
        return False

def process_data_config(config, output_dir, yesterday_str, last_month_str):
    """处理单个数据配置"""
    symbol = config['symbol']
    market_type = config['market_type']
    data_type = config['data_type']
    interval = config.get('interval')
    period = config['period']  # 'daily' or 'monthly'
    
    # 确定日期字符串
    date_str = yesterday_str if period == 'daily' else last_month_str
    
    # 构建文件名
    if interval:
        filename = f"{symbol.lower()}_{market_type}_{data_type}_{interval}_{period}_top20.csv"
    else:
        filename = f"{symbol.lower()}_{market_type}_{data_type}_{period}_top20.csv"
    
    output_path = os.path.join(output_dir, filename)
    
    logger.info(f"\n处理配置: {symbol} {market_type} {data_type} {interval or ''} ({period})")
    
    try:
        # 初始化下载器和读取器
        downloader = BinanceDataDownloader()
        reader = BinanceDataReader()
        
        # 尝试下载数据
        is_monthly = (period == 'monthly')
        download_success = download_data_if_needed(
            downloader, symbol, market_type, data_type, date_str, interval, is_monthly
        )
        
        # 读取数据
        if period == 'monthly':
            # 月度数据：读取整个月
            start_date = date_str + '-01'
            end_date = date_str + '-28'
        else:
            # 日度数据
            start_date = date_str
            end_date = date_str
            
        df = reader.read_data(
            symbol=symbol,
            market_type=market_type,
            data_type=data_type,
            interval=interval or '1h',
            start_date=start_date,
            end_date=end_date
        )
        
        if df is None or df.empty:
            logger.warning(f"没有找到数据: {symbol} {market_type} {data_type}")
            return False
        
        # 获取前20条数据
        top_20 = df.head(20)
        
        # 保存到CSV
        top_20.to_csv(output_path, index=False)
        
        logger.info(f"成功保存 {len(top_20)} 条记录到: {filename}")
        
        # 显示数据预览
        logger.info(f"数据预览 - 前3条:")
        for i, row in top_20.head(3).iterrows():
            logger.info(f"  [{i}] {dict(row)}")
        
        if len(top_20) > 3:
            logger.info(f"后3条:")
            for i, row in top_20.tail(3).iterrows():
                logger.info(f"  [{i}] {dict(row)}")
        
        logger.info("-" * 60)
        return True
        
    except Exception as e:
        logger.error(f"处理失败 {symbol} {market_type} {data_type}: {e}")
        return False

def main():
    """主函数"""
    # 获取日期
    yesterday_str, last_month_str = get_date_strings()
    
    # 创建输出目录
    output_dir = "comprehensive_eth_data_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义所有数据配置
    configs = [
        # 昨天的数据
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'aggTrades', 'period': 'daily'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1s', 'period': 'daily'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1m', 'period': 'daily'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1h', 'period': 'daily'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'trades', 'period': 'daily'},
        {'symbol': 'ETHUSDT', 'market_type': 'um', 'data_type': 'aggTrades', 'period': 'daily'},
        {'symbol': 'ETHUSD_PERP', 'market_type': 'cm', 'data_type': 'aggTrades', 'period': 'daily'},
        
        # 上个月的数据
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'aggTrades', 'period': 'monthly'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1s', 'period': 'monthly'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1m', 'period': 'monthly'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'klines', 'interval': '1h', 'period': 'monthly'},
        {'symbol': 'ETHUSDT', 'market_type': 'spot', 'data_type': 'trades', 'period': 'monthly'},
        {'symbol': 'ETHUSDT', 'market_type': 'um', 'data_type': 'aggTrades', 'period': 'monthly'},
        {'symbol': 'ETHUSD_PERP', 'market_type': 'cm', 'data_type': 'aggTrades', 'period': 'monthly'},
    ]
    
    logger.info(f"\n开始处理 {len(configs)} 个数据配置...")
    logger.info("=" * 80)
    
    # 处理所有配置
    success_count = 0
    for config in configs:
        if process_data_config(config, output_dir, yesterday_str, last_month_str):
            success_count += 1
    
    # 显示结果摘要
    logger.info(f"\n{'='*80}")
    logger.info(f"数据获取完成！成功: {success_count}/{len(configs)}")
    logger.info(f"所有CSV文件已保存到目录: {output_dir}")
    
    # 列出生成的文件
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        if files:
            logger.info(f"\n输出文件列表:")
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                logger.info(f"  {file} ({file_size} bytes)")
        else:
            logger.warning("没有生成任何CSV文件")
    
    logger.info("=" * 80)

if __name__ == "__main__":
    main()