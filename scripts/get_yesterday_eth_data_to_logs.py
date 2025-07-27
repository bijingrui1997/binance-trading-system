#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取上一天ETH相关交易对的各种数据并输出到日志文件

功能:
- 获取ETHUSDT现货的aggTrades、klines(1h)、trades数据
- 获取ETHUSDT永续(um)的aggTrades、klines(1h)、trades数据  
- 获取ETHUSD永续(cm)的aggTrades、klines(1h)、trades数据
- 每种数据类型输出前100条到单独的日志文件
"""

import os
import sys
from datetime import datetime, timedelta
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from historical_data_manager import HistoricalDataManager

def setup_logging():
    """设置日志配置"""
    # 创建logs目录
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 配置主日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'eth_data_extraction.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logs_dir

def get_yesterday_date():
    """获取昨天的日期"""
    # 由于昨天的数据可能不可用，使用今天的日期进行演示
    yesterday = datetime.now() - timedelta(days=2)
    return yesterday.strftime('%Y-%m-%d')

def save_data_to_log(data, filename, logs_dir, data_type, symbol, market_type, interval=None):
    """保存数据到日志文件"""
    if data is None or len(data) == 0:
        logging.warning(f"没有获取到 {symbol} {market_type} {data_type} 数据")
        return
    
    # 取前100条数据
    data_subset = data.head(100)
    
    # 创建日志文件路径
    log_file = os.path.join(logs_dir, filename)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {symbol} {market_type.upper()} {data_type.upper()}")
        if interval:
            f.write(f" ({interval})")
        f.write(f" 数据 ===\n")
        f.write(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据日期: {get_yesterday_date()}\n")
        f.write(f"数据条数: {len(data_subset)}\n")
        f.write("=" * 80 + "\n\n")
        
        # 写入数据
        f.write(data_subset.to_string(index=False))
        f.write("\n\n")
        
        # 写入数据统计信息
        f.write("=== 数据统计信息 ===\n")
        f.write(data_subset.describe().to_string())
        f.write("\n")
    
    logging.info(f"已保存 {len(data_subset)} 条 {symbol} {market_type} {data_type} 数据到 {filename}")

def main():
    """主函数"""
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"获取日期: {get_yesterday_date()}")
    
    # 设置日志
    logs_dir = setup_logging()
    logging.info("开始获取昨天的ETH相关数据")
    
    # 初始化数据管理器
    manager = HistoricalDataManager()
    yesterday = get_yesterday_date()
    
    # 定义要获取的数据配置
    data_configs = [
        # ETHUSDT 现货数据
        {
            'symbol': 'ETHUSDT',
            'market_type': 'spot',
            'data_type': 'aggTrades',
            'filename': f'ethusdt_spot_aggtrades_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSDT',
            'market_type': 'spot',
            'data_type': 'klines',
            'interval': '1h',
            'filename': f'ethusdt_spot_klines_1h_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSDT',
            'market_type': 'spot',
            'data_type': 'trades',
            'filename': f'ethusdt_spot_trades_{yesterday.replace("-", "")}.log'
        },
        
        # ETHUSDT 永续合约 (um)
        {
            'symbol': 'ETHUSDT',
            'market_type': 'um',
            'data_type': 'aggTrades',
            'filename': f'ethusdt_um_aggtrades_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSDT',
            'market_type': 'um',
            'data_type': 'trades',
            'filename': f'ethusdt_um_trades_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSDT',
            'market_type': 'um',
            'data_type': 'klines',
            'interval': '1h',
            'filename': f'ethusdt_um_klines_1h_{yesterday.replace("-", "")}.log'
        },
        
        # ETHUSD 永续合约 (cm)
        {
            'symbol': 'ETHUSD_PERP',
            'market_type': 'cm',
            'data_type': 'aggTrades',
            'filename': f'ethusd_cm_aggtrades_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSD_PERP',
            'market_type': 'cm',
            'data_type': 'trades',
            'filename': f'ethusd_cm_trades_{yesterday.replace("-", "")}.log'
        },
        {
            'symbol': 'ETHUSD_PERP',
            'market_type': 'cm',
            'data_type': 'klines',
            'interval': '1h',
            'filename': f'ethusd_cm_klines_1h_{yesterday.replace("-", "")}.log'
        }
    ]
    
    # 处理每个数据配置
    for config in data_configs:
        try:
            logging.info(f"正在获取 {config['symbol']} {config['market_type']} {config['data_type']} 数据...")
            
            # 构建参数
            params = {
                'symbol': config['symbol'],
                'market_type': config['market_type'],
                'data_type': config['data_type'],
                'start_date': yesterday,
                'end_date': yesterday
            }
            
            # 如果是klines数据，添加interval参数
            if config['data_type'] == 'klines':
                params['interval'] = config['interval']
            
            # 先尝试下载数据
            download_params = {
                'symbols': [config['symbol']],
                'market_type': config['market_type'],
                'data_type': config['data_type'],
                'start_date': yesterday,
                'end_date': yesterday
            }
            
            # 如果是klines数据，添加interval参数
            if config['data_type'] == 'klines':
                download_params['interval'] = config['interval']
            
            logging.info(f"正在下载 {config['symbol']} {config['market_type']} {config['data_type']} 数据...")
            manager.download_data(**download_params)
            
            # 读取数据
            data = manager.read_data(**params)
            
            # 保存数据到日志
            save_data_to_log(
                data, 
                config['filename'], 
                logs_dir, 
                config['data_type'],
                config['symbol'],
                config['market_type'],
                config.get('interval')
            )
            
        except Exception as e:
            logging.error(f"处理 {config['symbol']} {config['market_type']} {config['data_type']} 时出错: {e}")
            continue
    
    logging.info("所有ETH相关数据获取完成")
    print(f"\n所有日志文件已保存到: {logs_dir}")
    print("处理完成!")

if __name__ == "__main__":
    main()