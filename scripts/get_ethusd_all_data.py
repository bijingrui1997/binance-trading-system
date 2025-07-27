#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETHUSD全市场数据获取脚本
获取ETHUSD相关的spot、um、cm市场下的日级别和月级别数据
"""

import os
import logging
from datetime import datetime, timedelta
from historical_data_manager import HistoricalDataManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ethusd_all_data.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_output_directory():
    """创建输出目录"""
    output_dir = "ethusd_data_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"创建输出目录: {output_dir}")
    return output_dir

def download_data_if_needed(manager, symbol, market_type, data_type, interval=None):
    """如果需要，下载数据"""
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        logger.info(f"尝试下载 {symbol} {market_type} {data_type} 数据...")
        
        if data_type == "klines" and interval:
            manager.download_data(
                symbol=symbol,
                market_type=market_type,
                data_type=data_type,
                interval=interval,
                start_date=yesterday,
                end_date=yesterday
            )
        else:
            manager.download_data(
                symbol=symbol,
                market_type=market_type,
                data_type=data_type,
                start_date=yesterday,
                end_date=yesterday
            )
        return True
    except Exception as e:
        logger.warning(f"下载 {symbol} {market_type} {data_type} 数据失败: {e}")
        return False

def get_latest_data(manager, symbol, market_type, data_type, interval=None, limit=10):
    """获取最新数据"""
    try:
        # 获取昨天的日期作为结束日期
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = "2024-01-01"  # 从较早日期开始确保能获取到数据
        
        logger.info(f"正在获取 {symbol} {market_type} {data_type} 数据...")
        
        if data_type == "klines" and interval:
            df = manager.read_data(
                symbol=symbol,
                market_type=market_type,
                data_type=data_type,
                interval=interval,
                start_date=start_date,
                end_date=yesterday
            )
        else:
            df = manager.read_data(
                symbol=symbol,
                market_type=market_type,
                data_type=data_type,
                start_date=start_date,
                end_date=yesterday
            )
        
        if df.empty:
            logger.warning(f"未获取到 {symbol} {market_type} {data_type} 数据")
            return None
        
        # 获取最新的limit条数据
        latest_data = df.tail(limit)
        logger.info(f"成功获取 {symbol} {market_type} {data_type} 最新 {len(latest_data)} 条数据")
        return latest_data
        
    except Exception as e:
        logger.error(f"获取 {symbol} {market_type} {data_type} 数据时出错: {e}")
        return None

def save_to_csv(df, output_dir, filename):
    """保存数据到CSV文件"""
    if df is not None and not df.empty:
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"数据已保存到: {filepath}")
        return True
    return False

def process_data_config(manager, config, output_dir):
    """处理单个数据配置"""
    logger.info(f"\n处理配置: {config['symbol']} - {config['market_type']} - {config['data_type']}")
    
    # 先尝试下载数据
    download_data_if_needed(
        manager=manager,
        symbol=config["symbol"],
        market_type=config["market_type"],
        data_type=config["data_type"],
        interval=config.get("interval")
    )
    
    # 获取数据
    df = get_latest_data(
        manager=manager,
        symbol=config["symbol"],
        market_type=config["market_type"],
        data_type=config["data_type"],
        interval=config.get("interval"),
        limit=10
    )
    
    # 保存数据
    success = save_to_csv(df, output_dir, config["filename"])
    
    if success and df is not None and not df.empty:
        # 显示数据预览
        logger.info(f"数据预览 ({config['filename']}):")
        logger.info(f"数据形状: {df.shape}")
        logger.info(f"列名: {list(df.columns)}")
        if len(df) > 0:
            # 显示前3条和后3条数据
            logger.info("前3条数据:")
            for i, row in df.head(3).iterrows():
                logger.info(f"  [{i}] {row.to_dict()}")
            if len(df) > 3:
                logger.info("后3条数据:")
                for i, row in df.tail(3).iterrows():
                    logger.info(f"  [{i}] {row.to_dict()}")
    
    logger.info("-" * 60)
    return success

def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始获取ETHUSD全市场数据")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # 创建输出目录
    output_dir = create_output_directory()
    
    # 初始化数据管理器
    manager = HistoricalDataManager()
    
    # 定义要获取的数据配置 - 只包含实际可能存在的数据类型
    data_configs = [
        # ETHUSDT Spot 数据
        {"symbol": "ETHUSDT", "market_type": "spot", "data_type": "klines", "interval": "1h", "filename": "ethusdt_spot_klines_1h_latest10.csv"},
        {"symbol": "ETHUSDT", "market_type": "spot", "data_type": "klines", "interval": "1d", "filename": "ethusdt_spot_klines_1d_latest10.csv"},
        {"symbol": "ETHUSDT", "market_type": "spot", "data_type": "aggTrades", "filename": "ethusdt_spot_aggtrades_latest10.csv"},
        
        # ETHUSDT UM Futures 数据
        {"symbol": "ETHUSDT", "market_type": "um", "data_type": "klines", "interval": "1h", "filename": "ethusdt_um_klines_1h_latest10.csv"},
        {"symbol": "ETHUSDT", "market_type": "um", "data_type": "klines", "interval": "1d", "filename": "ethusdt_um_klines_1d_latest10.csv"},
        {"symbol": "ETHUSDT", "market_type": "um", "data_type": "aggTrades", "filename": "ethusdt_um_aggtrades_latest10.csv"},
        
        # ETHUSD_PERP CM Futures 数据
        {"symbol": "ETHUSD_PERP", "market_type": "cm", "data_type": "klines", "interval": "1h", "filename": "ethusd_perp_cm_klines_1h_latest10.csv"},
        {"symbol": "ETHUSD_PERP", "market_type": "cm", "data_type": "klines", "interval": "1d", "filename": "ethusd_perp_cm_klines_1d_latest10.csv"},
        {"symbol": "ETHUSD_PERP", "market_type": "cm", "data_type": "aggTrades", "filename": "ethusd_perp_cm_aggtrades_latest10.csv"},
    ]
    
    success_count = 0
    total_count = len(data_configs)
    
    # 获取并保存每种类型的数据
    for config in data_configs:
        if process_data_config(manager, config, output_dir):
            success_count += 1
    
    logger.info("\n" + "="*80)
    logger.info(f"数据获取完成！成功: {success_count}/{total_count}")
    logger.info(f"所有CSV文件已保存到目录: {output_dir}")
    
    # 显示输出目录内容
    logger.info("\n输出文件列表:")
    try:
        for filename in os.listdir(output_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                logger.info(f"  {filename} ({size} bytes)")
    except Exception as e:
        logger.error(f"列出输出文件时出错: {e}")
    
    logger.info("="*80)

if __name__ == "__main__":
    main()