#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块 - 币安交易系统回测结果可视化

功能:
- 权益曲线图
- 价格走势与交易信号图
- 收益分布图
- 回撤分析图
- 交易统计图表
- 风险指标展示
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
warnings.filterwarnings('ignore')

class BacktestVisualizer:
    """回测结果可视化器"""
    
    def __init__(self, figsize: Tuple[int, int] = (15, 10)):
        self.figsize = figsize
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
    
    def plot_equity_curve(self, equity_data: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
        """绘制权益曲线图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, height_ratios=[3, 1])
        
        # 权益曲线
        ax1.plot(equity_data['timestamp'], equity_data['total_equity'], 
                color=self.colors['primary'], linewidth=2, label='总权益')
        ax1.plot(equity_data['timestamp'], equity_data['cash'], 
                color=self.colors['secondary'], linewidth=1, alpha=0.7, label='现金')
        ax1.plot(equity_data['timestamp'], equity_data['market_value'], 
                color=self.colors['success'], linewidth=1, alpha=0.7, label='市值')
        
        ax1.set_title('投资组合权益曲线', fontsize=16, fontweight='bold')
        ax1.set_ylabel('金额 (USD)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 收益率曲线
        ax2.plot(equity_data['timestamp'], equity_data['return_pct'], 
                color=self.colors['info'], linewidth=1.5, label='累计收益率')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.set_ylabel('收益率 (%)', fontsize=12)
        ax2.set_xlabel('时间', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(equity_data)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_price_and_signals(self, price_data: pd.DataFrame, trade_history: pd.DataFrame, 
                              save_path: Optional[str] = None) -> plt.Figure:
        """绘制价格走势和交易信号图"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 价格走势
        ax.plot(price_data['timestamp'], price_data['close'], 
               color=self.colors['primary'], linewidth=1.5, label='收盘价')
        
        # 交易信号
        if not trade_history.empty:
            buy_signals = trade_history[trade_history['side'] == 'buy']
            sell_signals = trade_history[trade_history['side'] == 'sell']
            
            if not buy_signals.empty:
                ax.scatter(buy_signals['timestamp'], buy_signals['price'], 
                          color=self.colors['success'], marker='^', s=100, 
                          label='买入信号', zorder=5)
            
            if not sell_signals.empty:
                ax.scatter(sell_signals['timestamp'], sell_signals['price'], 
                          color=self.colors['danger'], marker='v', s=100, 
                          label='卖出信号', zorder=5)
        
        ax.set_title('价格走势与交易信号', fontsize=16, fontweight='bold')
        ax.set_ylabel('价格 (USD)', fontsize=12)
        ax.set_xlabel('时间', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 格式化x轴
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(price_data)//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_drawdown(self, equity_data: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
        """绘制回撤分析图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, height_ratios=[2, 1])
        
        # 计算回撤
        equity_data = equity_data.copy()
        equity_data['cummax'] = equity_data['total_equity'].cummax()
        equity_data['drawdown'] = (equity_data['total_equity'] - equity_data['cummax']) / equity_data['cummax'] * 100
        
        # 权益曲线和最高点
        ax1.plot(equity_data['timestamp'], equity_data['total_equity'], 
                color=self.colors['primary'], linewidth=2, label='总权益')
        ax1.plot(equity_data['timestamp'], equity_data['cummax'], 
                color=self.colors['success'], linewidth=1, alpha=0.7, label='历史最高点')
        
        ax1.set_title('权益曲线与回撤分析', fontsize=16, fontweight='bold')
        ax1.set_ylabel('金额 (USD)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 回撤曲线
        ax2.fill_between(equity_data['timestamp'], equity_data['drawdown'], 0, 
                        color=self.colors['danger'], alpha=0.3, label='回撤')
        ax2.plot(equity_data['timestamp'], equity_data['drawdown'], 
                color=self.colors['danger'], linewidth=1.5)
        
        max_dd = equity_data['drawdown'].min()
        ax2.axhline(y=max_dd, color=self.colors['danger'], linestyle='--', 
                   label=f'最大回撤: {max_dd:.2f}%')
        
        ax2.set_ylabel('回撤 (%)', fontsize=12)
        ax2.set_xlabel('时间', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(equity_data)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_returns_distribution(self, equity_data: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
        """绘制收益分布图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # 计算日收益率
        equity_data = equity_data.copy()
        equity_data['daily_return'] = equity_data['total_equity'].pct_change() * 100
        daily_returns = equity_data['daily_return'].dropna()
        
        # 收益率直方图
        ax1.hist(daily_returns, bins=30, color=self.colors['primary'], alpha=0.7, edgecolor='black')
        ax1.axvline(daily_returns.mean(), color=self.colors['danger'], linestyle='--', 
                   label=f'均值: {daily_returns.mean():.3f}%')
        ax1.axvline(daily_returns.median(), color=self.colors['success'], linestyle='--', 
                   label=f'中位数: {daily_returns.median():.3f}%')
        
        ax1.set_title('日收益率分布', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日收益率 (%)', fontsize=12)
        ax1.set_ylabel('频次', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q图
        from scipy import stats
        stats.probplot(daily_returns, dist="norm", plot=ax2)
        ax2.set_title('收益率正态性检验 (Q-Q图)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_trade_analysis(self, trade_history: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
        """绘制交易分析图"""
        if trade_history.empty:
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.text(0.5, 0.5, '无交易数据', ha='center', va='center', fontsize=20)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            return fig
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.figsize)
        
        # 交易次数统计
        trade_counts = trade_history['side'].value_counts()
        ax1.pie(trade_counts.values, labels=trade_counts.index, autopct='%1.1f%%', 
               colors=[self.colors['success'], self.colors['danger']])
        ax1.set_title('交易类型分布', fontsize=14, fontweight='bold')
        
        # 交易时间分布
        trade_history['hour'] = pd.to_datetime(trade_history['timestamp']).dt.hour
        hourly_trades = trade_history['hour'].value_counts().sort_index()
        ax2.bar(hourly_trades.index, hourly_trades.values, color=self.colors['primary'], alpha=0.7)
        ax2.set_title('交易时间分布', fontsize=14, fontweight='bold')
        ax2.set_xlabel('小时', fontsize=12)
        ax2.set_ylabel('交易次数', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 盈亏分布（如果有realized_pnl列）
        if 'realized_pnl' in trade_history.columns:
            pnl_data = trade_history['realized_pnl'].dropna()
            if not pnl_data.empty:
                profitable = pnl_data[pnl_data > 0]
                losing = pnl_data[pnl_data < 0]
                
                ax3.hist([profitable, losing], bins=20, color=[self.colors['success'], self.colors['danger']], 
                        alpha=0.7, label=['盈利交易', '亏损交易'])
                ax3.set_title('盈亏分布', fontsize=14, fontweight='bold')
                ax3.set_xlabel('盈亏金额 (USD)', fontsize=12)
                ax3.set_ylabel('频次', fontsize=12)
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, '无盈亏数据', ha='center', va='center')
        else:
            ax3.text(0.5, 0.5, '无盈亏数据', ha='center', va='center')
        
        # 交易价格分布
        ax4.hist(trade_history['price'], bins=20, color=self.colors['info'], alpha=0.7, edgecolor='black')
        ax4.set_title('交易价格分布', fontsize=14, fontweight='bold')
        ax4.set_xlabel('价格 (USD)', fontsize=12)
        ax4.set_ylabel('频次', fontsize=12)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_performance_summary(self, results: Dict, save_path: Optional[str] = None) -> plt.Figure:
        """创建性能摘要图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.figsize)
        
        # 关键指标
        metrics = {
            '总收益率': f"{results.get('total_return', 0):.2f}%",
            '夏普比率': f"{results.get('sharpe_ratio', 0):.3f}",
            '最大回撤': f"{results.get('max_drawdown', 0):.2f}%",
            '波动率': f"{results.get('volatility', 0):.2f}%",
            '胜率': f"{results.get('win_rate', 0):.1f}%",
            '交易次数': f"{results.get('total_trades', 0)}"
        }
        
        # 指标表格
        ax1.axis('tight')
        ax1.axis('off')
        table_data = [[k, v] for k, v in metrics.items()]
        table = ax1.table(cellText=table_data, colLabels=['指标', '数值'], 
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        ax1.set_title('关键性能指标', fontsize=14, fontweight='bold', pad=20)
        
        # 收益对比（与买入持有策略对比）
        strategies = ['策略收益', '买入持有']
        returns = [results.get('total_return', 0), 0]  # 这里需要实际的买入持有收益
        colors = [self.colors['success'] if r >= 0 else self.colors['danger'] for r in returns]
        
        bars = ax2.bar(strategies, returns, color=colors, alpha=0.7)
        ax2.set_title('收益对比', fontsize=14, fontweight='bold')
        ax2.set_ylabel('收益率 (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 在柱子上显示数值
        for bar, value in zip(bars, returns):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value:.2f}%', ha='center', va='bottom')
        
        # 风险收益散点图
        risk = results.get('volatility', 0)
        return_val = results.get('total_return', 0)
        
        ax3.scatter([risk], [return_val], s=200, color=self.colors['primary'], alpha=0.7)
        ax3.set_xlabel('风险 (波动率 %)', fontsize=12)
        ax3.set_ylabel('收益率 (%)', fontsize=12)
        ax3.set_title('风险收益图', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 添加标注
        ax3.annotate('策略位置', (risk, return_val), xytext=(10, 10), 
                    textcoords='offset points', fontsize=10)
        
        # 月度收益热力图（如果有足够数据）
        if 'equity_curve' in results and results['equity_curve']:
            equity_df = pd.DataFrame(results['equity_curve'])
            equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
            equity_df['month'] = equity_df['timestamp'].dt.to_period('M')
            
            if len(equity_df['month'].unique()) > 1:
                monthly_returns = equity_df.groupby('month')['return_pct'].last().diff()
                monthly_returns = monthly_returns.dropna()
                
                if len(monthly_returns) > 0:
                    months = [str(m) for m in monthly_returns.index]
                    returns_matrix = monthly_returns.values.reshape(1, -1)
                    
                    im = ax4.imshow(returns_matrix, cmap='RdYlGn', aspect='auto')
                    ax4.set_xticks(range(len(months)))
                    ax4.set_xticklabels(months, rotation=45)
                    ax4.set_yticks([])
                    ax4.set_title('月度收益热力图', fontsize=14, fontweight='bold')
                    
                    # 添加颜色条
                    cbar = plt.colorbar(im, ax=ax4)
                    cbar.set_label('收益率 (%)', fontsize=10)
                else:
                    ax4.text(0.5, 0.5, '数据不足', ha='center', va='center')
            else:
                ax4.text(0.5, 0.5, '数据不足', ha='center', va='center')
        else:
            ax4.text(0.5, 0.5, '无权益数据', ha='center', va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def generate_full_report(self, results: Dict, price_data: pd.DataFrame, 
                           output_dir: str = "backtest_results") -> Dict[str, str]:
        """生成完整的回测报告"""
        import os
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = {}
        
        # 权益曲线图
        if 'equity_curve' in results and results['equity_curve']:
            equity_df = pd.DataFrame(results['equity_curve'])
            equity_path = os.path.join(output_dir, 'equity_curve.png')
            self.plot_equity_curve(equity_df, equity_path)
            saved_files['equity_curve'] = equity_path
        
        # 价格和信号图
        if 'trade_history' in results and results['trade_history']:
            trade_df = pd.DataFrame(results['trade_history'])
            signals_path = os.path.join(output_dir, 'price_signals.png')
            self.plot_price_and_signals(price_data, trade_df, signals_path)
            saved_files['price_signals'] = signals_path
        
        # 回撤分析图
        if 'equity_curve' in results and results['equity_curve']:
            equity_df = pd.DataFrame(results['equity_curve'])
            drawdown_path = os.path.join(output_dir, 'drawdown_analysis.png')
            self.plot_drawdown(equity_df, drawdown_path)
            saved_files['drawdown_analysis'] = drawdown_path
        
        # 收益分布图
        if 'equity_curve' in results and results['equity_curve']:
            equity_df = pd.DataFrame(results['equity_curve'])
            returns_path = os.path.join(output_dir, 'returns_distribution.png')
            self.plot_returns_distribution(equity_df, returns_path)
            saved_files['returns_distribution'] = returns_path
        
        # 交易分析图
        if 'trade_history' in results and results['trade_history']:
            trade_df = pd.DataFrame(results['trade_history'])
            trade_path = os.path.join(output_dir, 'trade_analysis.png')
            self.plot_trade_analysis(trade_df, trade_path)
            saved_files['trade_analysis'] = trade_path
        
        # 性能摘要图
        summary_path = os.path.join(output_dir, 'performance_summary.png')
        self.create_performance_summary(results, summary_path)
        saved_files['performance_summary'] = summary_path
        
        return saved_files