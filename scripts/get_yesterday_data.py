#!/usr/bin/env python3
"""获取昨天ETHUSDT的前200条数据并输出到日志"""
import logging
from datetime import datetime, timedelta
from historical_data_manager import HistoricalDataManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ethusdt_data.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_yesterday_ethusdt_data():
    """获取昨天ETHUSDT的前200条数据"""
    # 获取当前时间和昨天日期
    current_time = datetime.now()
    yesterday = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
    
    logger.info(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"查询昨天日期: {yesterday}")
    
    # 初始化数据管理器
    manager = HistoricalDataManager()
    
    try:
        # 读取昨天的ETHUSDT数据
        logger.info("开始读取ETHUSDT数据...")
        df = manager.read_data(
            symbol="ETHUSDT",
            data_type="klines",
            interval="1h",
            start_date=yesterday,
            end_date=yesterday
        )
        
        if df.empty:
            logger.warning("未找到昨天的ETHUSDT数据")
            return
        
        # 获取前200条数据
        data_200 = df.head(200)
        
        logger.info(f"成功读取数据，总共 {len(df)} 条记录")
        logger.info(f"输出前 {len(data_200)} 条数据")
        logger.info(f"数据时间范围: {df.iloc[0, 0]} 到 {df.iloc[-1, 0]}")
        
        # 输出数据统计信息
        if len(df) > 0:
            logger.info(f"最高价: {df['high'].max():.4f}")
            logger.info(f"最低价: {df['low'].min():.4f}")
            logger.info(f"开盘价: {df.iloc[0]['open']:.4f}")
            logger.info(f"收盘价: {df.iloc[-1]['close']:.4f}")
            logger.info(f"总成交量: {df['volume'].sum():.2f}")
            logger.info(f"平均成交量: {df['volume'].mean():.2f}")
        
        # 输出前200条数据的详细信息
        logger.info("=" * 80)
        logger.info("前200条ETHUSDT数据详情:")
        logger.info("=" * 80)
        
        for i, row in data_200.iterrows():
            logger.info(
                f"[{i+1:3d}] 时间: {row['open_time']} | "
                f"开: {row['open']:8.4f} | 高: {row['high']:8.4f} | "
                f"低: {row['low']:8.4f} | 收: {row['close']:8.4f} | "
                f"量: {row['volume']:10.2f}"
            )
        
        logger.info("=" * 80)
        logger.info(f"数据输出完成，共输出 {len(data_200)} 条记录")
        
        # 保存前200条数据到CSV文件
        output_file = f"ethusdt_{yesterday}_top200.csv"
        data_200.to_csv(output_file, index=False)
        logger.info(f"数据已保存到文件: {output_file}")
        
    except Exception as e:
        logger.error(f"获取数据时出错: {e}")
        raise

if __name__ == '__main__':
    get_yesterday_ethusdt_data()