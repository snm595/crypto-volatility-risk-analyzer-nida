import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from data_engine import DataEngine
from analytics_engine import AnalyticsEngine

# Set page config to use Streamlit's dark theme
st.set_page_config(
    page_title="Crypto Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '1D'
if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = 'BTC'

# Initialize engines
@st.cache_resource(ttl=30)
def get_data_engine():
    return DataEngine()

@st.cache_resource(ttl=30)
def get_analytics_engine():
    return AnalyticsEngine()

# Minimal CSS that works WITH Streamlit
st.markdown("""
<style>
    /* Only minimal custom styles that complement Streamlit's dark theme */
    .main-header {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    .crypto-card {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: rgba(49, 51, 63, 0.5);
        border: 1px solid rgba(49, 51, 63, 0.8);
    }
    
    .chart-section {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        background-color: rgba(49, 51, 63, 0.3);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(49, 51, 63, 0.5);
        border: 1px solid rgba(49, 51, 63, 0.8);
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Render header using Streamlit components"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📊 Crypto Analytics Pro")
    
    with col2:
        data_engine = get_data_engine()
        if data_engine.get_data_status() == 'ready':
            st.success("🟢 Live")
        else:
            st.warning("🔄 Syncing...")
    
    with col3:
        if data_engine.last_update:
            st.caption(f"Updated: {data_engine.last_update.strftime('%H:%M:%S')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_crypto_selector(data):
    """Render crypto selector using Streamlit components"""
    if not data:
        st.warning("🔄 Loading market data...")
        return
    
    crypto_options = list(data.keys())
    selected_crypto = st.selectbox(
        "📈 Select Cryptocurrency",
        options=crypto_options,
        index=crypto_options.index(st.session_state.selected_crypto) if st.session_state.selected_crypto in crypto_options else 0,
        key="crypto_selector"
    )
    
    if selected_crypto != st.session_state.selected_crypto:
        st.session_state.selected_crypto = selected_crypto
        st.rerun()
    
    return selected_crypto

def render_price_card(data, selected_crypto):
    """Render price card using Streamlit components"""
    if not data or selected_crypto not in data:
        return
    
    st.markdown('<div class="crypto-card">', unsafe_allow_html=True)
    
    crypto_info = data[selected_crypto]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            selected_crypto,
            f"${crypto_info.get('price', 0):,.2f}",
            delta=f"{crypto_info.get('change_24h', 0):+.2f}%",
            delta_color="normal" if abs(crypto_info.get('change_24h', 0)) < 0.1 else "inverse"
        )
    
    with col2:
        st.metric(
            "24h Volume",
            f"${crypto_info.get('volume_24h', 0):,.0f}",
            delta=None
        )
    
    with col3:
        # Risk assessment
        analytics = get_analytics_engine()
        volatility_data = analytics.calculate_volatility(pd.DataFrame({'price': [crypto_info.get('price', 100)]}))
        
        if volatility_data:
            risk_level, explanation, risk_score, color = analytics.get_risk_assessment(volatility_data)
            st.metric(
                "Risk Level",
                risk_level,
                delta=f"Score: {risk_score:.0f}",
                delta_color="normal" if risk_score < 50 else "inverse"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_timeframe_selector():
    """Render timeframe selector using Streamlit components"""
    timeframes = ['1H', '4H', '1D', '1W', '1M']
    
    cols = st.columns(len(timeframes))
    for i, tf in enumerate(timeframes):
        with cols[i]:
            if st.button(tf, key=f"timeframe_{tf}", 
                      type="primary" if tf == st.session_state.timeframe else "secondary"):
                st.session_state.timeframe = tf
                st.rerun()

def render_chart(data, selected_crypto):
    """Render chart using Streamlit components"""
    if not data or selected_crypto not in data:
        st.info("📈 No chart data available")
        return
    
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    
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
    
    # Generate price data
    dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
    base_price = crypto_info.get('price', 100)
    
    prices = []
    for j in range(periods):
        if j == 0:
            price = base_price
        else:
            change = np.random.normal(0, 0.02 if st.session_state.timeframe in ['1H', '4H'] else 0.01)
            price = max(prices[-1] * (1 + change), 0.01)
        prices.append(price)
    
    # Create chart with Streamlit's dark theme
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name=selected_crypto,
        line=dict(width=3, color='#00d4ff')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickformat='$,.2f')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_market_overview(data):
    """Render market overview using Streamlit components"""
    if not data:
        st.warning("🔄 No market data available")
        return
    
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    analytics = get_analytics_engine()
    metrics = analytics.calculate_metrics(data)
    
    # Market metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Volume", f"${metrics.get('total_volume_24h', 0):,.0f}")
    
    with col2:
        st.metric("Avg Change", f"{metrics.get('avg_change_24h', 0):+.2f}%")
    
    with col3:
        st.metric("Positive", f"{metrics.get('positive_movers', 0)}")
    
    with col4:
        st.metric("Negative", f"{metrics.get('negative_movers', 0)}")
    
    # Individual crypto cards
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    for crypto in data:
        with st.container():
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    crypto,
                    f"${data[crypto].get('price', 0):,.2f}",
                    delta=f"{data[crypto].get('change_24h', 0):+.2f}%"
                )
            
            with col2:
                st.metric(
                    "Volume",
                    f"${data[crypto].get('volume_24h', 0):,.0f}",
                    delta=None
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main dashboard using Streamlit's native design system"""
    # Get data
    data_engine = get_data_engine()
    data = data_engine.sync_data()
    
    # Render components
    render_header()
    
    if data:
        # Main content
        selected_crypto = render_crypto_selector(data)
        
        # Tabbed interface
        tab1, tab2, tab3 = st.tabs(["💰 Price Analysis", "📈 Charts", "📊 Market Overview"])
        
        with tab1:
            render_price_card(data, selected_crypto)
        
        with tab2:
            render_timeframe_selector()
            render_chart(data, selected_crypto)
        
        with tab3:
            render_market_overview(data)
    else:
        st.error("❌ Unable to load market data. Please try again later.")

if __name__ == "__main__":
    main()
