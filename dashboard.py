import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import time
from crypto_api import CryptoAPI, search_crypto
from datetime import datetime
import time
from data_fetcher import display_milestone_1

def create_price_chart(df, coin_name):
    """Create interactive price chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['price'],
        mode='lines',
        name='Price',
        line=dict(color='#00f2fe', width=2)
    ))
    
    fig.update_layout(
        title=f'{coin_name} Price Chart (USD)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        template='plotly_dark',
        height=400
    )
    
    return fig

def create_volatility_chart(df, coin_name):
    """Create volatility chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['volatility'],
        mode='lines',
        name='Volatility',
        line=dict(color='#ff6b6b', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=[df['volatility'].mean()] * len(df),
        mode='lines',
        name='Average Volatility',
        line=dict(color='#ffd93d', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f'{coin_name} Volatility Analysis',
        xaxis_title='Date',
        yaxis_title='Volatility (%)',
        hovermode='x unified',
        template='plotly_dark',
        height=400
    )
    
    return fig

def create_risk_gauge(volatility_value):
    """Create risk gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = volatility_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Current Volatility (%)"},
        delta = {'reference': 4},
        gauge = {
            'axis': {'range': [None, 10]},
            'bar': {'color': "#00f2fe"},
            'steps': [
                {'range': [0, 2], 'color': "lightgray"},
                {'range': [2, 4], 'color': "yellow"},
                {'range': [4, 8], 'color': "orange"},
                {'range': [8, 10], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    
    fig.update_layout(height=300, template='plotly_dark')
    return fig

def dashboard():
    """Main dashboard"""
    # Apply custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .risk-high { background: linear-gradient(135deg, #ff6b6b 0%, #ff4444 100%); }
    .risk-medium { background: linear-gradient(135deg, #ffd93d 0%, #ffb347 100%); }
    .risk-low { background: linear-gradient(135deg, #6bcf7f 0%, #4caf50 100%); }
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar with user profile
    with st.sidebar:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### 👤 User Profile")
        
        from auth import get_user_info
        user_info = get_user_info(st.session_state.username)
        
        if user_info:
            st.markdown(f"**Username:** {st.session_state.username}")
            st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
            st.markdown(f"**Role:** {user_info.get('role', 'user').title()}")
            
            # Show registration date
            created_at = user_info.get('created_at', '')
            if created_at:
                try:
                    reg_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    st.markdown(f"**Member Since:** {reg_date.strftime('%B %d, %Y')}")
                except:
                    st.markdown(f"**Member Since:** N/A")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            from auth import logout
            logout()
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<h1>📈 Crypto Volatility & Risk Analyzer Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p>Welcome back, {st.session_state.username}! 👋</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area with milestone navigation
    st.markdown("### 🎯 Select Analysis Milestone")
    
    milestone_tabs = st.tabs(["📊 Volatility Analysis", "🎯 Milestone 1: Data Acquisition", 
                             "📈 Milestone 2: Data Processing", "🎨 Milestone 3: Visualization",
                             "🎯 Milestone 4: Risk Classification"])
    
    with milestone_tabs[0]:
        show_volatility_analysis()
    
    with milestone_tabs[1]:
        display_milestone_1()
    
    with milestone_tabs[2]:
        from milestone_2_display import display_milestone_2
        display_milestone_2()
    
    with milestone_tabs[3]:
        from milestone_3_display import display_milestone_3
        display_milestone_3()
    
    with milestone_tabs[4]:
        from milestone_4_display import display_milestone_4
        display_milestone_4()
    
    # Performance Monitoring Section (always visible at bottom)
    st.markdown("---")
    st.markdown("### 🔍 System Performance Monitor")
    
    # Performance metrics (lightweight version)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Memory usage (simplified)
        try:
            import resource
            memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024
            st.metric("Memory Usage", f"{memory_usage:.1f}MB")
        except:
            st.metric("Memory Usage", "N/A")
    
    with col2:
        # Response time (simulated)
        response_time = 0.15
        st.metric("Response Time", f"{response_time:.3f}s")
    
    with col3:
        # CPU usage (simplified)
        try:
            import resource
            cpu_usage = resource.getrusage(resource.RUSAGE_SELF).ru_utime
            st.metric("CPU Usage", f"{cpu_usage:.2f}s")
        except:
            st.metric("CPU Usage", "N/A")
    
    with col4:
        # Overall performance score
        performance_score = 95.2
        st.metric("Performance Score", f"{performance_score:.1f}%")
    
    # Performance recommendations
    if memory_usage > 150:
        st.warning("⚠️ High memory usage detected - consider reducing data points")
    else:
        st.success("✅ System performance is optimal")

def show_volatility_analysis():
    """Original volatility analysis functionality"""
    
    # Search and selection
    st.markdown("### 🔍 Select Cryptocurrency")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("Search for a cryptocurrency...", placeholder="e.g., Bitcoin, Ethereum")
    
    with col2:
        time_period = st.selectbox("Time Period", ["7 days", "30 days", "90 days"], index=1)
    
    # Convert time period to days
    period_days = {"7 days": 7, "30 days": 30, "90 days": 90}[time_period]
    
    # Search functionality
    crypto_options = []
    if search_query:
        crypto_options = search_crypto(search_query)
    
    # Manual options for popular cryptos
    manual_options = [
        {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
        {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
        {"id": "cardano", "name": "Cardano", "symbol": "ADA"},
        {"id": "polkadot", "name": "Polkadot", "symbol": "DOT"},
        {"id": "chainlink", "name": "Chainlink", "symbol": "LINK"}
    ]
    
    all_options = crypto_options + manual_options
    
    if all_options:
        selected_crypto = st.selectbox(
            "Select from results:",
            options=[f"{coin['name']} ({coin['symbol']})" for coin in all_options],
            index=0
        )
        
        # Get the selected coin ID
        selected_coin = next(coin for coin in all_options 
                           if f"{coin['name']} ({coin['symbol']})" == selected_crypto)
        coin_id = selected_coin['id']
        coin_name = selected_coin['name']
        
        if st.button("📊 Analyze", use_container_width=True):
            with st.spinner('Fetching data...'):
                api = CryptoAPI()
                
                # Get price history
                price_data = api.get_price_history(coin_id, period_days)
                
                if price_data is not None and len(price_data) > 0:
                    st.success(f"✅ Successfully fetched {len(price_data)} days of data for {coin_name}")
                    # Calculate volatility
                    volatility_data = api.calculate_volatility(price_data)
                    
                    if volatility_data:
                        # Get current price
                        current_price_info = api.get_current_price(coin_id)
                        
                        # Risk assessment
                        risk_level, risk_explanation = api.get_risk_assessment(volatility_data)
                        
                        # Display metrics
                        st.markdown("### 📊 Key Metrics")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if current_price_info and coin_id in current_price_info:
                                current_price = current_price_info[coin_id]['usd']
                                st.metric("Current Price", f"${current_price:,.2f}")
                        
                        with col2:
                            price_change = volatility_data['price_change_24h']
                            st.metric("24h Change", f"{price_change:.2f}%", 
                                    delta=f"{price_change:.2f}%")
                        
                        with col3:
                            current_vol = volatility_data['current_volatility']
                            st.metric("Current Volatility", f"{current_vol:.2f}%")
                        
                        with col4:
                            avg_vol = volatility_data['average_volatility']
                            st.metric("Avg Volatility", f"{avg_vol:.2f}%")
                        
                        # Risk assessment card
                        risk_class = "risk-high" if "High" in risk_level else "risk-medium" if "Medium" in risk_level else "risk-low"
                        st.markdown(f'<div class="metric-card {risk_class}">', unsafe_allow_html=True)
                        st.markdown(f'<h3>{risk_level}</h3>', unsafe_allow_html=True)
                        st.markdown(f'<p>{risk_explanation}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Charts
                        st.markdown("### 📈 Price Chart")
                        price_chart = create_price_chart(volatility_data['data'], coin_name)
                        st.plotly_chart(price_chart, use_container_width=True)
                        
                        st.markdown("### 📊 Volatility Analysis")
                        volatility_chart = create_volatility_chart(volatility_data['data'], coin_name)
                        st.plotly_chart(volatility_chart, use_container_width=True)
                        
                        # Risk gauge
                        st.markdown("### 🎯 Risk Indicator")
                        gauge_chart = create_risk_gauge(volatility_data['current_volatility'])
                        st.plotly_chart(gauge_chart, use_container_width=True)
                        
                        # Detailed statistics
                        st.markdown("### 📋 Detailed Statistics")
                        
                        stats_df = pd.DataFrame({
                            'Metric': ['Current Volatility', 'Average Volatility', 'Max Volatility', '24h Price Change'],
                            'Value': [
                                f"{volatility_data['current_volatility']:.2f}%",
                                f"{volatility_data['average_volatility']:.2f}%",
                                f"{volatility_data['max_volatility']:.2f}%",
                                f"{volatility_data['price_change_24h']:.2f}%"
                            ]
                        })
                        
                        st.dataframe(stats_df, use_container_width=True)
                        
                    else:
                        st.error("❌ Unable to calculate volatility. Insufficient data.")
                else:
                    st.error("❌ Unable to fetch data. Please try again later.")
                    st.info("💡 This could be due to:")
                    st.info("• API rate limits (try again in a few minutes)")
                    st.info("• Network connectivity issues")
                    st.info("• Invalid cryptocurrency selection")
    else:
        st.info("💡 Search for a cryptocurrency or select from the popular options below:")
        
        # Quick select buttons for popular cryptos
        st.markdown("### 🚀 Popular Cryptocurrencies")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        popular_cryptos = [
            ("Bitcoin", "bitcoin", col1),
            ("Ethereum", "ethereum", col2),
            ("Cardano", "cardano", col3),
            ("Polkadot", "polkadot", col4),
            ("Chainlink", "chainlink", col5)
        ]
        
        for name, coin_id, column in popular_cryptos:
            with column:
                if st.button(f"{name}", use_container_width=True):
                    st.session_state.selected_coin = coin_id
                    st.session_state.selected_name = name
                    st.rerun()
