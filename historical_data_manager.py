"""币安历史数据管理器"""
import os
from typing import List, Optional, Union, Iterator
import pandas as pd
from datetime import datetime

from data_downloader import BinanceDataDownloader
from data_reader import BinanceDataReader
from config import DEFAULT_CONFIG, KLINE_INTERVALS, MARKET_TYPES, DATA_TYPES


class HistoricalDataManager:
    """历史数据管理器 - 统一的数据下载和读取接口"""
    
    def __init__(self, data_directory: str = None):
        """
        初始化历史数据管理器
        
        Args:
            data_directory: 数据存储目录
        """
        self.data_directory = data_directory or DEFAULT_CONFIG["data_directory"]
        self.downloader = BinanceDataDownloader(self.data_directory)
        self.reader = BinanceDataReader(self.data_directory)
    
    def download_data(self, symbols: Union[str, List[str]], 
                     market_type: str = "spot", data_type: str = "klines",
                     interval: str = "1h", start_date: str = "2020-01-01",
                     end_date: str = None, download_monthly: bool = True,
                     download_daily: bool = True) -> List[str]:
        """
        下载历史数据
        
        Args:
            symbols: 交易对或交易对列表
            market_type: 市场类型 (spot, um, cm)
            data_type: 数据类型 (klines, trades, aggTrades)
            interval: K线间隔 (仅对klines有效)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            download_monthly: 是否下载月度数据
            download_daily: 是否下载日度数据
            
        Returns:
            下载成功的文件路径列表
        """
        # 参数验证
        self._validate_parameters(market_type, data_type, interval)
        
        if isinstance(symbols, str):
            symbols = [symbols]
        
        return self.downloader.download_data(
            symbols=symbols,
            market_type=market_type,
            data_type=data_type,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            download_monthly=download_monthly,
            download_daily=download_daily
        )
    
    def read_data(self, symbol: str, market_type: str = "spot",
                 data_type: str = "klines", interval: str = "1h",
                 start_date: str = "2020-01-01", end_date: str = None,
                 chunk_size: Optional[int] = None) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
        """
        读取历史数据
        
        Args:
            symbol: 交易对
            market_type: 市场类型 (spot, um, cm)
            data_type: 数据类型 (klines, trades, aggTrades)
            interval: K线间隔 (仅对klines有效)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            chunk_size: 分块大小，如果指定则返回生成器
            
        Returns:
            DataFrame或生成器
        """
        # 参数验证
        self._validate_parameters(market_type, data_type, interval)
        
        return self.reader.read_data(
            symbol=symbol,
            market_type=market_type,
            data_type=data_type,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            chunk_size=chunk_size
        )
    
    def get_data_info(self, symbol: str, market_type: str = "spot",
                     data_type: str = "klines", interval: str = "1h") -> dict:
        """
        获取数据信息
        
        Args:
            symbol: 交易对
            market_type: 市场类型
            data_type: 数据类型
            interval: K线间隔
            
        Returns:
            数据信息字典
        """
        self._validate_parameters(market_type, data_type, interval)
        
        return self.reader.get_data_info(
            symbol=symbol,
            market_type=market_type,
            data_type=data_type,
            interval=interval
        )
    
    def list_available_symbols(self, market_type: str = "spot") -> List[str]:
        """
        获取可用的交易对列表
        
        Args:
            market_type: 市场类型
            
        Returns:
            交易对列表
        """
        if market_type not in MARKET_TYPES:
            raise ValueError(f"无效的市场类型: {market_type}")
        
        return self.downloader.list_available_symbols(market_type)
    
    def get_local_symbols(self, market_type: str = "spot", 
                         data_type: str = "klines") -> List[str]:
        """
        获取本地已下载的交易对列表
        
        Args:
            market_type: 市场类型
            data_type: 数据类型
            
        Returns:
            本地交易对列表
        """
        self._validate_parameters(market_type, data_type)
        
        symbols = set()
        
        # 检查月度数据目录
        monthly_dir = os.path.join(self.data_directory, market_type, "monthly", data_type)
        if os.path.exists(monthly_dir):
            symbols.update(os.listdir(monthly_dir))
        
        # 检查日度数据目录
        daily_dir = os.path.join(self.data_directory, market_type, "daily", data_type)
        if os.path.exists(daily_dir):
            symbols.update(os.listdir(daily_dir))
        
        return sorted(list(symbols))
    
    def download_and_read(self, symbol: str, market_type: str = "spot",
                         data_type: str = "klines", interval: str = "1h",
                         start_date: str = "2020-01-01", end_date: str = None,
                         force_download: bool = False) -> pd.DataFrame:
        """
        下载并读取数据的便捷方法
        
        Args:
            symbol: 交易对
            market_type: 市场类型
            data_type: 数据类型
            interval: K线间隔
            start_date: 开始日期
            end_date: 结束日期
            force_download: 是否强制重新下载
            
        Returns:
            DataFrame
        """
        # 检查本地是否已有数据
        if not force_download:
            info = self.get_data_info(symbol, market_type, data_type, interval)
            if info["files_count"] > 0:
                print(f"发现本地数据，直接读取 {symbol}")
                return self.read_data(symbol, market_type, data_type, interval, start_date, end_date)
        
        # 下载数据
        print(f"开始下载 {symbol} 数据...")
        downloaded_files = self.download_data(
            symbols=[symbol],
            market_type=market_type,
            data_type=data_type,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )
        
        if not downloaded_files:
            print(f"未能下载到 {symbol} 的数据")
            return pd.DataFrame()
        
        # 读取数据
        return self.read_data(symbol, market_type, data_type, interval, start_date, end_date)
    
    def _validate_parameters(self, market_type: str, data_type: str, interval: str = None):
        """验证参数"""
        if market_type not in MARKET_TYPES:
            raise ValueError(f"无效的市场类型: {market_type}，支持的类型: {MARKET_TYPES}")
        
        if data_type not in DATA_TYPES:
            raise ValueError(f"无效的数据类型: {data_type}，支持的类型: {DATA_TYPES}")
        
        if data_type == "klines" and interval and interval not in KLINE_INTERVALS:
            raise ValueError(f"无效的K线间隔: {interval}，支持的间隔: {KLINE_INTERVALS}")
    
    def get_storage_stats(self) -> dict:
        """
        获取存储统计信息
        
        Returns:
            存储统计信息
        """
        stats = {
            "data_directory": self.data_directory,
            "total_size_mb": 0,
            "market_types": {},
            "total_files": 0
        }
        
        if not os.path.exists(self.data_directory):
            return stats
        
        for market_type in MARKET_TYPES:
            market_dir = os.path.join(self.data_directory, market_type)
            if os.path.exists(market_dir):
                market_stats = self._get_directory_stats(market_dir)
                stats["market_types"][market_type] = market_stats
                stats["total_size_mb"] += market_stats["size_mb"]
                stats["total_files"] += market_stats["file_count"]
        
        return stats
    
    def _get_directory_stats(self, directory: str) -> dict:
        """获取目录统计信息"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        return {
            "size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        清理旧数据文件
        
        Args:
            days_to_keep: 保留的天数
            
        Returns:
            删除的文件数量
        """
        if not os.path.exists(self.data_directory):
            return 0
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        deleted_count = 0
        
        for root, dirs, files in os.walk(self.data_directory):
            for file in files:
                if file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"删除旧文件: {file}")
                        except OSError as e:
                            print(f"删除文件失败 {file}: {e}")
        
        return deleted_count