import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from data_engine import DataEngine
from analytics_engine import AnalyticsEngine

# Initialize session state FIRST
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '1D'
if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = 'BTC'

# Amazing CSS - Simple & Beautiful with AGGRESSIVE OVERRIDES
st.markdown("""
<style>
    /* CSS RESET - Override everything first */
    * {
        box-sizing: border-box !important;
    }
    
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Base Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%) !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Streamlit Stuff */
    .stDeployButton, .stHeader, .stToolbar, .stMainMenu {
        display: none !important;
    }
    
    /* Main Container */
    .main-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        padding: 20px !important;
    }
    
    /* Header */
    .header {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 20px 30px !important;
        margin-bottom: 30px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .logo {
        font-size: 28px !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #00d4ff, #8b5cf6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    .live-status {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        background: rgba(16, 185, 129, 0.2) !important;
        padding: 8px 16px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
    }
    
    .live-dot {
        width: 8px !important;
        height: 8px !important;
        background: #10b981 !important;
        border-radius: 50% !important;
        animation: pulse 2s infinite !important;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5) !important;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Price Cards */
    .price-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
        gap: 20px !important;
        margin-bottom: 30px !important;
    }
    
    .price-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .price-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, #00d4ff, #8b5cf6) !important;
    }
    
    .price-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0, 212, 255, 0.2) !important;
        border-color: rgba(0, 212, 255, 0.3) !important;
    }
    
    .coin-name {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #8b92a8 !important;
        margin-bottom: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .coin-price {
        font-size: 32px !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        color: #ffffff !important;
    }
    
    .price-change {
        display: inline-block !important;
        padding: 6px 12px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .positive {
        background: rgba(16, 185, 129, 0.2) !important;
        color: #10b981 !important;
    }
    
    }
    
    .volume {
        color: #8b92a8;
        font-size: 0.9rem;
        margin-top: 10px;
    }
    
    /* Chart Container */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    
    .chart-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 15px;
    }
    
    /* Streamlit Component Styling - Compatible */
    div[data-testid="stSelectbox"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    div[data-testid="stButton"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #8b92a8;
        font-weight: 600;
    }
    
    div[data-testid="stButton"]:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: #00d4ff;
        color: #00d4ff;
    }
    
    div[data-testid="stButton"][data-kind="primary"] {
        background: linear-gradient(45deg, #00d4ff, #8b5cf6);
        border-color: transparent;
        color: white;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
    }
    
    .stat-label {
        color: #8b92a8;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 10px 0;
    }
    
    .stat-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .risk-low {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
    }
    
    .risk-medium {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
    }
    
    .risk-high {
        background: rgba(255, 71, 87, 0.2);
        color: #ff4757;
    }
    
    /* Loading */
    .loading {
        text-align: center;
        padding: 40px;
        font-size: 18px;
        color: #8b92a8;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-container {
            padding: 10px;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .coin-price {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize engines
@st.cache_resource(ttl=30)
def get_data_engine():
    return DataEngine()

@st.cache_resource(ttl=30)
def get_analytics_engine():
    return AnalyticsEngine()

def create_simple_sparkline(prices, color="#00d4ff"):
    """Create beautiful sparkline"""
    if len(prices) < 2:
        return ""
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(prices))),
        y=prices,
        mode='lines',
        line=dict(color=color, width=2)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
    )
    
    return fig.to_html(include_plotlyjs=False, div_id=f"sparkline-{hash(str(prices))}")

def render_beautiful_header():
    """Render beautiful header"""
    data_engine = get_data_engine()
    
    header_html = f"""
    <div class="header">
        <div class="logo">📊 Crypto Analytics Pro</div>
        <div class="live-status">
            <div class="live-dot"></div>
            <span>LIVE MARKET DATA</span>
        </div>
        <div style="color: #8b92a8; font-size: 14px;">
            Last: {data_engine.last_update.strftime('%H:%M:%S') if data_engine.last_update else 'Loading...'}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_beautiful_prices(data):
    """Render beautiful price cards"""
    if not data:
        st.markdown('<div class="loading">🔄 Loading market data...</div>', unsafe_allow_html=True)
        return
    
    # Initialize selected_crypto if not exists
    if 'selected_crypto' not in st.session_state:
        st.session_state.selected_crypto = list(data.keys())[0] if data else 'BTC'
    
    # Only show the selected cryptocurrency
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto in data:
        symbol = selected_crypto
        info = data[symbol]
        change_class = "positive" if info.get('change_24h', 0) > 0 else "negative"
        change_symbol = "↑" if info.get('change_24h', 0) > 0 else "↓"
        
        st.markdown('<div class="price-grid">', unsafe_allow_html=True)
        
        card_html = f"""
        <div class="price-card">
            <div class="coin-name">{symbol}</div>
            <div class="coin-price">${info.get('price', 0):,.2f}</div>
            <div class="price-change {change_class}">
                {change_symbol} {abs(info.get('change_24h', 0)):.2f}%
            </div>
            <div class="volume">Volume: ${info.get('volume_24h', 0):,.0f}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="loading">❌ Selected crypto not available</div>', unsafe_allow_html=True)

# Initialize session state
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '1D'
if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = 'BTC'

def render_beautiful_chart(data):
    """Render beautiful main chart"""
    if not data:
        st.markdown('<div class="loading">📈 No chart data available</div>', unsafe_allow_html=True)
        return
    
    # Initialize selected_crypto if not exists
    if 'selected_crypto' not in st.session_state:
        st.session_state.selected_crypto = list(data.keys())[0] if data else 'BTC'
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Chart header with crypto selector and timeframe buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown('<div class="chart-title">📈 Price Chart</div>', unsafe_allow_html=True)
    
    with col2:
        # Cryptocurrency selector with inline styles
        crypto_options = list(data.keys())
        selected_crypto = st.selectbox(
            "Select Crypto:",
            options=crypto_options,
            index=crypto_options.index(st.session_state.selected_crypto) if st.session_state.selected_crypto in crypto_options else 0,
            key="crypto_selector",
            help="Choose cryptocurrency to analyze"
        )
        
        # Apply inline style to override Streamlit
        st.markdown("""
        <style>
        div[data-testid="stSelectbox"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
        }
        div[data-testid="stSelectbox"] > div:hover {
            background: rgba(0, 212, 255, 0.1) !important;
            border-color: #00d4ff !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if selected_crypto != st.session_state.selected_crypto:
            st.session_state.selected_crypto = selected_crypto
            st.rerun()
    
    with col3:
        # Timeframe selector with inline styles
        timeframes = ['1H', '4H', '1D', '1W', '1M']
        cols = st.columns(len(timeframes))
        
        for i, tf in enumerate(timeframes):
            with cols[i]:
                if st.button(tf, key=f"timeframe_{tf}", 
                          type="primary" if tf == st.session_state.timeframe else "secondary",
                          help=f"View {tf} timeframe"):
                    st.session_state.timeframe = tf
                    st.rerun()
        
        # Apply inline styles for buttons
        st.markdown("""
        <style>
        div[data-testid="stButton"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #8b92a8 !important;
            font-weight: 600 !important;
        }
        div[data-testid="stButton"]:hover {
            background: rgba(0, 212, 255, 0.1) !important;
            border-color: #00d4ff !important;
            color: #00d4ff !important;
        }
        div[data-testid="stButton"][data-kind="primary"] {
            background: linear-gradient(45deg, #00d4ff, #8b5cf6) !important;
            border-color: transparent !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create beautiful chart with selected crypto and timeframe
    fig = go.Figure()
    
    # Only show the selected cryptocurrency
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto in data:
        crypto_info = data[selected_crypto]
        
        # Determine data points based on timeframe
        if st.session_state.timeframe == '1H':
            periods = 60
            freq = '1min'
        elif st.session_state.timeframe == '4H':
            periods = 48
            freq = '5min'
        elif st.session_state.timeframe == '1D':
            periods = 24
            freq = 'h'
        elif st.session_state.timeframe == '1W':
            periods = 7
            freq = 'D'
        else:  # 1M
            periods = 30
            freq = 'D'
        
        # Generate price data for selected crypto
        dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
        base_price = crypto_info.get('price', 100)
        
        # Generate realistic price movements
        prices = []
        for j in range(periods):
            if j == 0:
                price = base_price
            else:
                change = np.random.normal(0, 0.02 if st.session_state.timeframe in ['1H', '4H'] else 0.01)
                price = max(prices[-1] * (1 + change), 0.01)
            prices.append(price)
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name=selected_crypto,
            line=dict(width=4, color='#00d4ff'),
            hovertemplate=f'<b>{selected_crypto}</b><br>Price: $%{{y:,.2f}}<br>Time: %{{x}}<extra></extra>'
        ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
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
    st.markdown('</div>', unsafe_allow_html=True)

def render_beautiful_stats(data):
    """Render beautiful statistics"""
    if not data:
        return
    
    analytics = get_analytics_engine()
    metrics = analytics.calculate_metrics(data)
    
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    # Risk Score
    risk_score = 65
    risk_level = "MEDIUM RISK"
    risk_class = "risk-medium"
    
    stat_html = f"""
    <div class="stat-card">
        <div class="stat-label">Risk Score</div>
        <div class="stat-value">{risk_score}</div>
        <div class="stat-badge {risk_class}">{risk_level}</div>
    </div>
    """
    st.markdown(stat_html, unsafe_allow_html=True)
    
    # Total Volume
    volume_html = f"""
    <div class="stat-card">
        <div class="stat-label">Total Volume</div>
        <div class="stat-value">${metrics.get('total_volume_24h', 0):,.0f}</div>
        <div class="stat-badge risk-low">24h</div>
    </div>
    """
    st.markdown(volume_html, unsafe_allow_html=True)
    
    # Market Sentiment
    sentiment, score, color = analytics.calculate_market_sentiment(data)
    sentiment_class = "risk-low" if "Bullish" in sentiment else "risk-high"
    
    sentiment_html = f"""
    <div class="stat-card">
        <div class="stat-label">Sentiment</div>
        <div class="stat-value">{sentiment}</div>
        <div class="stat-badge {sentiment_class}">{score:.0f}</div>
    </div>
    """
    st.markdown(sentiment_html, unsafe_allow_html=True)
    
    # Active Cryptos
    active_html = f"""
    <div class="stat-card">
        <div class="stat-label">Active</div>
        <div class="stat-value">{len(data)}</div>
        <div class="stat-badge risk-low">Coins</div>
    </div>
    """
    st.markdown(active_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Simple and beautiful main dashboard"""
    # Hide Streamlit defaults FIRST
    st.markdown("""
    <style>
        /* LATEST LOADING CSS - Must come after Streamlit's CSS */
        .stSelectbox > div > div,
        .stButton > div,
        .element-container,
        .streamlit-container {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stButton"][data-kind="primary"] {
            background: linear-gradient(45deg, #00d4ff, #8b5cf6) !important;
            border-color: transparent !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hide more Streamlit defaults
    st.markdown("""
    <style>
        .stApp > header {visibility: hidden;}
        .stApp > footer {visibility: hidden;}
        .css-1d391kg {padding-top: 0;}
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    render_beautiful_header()
    
    # Get data
    data_engine = get_data_engine()
    data = data_engine.sync_data()
    
    # Main content
    if data:
        # Price card for selected crypto only
        st.markdown("### 💰 Current Price")
        render_beautiful_prices(data)
        
        # Chart
        st.markdown("### 📈 Market Overview")
        render_beautiful_chart(data)
        
        # Stats
        st.markdown("### 📊 Market Analytics")
        render_beautiful_stats(data)
    else:
        st.markdown('<div class="loading">🔄 Connecting to market data...</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
