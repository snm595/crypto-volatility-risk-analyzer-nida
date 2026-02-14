import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_engine import DataEngine
import numpy as np
from datetime import datetime

def display_milestone_2():
    """Display Milestone 2: Data Processing and Calculation"""
    
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;'>
        <h2>📊 Milestone 2: Data Processing and Calculation</h2>
        <p>Advanced statistical analysis with log returns, volatility, Sharpe ratio, and beta calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Data Engine
    data_engine = DataEngine()
    
    # Main controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🎛 Analysis Controls")
        selected_assets = st.multiselect(
            "Select Cryptocurrencies",
            options=[crypto["symbol"] for crypto in data_engine.cryptocurrencies],
            default=["BTC", "ETH", "SOL"]
        )
    
    with col2:
        time_period = st.selectbox(
            "Time Period",
            options=[30, 60, 90, 180],
            index=2,
            format_func=lambda x: f"{x} days"
        )
    
    with col3:
        benchmark = st.selectbox(
            "Benchmark",
            options=["BTC", "ETH"],
            index=0
        )
    
    if not selected_assets:
        st.warning("⚠️ Please select at least one cryptocurrency to analyze.")
        return
    
    # Generate metrics table
    with st.spinner("🔄 Processing data and calculating metrics..."):
        try:
            metrics_df = data_engine.generate_metrics_table(benchmark)
            
            if metrics_df is None or len(metrics_df) == 0:
                st.error("❌ Unable to fetch data. Please check your internet connection.")
                return
            
            # Filter for selected assets
            filtered_metrics = metrics_df[metrics_df['symbol'].isin(selected_assets)]
            
            if len(filtered_metrics) == 0:
                st.error("❌ No data available for selected assets.")
                return
            
            # Display comprehensive metrics table
            st.markdown("### 📈 Comprehensive Metrics Table")
            
            # Format the metrics for display
            display_df = filtered_metrics.copy()
            display_df['Current Price'] = display_df['current_price'].apply(lambda x: f"${x:,.2f}")
            display_df['24h Change'] = display_df['price_change_24h'].apply(lambda x: f"{x:.2f}%")
            display_df['Daily Vol'] = display_df['daily_volatility'].apply(lambda x: f"{x:.4f}")
            display_df['Annual Vol'] = display_df['annualized_volatility'].apply(lambda x: f"{x:.2%}")
            display_df['Sharpe Ratio'] = display_df['sharpe_ratio'].apply(lambda x: f"{x:.3f}")
            display_df['Annual Return'] = display_df['annual_return'].apply(lambda x: f"{x:.2%}")
            display_df['Beta'] = display_df['beta'].apply(lambda x: f"{x:.3f}")
            display_df['Correlation'] = display_df['correlation_vs_btc'].apply(lambda x: f"{x:.3f}")
            display_df['R²'] = display_df['r_squared'].apply(lambda x: f"{x:.3f}")
            
            # Rearrange columns for better display
            display_columns = ['symbol', 'name', 'Current Price', '24h Change', 'Daily Vol', 
                             'Annual Vol', 'Sharpe Ratio', 'Annual Return', 'Beta', 'Correlation', 'R²', 'risk_level']
            display_df = display_df[display_columns]
            
            # Rename columns
            display_df.columns = ['Symbol', 'Name', 'Current Price', '24h Change', 'Daily Volatility',
                                'Annual Volatility', 'Sharpe Ratio', 'Annual Return', 'Beta', 
                                'Correlation', 'R²', 'Risk Level']
            
            # Display with styling
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Risk distribution chart
            st.markdown("### 🎯 Risk Distribution Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                risk_counts = filtered_metrics['risk_level'].value_counts()
                fig_risk = go.Figure(data=[
                    go.Pie(labels=risk_counts.index, values=risk_counts.values, 
                          hole=0.4, textinfo='label+percent')
                ])
                fig_risk.update_layout(
                    title="Risk Level Distribution",
                    height=400,
                    template='plotly_dark'
                )
                st.plotly_chart(fig_risk, use_container_width=True)
            
            with col2:
                # Sharpe vs Volatility scatter
                fig_sharpe_vol = go.Figure()
                
                colors = {'Low Risk': '#00ff00', 'Medium Risk': '#ffff00', 
                         'High Risk': '#ff9900', 'Very High Risk': '#ff0000'}
                
                for risk_level in filtered_metrics['risk_level'].unique():
                    risk_data = filtered_metrics[filtered_metrics['risk_level'] == risk_level]
                    fig_sharpe_vol.add_trace(go.Scatter(
                        x=risk_data['annualized_volatility'],
                        y=risk_data['sharpe_ratio'],
                        mode='markers+text',
                        text=risk_data['symbol'],
                        textposition="top center",
                        marker=dict(color=colors.get(risk_level, '#8888ff'), size=12),
                        name=risk_level
                    ))
                
                fig_sharpe_vol.update_layout(
                    title="Risk-Return Profile (Sharpe vs Volatility)",
                    xaxis_title="Annualized Volatility",
                    yaxis_title="Sharpe Ratio",
                    height=400,
                    template='plotly_dark'
                )
                st.plotly_chart(fig_sharpe_vol, use_container_width=True)
            
            # Beta analysis
            st.markdown("### 📊 Beta Analysis vs Benchmark")
            
            beta_data = filtered_metrics[filtered_metrics['symbol'] != benchmark].copy()
            
            if len(beta_data) > 0:
                # Beta bar chart
                fig_beta = go.Figure(data=[
                    go.Bar(x=beta_data['symbol'], y=beta_data['beta'],
                          text=beta_data['beta'].apply(lambda x: f"{x:.3f}"),
                          textposition='auto')
                ])
                fig_beta.update_layout(
                    title=f"Beta Coefficients vs {benchmark}",
                    xaxis_title="Cryptocurrency",
                    yaxis_title="Beta",
                    height=400,
                    template='plotly_dark'
                )
                st.plotly_chart(fig_beta, use_container_width=True)
                
                # Beta interpretation
                st.markdown("#### 📋 Beta Interpretation")
                beta_info = pd.DataFrame({
                    'Symbol': beta_data['symbol'],
                    'Beta': beta_data['beta'].round(3),
                    'Interpretation': beta_data['beta'].apply(lambda x: 
                        'Less volatile than market' if x < 1 else 
                        'More volatile than market' if x > 1 else 
                        'Same volatility as market')
                })
                st.dataframe(beta_info, use_container_width=True, hide_index=True)
            
            # Detailed analysis for selected asset
            st.markdown("### 🔍 Detailed Asset Analysis")
            
            selected_detail = st.selectbox(
                "Select asset for detailed analysis",
                options=selected_assets,
                index=0
            )
            
            if selected_detail:
                detail_data = filtered_metrics[filtered_metrics['symbol'] == selected_detail].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Price", f"${detail_data['current_price']:,.2f}")
                    st.metric("24h Change", f"{detail_data['price_change_24h']:.2f}%")
                
                with col2:
                    st.metric("Daily Volatility", f"{detail_data['daily_volatility']:.4f}")
                    st.metric("Annual Volatility", f"{detail_data['annualized_volatility']:.2%}")
                
                with col3:
                    st.metric("Sharpe Ratio", f"{detail_data['sharpe_ratio']:.3f}")
                    st.metric("Beta", f"{detail_data['beta']:.3f}")
                
                # Get visualization data
                viz_data = data_engine.prepare_visualization_data([selected_detail], time_period)
                
                if selected_detail in viz_data:
                    asset_viz = viz_data[selected_detail]
                    
                    # Price chart with moving averages
                    st.markdown("#### 📈 Price Chart with Moving Averages")
                    price_df = asset_viz['price_data']
                    
                    fig_price = go.Figure()
                    
                    # Price line
                    fig_price.add_trace(go.Scatter(
                        x=price_df.index,
                        y=price_df['price'],
                        mode='lines',
                        name='Price',
                        line=dict(color='#00f2fe', width=2)
                    ))
                    
                    # Moving averages
                    for ma_period in [7, 14, 30]:
                        ma_col = f'MA_{ma_period}'
                        if ma_col in price_df.columns:
                            fig_price.add_trace(go.Scatter(
                                x=price_df.index,
                                y=price_df[ma_col],
                                mode='lines',
                                name=f'MA {ma_period}',
                                line=dict(width=1, dash='dash')
                            ))
                    
                    fig_price.update_layout(
                        title=f"{selected_detail} Price Analysis",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        height=400,
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig_price, use_container_width=True)
                    
                    # Rolling volatility chart
                    st.markdown("#### 📊 Rolling Volatility Analysis")
                    returns_df = asset_viz['returns_data']
                    
                    fig_rolling_vol = go.Figure()
                    
                    for window in [7, 14, 30]:
                        vol_col = f'rolling_vol_annual_{window}'
                        if vol_col in returns_df.columns:
                            fig_rolling_vol.add_trace(go.Scatter(
                                x=returns_df.index,
                                y=returns_df[vol_col],
                                mode='lines',
                                name=f'{window}-day Rolling Vol',
                                line=dict(width=2)
                            ))
                    
                    fig_rolling_vol.update_layout(
                        title=f"{selected_detail} Rolling Volatility",
                        xaxis_title="Date",
                        yaxis_title="Annualized Volatility",
                        height=400,
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig_rolling_vol, use_container_width=True)
            
            # Export functionality
            st.markdown("### 💾 Export Data")
            
            if st.button("📥 Export Metrics to CSV"):
                csv_data = filtered_metrics.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"crypto_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Summary statistics
            st.markdown("### 📋 Summary Statistics")
            
            summary_stats = {
                'Total Assets Analyzed': len(filtered_metrics),
                'Average Sharpe Ratio': filtered_metrics['sharpe_ratio'].mean(),
                'Average Annual Volatility': filtered_metrics['annualized_volatility'].mean(),
                'Highest Sharpe Ratio': filtered_metrics.loc[filtered_metrics['sharpe_ratio'].idxmax(), 'symbol'],
                'Most Volatile Asset': filtered_metrics.loc[filtered_metrics['annualized_volatility'].idxmax(), 'symbol'],
                'Best Risk-Adjusted Return': filtered_metrics.loc[filtered_metrics['sharpe_ratio'].idxmax(), 'symbol']
            }
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Assets Analyzed", summary_stats['Total Assets Analyzed'])
                st.metric("Avg Sharpe Ratio", f"{summary_stats['Average Sharpe Ratio']:.3f}")
            
            with col2:
                st.metric("Avg Annual Volatility", f"{summary_stats['Average Annual Volatility']:.2%}")
                st.metric("Highest Sharpe", summary_stats['Highest Sharpe Ratio'])
            
            with col3:
                st.metric("Most Volatile", summary_stats['Most Volatile Asset'])
                st.metric("Best Risk-Adjusted", summary_stats['Best Risk-Adjusted Return'])
            
        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            st.info("💡 This might be due to API rate limits. Please try again in a few minutes.")
