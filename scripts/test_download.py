#!/usr/bin/env python3
"""测试下载BTCUSDT和ETHUSD_PERP数据"""
import logging
from datetime import datetime, timedelta
from historical_data_manager import HistoricalDataManager

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_download():
    """测试下载数据"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    manager = HistoricalDataManager()
    
    # 测试BTCUSDT U本位合约
    logger.info("测试下载BTCUSDT U本位合约数据...")
    try:
        files = manager.download_data(
            symbols=["BTCUSDT"],
            market_type="um",
            data_type="aggTrades",
            start_date=yesterday,
            end_date=yesterday
        )
        logger.info(f"BTCUSDT下载成功: {files}")
    except Exception as e:
        logger.error(f"BTCUSDT下载失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # 测试ETHUSD_PERP 币本位合约
    logger.info("测试下载ETHUSD_PERP 币本位合约数据...")
    try:
        files = manager.download_data(
            symbols=["ETHUSD_PERP"],
            market_type="cm",
            data_type="aggTrades",
            start_date=yesterday,
            end_date=yesterday
        )
        logger.info(f"ETHUSD_PERP下载成功: {files}")
    except Exception as e:
        logger.error(f"ETHUSD_PERP下载失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    test_download()