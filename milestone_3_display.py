import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from data_engine import DataEngine
from report_generator import CryptoReportGenerator

def display_milestone_3():
    """Display Milestone 3: Visualization and Dashboard Development"""
    
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;'>
        <h2>📊 Milestone 3: Visualization and Dashboard Development</h2>
        <p>Interactive visualizations with advanced analytics and multi-crypto comparisons</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Data Engine
    data_engine = DataEngine()
    report_gen = CryptoReportGenerator()
    
    # Sidebar controls for enhanced interactivity
    st.sidebar.markdown("### 🎛 Dashboard Controls")
    
    # Asset selection
    available_assets = [crypto["symbol"] for crypto in data_engine.cryptocurrencies]
    selected_assets = st.sidebar.multiselect(
        "Select Cryptocurrencies",
        options=available_assets,
        default=["BTC", "ETH", "SOL"],
        help="Choose multiple assets for comparison"
    )
    
    # Date range selection
    st.sidebar.markdown("### 📅 Date Range")
    date_range_option = st.sidebar.selectbox(
        "Time Period",
        options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 180 Days", "Custom"],
        index=2
    )
    
    if date_range_option == "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        days = (end_date - start_date).days
    else:
        days_map = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "Last 180 Days": 180
        }
        days = days_map[date_range_option]
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
    
    # Visualization options
    st.sidebar.markdown("### 📈 Visualization Options")
    show_price_chart = st.sidebar.checkbox("Price Charts", value=True)
    show_volatility_chart = st.sidebar.checkbox("Volatility Charts", value=True)
    show_risk_return = st.sidebar.checkbox("Risk-Return Analysis", value=True)
    show_correlation = st.sidebar.checkbox("Correlation Matrix", value=True)
    show_comparison = st.sidebar.checkbox("Asset Comparison", value=True)
    
    # Benchmark selection
    benchmark = st.sidebar.selectbox(
        "Benchmark for Beta",
        options=["BTC", "ETH"],
        index=0,
        help="Select benchmark for beta calculations"
    )
    
    if not selected_assets:
        st.warning("⚠️ Please select at least one cryptocurrency to analyze.")
        return
    
    # Load data with progress indicator
    with st.spinner("🔄 Loading market data and calculating metrics..."):
        try:
            # Prepare visualization data
            viz_data = data_engine.prepare_visualization_data(selected_assets, days)
            
            if not viz_data:
                st.error("❌ Unable to fetch data. Please check your internet connection.")
                return
            
            # Generate comprehensive metrics
            metrics_df = data_engine.generate_metrics_table(benchmark)
            filtered_metrics = metrics_df[metrics_df['symbol'].isin(selected_assets)] if metrics_df is not None else None
            
            st.success(f"✅ Successfully loaded data for {len(viz_data)} assets")
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            return
    
    # Key Metrics Summary
    st.markdown("### 📊 Key Metrics Summary")
    
    if filtered_metrics is not None and len(filtered_metrics) > 0:
        # Create metrics cards
        cols = st.columns(len(selected_assets))
        for i, (_, row) in enumerate(filtered_metrics.iterrows()):
            if i < len(cols):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 15px; border-radius: 10px; color: white; text-align: center;'>
                        <h4>{row['symbol']}</h4>
                        <p style='font-size: 24px; margin: 5px 0;'>${row['current_price']:,.2f}</p>
                        <p style='margin: 2px 0;'>24h: {row['price_change_24h']:+.2f}%</p>
                        <p style='margin: 2px 0;'>Vol: {row['annualized_volatility']:.1%}</p>
                        <p style='margin: 2px 0;'>Sharpe: {row['sharpe_ratio']:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Interactive Price Charts
    if show_price_chart:
        st.markdown("### 📈 Interactive Price Analysis")
        
        # Create subplot for multiple assets
        fig_price = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Price Trends', 'Price with Moving Averages'),
            vertical_spacing=0.1
        )
        
        colors = px.colors.qualitative.Set3
        
        for i, symbol in enumerate(selected_assets):
            if symbol in viz_data:
                asset_data = viz_data[symbol]
                price_df = asset_data['price_data']
                
                color = colors[i % len(colors)]
                
                # Price trend
                fig_price.add_trace(
                    go.Scatter(
                        x=price_df.index,
                        y=price_df['price'],
                        mode='lines',
                        name=f'{symbol} Price',
                        line=dict(color=color, width=2),
                        hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:,.2f}}<extra></extra>'
                    ),
                    row=1, col=1
                )
                
                # Price with moving averages
                fig_price.add_trace(
                    go.Scatter(
                        x=price_df.index,
                        y=price_df['price'],
                        mode='lines',
                        name=f'{symbol} Price',
                        line=dict(color=color, width=2),
                        showlegend=False,
                        hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:,.2f}}<extra></extra>'
                    ),
                    row=2, col=1
                )
                
                # Add moving averages
                for ma_period in [7, 30]:
                    ma_col = f'MA_{ma_period}'
                    if ma_col in price_df.columns:
                        fig_price.add_trace(
                            go.Scatter(
                                x=price_df.index,
                                y=price_df[ma_col],
                                mode='lines',
                                name=f'{symbol} MA {ma_period}',
                                line=dict(color=color, width=1, dash='dash'),
                                showlegend=False,
                                hovertemplate=f'<b>{symbol} MA {ma_period}</b><br>Date: %{{x}}<br>MA: $%{{y:,.2f}}<extra></extra>'
                            ),
                            row=2, col=1
                        )
        
        fig_price.update_layout(
            height=800,
            title_text="Cryptocurrency Price Analysis",
            template='plotly_dark',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
    
    # Volatility Analysis
    if show_volatility_chart:
        st.markdown("### 📊 Volatility Analysis")
        
        fig_volatility = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Returns', 'Rolling Volatility'),
            vertical_spacing=0.1
        )
        
        for i, symbol in enumerate(selected_assets):
            if symbol in viz_data:
                asset_data = viz_data[symbol]
                returns_df = asset_data['returns_data']
                
                color = colors[i % len(colors)]
                
                # Daily returns
                fig_volatility.add_trace(
                    go.Scatter(
                        x=returns_df.index,
                        y=returns_df['simple_return'] * 100,
                        mode='lines',
                        name=f'{symbol} Returns',
                        line=dict(color=color, width=1),
                        hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Return: %{{y:.2f}}%<extra></extra>'
                    ),
                    row=1, col=1
                )
                
                # Rolling volatility
                for window in [7, 30]:
                    vol_col = f'rolling_vol_annual_{window}'
                    if vol_col in returns_df.columns:
                        fig_volatility.add_trace(
                            go.Scatter(
                                x=returns_df.index,
                                y=returns_df[vol_col] * 100,
                                mode='lines',
                                name=f'{symbol} {window}-day Vol',
                                line=dict(color=color, width=2),
                                showlegend=window == 7,  # Only show legend for 7-day
                                hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Vol: %{{y:.1f}}%<extra></extra>'
                            ),
                            row=2, col=1
                        )
        
        fig_volatility.update_layout(
            height=800,
            title_text="Volatility and Returns Analysis",
            template='plotly_dark',
            hovermode='x unified'
        )
        
        fig_volatility.update_yaxes(title_text="Daily Return (%)", row=1, col=1)
        fig_volatility.update_yaxes(title_text="Annualized Volatility (%)", row=2, col=1)
        
        st.plotly_chart(fig_volatility, use_container_width=True)
    
    # Risk-Return Analysis
    if show_risk_return and filtered_metrics is not None and len(filtered_metrics) > 0:
        st.markdown("### 🎯 Risk-Return Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk-Return Scatter Plot
            fig_risk_return = go.Figure()
            
            # Add color mapping for risk levels
            risk_colors = {
                'Low Risk': '#00ff00',
                'Medium Risk': '#ffff00',
                'High Risk': '#ff9900',
                'Very High Risk': '#ff0000'
            }
            
            for _, row in filtered_metrics.iterrows():
                fig_risk_return.add_trace(go.Scatter(
                    x=[float(row['annualized_volatility'])],  # Convert to list
                    y=[float(row['sharpe_ratio'])],          # Convert to list
                    mode='markers+text',
                    text=row['symbol'],
                    textposition="top center",
                    marker=dict(
                        color=risk_colors.get(row['risk_level'], '#8888ff'),
                        size=15,
                        line=dict(width=2, color='white')
                    ),
                    name=row['symbol'],
                    hovertemplate=f"<b>{row['symbol']}</b><br>Volatility: {row['annualized_volatility']:.2%}<br>Sharpe: {row['sharpe_ratio']:.3f}<br>Risk: {row['risk_level']}<extra></extra>"
                ))
            
            fig_risk_return.update_layout(
                title="Risk-Return Profile",
                xaxis_title="Annualized Volatility",
                yaxis_title="Sharpe Ratio",
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig_risk_return, use_container_width=True)
        
        with col2:
            # Risk Distribution Pie Chart
            risk_counts = filtered_metrics['risk_level'].value_counts()
            
            fig_risk_dist = go.Figure(data=[
                go.Pie(
                    labels=risk_counts.index,
                    values=risk_counts.values,
                    hole=0.4,
                    textinfo='label+percent+value',
                    marker_colors=[risk_colors.get(risk, '#8888ff') for risk in risk_counts.index]
                )
            ])
            
            fig_risk_dist.update_layout(
                title="Risk Level Distribution",
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig_risk_dist, use_container_width=True)
    
    # Correlation Analysis
    if show_correlation and len(selected_assets) > 1:
        st.markdown("### 🔗 Correlation Analysis")
        
        # Calculate correlation matrix
        returns_data = {}
        for symbol in selected_assets:
            if symbol in viz_data:
                returns_data[symbol] = viz_data[symbol]['returns_data']['simple_return']
        
        if len(returns_data) > 1:
            correlation_df = pd.DataFrame(returns_data)
            correlation_matrix = correlation_df.corr()
            
            # Create heatmap
            fig_correlation = go.Figure(data=go.Heatmap(
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
            
            fig_correlation.update_layout(
                title="Cryptocurrency Correlation Matrix",
                template='plotly_dark',
                height=500
            )
            
            st.plotly_chart(fig_correlation, use_container_width=True)
    
    # Multi-Asset Comparison
    if show_comparison and len(selected_assets) > 1:
        st.markdown("### 📊 Multi-Asset Comparison")
        
        # Normalized price comparison
        fig_comparison = go.Figure()
        
        for i, symbol in enumerate(selected_assets):
            if symbol in viz_data:
                asset_data = viz_data[symbol]
                price_df = asset_data['price_data']
                
                # Normalize prices to start at 100
                normalized_prices = (price_df['price'] / price_df['price'].iloc[0]) * 100
                
                fig_comparison.add_trace(go.Scatter(
                    x=price_df.index,
                    y=normalized_prices,
                    mode='lines',
                    name=f'{symbol} (Normalized)',
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Normalized: %{{y:.1f}}<extra></extra>'
                ))
        
        fig_comparison.update_layout(
            title="Normalized Price Comparison (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            template='plotly_dark',
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Performance metrics comparison
        if filtered_metrics is not None and len(filtered_metrics) > 0:
            st.markdown("#### 📈 Performance Metrics Comparison")
            
            # Create comparison table
            comparison_metrics = filtered_metrics[['symbol', 'current_price', 'price_change_24h', 
                                                  'annualized_volatility', 'sharpe_ratio', 'beta']].copy()
            
            comparison_metrics['Current Price'] = comparison_metrics['current_price'].apply(lambda x: f"${x:,.2f}")
            comparison_metrics['24h Change'] = comparison_metrics['price_change_24h'].apply(lambda x: f"{x:+.2f}%")
            comparison_metrics['Annual Vol'] = comparison_metrics['annualized_volatility'].apply(lambda x: f"{x:.1%}")
            comparison_metrics['Sharpe Ratio'] = comparison_metrics['sharpe_ratio'].apply(lambda x: f"{x:.3f}")
            comparison_metrics['Beta'] = comparison_metrics['beta'].apply(lambda x: f"{x:.3f}")
            
            comparison_metrics = comparison_metrics[['symbol', 'Current Price', '24h Change', 'Annual Vol', 'Sharpe Ratio', 'Beta']]
            comparison_metrics.columns = ['Asset', 'Current Price', '24h Change', 'Annual Volatility', 'Sharpe Ratio', 'Beta']
            
            st.dataframe(comparison_metrics, use_container_width=True, hide_index=True)
    
    # Beta Analysis
    if len(selected_assets) > 1:
        st.markdown("### 📊 Beta Analysis")
        
        beta_data = filtered_metrics[filtered_metrics['symbol'] != benchmark].copy() if filtered_metrics is not None else None
        
        if beta_data is not None and len(beta_data) > 0:
            # Beta bar chart
            fig_beta = go.Figure(data=[
                go.Bar(
                    x=beta_data['symbol'],
                    y=beta_data['beta'],
                    text=beta_data['beta'].apply(lambda x: f"{x:.3f}"),
                    textposition='auto',
                    marker_color='lightblue'
                )
            ])
            
            fig_beta.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Market Beta (1.0)")
            
            fig_beta.update_layout(
                title=f"Beta Coefficients vs {benchmark}",
                xaxis_title="Cryptocurrency",
                yaxis_title="Beta",
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig_beta, use_container_width=True)
            
            # Beta interpretation
            beta_interpretation = beta_data.copy()
            beta_interpretation['Interpretation'] = beta_interpretation['beta'].apply(lambda x: 
                'Less volatile than market' if x < 0.8 else 
                'Similar volatility to market' if x <= 1.2 else 
                'More volatile than market')
            
            st.dataframe(
                beta_interpretation[['symbol', 'beta', 'Interpretation']].rename(columns={
                    'symbol': 'Asset', 'beta': 'Beta', 'Interpretation': 'Risk Interpretation'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # Export and Download Options
    st.markdown("### 💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Metrics CSV"):
            if filtered_metrics is not None:
                csv_data = filtered_metrics.to_csv(index=False)
                st.download_button(
                    label="Download Metrics CSV",
                    data=csv_data,
                    file_name=f"crypto_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("📊 Export Price Data"):
            if viz_data:
                # Combine all price data
                all_prices = pd.DataFrame()
                for symbol, data in viz_data.items():
                    price_df = data['price_data'][['price']].copy()
                    price_df.columns = [f'{symbol}_price']
                    all_prices = pd.concat([all_prices, price_df], axis=1)
                
                csv_data = all_prices.to_csv()
                st.download_button(
                    label="Download Price Data CSV",
                    data=csv_data,
                    file_name=f"crypto_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("📈 Generate Report"):
            with st.spinner("Generating comprehensive report..."):
                try:
                    # Generate comprehensive report
                    report = report_gen.generate_comprehensive_report(
                        selected_assets, 
                        days, 
                        benchmark
                    )
                    
                    if report:
                        st.success("✅ Report generated successfully!")
                        
                        # Store report in session state
                        st.session_state.current_report = report
                        st.session_state.report_generated = True
                        st.session_state.report_assets = selected_assets
                        st.session_state.report_days = days
                        st.session_state.report_benchmark = benchmark
                    else:
                        st.error("❌ Failed to generate report")
                        
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    # Summary Statistics
    st.markdown("### 📋 Analysis Summary")
    
    if filtered_metrics is not None and len(filtered_metrics) > 0:
        summary_stats = {
            'Total Assets': len(filtered_metrics),
            'Avg Sharpe Ratio': filtered_metrics['sharpe_ratio'].mean(),
            'Avg Volatility': filtered_metrics['annualized_volatility'].mean(),
            'Best Performer': filtered_metrics.loc[filtered_metrics['sharpe_ratio'].idxmax(), 'symbol'],
            'Most Volatile': filtered_metrics.loc[filtered_metrics['annualized_volatility'].idxmax(), 'symbol'],
            'Lowest Risk': filtered_metrics.loc[filtered_metrics['annualized_volatility'].idxmin(), 'symbol']
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Assets Analyzed", summary_stats['Total Assets'])
            st.metric("Avg Sharpe Ratio", f"{summary_stats['Avg Sharpe Ratio']:.3f}")
        
        with col2:
            st.metric("Avg Volatility", f"{summary_stats['Avg Volatility']:.1%}")
            st.metric("Best Performer", summary_stats['Best Performer'])
        
        with col3:
            st.metric("Most Volatile", summary_stats['Most Volatile'])
            st.metric("Lowest Risk", summary_stats['Lowest Risk'])
    
    # Footer with data info
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #888; font-size: 12px;'>
        📊 Data Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} | 
        🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
        💡 Powered by Binance API & Advanced Analytics
    </div>
    """, unsafe_allow_html=True)
    
    # Report Display Section
    if st.session_state.get('report_generated', False) and 'current_report' in st.session_state:
        st.markdown("---")
        st.markdown("### 📄 Comprehensive Analysis Report")
        
        report = st.session_state.current_report
        
        # Report tabs
        report_tabs = st.tabs(["📋 Executive Summary", "📊 Detailed Analysis", "⚠️ Risk Assessment", "💡 Recommendations"])
        
        with report_tabs[0]:
            st.markdown("#### 🎯 Executive Summary")
            
            # Key findings
            st.markdown("**Key Findings:**")
            for finding in report['executive_summary']['key_findings']:
                st.markdown(f"• {finding}")
            
            # Market overview
            market = report['executive_summary']['market_overview']
            st.markdown("**Market Overview:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Market Condition", market['condition'])
            with col2:
                st.metric("Average Return", market['average_return'])
            with col3:
                st.metric("Average Volatility", market['average_volatility'])
            with col4:
                st.metric("Volatility Level", market['volatility_level'])
            
            st.markdown(f"**Outlook:** {market['outlook']}")
            
            # Risk summary
            st.markdown("**Risk Distribution:**")
            for item in report['executive_summary']['risk_summary']['distribution']:
                st.markdown(f"• {item}")
        
        with report_tabs[1]:
            st.markdown("#### 📈 Detailed Asset Analysis")
            
            # Create detailed analysis table
            detailed_data = []
            for symbol, analysis in report['detailed_analysis'].items():
                detailed_data.append({
                    'Asset': symbol,
                    'Current Price': analysis['basic_metrics']['current_price'],
                    '24h Change': analysis['basic_metrics']['24h_change'],
                    'Volatility': analysis['basic_metrics']['annualized_volatility'],
                    'Sharpe Ratio': analysis['basic_metrics']['sharpe_ratio'],
                    'Beta': analysis['basic_metrics']['beta'],
                    'Max Drawdown': analysis['risk_metrics']['max_drawdown'],
                    'VaR (95%)': analysis['risk_metrics']['var_95'],
                    'Risk Level': analysis['risk_metrics']['risk_level']
                })
            
            detailed_df = pd.DataFrame(detailed_data)
            st.dataframe(detailed_df, use_container_width=True, hide_index=True)
            
            # Performance analysis
            st.markdown("**Performance Analysis:**")
            for symbol, analysis in report['detailed_analysis'].items():
                with st.expander(f"📊 {symbol} Performance Details"):
                    perf = analysis['performance_analysis']
                    st.markdown(f"**Total Return:** {perf['total_return']}")
                    st.markdown(f"**Best Week:** {perf['best_week']}")
                    st.markdown(f"**Worst Week:** {perf['worst_week']}")
                    st.markdown(f"**Volatility Trend:** {perf['volatility_trend']}")
                    st.markdown(f"**Consistency:** {perf['consistency']}")
        
        with report_tabs[2]:
            st.markdown("#### ⚠️ Risk Assessment")
            
            # Risk assessment table
            risk_data = []
            for symbol, risk in report['risk_assessment'].items():
                risk_data.append({
                    'Asset': symbol,
                    'Risk Level': risk['overall_risk'],
                    'Risk Score': f"{risk['risk_score']:.1f}/100",
                    'Risk Factors': ', '.join(risk['risk_factors']),
                    'Recommendation': risk['recommendation']
                })
            
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            # Risk score visualization
            st.markdown("**Risk Score Breakdown:**")
            risk_scores = {symbol: risk['risk_score'] for symbol, risk in report['risk_assessment'].items()}
            
            fig_risk_scores = go.Figure(data=[
                go.Bar(
                    x=list(risk_scores.keys()),
                    y=list(risk_scores.values()),
                    text=[f"{score:.1f}" for score in risk_scores.values()],
                    textposition='auto',
                    marker_color='lightcoral'
                )
            ])
            
            fig_risk_scores.update_layout(
                title="Risk Scores (0-100, lower is better)",
                xaxis_title="Asset",
                yaxis_title="Risk Score",
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig_risk_scores, use_container_width=True)
        
        with report_tabs[3]:
            st.markdown("#### 💡 Investment Recommendations")
            
            # Portfolio suggestions
            st.markdown("**Portfolio Suggestions:**")
            for suggestion in report['recommendations']['portfolio_suggestions']:
                st.markdown(f"• {suggestion}")
            
            # Risk management
            st.markdown("**Risk Management:**")
            for risk_mgmt in report['recommendations']['risk_management']:
                st.markdown(f"• {risk_mgmt}")
            
            # Monitoring points
            st.markdown("**Monitoring Points:**")
            for point in report['recommendations']['monitoring_points']:
                st.markdown(f"• {point}")
            
            # Correlation analysis if available
            if 'correlation_analysis' in report and 'error' not in report['correlation_analysis']:
                st.markdown("**Diversification Analysis:**")
                corr = report['correlation_analysis']
                st.markdown(f"• Diversification Benefit: {corr['diversification_benefit']}")
                
                if corr['highest_correlation']:
                    asset1, asset2, value = corr['highest_correlation']
                    st.markdown(f"• Highest Correlation: {asset1}-{asset2} ({value:.3f})")
                
                if corr['lowest_correlation']:
                    asset1, asset2, value = corr['lowest_correlation']
                    st.markdown(f"• Lowest Correlation: {asset1}-{asset2} ({value:.3f})")
        
        # Export options for report
        st.markdown("#### 📥 Export Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Text format
            text_report = report_gen.format_report_as_text(report)
            st.download_button(
                label="📄 Download Text Report",
                data=text_report,
                file_name=f"crypto_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col2:
            # HTML format
            html_report = report_gen.format_report_as_html(report)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report,
                file_name=f"crypto_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        with col3:
            # CSV format
            csv_report = report_gen.generate_csv_report(report)
            if csv_report:
                st.download_button(
                    label="📊 Download CSV Report",
                    data=csv_report,
                    file_name=f"crypto_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
