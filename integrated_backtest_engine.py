#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成回测引擎
支持自动数据下载和流式回测处理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import threading
import time
import os
from typing import Optional, Dict, Any, List

from backtest_engine import BacktestEngine, Portfolio
from data_downloader import BinanceDataDownloader
from data_reader import BinanceDataReader
from strategies import BaseStrategy

class IntegratedBacktestEngine(BacktestEngine):
    """集成回测引擎，支持自动数据下载和流式处理"""
    
    def __init__(self, initial_capital: float = 100000):
        super().__init__(initial_capital)
        self.downloader = BinanceDataDownloader()
        self.reader = BinanceDataReader()
        self.download_progress = {}
    
    def _get_last_day_of_month(self, year: int, month: int) -> int:
        """获取指定年月的最后一天"""
        import calendar
        return calendar.monthrange(year, month)[1]
        
    def load_data_with_auto_download(self, symbol: str, start_date: str, end_date: str, 
                                   interval: str = '1h', market_type: str = 'spot') -> Optional[pd.DataFrame]:
        """加载数据，如果本地不存在则自动下载"""
        try:
            print(f"📊 正在加载 {symbol} 数据...")
            
            # 首先尝试从本地读取数据
            try:
                data = self.reader.read_data(
                    symbol=symbol,
                    market_type=market_type,
                    data_type='klines',
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if data is not None and not data.empty:
                    print(f"✅ 从本地加载了 {len(data)} 条数据")
                    return self._prepare_data_for_backtest(data)
                    
            except Exception as e:
                print(f"⚠️ 本地数据读取失败: {e}")
            
            # 如果本地数据不存在或不完整，开始下载
            print(f"🔄 本地数据不足，开始下载 {symbol} 数据...")
            
            # 下载数据
            success = self._download_missing_data(symbol, start_date, end_date, interval, market_type)
            
            if success:
                # 重新尝试读取数据
                data = self.reader.read_data(
                    symbol=symbol,
                    market_type=market_type,
                    data_type='klines',
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if data is not None and not data.empty:
                    print(f"✅ 下载并加载了 {len(data)} 条数据")
                    return self._prepare_data_for_backtest(data)
            
            print(f"❌ 无法获取 {symbol} 的数据")
            return None
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return None
    
    def _download_missing_data(self, symbol: str, start_date: str, end_date: str, 
                             interval: str, market_type: str) -> bool:
        """下载缺失的数据"""
        try:
            # 解析日期
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 按月下载数据
            current_date = start_dt
            download_success = True
            
            while current_date <= end_dt:
                year = current_date.year
                month = current_date.month
                
                print(f"📥 下载 {symbol} {year}-{month:02d} 数据...")
                
                try:
                    # 下载月度数据
                    downloaded_files = self.downloader.download_data(
                        symbols=[symbol],
                        market_type=market_type,
                        data_type='klines',
                        interval=interval,
                        start_date=f"{year}-{month:02d}-01",
                        end_date=f"{year}-{month:02d}-{self._get_last_day_of_month(year, month):02d}",
                        download_monthly=True,
                        download_daily=False
                    )
                    success = len(downloaded_files) > 0
                    
                    if success:
                        print(f"✅ {year}-{month:02d} 数据下载成功")
                    else:
                        print(f"⚠️ {year}-{month:02d} 数据下载失败")
                        download_success = False
                        
                except Exception as e:
                    print(f"❌ {year}-{month:02d} 数据下载错误: {e}")
                    download_success = False
                
                # 移动到下个月
                if month == 12:
                    current_date = current_date.replace(year=year+1, month=1)
                else:
                    current_date = current_date.replace(month=month+1)
            
            return download_success
            
        except Exception as e:
            print(f"❌ 数据下载过程失败: {e}")
            return False
    
    def _prepare_data_for_backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """为回测准备数据格式"""
        try:
            # 确保数据包含必要的列
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            
            if not all(col in data.columns for col in required_columns):
                print(f"❌ 数据缺少必要列: {required_columns}")
                return None
            
            # 确保索引是时间戳
            if not isinstance(data.index, pd.DatetimeIndex):
                if 'timestamp' in data.columns:
                    data['timestamp'] = pd.to_datetime(data['timestamp'])
                    data = data.set_index('timestamp')
                elif 'open_time' in data.columns:
                    data['open_time'] = pd.to_datetime(data['open_time'])
                    data = data.set_index('open_time')
                else:
                    print("❌ 无法找到时间戳列")
                    return None
            
            # 确保数据类型正确
            for col in required_columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # 移除空值
            data = data.dropna()
            
            # 按时间排序
            data = data.sort_index()
            
            print(f"📊 数据准备完成: {len(data)} 条记录，时间范围 {data.index[0]} 到 {data.index[-1]}")
            
            return data
            
        except Exception as e:
            print(f"❌ 数据准备失败: {e}")
            return None
    
    def run_backtest_with_auto_download(self, symbol: str, strategy: BaseStrategy, 
                                      start_date: str, end_date: str, 
                                      initial_capital: float = None,
                                      interval: str = '1h', market_type: str = 'spot') -> Optional[Dict[str, Any]]:
        """运行带自动下载的回测"""
        try:
            print(f"🚀 开始集成回测: {symbol}")
            print(f"📅 时间范围: {start_date} 到 {end_date}")
            print(f"💰 初始资金: ${initial_capital or self.portfolio.initial_capital:,.2f}")
            print(f"📈 策略: {strategy.__class__.__name__}")
            
            # 设置初始资金
            if initial_capital:
                self.portfolio = Portfolio(initial_capital)
            
            # 加载数据（自动下载）
            data = self.load_data_with_auto_download(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                market_type=market_type
            )
            
            if data is None or data.empty:
                print("❌ 无法获取数据，回测终止")
                return None
            
            # 运行回测
            print(f"🔄 开始回测处理...")
            results = self.run_backtest(data, strategy)
            
            if results:
                print(f"✅ 回测完成！")
                print(f"📊 处理了 {len(data)} 条数据")
                print(f"💹 总收益率: {results.get('total_return', 0):.2%}")
            
            return results
            
        except Exception as e:
            print(f"❌ 集成回测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_streaming_backtest(self, symbol: str, strategy: BaseStrategy, 
                             start_date: str, end_date: str, 
                             chunk_size: int = 1000,
                             interval: str = '1h', market_type: str = 'spot') -> Optional[Dict[str, Any]]:
        """运行流式回测，分块处理数据"""
        try:
            print(f"🌊 开始流式回测: {symbol}")
            print(f"📦 分块大小: {chunk_size} 条记录")
            
            # 解析日期范围
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 重置组合
            self.portfolio = Portfolio(self.portfolio.initial_capital)
            
            # 按时间块流式处理
            current_date = start_dt
            chunk_days = 30  # 每次处理30天的数据
            
            while current_date <= end_dt:
                chunk_end = min(current_date + timedelta(days=chunk_days), end_dt)
                chunk_start = current_date.strftime('%Y-%m-%d')
                chunk_end_str = chunk_end.strftime('%Y-%m-%d')
                
                print(f"🔄 处理时间段: {chunk_start} 到 {chunk_end_str}")
                
                # 尝试读取已下载的数据块
                chunk_data = self.reader.read_data(
                    symbol=symbol,
                    market_type=market_type,
                    data_type='klines',
                    interval=interval,
                    start_date=chunk_start,
                    end_date=chunk_end_str
                )
                
                # 如果数据不存在，下载该时间段的数据
                if chunk_data is None or chunk_data.empty:
                    print(f"📥 下载 {chunk_start} 到 {chunk_end_str} 的数据...")
                    success = self._download_missing_data(
                        symbol, chunk_start, chunk_end_str, interval, market_type
                    )
                    
                    if success:
                        chunk_data = self.reader.read_data(
                            symbol=symbol,
                            market_type=market_type,
                            data_type='klines',
                            interval=interval,
                            start_date=chunk_start,
                            end_date=chunk_end_str
                        )
                
                # 处理数据块
                if chunk_data is not None and not chunk_data.empty:
                    chunk_data = self._prepare_data_for_backtest(chunk_data)
                    
                    if chunk_data is not None:
                        print(f"📊 处理 {len(chunk_data)} 条记录")
                        
                        # 处理当前块的每条记录
                        for timestamp, row in chunk_data.iterrows():
                            signal = strategy.generate_signal(chunk_data.loc[:timestamp])
                            if signal != 0:
                                self.portfolio.execute_trade(signal, row['close'], timestamp)
                        
                        # 更新组合价值
                        last_price = chunk_data['close'].iloc[-1]
                        self.portfolio.update_market_value(last_price)
                        
                        print(f"💰 当前资金: ${self.portfolio.total_equity:.2f}")
                
                # 移动到下一个时间块
                current_date = chunk_end + timedelta(days=1)
            
            # 计算最终结果（使用完整数据进行性能计算）
            full_data = self.load_data_with_auto_download(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                market_type=market_type
            )
            
            if full_data is not None:
                results = self._calculate_performance_metrics(full_data)
            else:
                results = self._calculate_basic_performance_metrics()
            
            print(f"✅ 流式回测完成！")
            return results
            
        except Exception as e:
            print(f"❌ 流式回测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_basic_performance_metrics(self) -> Dict[str, Any]:
        """计算基础性能指标（当无法获取完整数据时使用）"""
        try:
            initial_capital = self.portfolio.initial_capital
            final_equity = self.portfolio.total_equity
            total_return = (final_equity - initial_capital) / initial_capital
            
            return {
                'initial_capital': initial_capital,
                'final_equity': final_equity,
                'total_return': total_return,
                'total_trades': len(self.portfolio.trades),
                'portfolio_history': self.portfolio.equity_history
            }
            
        except Exception as e:
            print(f"❌ 性能指标计算失败: {e}")
            return {}
    
    def get_download_progress(self, symbol: str) -> Dict[str, Any]:
        """获取下载进度"""
        return self.download_progress.get(symbol, {})
    
    def cancel_download(self, symbol: str) -> bool:
        """取消下载"""
        try:
            if symbol in self.download_progress:
                self.download_progress[symbol]['cancelled'] = True
                return True
            return False
        except Exception:
            return False
    
    def run_multi_symbol_backtest(self, symbols: List[str], strategy: BaseStrategy,
                                start_date: str, end_date: str,
                                weights: Optional[Dict[str, float]] = None,
                                interval: str = '1h', market_type: str = 'spot') -> Optional[Dict[str, Any]]:
        """运行多标的回测"""
        try:
            print(f"🎯 开始多标的回测: {symbols}")
            
            if weights is None:
                # 等权重分配
                weights = {symbol: 1.0/len(symbols) for symbol in symbols}
            
            # 为每个标的分配资金
            symbol_capitals = {}
            for symbol in symbols:
                symbol_capitals[symbol] = self.portfolio.initial_capital * weights.get(symbol, 0)
            
            # 存储每个标的的结果
            symbol_results = {}
            
            for symbol in symbols:
                print(f"\n📈 处理标的: {symbol}")
                
                # 创建独立的回测引擎
                symbol_engine = IntegratedBacktestEngine(symbol_capitals[symbol])
                
                # 运行单标的回测
                result = symbol_engine.run_backtest_with_auto_download(
                    symbol=symbol,
                    strategy=strategy,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=symbol_capitals[symbol],
                    interval=interval,
                    market_type=market_type
                )
                
                if result:
                    symbol_results[symbol] = result
                    print(f"✅ {symbol} 回测完成，收益率: {result.get('total_return', 0):.2%}")
                else:
                    print(f"❌ {symbol} 回测失败")
            
            # 合并结果
            if symbol_results:
                combined_results = self._combine_multi_symbol_results(symbol_results, weights)
                print(f"\n🎉 多标的回测完成！")
                print(f"💹 组合总收益率: {combined_results.get('total_return', 0):.2%}")
                return combined_results
            else:
                print("❌ 所有标的回测都失败了")
                return None
                
        except Exception as e:
            print(f"❌ 多标的回测失败: {e}")
            return None
    
    def _combine_multi_symbol_results(self, symbol_results: Dict[str, Dict], 
                                    weights: Dict[str, float]) -> Dict[str, Any]:
        """合并多标的回测结果"""
        try:
            total_initial = sum(result['initial_capital'] for result in symbol_results.values())
            total_final = sum(result['final_equity'] for result in symbol_results.values())
            
            combined_return = (total_final - total_initial) / total_initial
            
            # 计算加权收益率
            weighted_return = sum(
                weights.get(symbol, 0) * result.get('total_return', 0)
                for symbol, result in symbol_results.items()
            )
            
            return {
                'total_initial_capital': total_initial,
                'total_final_equity': total_final,
                'total_return': combined_return,
                'weighted_return': weighted_return,
                'symbol_results': symbol_results,
                'weights': weights,
                'symbols': list(symbol_results.keys())
            }
            
        except Exception as e:
            print(f"❌ 结果合并失败: {e}")
            return {}