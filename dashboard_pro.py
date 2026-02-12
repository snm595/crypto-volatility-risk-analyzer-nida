import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from data_engine import DataEngine
from analytics_engine import AnalyticsEngine

# Custom CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
""", unsafe_allow_html=True)

# Initialize engines
@st.cache_resource(ttl=60)  # Cache for 60 seconds
def get_data_engine():
    return DataEngine()

@st.cache_resource(ttl=60)
def get_analytics_engine():
    return AnalyticsEngine()

def render_navbar():
    """Render top navigation bar"""
    data_engine = get_data_engine()
    status = data_engine.get_data_status()
    
    navbar_html = f"""
    <div class="navbar">
        <div class="navbar-brand">
            📊 Crypto Analytics Pro
        </div>
        <div class="navbar-status">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>🟢 Market Active</span>
            </div>
            <div>
                Last Update: {data_engine.last_update.strftime('%H:%M:%S') if data_engine.last_update else 'Never'}
            </div>
            <div>
                Status: <span style="color: {'#10b981' if status == 'ready' else '#f59e0b' if status == 'stale' else '#ef4444'}">{status.upper()}</span>
            </div>
            <button onclick="location.reload()" style="background: var(--gradient-primary); border: none; color: white; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">
                🔄 Sync
            </button>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

def render_sidebar():
    """Render left sidebar navigation"""
    st.markdown("""
    <div class="sidebar">
        <div class="sidebar-nav">
            <a href="#" class="nav-item active">
                📊 Dashboard
            </a>
            <a href="#" class="nav-item">
                📈 Markets
            </a>
            <a href="#" class="nav-item">
                ⚠️ Risk Analytics
            </a>
            <a href="#" class="nav-item">
                ⚙️ Data Engine
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_price_cards(data):
    """Render live price ticker cards"""
    if not data:
        return
    
    cols = st.columns(len(data))
    
    for i, (symbol, info) in enumerate(data.items()):
        with cols[i]:
            change_class = "positive" if info.get('change_24h', 0) > 0 else "negative"
            change_symbol = "↑" if info.get('change_24h', 0) > 0 else "↓"
            
            card_html = f"""
            <div class="price-card">
                <div class="price-symbol">{symbol}</div>
                <div class="price-value">${info.get('price', 0):,.2f}</div>
                <div class="price-change {change_class}">
                    {change_symbol} {abs(info.get('change_24h', 0)):.2f}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    Vol: ${info.get('volume_24h', 0):,.0f}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

def render_main_chart(data, timeframe='1D'):
    """Render main price chart"""
    if not data:
        st.info("No data available for chart")
        return
    
    # Create sample chart data (in real implementation, use historical data)
    fig = go.Figure()
    
    for symbol, info in data.items():
        # Generate sample price line
        dates = pd.date_range(end=datetime.now(), periods=24, freq='h')
        base_price = info.get('price', 100)
        prices = [base_price * (1 + np.random.normal(0, 0.02)) for _ in range(24)]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name=symbol,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>Price: $%{y:,.2f}<br>Time: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title=None,
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_timeframe_selector():
    """Render timeframe selector"""
    timeframes = ['1H', '4H', '1D', '7D', '1M', '3M', '1Y']
    
    selector_html = """
    <div class="timeframe-selector">
    """
    
    for tf in timeframes:
        active_class = "active" if tf == '1D' else ""
        selector_html += f'<button class="timeframe-btn {active_class}">{tf}</button>'
    
    selector_html += "</div>"
    
    st.markdown(selector_html, unsafe_allow_html=True)

def render_risk_panel(data):
    """Render risk analysis panel"""
    analytics = get_analytics_engine()
    
    # Calculate overall market risk
    if data:
        # Use BTC as primary risk indicator
        btc_data = data.get('BTC', {})
        if btc_data:
            # Mock volatility calculation
            volatility = 3.5  # Sample value
            risk_level, explanation, risk_score, color = analytics.get_risk_assessment({'current_volatility': volatility})
            
            panel_html = f"""
            <div class="risk-gauge">
                <div style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    MARKET RISK SCORE
                </div>
                <div class="risk-score">{risk_score:.0f}</div>
                <div class="risk-label" style="color: {color};">{risk_level}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    {explanation}
                </div>
            </div>
            """
            st.markdown(panel_html, unsafe_allow_html=True)
    
    # Market Sentiment
    sentiment, score, color = analytics.calculate_market_sentiment(data)
    
    sentiment_html = f"""
    <div class="risk-gauge" style="margin-top: 1rem;">
        <div style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 1rem;">
            MARKET SENTIMENT
        </div>
        <div class="risk-score" style="font-size: 1.5rem;">{score:.0f}</div>
        <div class="risk-label" style="color: {color};">{sentiment}</div>
    </div>
    """
    st.markdown(sentiment_html, unsafe_allow_html=True)

def render_volatility_chart():
    """Render volatility trend chart"""
    # Sample volatility data
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
        line=dict(color='#7c3aed', width=2),
        fill='tonexty',
        fillcolor='rgba(124, 58, 237, 0.1)'
    ))
    
    fig.update_layout(
        title="30-Day Volatility Trend",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_stats_table(data):
    """Render statistical summary table"""
    analytics = get_analytics_engine()
    metrics = analytics.calculate_metrics(data)
    
    if not metrics:
        return
    
    stats_data = [
        ['Total Volume 24h', f"${metrics.get('total_volume_24h', 0):,.0f}"],
        ['Average Change 24h', f"{metrics.get('avg_change_24h', 0):+.2f}%"],
        ['Positive Movers', str(metrics.get('positive_movers', 0))],
        ['Negative Movers', str(metrics.get('negative_movers', 0))]
    ]
    
    if metrics.get('biggest_gainer'):
        symbol, info = metrics['biggest_gainer']
        stats_data.append(['Top Gainer', f"{symbol} {info.get('change_24h', 0):+.2f}%"])
    
    if metrics.get('biggest_loser'):
        symbol, info = metrics['biggest_loser']
        stats_data.append(['Top Loser', f"{symbol} {info.get('change_24h', 0):+.2f}%"])
    
    table_html = """
    <div class="stats-table">
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for metric, value in stats_data:
        table_html += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{value}</td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)

def main():
    """Main dashboard application"""
    # Hide default Streamlit elements
    st.markdown("""
    <style>
        .stApp > header {visibility: hidden;}
        .stApp > footer {visibility: hidden;}
        .css-1d391kg {padding-top: 0;}
    </style>
    """, unsafe_allow_html=True)
    
    # Render layout components
    render_navbar()
    
    # Create main layout
    col1, col2, col3 = st.columns([1, 4, 1.5])
    
    with col1:
        render_sidebar()
    
    with col2:
        # Main content area
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Sync data
        data_engine = get_data_engine()
        data = data_engine.sync_data()
        
        if data:
            # Top section - Price cards
            st.markdown("### 📊 Live Market Prices")
            render_price_cards(data)
            
            st.markdown("---")
            
            # Center section - Main chart
            st.markdown("### 📈 Price Chart")
            render_timeframe_selector()
            render_main_chart(data)
            
            st.markdown("---")
            
            # Bottom section - Volatility chart
            st.markdown("### 📊 Volatility Analysis")
            render_volatility_chart()
        else:
            st.error("Unable to load market data. Please check your connection and try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Right panel
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        if data:
            st.markdown("### ⚠️ Risk Analytics")
            render_risk_panel(data)
            
            st.markdown("---")
            
            st.markdown("### 📋 Market Statistics")
            render_stats_table(data)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
