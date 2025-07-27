#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易策略模块 - 币安交易系统策略集合

包含各种交易策略的实现:
- 移动平均策略
- 布林带策略
- RSI策略
- 自定义策略基类
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import warnings
import logging

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.parameters = {}
        
    @abstractmethod
    def generate_signal(self, current_data: pd.Series, index: int, full_data: pd.DataFrame) -> Optional[Dict]:
        """生成交易信号
        
        Args:
            current_data: 当前时刻的数据
            index: 当前数据在完整数据中的索引
            full_data: 完整的历史数据
            
        Returns:
            交易信号字典，包含 action ('buy'/'sell') 和 quantity
        """
        pass
    
    def set_parameters(self, **kwargs):
        """设置策略参数"""
        self.parameters.update(kwargs)
        
    def get_parameters(self) -> Dict:
        """获取策略参数"""
        return self.parameters.copy()

class MovingAverageStrategy(BaseStrategy):
    """移动平均策略
    
    当短期均线上穿长期均线时买入，下穿时卖出
    """
    
    def __init__(self, short_window: int = 5, long_window: int = 20, position_size: float = 1000.0):
        super().__init__("MovingAverage")
        self.short_window = short_window
        self.long_window = long_window
        self.position_size = position_size  # 每次交易的金额
        self.last_signal = None
        
        self.set_parameters(
            short_window=short_window,
            long_window=long_window,
            position_size=position_size
        )
    
    def generate_signal(self, current_data: pd.Series, index: int, full_data: pd.DataFrame) -> Optional[Dict]:
        """生成移动平均交叉信号"""
        # 需要足够的历史数据
        if index < self.long_window:
            return None
        
        # 计算移动平均线
        recent_data = full_data.iloc[max(0, index - self.long_window + 1):index + 1]
        
        if len(recent_data) < self.long_window:
            return None
        
        short_ma = recent_data['close'].rolling(window=self.short_window).mean().iloc[-1]
        long_ma = recent_data['close'].rolling(window=self.long_window).mean().iloc[-1]
        
        # 获取前一个时刻的均线值（用于判断交叉）
        if index >= self.long_window:
            prev_data = full_data.iloc[max(0, index - self.long_window):index]
            if len(prev_data) >= self.long_window:
                prev_short_ma = prev_data['close'].rolling(window=self.short_window).mean().iloc[-1]
                prev_long_ma = prev_data['close'].rolling(window=self.long_window).mean().iloc[-1]
            else:
                return None
        else:
            return None
        
        current_price = float(current_data['close'])
        
        # 判断交叉信号
        # 金叉：短期均线从下方穿越长期均线
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            quantity = self.position_size / current_price
            self.last_signal = 'buy'
            return {
                'action': 'buy',
                'quantity': quantity,
                'reason': f'金叉信号: 短期MA({short_ma:.2f}) > 长期MA({long_ma:.2f})'
            }
        
        # 死叉：短期均线从上方穿越长期均线
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            # 只有在有持仓的情况下才卖出
            if self.last_signal == 'buy':
                quantity = self.position_size / current_price
                self.last_signal = 'sell'
                return {
                    'action': 'sell',
                    'quantity': quantity,
                    'reason': f'死叉信号: 短期MA({short_ma:.2f}) < 长期MA({long_ma:.2f})'
                }
        
        return None

class RSIStrategy(BaseStrategy):
    """RSI策略
    
    RSI超买超卖策略：RSI > 70时卖出，RSI < 30时买入
    """
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70, position_size: float = 1000.0):
        super().__init__("RSI")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.position_size = position_size
        self.last_signal = None
        
        self.set_parameters(
            rsi_period=rsi_period,
            oversold=oversold,
            overbought=overbought,
            position_size=position_size
        )
    
    def calculate_rsi(self, prices: pd.Series) -> float:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def generate_signal(self, current_data: pd.Series, index: int, full_data: pd.DataFrame) -> Optional[Dict]:
        """生成RSI信号"""
        # 需要足够的历史数据
        if index < self.rsi_period + 1:
            return None
        
        # 获取用于计算RSI的数据
        recent_data = full_data.iloc[max(0, index - self.rsi_period):index + 1]
        
        if len(recent_data) < self.rsi_period + 1:
            return None
        
        # 计算RSI
        rsi = self.calculate_rsi(recent_data['close'])
        
        if np.isnan(rsi):
            return None
        
        current_price = float(current_data['close'])
        
        # RSI超卖，买入信号
        if rsi < self.oversold and self.last_signal != 'buy':
            quantity = self.position_size / current_price
            self.last_signal = 'buy'
            return {
                'action': 'buy',
                'quantity': quantity,
                'reason': f'RSI超卖信号: RSI({rsi:.2f}) < {self.oversold}'
            }
        
        # RSI超买，卖出信号
        elif rsi > self.overbought and self.last_signal == 'buy':
            quantity = self.position_size / current_price
            self.last_signal = 'sell'
            return {
                'action': 'sell',
                'quantity': quantity,
                'reason': f'RSI超买信号: RSI({rsi:.2f}) > {self.overbought}'
            }
        
        return None

