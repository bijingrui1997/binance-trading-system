"""币安历史数据下载器"""
import os
import requests
import zipfile
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional
from tqdm import tqdm
import pandas as pd

from config import (
    BASE_URL, DEFAULT_CONFIG, FILE_PATH_TEMPLATE, 
    DAILY_FILE_PATH_TEMPLATE, KLINE_INTERVALS, get_market_path_prefix
)


class BinanceDataDownloader:
    """币安历史数据下载器"""
    
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or DEFAULT_CONFIG["data_directory"]
        self.session = requests.Session()
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """确保数据目录存在"""
        os.makedirs(self.data_directory, exist_ok=True)
    
    def _get_file_url(self, market_type: str, data_type: str, symbol: str, 
                     interval: str = None, year: int = None, month: int = None, 
                     date: str = None, is_daily: bool = True) -> str:
        """构建文件下载URL"""
        market_prefix = get_market_path_prefix(market_type)
        
        if is_daily:
            template = DAILY_FILE_PATH_TEMPLATE[data_type]
            if data_type == "klines":
                file_path = template.format(
                    market_prefix=market_prefix, symbol=symbol, 
                    interval=interval, date=date
                )
            else:
                file_path = template.format(
                    market_prefix=market_prefix, symbol=symbol, date=date
                )
        else:
            template = FILE_PATH_TEMPLATE[data_type]
            if data_type == "klines":
                file_path = template.format(
                    market_prefix=market_prefix, symbol=symbol, 
                    interval=interval, year=year, month=month
                )
            else:
                file_path = template.format(
                    market_prefix=market_prefix, symbol=symbol, 
                    year=year, month=month
                )
        
        return f"{BASE_URL}/data/{file_path}"
    
    def _get_local_file_path(self, market_type: str, data_type: str, symbol: str,
                           interval: str = None, year: int = None, month: int = None,
                           date: str = None, is_daily: bool = True) -> str:
        """获取本地文件路径"""
        if is_daily:
            if data_type == "klines":
                filename = f"{symbol}-{interval}-{date}.zip"
                subdir = f"{market_type}/daily/{data_type}/{symbol}/{interval}"
            else:
                filename = f"{symbol}-{data_type}-{date}.zip"
                subdir = f"{market_type}/daily/{data_type}/{symbol}"
        else:
            if data_type == "klines":
                filename = f"{symbol}-{interval}-{year}-{month:02d}.zip"
                subdir = f"{market_type}/monthly/{data_type}/{symbol}/{interval}"
            else:
                filename = f"{symbol}-{data_type}-{year}-{month:02d}.zip"
                subdir = f"{market_type}/monthly/{data_type}/{symbol}"
        
        local_dir = os.path.join(self.data_directory, subdir)
        os.makedirs(local_dir, exist_ok=True)
        return os.path.join(local_dir, filename)
    
    def _download_file(self, url: str, local_path: str) -> bool:
        """下载单个文件"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(local_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc=os.path.basename(local_path)) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"下载失败 {url}: {e}")
            if os.path.exists(local_path):
                os.remove(local_path)
            return False
    
    def download_data(self, symbols: List[str], market_type: str = "spot",
                     data_type: str = "klines", interval: str = "1h",
                     start_date: str = "2020-01-01", end_date: str = None,
                     download_monthly: bool = False, download_daily: bool = True) -> List[str]:
        """下载历史数据
        
        Args:
            symbols: 交易对列表
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
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if data_type == "klines" and interval not in KLINE_INTERVALS:
            raise ValueError(f"无效的K线间隔: {interval}")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        downloaded_files = []
        
        for symbol in symbols:
            print(f"开始下载 {symbol} 数据...")
            
            # 下载月度数据
            if download_monthly:
                current_dt = start_dt.replace(day=1)
                while current_dt <= end_dt:
                    url = self._get_file_url(
                        market_type, data_type, symbol, interval,
                        current_dt.year, current_dt.month, is_daily=True
                    )
                    local_path = self._get_local_file_path(
                        market_type, data_type, symbol, interval,
                        current_dt.year, current_dt.month, is_daily=True
                    )
                    
                    if not os.path.exists(local_path):
                        if self._download_file(url, local_path):
                            downloaded_files.append(local_path)
                    else:
                        print(f"文件已存在: {os.path.basename(local_path)}")
                        downloaded_files.append(local_path)
                    
                    current_dt += relativedelta(months=1)
            
            # 下载日度数据
            if download_daily:
                current_dt = start_dt
                while current_dt <= end_dt:
                    date_str = current_dt.strftime("%Y-%m-%d")
                    url = self._get_file_url(
                        market_type, data_type, symbol, interval,
                        date=date_str, is_daily=True
                    )
                    local_path = self._get_local_file_path(
                        market_type, data_type, symbol, interval,
                        date=date_str, is_daily=True
                    )
                    
                    if not os.path.exists(local_path):
                        if self._download_file(url, local_path):
                            downloaded_files.append(local_path)
                    else:
                        print(f"文件已存在: {os.path.basename(local_path)}")
                        downloaded_files.append(local_path)
                    
                    current_dt += timedelta(days=1)
        
        print(f"下载完成，共下载 {len(downloaded_files)} 个文件")
        return downloaded_files
    
    def list_available_symbols(self, market_type: str = "spot") -> List[str]:
        """获取可用的交易对列表（简化版本，实际应该从API获取）"""
        # 这里返回一些常见的交易对，实际项目中应该从币安API获取
        common_symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
            "SOLUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "SHIBUSDT"
        ]
        return common_symbols