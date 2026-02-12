import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from data_engine import DataEngine
from analytics_engine import AnalyticsEngine

# Initialize engines
@st.cache_resource(ttl=30)
def get_data_engine():
    return DataEngine()

@st.cache_resource(ttl=30)
def get_analytics_engine():
    return AnalyticsEngine()

# Initialize session state
if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = 'BTC'
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '1D'

def render_crypto_price_card(data):
    """Render crypto price card using Streamlit components"""
    if not data:
        st.info("🔄 Loading market data...")
        return
    
    # Only show the selected cryptocurrency
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto in data:
        symbol = selected_crypto
        info = data[symbol]
        change_class = "positive" if info.get('change_24h', 0) > 0 else "negative"
        
        # Use Streamlit's native card styling
        with st.container():
            st.markdown(f"### {symbol}")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.metric(
                    "Price",
                    f"${info.get('price', 0):,.2f}",
                    delta=f"{info.get('change_24h', 0):+.2f}%",
                    delta_color="normal" if abs(info.get('change_24h', 0)) < 0.1 else "inverse"
                )
            
            with col2:
                # Large price display
                st.markdown(f"# {symbol}")
                st.markdown(f"## ${info.get('price', 0):,.2f}")
                
            with col3:
                st.metric(
                    "24h Change",
                    f"{abs(info.get('change_24h', 0)):.2f}%",
                    delta=f"{info.get('change_24h', 0):+.2f}%",
                    delta_color="normal" if abs(info.get('change_24h', 0)) < 0.1 else "inverse"
                )
            
            st.markdown(f"**Volume:** ${info.get('volume_24h', 0):,.0f}")

def render_crypto_chart(data):
    """Render crypto chart using Streamlit's native styling"""
    if not data:
        st.info("📈 No chart data available")
        return
    
    # Only show the selected cryptocurrency
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto in data:
        crypto_info = data[selected_crypto]
        
        # Chart with Streamlit's native tabs
        tab1, tab2 = st.tabs(["📈 Price Chart", "📊 Statistics"])
        
        with tab1:
            st.subheader(f"{selected_crypto} Price Chart")
            
            # Timeframe selector
            timeframes = ['1H', '4H', '1D', '1W', '1M']
            selected_timeframe = st.selectbox(
                "Timeframe:",
                options=timeframes,
                index=timeframes.index(st.session_state.timeframe),
                key="timeframe_selector"
            )
            st.session_state.timeframe = selected_timeframe
            
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
            
            # Create chart with Streamlit's native styling
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
        
        with tab2:
            st.subheader(f"{selected_crypto} Statistics")
            
            # Statistics using Streamlit metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${crypto_info.get('price', 0):,.2f}",
                    delta=None
                )
                
                st.metric(
                    "24h Change",
                    f"{crypto_info.get('change_24h', 0):+.2f}%",
                    delta=f"{crypto_info.get('change_24h', 0):+.2f}%"
                )
            
            with col2:
                st.metric(
                    "Volume 24h",
                    f"${crypto_info.get('volume_24h', 0):,.0f}",
                    delta=None
                )
                
                # Risk assessment
                analytics = get_analytics_engine()
                volatility_data = analytics.calculate_volatility(pd.DataFrame({'price': [crypto_info.get('price', 100)]}))
                
                if volatility_data:
                    risk_level, explanation, risk_score, color = analytics.get_risk_assessment(volatility_data)
                    st.metric(
                        "Risk Level",
                        risk_level,
                        delta=None,
                        delta_color=color.replace('#', '')
                    )
                    
                    st.metric(
                        "Risk Score",
                        f"{risk_score:.0f}",
                        delta=None
                    )
                
                    st.info(explanation)

def render_header():
    """Render header using Streamlit's native components"""
    data_engine = get_data_engine()
    
    # Use Streamlit's native columns for header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("## 📊 Crypto Analytics Pro")
    
    with col2:
        # Live status using Streamlit's native components
        if data_engine.get_data_status() == 'ready':
            st.success("🟢 Live Market Data")
        else:
            st.warning("🔄 Syncing...")
    
    with col3:
        if data_engine.last_update:
            st.caption(f"Last updated: {data_engine.last_update.strftime('%H:%M:%S')}")
        else:
            st.caption("Never updated")

def render_market_overview(data):
    """Render market overview using Streamlit components"""
    if not data:
        st.warning("🔄 No market data available")
        return
    
    st.subheader("🌍 Market Overview")
    
    # Market metrics using Streamlit's native metrics
    analytics = get_analytics_engine()
    metrics = analytics.calculate_metrics(data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Volume", f"${metrics.get('total_volume_24h', 0):,.0f}")
    
    with col2:
        st.metric("Avg Change", f"{metrics.get('avg_change_24h', 0):+.2f}%")
    
    with col3:
        st.metric("Positive", f"{metrics.get('positive_movers', 0)}")
    
    with col4:
        st.metric("Negative", f"{metrics.get('negative_movers', 0)}")

def main():
    """Main dashboard using Streamlit's native design system"""
    # Set page config to use Streamlit's dark theme
    st.set_page_config(
        page_title="Crypto Analytics Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Get data
    data_engine = get_data_engine()
    data = data_engine.sync_data()
    
    # Render components using Streamlit's native system
    render_header()
    
    if data:
        # Main content with tabs
        tab1, tab2, tab3 = st.tabs(["💰 Price Analysis", "📈 Charts", "📊 Market Overview"])
        
        with tab1:
            # Crypto selector that updates the chart
            crypto_options = list(data.keys())
            selected_crypto = st.selectbox(
                "Select Cryptocurrency:",
                options=crypto_options,
                index=crypto_options.index(st.session_state.selected_crypto) if st.session_state.selected_crypto in crypto_options else 0,
                key="crypto_selector"
            )
            
            # Update session state and rerun if changed
            if selected_crypto != st.session_state.selected_crypto:
                st.session_state.selected_crypto = selected_crypto
                st.rerun()
            
            # Render selected crypto card
            render_crypto_price_card(data)
            
            # Render chart for selected crypto
            render_crypto_chart(data)
        
        with tab2:
            render_crypto_chart(data)
        
        with tab3:
            render_market_overview(data)
    else:
        st.error("❌ Unable to load market data. Please try again later.")
