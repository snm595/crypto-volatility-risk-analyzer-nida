import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from data_engine import DataEngine
from analytics_engine import AnalyticsEngine

# Professional CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles_pro.css">
""", unsafe_allow_html=True)

# Initialize engines
@st.cache_resource(ttl=30)  # Cache for 30 seconds
def get_data_engine():
    return DataEngine()

@st.cache_resource(ttl=30)
def get_analytics_engine():
    return AnalyticsEngine()

def render_professional_navbar():
    """Render institutional-grade top navigation"""
    data_engine = get_data_engine()
    status = data_engine.get_data_status()
    
    navbar_html = f"""
    <div class="pro-navbar">
        <div class="navbar-brand">
            Crypto Analytics Pro
        </div>
        
        <div class="navbar-center">
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span>Live</span>
            </div>
            <div class="sync-time">
                {data_engine.last_update.strftime('%H:%M:%S') if data_engine.last_update else 'Syncing...'}
            </div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 1rem;">
            <button class="sync-btn" onclick="location.reload()" title="Sync Data">
                🔄
            </button>
            <div class="user-profile" title="User Profile">
                JD
            </div>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

def render_professional_sidebar():
    """Render minimal icon-based sidebar"""
    sidebar_html = """
    <div class="pro-sidebar">
        <div class="sidebar-nav">
            <a href="#" class="nav-icon active" title="Dashboard">
                <span>📊</span>
                <div>Dashboard</div>
            </a>
            <a href="#" class="nav-icon" title="Markets">
                <span>📈</span>
                <div>Markets</div>
            </a>
            <a href="#" class="nav-icon" title="Risk Analytics">
                <span>⚠</span>
                <div>Risk</div>
            </a>
            <a href="#" class="nav-icon" title="Data Engine">
                <span>⚙</span>
                <div>Engine</div>
            </a>
        </div>
    </div>
    """
    st.markdown(sidebar_html, unsafe_allow_html=True)

def create_sparkline(prices, color="#00D4FF"):
    """Create mini sparkline chart"""
    if len(prices) < 2:
        return ""
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(prices))),
        y=prices,
        mode='lines',
        line=dict(color=color, width=1.5),
        fill='tonexty',
        fillcolor=f'{color}20'
    ))
    
    fig.update_layout(
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
    )
    
    return fig.to_html(include_plotlyjs=False, div_id=f"sparkline-{hash(str(prices))}")

def render_professional_tickers(data):
    """Render horizontal ticker-style price cards with sparklines"""
    if not data:
        return st.info("No market data available")
    
    cols = st.columns(len(data))
    
    for i, (symbol, info) in enumerate(data.items()):
        with cols[i]:
            change_class = "positive" if info.get('change_24h', 0) > 0 else "negative"
            ticker_class = f"price-ticker {change_class}"
            
            # Generate mini sparkline data
            sparkline_prices = [info.get('price', 100) * (1 + np.random.normal(0, 0.01)) for _ in range(10)]
            sparkline_html = create_sparkline(sparkline_prices, "#00D4FF" if change_class == "positive" else "#EF4444")
            
            ticker_html = f"""
            <div class="{ticker_class}">
                <div class="ticker-header">
                    <div class="ticker-symbol">{symbol}</div>
                    <div class="sparkline">{sparkline_html}</div>
                </div>
                <div class="ticker-body">
                    <div class="ticker-price">${info.get('price', 0):,.2f}</div>
                    <div class="ticker-change {change_class}">
                        {info.get('change_24h', 0):+.2f}%
                    </div>
                </div>
                <div class="ticker-volume">
                    VOL ${info.get('volume_24h', 0):,.0f}
                </div>
            </div>
            """
            st.markdown(ticker_html, unsafe_allow_html=True)

