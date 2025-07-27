#!/usr/bin/env python3
"""获取多个市场的aggTrades数据并输出到日志"""
import logging
from datetime import datetime, timedelta
from historical_data_manager import HistoricalDataManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_market_aggtrades.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_aggtrades_data(symbol, market_type, market_name):
    """获取指定交易对和市场的aggTrades数据"""
    # 获取当前时间和昨天日期
    current_time = datetime.now()
    yesterday = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
    
    logger.info(f"\n{'='*80}")
    logger.info(f"开始获取 {symbol} ({market_name}) 的aggTrades数据")
    logger.info(f"市场类型: {market_type}")
    logger.info(f"查询日期: {yesterday}")
    logger.info(f"{'='*80}")
    
    # 初始化数据管理器
    manager = HistoricalDataManager()
    
    try:
        # 先尝试下载数据
        logger.info(f"正在下载 {symbol} 的aggTrades数据...")
        downloaded_files = manager.download_data(
            symbols=[symbol],
            market_type=market_type,
            data_type="aggTrades",
            start_date=yesterday,
            end_date=yesterday
        )
        logger.info(f"下载完成，共下载 {len(downloaded_files)} 个文件")
        
        # 读取数据
        logger.info(f"正在读取 {symbol} 的aggTrades数据...")
        df = manager.read_data(
            symbol=symbol,
            market_type=market_type,
            data_type="aggTrades",
            start_date=yesterday,
            end_date=yesterday
        )
        
        if df.empty:
            logger.warning(f"未找到 {symbol} ({market_name}) 的aggTrades数据")
            return
        
        # 获取前200条数据
        data_200 = df.head(200)
        
        logger.info(f"成功读取数据，总共 {len(df)} 条记录")
        logger.info(f"输出前 {len(data_200)} 条数据")
        
        if len(df) > 0:
            logger.info(f"数据时间范围: {df.iloc[0, 0]} 到 {df.iloc[-1, 0]}")
            logger.info(f"最高价: {df['price'].max():.4f}")
            logger.info(f"最低价: {df['price'].min():.4f}")
            logger.info(f"总成交量: {df['quantity'].sum():.4f}")
            logger.info(f"平均成交量: {df['quantity'].mean():.4f}")
            logger.info(f"总交易笔数: {len(df)}")
        
        # 输出前200条数据的详细信息
        logger.info(f"\n{'-'*60}")
        logger.info(f"{symbol} ({market_name}) 前200条aggTrades数据详情:")
        logger.info(f"{'-'*60}")
        
        for i, row in data_200.iterrows():
            logger.info(
                f"[{i+1:3d}] 时间: {row['timestamp']} | "
                f"价格: {row['price']:10.4f} | 数量: {row['quantity']:12.4f} | "
                f"买方: {'是' if row['is_buyer_maker'] else '否'} | "
                f"聚合交易ID: {row['agg_trade_id']}"
            )
        
        logger.info(f"{'-'*60}")
        logger.info(f"{symbol} ({market_name}) 数据输出完成，共输出 {len(data_200)} 条记录")
        
        # 保存数据到CSV文件
        output_file = f"{symbol.lower()}_{market_type}_{yesterday}_aggtrades_top200.csv"
        data_200.to_csv(output_file, index=False)
        logger.info(f"数据已保存到文件: {output_file}")
        
    except Exception as e:
        logger.error(f"获取 {symbol} ({market_name}) 数据时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """主函数"""
    # 获取当前时间
    current_time = datetime.now()
    yesterday = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
    
    logger.info(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"查询昨天日期: {yesterday}")
    
    # 定义要获取的数据
    data_requests = [
        ("ETHUSDT", "spot", "现货市场"),
        ("BTCUSDT", "um", "U本位合约"),
        ("ETHUSD_PERP", "cm", "币本位永续合约")
    ]
    
    logger.info(f"\n开始获取多个市场的aggTrades数据...")
    logger.info(f"总共需要获取 {len(data_requests)} 个市场的数据")
    
    # 逐个获取数据
    for symbol, market_type, market_name in data_requests:
        try:
            get_aggtrades_data(symbol, market_type, market_name)
        except Exception as e:
            logger.error(f"处理 {symbol} ({market_name}) 时发生错误: {e}")
            continue
    
    logger.info(f"\n{'='*80}")
    logger.info("所有市场数据获取完成！")
    logger.info(f"{'='*80}")

if __name__ == '__main__':
    main()