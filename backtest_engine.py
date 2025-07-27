#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎 - 币安交易系统回测核心模块

功能:
- 策略回测执行
- 交易信号处理
- 资金管理
- 性能指标计算
- 风险控制
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    """订单类型"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"

@dataclass
class Order:
    """订单数据结构"""
    timestamp: datetime
    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    status: OrderStatus = OrderStatus.PENDING
    order_id: str = ""
    commission: float = 0.0
    
    def __post_init__(self):
        if not self.order_id:
            self.order_id = f"{self.symbol}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{self.order_type.value}"

@dataclass
class Position:
    """持仓数据结构"""
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.avg_price

class Portfolio:
    """投资组合管理"""
    
    def __init__(self, initial_capital: float = 100000.0, commission_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trade_history: List[Dict] = []
        self.equity_curve: List[Dict] = []
        
    def add_order(self, order: Order) -> bool:
        """添加订单"""
        try:
            if order.order_type == OrderType.BUY:
                required_cash = order.quantity * order.price * (1 + self.commission_rate)
                if self.cash >= required_cash:
                    self._execute_buy_order(order)
                    return True
                else:
                    logger.warning(f"资金不足，无法执行买入订单: {order.order_id}")
                    return False
            else:  # SELL
                if self._can_sell(order.symbol, order.quantity):
                    self._execute_sell_order(order)
                    return True
                else:
                    logger.warning(f"持仓不足，无法执行卖出订单: {order.order_id}")
                    return False
        except Exception as e:
            logger.error(f"执行订单失败: {e}")
            return False
    
    def _execute_buy_order(self, order: Order):
        """执行买入订单"""
        commission = order.quantity * order.price * self.commission_rate
        total_cost = order.quantity * order.price + commission
        
        # 更新现金
        self.cash -= total_cost
        
        # 更新持仓
        if order.symbol not in self.positions:
            self.positions[order.symbol] = Position(order.symbol)
        
        position = self.positions[order.symbol]
        total_quantity = position.quantity + order.quantity
        total_cost_basis = position.quantity * position.avg_price + order.quantity * order.price
        
        position.quantity = total_quantity
        position.avg_price = total_cost_basis / total_quantity if total_quantity > 0 else 0
        
        # 记录订单和交易
        order.status = OrderStatus.FILLED
        order.commission = commission
        self.orders.append(order)
        
        self.trade_history.append({
            'timestamp': order.timestamp,
            'symbol': order.symbol,
            'side': 'buy',
            'quantity': order.quantity,
            'price': order.price,
            'commission': commission,
            'cash_after': self.cash
        })
    
    def _execute_sell_order(self, order: Order):
        """执行卖出订单"""
        commission = order.quantity * order.price * self.commission_rate
        total_proceeds = order.quantity * order.price - commission
        
        # 更新现金
        self.cash += total_proceeds
        
        # 更新持仓
        position = self.positions[order.symbol]
        
        # 计算已实现盈亏
        realized_pnl = order.quantity * (order.price - position.avg_price) - commission
        position.realized_pnl += realized_pnl
        position.quantity -= order.quantity
        
        # 如果持仓为0，重置平均价格
        if position.quantity <= 0:
            position.quantity = 0
            position.avg_price = 0
        
        # 记录订单和交易
        order.status = OrderStatus.FILLED
        order.commission = commission
        self.orders.append(order)
        
        self.trade_history.append({
            'timestamp': order.timestamp,
            'symbol': order.symbol,
            'side': 'sell',
            'quantity': order.quantity,
            'price': order.price,
            'commission': commission,
            'realized_pnl': realized_pnl,
            'cash_after': self.cash
        })
    
    def _can_sell(self, symbol: str, quantity: float) -> bool:
        """检查是否可以卖出"""
        if symbol not in self.positions:
            return False
        return self.positions[symbol].quantity >= quantity
    
    def update_positions(self, current_prices: Dict[str, float], timestamp: datetime):
        """更新持仓市值和未实现盈亏"""
        total_market_value = 0
        total_unrealized_pnl = 0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices and position.quantity > 0:
                current_price = current_prices[symbol]
                market_value = position.quantity * current_price
                unrealized_pnl = position.quantity * (current_price - position.avg_price)
                
                position.unrealized_pnl = unrealized_pnl
                total_market_value += market_value
                total_unrealized_pnl += unrealized_pnl
        
        # 记录权益曲线
        total_equity = self.cash + total_market_value
        self.equity_curve.append({
            'timestamp': timestamp,
            'cash': self.cash,
            'market_value': total_market_value,
            'total_equity': total_equity,
            'unrealized_pnl': total_unrealized_pnl,
            'return_pct': (total_equity - self.initial_capital) / self.initial_capital * 100
        })
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        if not self.equity_curve:
            return {}
        
        latest = self.equity_curve[-1]
        total_trades = len(self.trade_history)
        
        # 计算胜率
        profitable_trades = sum(1 for trade in self.trade_history 
                              if trade.get('realized_pnl', 0) > 0)
        win_rate = profitable_trades / total_trades * 100 if total_trades > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': latest['total_equity'],
            'total_return': latest['return_pct'],
            'cash': latest['cash'],
            'market_value': latest['market_value'],
            'total_trades': total_trades,
            'win_rate': win_rate,
            'commission_paid': sum(order.commission for order in self.orders)
        }

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000.0, commission_rate: float = 0.001):
        self.portfolio = Portfolio(initial_capital, commission_rate)
        self.data: Optional[pd.DataFrame] = None
        self.strategy = None
        self.results: Dict = {}
        
    def load_data(self, data: pd.DataFrame):
        """加载历史数据"""
        self.data = data.copy()
        # 确保时间戳列存在并转换为datetime
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        elif 'open_time' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['open_time'])
        
        # 确保数据按时间排序
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
        logger.info(f"加载数据完成，共 {len(self.data)} 条记录")
    
    def set_strategy(self, strategy):
        """设置交易策略"""
        self.strategy = strategy
        logger.info(f"设置策略: {strategy.__class__.__name__}")
    
    def run_backtest(self, symbol: str = "ETHUSDT") -> Dict:
        """运行回测"""
        if self.data is None:
            raise ValueError("请先加载数据")
        if self.strategy is None:
            raise ValueError("请先设置策略")
        
        logger.info("开始回测...")
        
        for i, row in self.data.iterrows():
            current_time = row['timestamp']
            current_price = float(row['close'])
            
            # 更新持仓市值
            self.portfolio.update_positions({symbol: current_price}, current_time)
            
            # 获取策略信号
            signal = self.strategy.generate_signal(row, i, self.data)
            
            # 执行交易
            if signal:
                self._execute_signal(signal, symbol, current_price, current_time)
        
        # 计算回测结果
        self.results = self._calculate_results()
        logger.info("回测完成")
        
        return self.results
    
    def _execute_signal(self, signal: Dict, symbol: str, price: float, timestamp: datetime):
        """执行交易信号"""
        if signal['action'] == 'buy' and signal['quantity'] > 0:
            order = Order(
                timestamp=timestamp,
                symbol=symbol,
                order_type=OrderType.BUY,
                quantity=signal['quantity'],
                price=price
            )
            self.portfolio.add_order(order)
        
        elif signal['action'] == 'sell' and signal['quantity'] > 0:
            order = Order(
                timestamp=timestamp,
                symbol=symbol,
                order_type=OrderType.SELL,
                quantity=signal['quantity'],
                price=price
            )
            self.portfolio.add_order(order)
    
    def _calculate_results(self) -> Dict:
        """计算回测结果"""
        portfolio_summary = self.portfolio.get_portfolio_summary()
        
        if not self.portfolio.equity_curve:
            return portfolio_summary
        
        # 转换为DataFrame便于计算
        equity_df = pd.DataFrame(self.portfolio.equity_curve)
        
        # 计算收益率序列
        equity_df['daily_return'] = equity_df['total_equity'].pct_change()
        
        # 计算风险指标
        returns = equity_df['daily_return'].dropna()
        
        # 最大回撤
        equity_df['cummax'] = equity_df['total_equity'].cummax()
        equity_df['drawdown'] = (equity_df['total_equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min() * 100
        
        # 夏普比率 (假设无风险利率为0)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # 波动率
        volatility = returns.std() * np.sqrt(252) * 100
        
        portfolio_summary.update({
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'equity_curve': self.portfolio.equity_curve,
            'trade_history': self.portfolio.trade_history
        })
        
        return portfolio_summary
    
    def get_equity_curve(self) -> pd.DataFrame:
        """获取权益曲线数据"""
        return pd.DataFrame(self.portfolio.equity_curve)
    
    def get_trade_history(self) -> pd.DataFrame:
        """获取交易历史数据"""
        return pd.DataFrame(self.portfolio.trade_history)