def render_candlestick_chart(data, timeframe='1D'):
    """Render professional candlestick chart"""
    if not data:
        st.info("No data available for chart")
        return
    
    fig = go.Figure()
    
    # Generate professional candlestick data
    for symbol, info in data.items():
        dates = pd.date_range(end=datetime.now(), periods=96, freq='15min')  # 24h of 15-min candles
        base_price = info.get('price', 100)
        
        # Generate OHLC data
        ohlc_data = []
        for i, date in enumerate(dates):
            price = base_price * (1 + np.random.normal(0, 0.005))
            high = price * (1 + abs(np.random.normal(0, 0.002)))
            low = price * (1 - abs(np.random.normal(0, 0.002)))
            open_price = ohlc_data[-1][1] if ohlc_data else price
            close_price = price
            
            ohlc_data.append([date, open_price, high, low, close_price])
        
        df = pd.DataFrame(ohlc_data, columns=['date', 'open', 'high', 'low', 'close'])
        
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol,
            increasing_line_color='#00D4FF',
            decreasing_line_color='#EF4444',
            increasing_fillcolor='#00D4FF20',
            decreasing_fillcolor='#EF444420'
        ))
    
    fig.update_layout(
        title=None,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
            tickformat='$,.2f'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_professional_timeframes():
    """Render professional timeframe selector"""
    timeframes = ['1H', '4H', '1D', '1W', '1M']
    
    selector_html = """
    <div class="timeframe-selector">
    """
    
    for tf in timeframes:
        active_class = "active" if tf == '1D' else ""
        selector_html += f'<button class="timeframe-btn {active_class}">{tf}</button>'
    
    selector_html += "</div>"
    
    st.markdown(selector_html, unsafe_allow_html=True)

def render_risk_analytics(data):
    """Render institutional-grade risk analytics"""
    analytics = get_analytics_engine()
    
    # Risk Score Card
    st.markdown("### RISK SCORE")
    risk_score = 65  # Calculate from real data
    risk_level = "MEDIUM" if risk_score > 40 else "LOW"
    risk_class = "medium" if risk_score > 40 else "low"
    
    risk_html = f"""
    <div class="metric-card">
        <div class="metric-label">Portfolio Risk</div>
        <div class="metric-value number-change">{risk_score}</div>
        <div class="metric-badge {risk_class}">{risk_level}</div>
    </div>
    """
    st.markdown(risk_html, unsafe_allow_html=True)
    
    # Volatility Level
    st.markdown("### VOLATILITY")
    volatility = 3.8  # Calculate from real data
    vol_level = "MODERATE" if volatility > 3 else "LOW"
    vol_class = "medium" if volatility > 3 else "low"
    
    vol_html = f"""
    <div class="metric-card">
        <div class="metric-label">24h Volatility</div>
        <div class="metric-value small number-change">{volatility:.1f}%</div>
        <div class="metric-badge {vol_class}">{vol_level}</div>
    </div>
    """
    st.markdown(vol_html, unsafe_allow_html=True)
    
    # Market Sentiment
    st.markdown("### SENTIMENT")
    sentiment, score, color = analytics.calculate_market_sentiment(data)
    sentiment_class = "bullish" if "Bullish" in sentiment else "bearish"
    
    sentiment_html = f"""
    <div class="metric-card">
        <div class="metric-label">Market Sentiment</div>
        <div class="metric-value small number-change">{score:.0f}</div>
        <div class="metric-badge sentiment-{sentiment_class}">{sentiment}</div>
    </div>
    """
    st.markdown(sentiment_html, unsafe_allow_html=True)

def render_kpi_stack(data):
    """Render vertical KPI metrics stack"""
    analytics = get_analytics_engine()
    metrics = analytics.calculate_metrics(data)
    
    if not metrics:
        return
    
    st.markdown("### MARKET METRICS")
    
    kpis = [
        ("24h Volume", f"${metrics.get('total_volume_24h', 0):,.0f}"),
        ("Avg Change", f"{metrics.get('avg_change_24h', 0):+.2f}%"),
        ("Positive", f"{metrics.get('positive_movers', 0)}"),
        ("Negative", f"{metrics.get('negative_movers', 0)}")
    ]
    
    for label, value in kpis:
        kpi_html = f"""
        <div class="kpi-item">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)

def render_volatility_trend():
    """Render professional volatility trend chart"""
    # Generate sample volatility data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    volatility = [3.2, 3.5, 4.1, 3.8, 3.3, 2.9, 3.1, 3.7, 4.2, 3.9, 
                  3.4, 3.0, 2.8, 3.2, 3.6, 4.0, 3.8, 3.5, 3.1, 2.9,
                  3.3, 3.7, 4.1, 3.9, 3.6, 3.2, 2.8, 3.0, 3.4, 3.5]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=volatility,
        mode='lines',
        name='Volatility',
        line=dict(color='#8B5CF6', width=2),
        fill='tonexty',
        fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    
    fig.update_layout(
        title="30-Day Volatility Trend",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickformat='.1f%'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main institutional dashboard"""
    # Hide default Streamlit elements
    st.markdown("""
    <style>
        .stApp > header {visibility: hidden;}
        .stApp > footer {visibility: hidden;}
        .css-1d391kg {padding-top: 0;}
        .main .block-container {padding-top: 0;}
    </style>
    """, unsafe_allow_html=True)
    
    # Render professional layout
    render_professional_navbar()
    
    # Create main grid layout
    col1, col2 = st.columns([0.15, 0.85])
    
    with col1:
        render_professional_sidebar()
    
    with col2:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Sync data in background
        data_engine = get_data_engine()
        data = data_engine.sync_data()
        
        if data:
            # Price Tickers
            render_professional_tickers(data)
            
            st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
            
            # Main chart section
            chart_col, risk_col = st.columns([0.7, 0.3])
            
            with chart_col:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                render_professional_timeframes()
                render_candlestick_chart(data)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with risk_col:
                render_risk_analytics(data)
            
            # Bottom analytics
            st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
            
            analytics_col1, analytics_col2 = st.columns([0.6, 0.4])
            
            with analytics_col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                render_volatility_trend()
                st.markdown('</div>', unsafe_allow_html=True)
            
            with analytics_col2:
                render_kpi_stack(data)
        
        else:
            # Professional loading state
            st.markdown('<div class="loading-shimmer"></div>', unsafe_allow_html=True)
            st.markdown('<div class="loading-shimmer" style="height: 200px; margin-top: 1rem;"></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