class BollingerBandsStrategy(BaseStrategy):
    """布林带策略
    
    价格触及下轨时买入，触及上轨时卖出
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, position_size: float = 1000.0):
        super().__init__("BollingerBands")
        self.period = period
        self.std_dev = std_dev
        self.position_size = position_size
        self.last_signal = None
        
        self.set_parameters(
            period=period,
            std_dev=std_dev,
            position_size=position_size
        )
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> Dict[str, float]:
        """计算布林带"""
        sma = prices.rolling(window=self.period).mean().iloc[-1]
        std = prices.rolling(window=self.period).std().iloc[-1]
        
        upper_band = sma + (self.std_dev * std)
        lower_band = sma - (self.std_dev * std)
        
        return {
            'middle': sma,
            'upper': upper_band,
            'lower': lower_band
        }
    
    def generate_signal(self, current_data: pd.Series, index: int, full_data: pd.DataFrame) -> Optional[Dict]:
        """生成布林带信号"""
        # 需要足够的历史数据
        if index < self.period:
            return None
        
        # 获取用于计算布林带的数据
        recent_data = full_data.iloc[max(0, index - self.period + 1):index + 1]
        
        if len(recent_data) < self.period:
            return None
        
        # 计算布林带
        bands = self.calculate_bollinger_bands(recent_data['close'])
        
        if any(np.isnan(v) for v in bands.values()):
            return None
        
        current_price = float(current_data['close'])
        
        # 价格触及下轨，买入信号
        if current_price <= bands['lower'] and self.last_signal != 'buy':
            quantity = self.position_size / current_price
            self.last_signal = 'buy'
            return {
                'action': 'buy',
                'quantity': quantity,
                'reason': f'触及下轨: 价格({current_price:.2f}) <= 下轨({bands["lower"]:.2f})'
            }
        
        # 价格触及上轨，卖出信号
        elif current_price >= bands['upper'] and self.last_signal == 'buy':
            quantity = self.position_size / current_price
            self.last_signal = 'sell'
            return {
                'action': 'sell',
                'quantity': quantity,
                'reason': f'触及上轨: 价格({current_price:.2f}) >= 上轨({bands["upper"]:.2f})'
            }
        
        return None

class BuyAndHoldStrategy(BaseStrategy):
    """买入持有策略
    
    在第一个时刻买入并持有到最后
    """
    
    def __init__(self, position_size: float = 10000.0):
        super().__init__("BuyAndHold")
        self.position_size = position_size
        self.has_bought = False
        
        self.set_parameters(position_size=position_size)
    
    def generate_signal(self, current_data: pd.Series, index: int, full_data: pd.DataFrame) -> Optional[Dict]:
        """生成买入持有信号"""
        # 只在第一次执行时买入
        if not self.has_bought and index == 0:
            current_price = float(current_data['close'])
            quantity = self.position_size / current_price
            self.has_bought = True
            return {
                'action': 'buy',
                'quantity': quantity,
                'reason': '买入持有策略初始买入'
            }
        
        return None

# 策略工厂
class StrategyFactory:
    """策略工厂类"""
    
    @staticmethod
    def create_strategy(strategy_name: str, **kwargs) -> BaseStrategy:
        """创建策略实例"""
        strategies = {
            'ma': MovingAverageStrategy,
            'moving_average': MovingAverageStrategy,
            'rsi': RSIStrategy,
            'bollinger': BollingerBandsStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'buy_hold': BuyAndHoldStrategy,
            'buy_and_hold': BuyAndHoldStrategy
        }
        
        strategy_name = strategy_name.lower()
        if strategy_name not in strategies:
            raise ValueError(f"未知策略: {strategy_name}. 可用策略: {list(strategies.keys())}")
        
        return strategies[strategy_name](**kwargs)
    
    @staticmethod
    def list_strategies() -> List[str]:
        """列出所有可用策略"""
        return ['moving_average', 'rsi', 'bollinger_bands', 'buy_and_hold']