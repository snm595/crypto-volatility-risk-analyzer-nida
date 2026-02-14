"""
Advanced visualization utilities for cryptocurrency analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CryptoVisualizer:
    """Advanced visualization utilities for cryptocurrency analysis"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.risk_colors = {
            'Low Risk': '#00ff00',
            'Medium Risk': '#ffff00', 
            'High Risk': '#ff9900',
            'Very High Risk': '#ff0000'
        }
    
    def create_interactive_price_chart(self, price_data_dict, title="Cryptocurrency Prices"):
        """Create interactive price chart with multiple assets"""
        fig = go.Figure()
        
        for i, (symbol, df) in enumerate(price_data_dict.items()):
            color = self.color_palette[i % len(self.color_palette)]
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['price'],
                mode='lines',
                name=f'{symbol}',
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:,.2f}}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template='plotly_dark',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_volatility_chart(self, returns_data_dict, title="Volatility Analysis"):
        """Create comprehensive volatility chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Returns', 'Rolling Volatility'),
            vertical_spacing=0.1
        )
        
        for i, (symbol, df) in enumerate(returns_data_dict.items()):
            color = self.color_palette[i % len(self.color_palette)]
            
            # Daily returns
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['simple_return'] * 100,
                    mode='lines',
                    name=f'{symbol} Returns',
                    line=dict(color=color, width=1),
                    hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Return: %{{y:.2f}}%<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Rolling volatility (7-day and 30-day)
            for window in [7, 30]:
                vol_col = f'rolling_vol_annual_{window}'
                if vol_col in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[vol_col] * 100,
                            mode='lines',
                            name=f'{symbol} {window}-day Vol',
                            line=dict(color=color, width=2),
                            showlegend=window == 7,  # Only show legend for 7-day
                            hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Vol: %{{y:.1f}}%<extra></extra>'
                        ),
                        row=2, col=1
                    )
        
        fig.update_layout(
            height=800,
            title_text=title,
            template='plotly_dark',
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Daily Return (%)", row=1, col=1)
        fig.update_yaxes(title_text="Annualized Volatility (%)", row=2, col=1)
        
        return fig
    
    def create_risk_return_scatter(self, metrics_df, title="Risk-Return Analysis"):
        """Create risk-return scatter plot with risk classification"""
        fig = go.Figure()
        
        for _, row in metrics_df.iterrows():
            fig.add_trace(go.Scatter(
                x=[float(row['annualized_volatility'])],  # Ensure float conversion
                y=[float(row['sharpe_ratio'])],          # Ensure float conversion
                mode='markers+text',
                text=row['symbol'],
                textposition="top center",
                marker=dict(
                    color=self.risk_colors.get(row['risk_level'], '#8888ff'),
                    size=15,
                    line=dict(width=2, color='white')
                ),
                name=row['symbol'],
                hovertemplate=f"<b>{row['symbol']}</b><br>Volatility: {row['annualized_volatility']:.2%}<br>Sharpe: {row['sharpe_ratio']:.3f}<br>Risk: {row['risk_level']}<extra></extra>"
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Annualized Volatility",
            yaxis_title="Sharpe Ratio",
            template='plotly_dark',
            height=500
        )
        
        return fig
    
    def create_correlation_heatmap(self, correlation_matrix, title="Correlation Matrix"):
        """Create correlation heatmap"""
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=500
        )
        
        return fig
    
    def create_normalized_comparison(self, price_data_dict, title="Normalized Price Comparison"):
        """Create normalized price comparison chart"""
        fig = go.Figure()
        
        for i, (symbol, df) in enumerate(price_data_dict.items()):
            color = self.color_palette[i % len(self.color_palette)]
            
            # Normalize prices to start at 100
            normalized_prices = (df['price'] / df['price'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized_prices,
                mode='lines',
                name=f'{symbol} (Normalized)',
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Normalized: %{{y:.1f}}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f"{title} (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            template='plotly_dark',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_beta_comparison(self, metrics_df, benchmark='BTC', title="Beta Analysis"):
        """Create beta comparison chart"""
        beta_data = metrics_df[metrics_df['symbol'] != benchmark].copy()
        
        fig = go.Figure(data=[
            go.Bar(
                x=beta_data['symbol'],
                y=beta_data['beta'],
                text=beta_data['beta'].apply(lambda x: f"{x:.3f}"),
                textposition='auto',
                marker_color='lightblue'
            )
        ])
        
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Market Beta (1.0)")
        
        fig.update_layout(
            title=f"{title} vs {benchmark}",
            xaxis_title="Cryptocurrency",
            yaxis_title="Beta",
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    def create_risk_distribution_pie(self, metrics_df, title="Risk Distribution"):
        """Create risk level distribution pie chart"""
        risk_counts = metrics_df['risk_level'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                hole=0.4,
                textinfo='label+percent+value',
                marker_colors=[self.risk_colors.get(risk, '#8888ff') for risk in risk_counts.index]
            )
        ])
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    def create_portfolio_performance_chart(self, portfolio_data, benchmark_data=None):
        """Create portfolio performance chart"""
        fig = go.Figure()
        
        # Portfolio performance
        fig.add_trace(go.Scatter(
            x=portfolio_data.index,
            y=portfolio_data['portfolio_value'],
            mode='lines',
            name='Portfolio',
            line=dict(color='#00f2fe', width=3),
            hovertemplate='Portfolio<br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
        ))
        
        # Benchmark comparison
        if benchmark_data is not None:
            fig.add_trace(go.Scatter(
                x=benchmark_data.index,
                y=benchmark_data['benchmark_value'],
                mode='lines',
                name='Benchmark',
                line=dict(color='#ff6b6b', width=2, dash='dash'),
                hovertemplate='Benchmark<br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Portfolio Performance",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (USD)",
            template='plotly_dark',
            height=500
        )
        
        return fig
    
    def create_drawdown_chart(self, price_data, title="Drawdown Analysis"):
        """Create drawdown chart"""
        # Calculate drawdown
        peak = price_data['price'].expanding().max()
        drawdown = (price_data['price'] - peak) / peak * 100
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Price', 'Drawdown'),
            vertical_spacing=0.1
        )
        
        # Price chart
        fig.add_trace(
            go.Scatter(
                x=price_data.index,
                y=price_data['price'],
                mode='lines',
                name='Price',
                line=dict(color='#00f2fe', width=2),
                hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Drawdown chart
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown,
                mode='lines',
                name='Drawdown',
                line=dict(color='#ff6b6b', width=2),
                fill='tonexty',
                hovertemplate='Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            title_text=title,
            template='plotly_dark'
        )
        
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        return fig
    
    def create_metrics_dashboard(self, metrics_df):
        """Create comprehensive metrics dashboard"""
        # Create subplots for different metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sharpe Ratio', 'Annual Volatility', 'Beta', '24h Change'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Sharpe Ratio
        fig.add_trace(
            go.Bar(x=metrics_df['symbol'], y=metrics_df['sharpe_ratio'], name='Sharpe Ratio'),
            row=1, col=1
        )
        
        # Volatility
        fig.add_trace(
            go.Bar(x=metrics_df['symbol'], y=metrics_df['annualized_volatility'], name='Volatility'),
            row=1, col=2
        )
        
        # Beta
        fig.add_trace(
            go.Bar(x=metrics_df['symbol'], y=metrics_df['beta'], name='Beta'),
            row=2, col=1
        )
        
        # 24h Change
        fig.add_trace(
            go.Bar(x=metrics_df['symbol'], y=metrics_df['price_change_24h'], name='24h Change'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Comprehensive Metrics Dashboard",
            template='plotly_dark',
            showlegend=False
        )
        
        return fig
    
    def create_time_series_analysis(self, price_data_dict, indicators=['MA_7', 'MA_30']):
        """Create advanced time series analysis with indicators"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Price with Moving Averages', 'Volume', 'RSI'),
            vertical_spacing=0.05
        )
        
        for i, (symbol, df) in enumerate(price_data_dict.items()):
            color = self.color_palette[i % len(self.color_palette)]
            
            # Price and moving averages
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['price'],
                    mode='lines',
                    name=f'{symbol} Price',
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:,.2f}}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add moving averages
            for ma in indicators:
                if ma in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[ma],
                            mode='lines',
                            name=f'{symbol} {ma}',
                            line=dict(color=color, width=1, dash='dash'),
                            showlegend=False,
                            hovertemplate=f'<b>{symbol} {ma}</b><br>Date: %{{x}}<br>MA: $%{{y:,.2f}}<extra></extra>'
                        ),
                        row=1, col=1
                    )
            
            # Volume (if available)
            if 'volume' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['volume'],
                        mode='lines',
                        name=f'{symbol} Volume',
                        line=dict(color=color, width=1),
                        showlegend=False,
                        hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Volume: %{{y:,.0f}}<extra></extra>'
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            height=1000,
            title_text="Advanced Time Series Analysis",
            template='plotly_dark',
            hovermode='x unified'
        )
        
        return fig
