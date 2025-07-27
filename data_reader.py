"""币安历史数据读取器"""
import os
import zipfile
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Iterator, Tuple
import glob

from config import DEFAULT_CONFIG, KLINE_INTERVALS


class BinanceDataReader:
    """币安历史数据读取器"""
    
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or DEFAULT_CONFIG["data_directory"]
        
        # K线数据列名
        self.kline_columns = [
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'count',
            'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
        ]

        # 交易数据列名
        self.trade_columns = [
            'id', 'price', 'qty', 'quote_qty',
            'time', 'is_buyer_maker', 'is_best_match'
        ]

        # 聚合交易数据列名
        self.agg_trade_columns = [
            'agg_trade_id', 'price', 'quantity', 'first_trade_id',
            'last_trade_id', 'transact_time', 'is_buyer_maker', 'is_best_match'
        ]
    
    def _find_data_files(self, symbol: str, market_type: str = "spot",
                        data_type: str = "aggTrades", interval: str = "1h",
                        start_date: str = "2025-07-26", end_date: str = None,
                        prefer_monthly: bool = False) -> List[str]:
        """查找指定条件的数据文件"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        files = []
        
        if prefer_monthly:
            # 优先查找月度文件
            if data_type == "klines":
                pattern = os.path.join(
                    self.data_directory, market_type, "monthly", data_type,
                    symbol, interval, f"{symbol}-{interval}-*.zip"
                )
            else:
                pattern = os.path.join(
                    self.data_directory, market_type, "monthly", data_type,
                    symbol, f"{symbol}-{data_type}-*.zip"
                )
            
            monthly_files = glob.glob(pattern)
            monthly_files.sort()
            
            for file_path in monthly_files:
                filename = os.path.basename(file_path)
                try:
                    if data_type == "klines":
                        # 格式: SYMBOL-INTERVAL-YYYY-MM.zip
                        parts = filename.replace('.zip', '').split('-')
                        year, month = int(parts[-2]), int(parts[-1])
                    else:
                        # 格式: SYMBOL-DATATYPE-YYYY-MM.zip
                        parts = filename.replace('.zip', '').split('-')
                        year, month = int(parts[-2]), int(parts[-1])
                    
                    file_dt = datetime(year, month, 1)
                    if start_dt <= file_dt <= end_dt:
                        files.append(file_path)
                except (ValueError, IndexError):
                    continue
        else:
            # 查找日度文件补充缺失的数据
            if data_type == "klines":
                daily_pattern = os.path.join(
                    self.data_directory, market_type, "daily", data_type,
                    symbol, interval, f"{symbol}-{interval}-*.zip"
                )
            else:
                daily_pattern = os.path.join(
                    self.data_directory, market_type, "daily", data_type,
                    symbol, f"{symbol}-{data_type}-*.zip"
                )
            
            daily_files = glob.glob(daily_pattern)
            daily_files.sort()
            
            for file_path in daily_files:
                filename = os.path.basename(file_path)
                try:
                    if data_type == "klines":
                        # 格式: SYMBOL-INTERVAL-YYYY-MM-DD.zip
                        date_part = filename.replace('.zip', '').split('-')[-3:]
                        file_date = '-'.join(date_part)
                    else:
                        # 格式: SYMBOL-DATATYPE-YYYY-MM-DD.zip
                        date_part = filename.replace('.zip', '').split('-')[-3:]
                        file_date = '-'.join(date_part)
                    
                    file_dt = datetime.strptime(file_date, "%Y-%m-%d")
                    if start_dt <= file_dt <= end_dt:
                        files.append(file_path)
                except (ValueError, IndexError):
                    continue
            
        return sorted(list(set(files)))
    
    def _read_zip_file(self, file_path: str, data_type: str, market_type: str) -> pd.DataFrame:
        """读取ZIP文件中的CSV数据"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
                if not csv_files:
                    return pd.DataFrame()
                
                csv_file = csv_files[0]
                with zip_ref.open(csv_file) as csv_data:
                    if market_type == "spot":
                        if data_type == "klines":
                            df = pd.read_csv(csv_data, names=self.kline_columns)
                        elif data_type == "trades":
                            df = pd.read_csv(csv_data, names=self.trade_columns)
                        elif data_type == "aggTrades":
                            df = pd.read_csv(csv_data, names=self.agg_trade_columns)
                    else:
                        df = pd.read_csv(csv_data)
                    
                    return df
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return pd.DataFrame()
    
    def read_data(self, symbol: str, market_type: str = "spot",
                 data_type: str = "aggTrades", interval: str = "1h",
                 start_date: str = "2025-07-26", end_date: str = None,
                 chunk_size: Optional[int] = None) -> pd.DataFrame:
        """读取历史数据
        
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
        if data_type == "klines" and interval not in KLINE_INTERVALS:
            raise ValueError(f"无效的K线间隔: {interval}")
        
        files = self._find_data_files(
            symbol, market_type, data_type, interval, start_date, end_date
        )
        
        if not files:
            print(f"未找到 {symbol} 的数据文件")
            return pd.DataFrame()
        
        print(f"找到 {len(files)} 个数据文件")
        
        if chunk_size:
            return self._read_data_chunks(files, data_type, market_type, chunk_size)
        else:
            return self._read_all_data(files, data_type, market_type)
    
    def _read_all_data(self, files: List[str], data_type: str, market_type: str) -> pd.DataFrame:
        """读取所有数据文件"""
        dfs = []
        
        for file_path in files:
            print(f"读取文件: {os.path.basename(file_path)}")
            df = self._read_zip_file(file_path, data_type, market_type)
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        result = pd.concat(dfs, ignore_index=True)
        return result
    
    def _read_data_chunks(self, files: List[str], data_type: str, market_type: str,
                         chunk_size: int) -> Iterator[pd.DataFrame]:
        """分块读取数据文件"""
        current_chunk = []
        current_size = 0
        
        for file_path in files:
            print(f"读取文件: {os.path.basename(file_path)}")
            df = self._read_zip_file(file_path, data_type, market_type)
            
            if df.empty:
                continue
            
            current_chunk.append(df)
            current_size += len(df)
            
            if current_size >= chunk_size:
                result = pd.concat(current_chunk, ignore_index=True)
                current_chunk = []
                current_size = 0
        
        # 处理剩余数据
        if current_chunk:
            result = pd.concat(current_chunk, ignore_index=True)
    
    
    def get_data_info(self, symbol: str, market_type: str = "spot",
                     data_type: str = "aggTrades", interval: str = "1h") -> dict:
        """获取数据信息"""
        files = self._find_data_files(symbol, market_type, data_type, interval)
        
        if not files:
            return {"symbol": symbol, "files_count": 0, "date_range": None}
        
        # 分析文件日期范围
        dates = []
        for file_path in files:
            filename = os.path.basename(file_path)
            try:
                if "monthly" in file_path:
                    if data_type == "klines":
                        parts = filename.replace('.zip', '').split('-')
                        year, month = int(parts[-2]), int(parts[-1])
                        dates.append(datetime(year, month, 1))
                    else:
                        parts = filename.replace('.zip', '').split('-')
                        year, month = int(parts[-2]), int(parts[-1])
                        dates.append(datetime(year, month, 1))
                elif "daily" in file_path:
                    if data_type == "klines":
                        date_part = filename.replace('.zip', '').split('-')[-3:]
                        file_date = '-'.join(date_part)
                    else:
                        date_part = filename.replace('.zip', '').split('-')[-3:]
                        file_date = '-'.join(date_part)
                    dates.append(datetime.strptime(file_date, "%Y-%m-%d"))
            except (ValueError, IndexError):
                continue
        
        if dates:
            dates.sort()
            date_range = (dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d"))
        else:
            date_range = None
        
        return {
            "symbol": symbol,
            "market_type": market_type,
            "data_type": data_type,
            "interval": interval if data_type == "klines" else None,
            "files_count": len(files),
            "date_range": date_range,
            "files": [os.path.basename(f) for f in files]
        }