"""配置文件"""
import os
from datetime import datetime

# 基础配置
BASE_URL = "https://data.binance.vision"
DATA_TYPES = ["klines", "trades", "aggTrades"]
MARKET_TYPES = ["spot", "um", "cm"]  # spot, USD-M Futures, COIN-M Futures

# K线间隔
KLINE_INTERVALS = [
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"
]

# 默认配置
DEFAULT_CONFIG = {
    "data_directory": os.path.join(os.getcwd(), "data"),
    "market_type": "spot",
    "data_type": "klines",
    "interval": "1h",
    "start_date": "2020-01-01",
    "end_date": datetime.now().strftime("%Y-%m-%d"),
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "download_monthly": True,
    "download_daily": True,
    "verify_checksum": False
}

# 文件路径模板
def get_market_path_prefix(market_type):
    """获取市场类型的路径前缀"""
    if market_type == "spot":
        return "spot"
    elif market_type == "um":
        return "futures/um"
    elif market_type == "cm":
        return "futures/cm"
    else:
        return market_type

FILE_PATH_TEMPLATE = {
    "klines": "{market_prefix}/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02d}.zip",
    "trades": "{market_prefix}/monthly/trades/{symbol}/{symbol}-trades-{year}-{month:02d}.zip",
    "aggTrades": "{market_prefix}/monthly/aggTrades/{symbol}/{symbol}-aggTrades-{year}-{month:02d}.zip"
}

DAILY_FILE_PATH_TEMPLATE = {
    "klines": "{market_prefix}/daily/klines/{symbol}/{interval}/{symbol}-{interval}-{date}.zip",
    "trades": "{market_prefix}/daily/trades/{symbol}/{symbol}-trades-{date}.zip",
    "aggTrades": "{market_prefix}/daily/aggTrades/{symbol}/{symbol}-aggTrades-{date}.zip"
}