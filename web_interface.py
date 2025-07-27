#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面 - 币安交易系统回测平台

功能:
- 策略配置界面
- 回测参数设置
- 实时回测执行
- 结果可视化展示
- 报告下载
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 导入回测模块
from run_backtest import BacktestRunner
from strategies import StrategyFactory

# 页面配置
st.set_page_config(
    page_title="币安交易系统回测平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.success-metric {
    border-left-color: #28a745;
}
.danger-metric {
    border-left-color: #dc3545;
}
.warning-metric {
    border-left-color: #ffc107;
}
</style>
""", unsafe_allow_html=True)

class WebInterface:
    """Web界面类"""
    
    def __init__(self):
        self.runner = BacktestRunner()
        self.results = None
        
        # 初始化session state
        if 'backtest_results' not in st.session_state:
            st.session_state.backtest_results = None
        if 'backtest_running' not in st.session_state:
            st.session_state.backtest_running = False
    
    def render_header(self):
        """渲染页面头部"""
        st.markdown('<h1 class="main-header">📈 币安交易系统回测平台</h1>', unsafe_allow_html=True)
        st.markdown("---")
    
    def render_sidebar(self) -> Dict:
        """渲染侧边栏配置"""
        st.sidebar.header("🔧 回测配置")
        
        # 基本配置
        st.sidebar.subheader("基本设置")
        symbol = st.sidebar.selectbox(
            "交易对",
            ["ETHUSDT", "BTCUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"],
            index=0
        )
        
        initial_capital = st.sidebar.number_input(
            "初始资金 (USD)",
            min_value=1000.0,
            max_value=1000000.0,
            value=10000.0,
            step=1000.0
        )
        
        # 策略选择
        st.sidebar.subheader("策略配置")
        strategy_name = st.sidebar.selectbox(
            "交易策略",
            ["ma", "rsi", "bb", "buy_hold"],
            format_func=lambda x: {
                "ma": "移动平均线策略",
                "rsi": "RSI策略", 
                "bb": "布林带策略",
                "buy_hold": "买入持有策略"
            }[x]
        )
        
        # 策略参数
        strategy_params = {}
        
        if strategy_name == "ma":
            st.sidebar.subheader("移动平均线参数")
            strategy_params = {
                "short_window": st.sidebar.slider("短期均线", 3, 20, 5),
                "long_window": st.sidebar.slider("长期均线", 10, 50, 20)
            }
        
        elif strategy_name == "rsi":
            st.sidebar.subheader("RSI参数")
            strategy_params = {
                "period": st.sidebar.slider("RSI周期", 5, 30, 14),
                "oversold_threshold": st.sidebar.slider("超卖阈值", 20, 40, 30),
                "overbought_threshold": st.sidebar.slider("超买阈值", 60, 80, 70)
            }
        
        elif strategy_name == "bb":
            st.sidebar.subheader("布林带参数")
            strategy_params = {
                "period": st.sidebar.slider("周期", 10, 30, 20),
                "std_dev": st.sidebar.slider("标准差倍数", 1.0, 3.0, 2.0, 0.1)
            }
        
        # 时间范围
        st.sidebar.subheader("时间范围")
        use_date_range = st.sidebar.checkbox("指定时间范围")
        
        start_date = None
        end_date = None
        
        if use_date_range:
            start_date = st.sidebar.date_input(
                "开始日期",
                value=datetime.now() - timedelta(days=30)
            ).strftime('%Y-%m-%d')
            
            end_date = st.sidebar.date_input(
                "结束日期",
                value=datetime.now()
            ).strftime('%Y-%m-%d')
        
        # 数据文件
        st.sidebar.subheader("数据源")
        data_file = st.sidebar.text_input(
            "数据文件路径 (可选)",
            placeholder="留空自动查找"
        )
        
        return {
            'symbol': symbol,
            'strategy_name': strategy_name,
            'strategy_params': strategy_params,
            'initial_capital': initial_capital,
            'start_date': start_date,
            'end_date': end_date,
            'data_file': data_file if data_file else None
        }
    
    def run_backtest_ui(self, config: Dict):
        """运行回测UI"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 开始回测", type="primary", use_container_width=True):
                st.session_state.backtest_running = True
                
                with st.spinner("正在运行回测，请稍候..."):
                    try:
                        results = self.runner.run_backtest(**config)
                        st.session_state.backtest_results = results
                        st.session_state.backtest_running = False
                        st.success("回测完成！")
                        st.rerun()
                        
                    except Exception as e:
                        st.session_state.backtest_running = False
                        st.error(f"回测失败: {str(e)}")
    
    def render_results(self, results: Dict):
        """渲染回测结果"""
        if not results:
            st.info("请先运行回测以查看结果")
            return
        
        st.header("📊 回测结果")
        
        # 关键指标
        self.render_key_metrics(results)
        
        # 图表展示
        self.render_charts(results)
        
        # 交易记录
        self.render_trade_history(results)
    
    def render_key_metrics(self, results: Dict):
        """渲染关键指标"""
        st.subheader("关键指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = results.get('total_return', 0)
            delta_color = "normal" if total_return >= 0 else "inverse"
            st.metric(
                "总收益率",
                f"{total_return:.2f}%",
                delta=f"{total_return:.2f}%",
                delta_color=delta_color
            )
        
        with col2:
            max_drawdown = results.get('max_drawdown', 0)
            st.metric(
                "最大回撤",
                f"{max_drawdown:.2f}%",
                delta=f"{max_drawdown:.2f}%",
                delta_color="inverse"
            )
        
        with col3:
            sharpe_ratio = results.get('sharpe_ratio', 0)
            st.metric(
                "夏普比率",
                f"{sharpe_ratio:.3f}",
                delta=f"{sharpe_ratio:.3f}"
            )
        
        with col4:
            win_rate = results.get('win_rate', 0)
            st.metric(
                "胜率",
                f"{win_rate:.1f}%",
                delta=f"{win_rate:.1f}%"
            )
        
        # 第二行指标
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            volatility = results.get('volatility', 0)
            st.metric("波动率", f"{volatility:.2f}%")
        
        with col6:
            total_trades = results.get('total_trades', 0)
            st.metric("总交易次数", f"{total_trades}")
        
        with col7:
            annualized_return = results.get('annualized_return', 0)
            st.metric("年化收益率", f"{annualized_return:.2f}%")
        
        with col8:
            if 'portfolio' in results:
                final_equity = results['portfolio'].total_equity
                st.metric("最终权益", f"${final_equity:,.2f}")
    
    def render_charts(self, results: Dict):
        """渲染图表"""
        st.subheader("图表分析")
        
        # 权益曲线
        if 'equity_curve' in results and results['equity_curve']:
            self.plot_equity_curve(results['equity_curve'])
        
        # 价格和信号
        if 'trade_history' in results and results['trade_history']:
            self.plot_price_and_signals(results)
        
        # 回撤分析
        if 'equity_curve' in results and results['equity_curve']:
            self.plot_drawdown_analysis(results['equity_curve'])
    
    def plot_equity_curve(self, equity_data: List[Dict]):
        """绘制权益曲线"""
        df = pd.DataFrame(equity_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['权益曲线', '收益率'],
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # 权益曲线
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['total_equity'],
                mode='lines',
                name='总权益',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['cash'],
                mode='lines',
                name='现金',
                line=dict(color='#ff7f0e', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['market_value'],
                mode='lines',
                name='市值',
                line=dict(color='#2ca02c', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # 收益率
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['return_pct'],
                mode='lines',
                name='累计收益率',
                line=dict(color='#17a2b8', width=1.5)
            ),
            row=2, col=1
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=1)
        
        fig.update_layout(
            title="投资组合权益曲线",
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="时间", row=2, col=1)
        fig.update_yaxes(title_text="金额 (USD)", row=1, col=1)
        fig.update_yaxes(title_text="收益率 (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_price_and_signals(self, results: Dict):
        """绘制价格和交易信号"""
        # 重新加载价格数据
        data_file = results.get('data_file')
        if not data_file or not os.path.exists(data_file):
            st.warning("无法加载价格数据")
            return
        
        try:
            price_data = self.runner.load_data_from_csv(data_file)
            trade_history = pd.DataFrame(results['trade_history'])
            
            fig = go.Figure()
            
            # 价格线
            fig.add_trace(
                go.Scatter(
                    x=price_data['timestamp'],
                    y=price_data['close'],
                    mode='lines',
                    name='收盘价',
                    line=dict(color='#1f77b4', width=1.5)
                )
            )
            
            # 交易信号
            if not trade_history.empty:
                trade_history['timestamp'] = pd.to_datetime(trade_history['timestamp'])
                
                buy_signals = trade_history[trade_history['side'] == 'buy']
                sell_signals = trade_history[trade_history['side'] == 'sell']
                
                if not buy_signals.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=buy_signals['timestamp'],
                            y=buy_signals['price'],
                            mode='markers',
                            name='买入信号',
                            marker=dict(
                                symbol='triangle-up',
                                size=10,
                                color='#2ca02c'
                            )
                        )
                    )
                
                if not sell_signals.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=sell_signals['timestamp'],
                            y=sell_signals['price'],
                            mode='markers',
                            name='卖出信号',
                            marker=dict(
                                symbol='triangle-down',
                                size=10,
                                color='#d62728'
                            )
                        )
                    )
            
            fig.update_layout(
                title="价格走势与交易信号",
                xaxis_title="时间",
                yaxis_title="价格 (USD)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"绘制价格图表失败: {e}")
    
    def plot_drawdown_analysis(self, equity_data: List[Dict]):
        """绘制回撤分析"""
        df = pd.DataFrame(equity_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['cummax'] = df['total_equity'].cummax()
        df['drawdown'] = (df['total_equity'] - df['cummax']) / df['cummax'] * 100
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['权益曲线与历史最高点', '回撤分析'],
            vertical_spacing=0.1,
            row_heights=[0.6, 0.4]
        )
        
        # 权益曲线
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['total_equity'],
                mode='lines',
                name='总权益',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['cummax'],
                mode='lines',
                name='历史最高点',
                line=dict(color='#2ca02c', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # 回撤
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['drawdown'],
                mode='lines',
                name='回撤',
                fill='tonexty',
                line=dict(color='#d62728', width=1.5),
                fillcolor='rgba(214, 39, 40, 0.3)'
            ),
            row=2, col=1
        )
        
        max_dd = df['drawdown'].min()
        fig.add_hline(
            y=max_dd,
            line_dash="dash",
            line_color="#d62728",
            annotation_text=f"最大回撤: {max_dd:.2f}%",
            row=2, col=1
        )
        
        fig.update_layout(
            title="回撤分析",
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="时间", row=2, col=1)
        fig.update_yaxes(title_text="金额 (USD)", row=1, col=1)
        fig.update_yaxes(title_text="回撤 (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_trade_history(self, results: Dict):
        """渲染交易历史"""
        if 'trade_history' not in results or not results['trade_history']:
            return
        
        st.subheader("交易记录")
        
        trade_df = pd.DataFrame(results['trade_history'])
        trade_df['timestamp'] = pd.to_datetime(trade_df['timestamp'])
        
        # 格式化显示
        display_df = trade_df.copy()
        display_df['时间'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['方向'] = display_df['side'].map({'buy': '买入', 'sell': '卖出'})
        display_df['价格'] = display_df['price'].round(4)
        display_df['数量'] = display_df['quantity'].round(6)
        display_df['金额'] = (display_df['price'] * display_df['quantity']).round(2)
        
        # 选择显示列
        columns_to_show = ['时间', '方向', '价格', '数量', '金额']
        if 'realized_pnl' in display_df.columns:
            display_df['已实现盈亏'] = display_df['realized_pnl'].round(2)
            columns_to_show.append('已实现盈亏')
        
        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            hide_index=True
        )
        
        # 交易统计
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**交易统计:**")
            st.write(f"- 总交易次数: {len(trade_df)}")
            st.write(f"- 买入次数: {len(trade_df[trade_df['side'] == 'buy'])}")
            st.write(f"- 卖出次数: {len(trade_df[trade_df['side'] == 'sell'])}")
        
        with col2:
            if 'realized_pnl' in trade_df.columns:
                pnl_data = trade_df['realized_pnl'].dropna()
                if not pnl_data.empty:
                    profitable_trades = len(pnl_data[pnl_data > 0])
                    total_pnl_trades = len(pnl_data)
                    win_rate = (profitable_trades / total_pnl_trades * 100) if total_pnl_trades > 0 else 0
                    
                    st.write("**盈亏统计:**")
                    st.write(f"- 盈利交易: {profitable_trades}")
                    st.write(f"- 亏损交易: {total_pnl_trades - profitable_trades}")
                    st.write(f"- 胜率: {win_rate:.1f}%")
    
    def run(self):
        """运行Web界面"""
        self.render_header()
        
        # 侧边栏配置
        config = self.render_sidebar()
        
        # 主要内容区域
        tab1, tab2 = st.tabs(["🚀 回测执行", "📊 结果分析"])
        
        with tab1:
            st.header("回测配置")
            
            # 显示当前配置
            with st.expander("当前配置", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**交易对:** {config['symbol']}")
                    st.write(f"**策略:** {config['strategy_name']}")
                    st.write(f"**初始资金:** ${config['initial_capital']:,.2f}")
                
                with col2:
                    if config['start_date']:
                        st.write(f"**开始日期:** {config['start_date']}")
                    if config['end_date']:
                        st.write(f"**结束日期:** {config['end_date']}")
                    if config['strategy_params']:
                        st.write(f"**策略参数:** {config['strategy_params']}")
            
            # 运行回测按钮
            self.run_backtest_ui(config)
            
            # 显示运行状态
            if st.session_state.backtest_running:
                st.info("回测正在运行中...")
        
        with tab2:
            # 显示结果
            if st.session_state.backtest_results:
                self.render_results(st.session_state.backtest_results)
                
                # 下载报告按钮
                if st.button("📥 生成并下载完整报告"):
                    with st.spinner("生成报告中..."):
                        try:
                            self.runner.results = st.session_state.backtest_results
                            saved_files = self.runner.generate_report()
                            st.success("报告生成完成！")
                            
                            # 显示文件列表
                            st.write("生成的文件:")
                            for name, path in saved_files.items():
                                st.write(f"- {name}: {path}")
                                
                        except Exception as e:
                            st.error(f"生成报告失败: {e}")
            else:
                st.info("请先在'回测执行'标签页中运行回测")

def main():
    """主函数"""
    interface = WebInterface()
    interface.run()

if __name__ == '__main__':
    main()