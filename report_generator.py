"""
Comprehensive report generation for cryptocurrency analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_engine import DataEngine
import base64
import io

class CryptoReportGenerator:
    """Generate comprehensive cryptocurrency analysis reports"""
    
    def __init__(self):
        self.data_engine = DataEngine()
    
    def generate_comprehensive_report(self, symbols, days=90, benchmark='BTC'):
        """Generate a comprehensive analysis report"""
        
        # Load data
        viz_data = self.data_engine.prepare_visualization_data(symbols, days)
        metrics_df = self.data_engine.generate_metrics_table(benchmark)
        
        if not viz_data or metrics_df is None:
            return None
        
        # Filter metrics for selected symbols
        filtered_metrics = metrics_df[metrics_df['symbol'].isin(symbols)]
        
        # Generate report sections
        report = {
            'metadata': self._generate_report_metadata(symbols, days, benchmark),
            'executive_summary': self._generate_executive_summary(filtered_metrics),
            'detailed_analysis': self._generate_detailed_analysis(viz_data, filtered_metrics),
            'risk_assessment': self._generate_risk_assessment(filtered_metrics),
            'correlation_analysis': self._generate_correlation_analysis(viz_data),
            'performance_comparison': self._generate_performance_comparison(filtered_metrics),
            'recommendations': self._generate_recommendations(filtered_metrics),
            'appendix': self._generate_appendix(viz_data, filtered_metrics)
        }
        
        return report
    
    def _generate_report_metadata(self, symbols, days, benchmark):
        """Generate report metadata"""
        return {
            'report_title': 'Cryptocurrency Volatility & Risk Analysis Report',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_period': f'{days} days',
            'assets_analyzed': symbols,
            'benchmark': benchmark,
            'data_sources': ['Binance API', 'CoinGecko API (fallback)'],
            'methodology': 'Statistical analysis using log returns, rolling volatility, and beta calculations'
        }
    
    def _generate_executive_summary(self, metrics_df):
        """Generate executive summary"""
        if len(metrics_df) == 0:
            return {"error": "No data available"}
        
        best_performer = metrics_df.loc[metrics_df['sharpe_ratio'].idxmax()]
        most_volatile = metrics_df.loc[metrics_df['annualized_volatility'].idxmax()]
        least_risky = metrics_df.loc[metrics_df['annualized_volatility'].idxmin()]
        
        avg_volatility = metrics_df['annualized_volatility'].mean()
        avg_sharpe = metrics_df['sharpe_ratio'].mean()
        
        return {
            'key_findings': [
                f"Best risk-adjusted performance: {best_performer['symbol']} (Sharpe: {best_performer['sharpe_ratio']:.3f})",
                f"Highest volatility: {most_volatile['symbol']} ({most_volatile['annualized_volatility']:.1%})",
                f"Lowest risk: {least_risky['symbol']} ({least_risky['annualized_volatility']:.1%})",
                f"Portfolio average volatility: {avg_volatility:.1%}",
                f"Portfolio average Sharpe ratio: {avg_sharpe:.3f}"
            ],
            'market_overview': self._analyze_market_conditions(metrics_df),
            'risk_summary': self._summarize_risk_levels(metrics_df)
        }
    
    def _analyze_market_conditions(self, metrics_df):
        """Analyze overall market conditions"""
        avg_return = metrics_df['annual_return'].mean()
        avg_volatility = metrics_df['annualized_volatility'].mean()
        
        if avg_return > 0.5:  # 50% annual return
            market_condition = "Bull Market"
            outlook = "Strong upward momentum across analyzed assets"
        elif avg_return < -0.3:  # -30% annual return
            market_condition = "Bear Market"
            outlook = "Significant downward pressure across assets"
        else:
            market_condition = "Sideways/Neutral"
            outlook = "Mixed performance with no clear directional bias"
        
        return {
            'condition': market_condition,
            'outlook': outlook,
            'average_return': f"{avg_return:.2%}",
            'average_volatility': f"{avg_volatility:.1%}",
            'volatility_level': "High" if avg_volatility > 0.8 else "Moderate" if avg_volatility > 0.4 else "Low"
        }
    
    def _summarize_risk_levels(self, metrics_df):
        """Summarize risk distribution"""
        risk_counts = metrics_df['risk_level'].value_counts()
        total_assets = len(metrics_df)
        
        summary = []
        for risk_level, count in risk_counts.items():
            percentage = (count / total_assets) * 100
            summary.append(f"{risk_level}: {count} assets ({percentage:.1f}%)")
        
        return {
            'distribution': summary,
            'dominant_risk_level': risk_counts.index[0],
            'risk_diversification': "Well diversified" if len(risk_counts) > 2 else "Concentrated risk profile"
        }
    
    def _generate_detailed_analysis(self, viz_data, metrics_df):
        """Generate detailed analysis for each asset"""
        analysis = {}
        
        for _, row in metrics_df.iterrows():
            symbol = row['symbol']
            
            if symbol in viz_data:
                asset_data = viz_data[symbol]
                price_df = asset_data['price_data']
                returns_df = asset_data['returns_data']
                
                # Calculate additional metrics
                max_drawdown = self._calculate_max_drawdown(price_df)
                var_95 = self._calculate_var(returns_df['simple_return'], 0.05)
                skewness = returns_df['simple_return'].skew()
                kurtosis = returns_df['simple_return'].kurtosis()
                
                analysis[symbol] = {
                    'basic_metrics': {
                        'current_price': f"${row['current_price']:,.2f}",
                        '24h_change': f"{row['price_change_24h']:+.2f}%",
                        'annualized_volatility': f"{row['annualized_volatility']:.1%}",
                        'sharpe_ratio': f"{row['sharpe_ratio']:.3f}",
                        'beta': f"{row['beta']:.3f}"
                    },
                    'risk_metrics': {
                        'max_drawdown': f"{max_drawdown:.2%}",
                        'var_95': f"{var_95:.2%}",
                        'risk_level': row['risk_level']
                    },
                    'distribution_metrics': {
                        'skewness': f"{skewness:.3f}",
                        'kurtosis': f"{kurtosis:.3f}",
                        'interpretation': self._interpret_distribution(skewness, kurtosis)
                    },
                    'performance_analysis': self._analyze_performance(price_df, returns_df)
                }
        
        return analysis
    
    def _calculate_max_drawdown(self, price_df):
        """Calculate maximum drawdown"""
        peak = price_df['price'].expanding().max()
        drawdown = (price_df['price'] - peak) / peak
        return drawdown.min()
    
    def _calculate_var(self, returns, confidence_level):
        """Calculate Value at Risk"""
        return np.percentile(returns.dropna(), confidence_level * 100)
    
    def _interpret_distribution(self, skewness, kurtosis):
        """Interpret distribution characteristics"""
        skew_interpretation = (
            "Right-skewed (positive returns more likely)" if skewness > 0.5 else
            "Left-skewed (negative returns more likely)" if skewness < -0.5 else
            "Approximately symmetric"
        )
        
        kurt_interpretation = (
            "Heavy-tailed (extreme events more likely)" if kurtosis > 3 else
            "Light-tailed (extreme events less likely)" if kurtosis < 3 else
            "Normal-like distribution"
        )
        
        return f"{skew_interpretation}, {kurt_interpretation}"
    
    def _analyze_performance(self, price_df, returns_df):
        """Analyze performance patterns"""
        total_return = (price_df['price'].iloc[-1] / price_df['price'].iloc[0] - 1) * 100
        
        # Calculate best and worst periods
        rolling_returns = returns_df['simple_return'].rolling(7).sum()
        best_week = rolling_returns.max() * 100
        worst_week = rolling_returns.min() * 100
        
        # Volatility analysis
        vol_trend = self._analyze_volatility_trend(returns_df)
        
        return {
            'total_return': f"{total_return:.2f}%",
            'best_week': f"{best_week:.2f}%",
            'worst_week': f"{worst_week:.2f}%",
            'volatility_trend': vol_trend,
            'consistency': self._assess_consistency(returns_df)
        }
    
    def _analyze_volatility_trend(self, returns_df):
        """Analyze volatility trend"""
        if 'rolling_vol_7' in returns_df.columns:
            recent_vol = returns_df['rolling_vol_7'].iloc[-7:].mean()
            earlier_vol = returns_df['rolling_vol_7'].iloc[-14:-7].mean()
            
            if recent_vol > earlier_vol * 1.2:
                return "Increasing (higher risk)"
            elif recent_vol < earlier_vol * 0.8:
                return "Decreasing (lower risk)"
            else:
                return "Stable"
        return "Insufficient data"
    
    def _assess_consistency(self, returns_df):
        """Assess return consistency"""
        positive_days = (returns_df['simple_return'] > 0).sum()
        total_days = len(returns_df)
        win_rate = positive_days / total_days
        
        if win_rate > 0.55:
            return "High consistency"
        elif win_rate > 0.45:
            return "Moderate consistency"
        else:
            return "Low consistency"
    
    def _generate_risk_assessment(self, metrics_df):
        """Generate comprehensive risk assessment"""
        risk_summary = {}
        
        for _, row in metrics_df.iterrows():
            symbol = row['symbol']
            
            risk_factors = []
            if row['annualized_volatility'] > 0.8:
                risk_factors.append("High volatility")
            if row['sharpe_ratio'] < -1:
                risk_factors.append("Poor risk-adjusted returns")
            if row['beta'] > 1.5:
                risk_factors.append("High market sensitivity")
            if row['price_change_24h'] < -10:
                risk_factors.append("Recent significant decline")
            
            risk_summary[symbol] = {
                'overall_risk': row['risk_level'],
                'risk_factors': risk_factors if risk_factors else ["No significant risk factors"],
                'risk_score': self._calculate_risk_score(row),
                'recommendation': self._get_risk_recommendation(row)
            }
        
        return risk_summary
    
    def _calculate_risk_score(self, row):
        """Calculate comprehensive risk score (0-100)"""
        volatility_score = min(row['annualized_volatility'] * 100, 40)  # Max 40 points
        sharpe_score = max(0, -row['sharpe_ratio'] * 10)  # Max 30 points
        beta_score = min(abs(row['beta'] - 1) * 20, 20)  # Max 20 points
        momentum_score = max(0, -row['price_change_24h']) * 2  # Max 10 points
        
        total_score = volatility_score + sharpe_score + beta_score + momentum_score
        return min(total_score, 100)
    
    def _get_risk_recommendation(self, row):
        """Get risk-based recommendation"""
        if row['risk_level'] == 'Low Risk':
            return "Suitable for conservative portfolios"
        elif row['risk_level'] == 'Medium Risk':
            return "Suitable for balanced portfolios"
        elif row['risk_level'] == 'High Risk':
            return "Suitable for aggressive portfolios with proper risk management"
        else:
            return "Highly speculative - only for experienced traders"
    
    def _generate_correlation_analysis(self, viz_data):
        """Generate correlation analysis"""
        if len(viz_data) < 2:
            return {"error": "Insufficient assets for correlation analysis"}
        
        # Calculate correlation matrix
        returns_data = {}
        for symbol, data in viz_data.items():
            returns_data[symbol] = data['returns_data']['simple_return']
        
        correlation_df = pd.DataFrame(returns_data)
        correlation_matrix = correlation_df.corr()
        
        # Find highest and lowest correlations
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                asset1 = correlation_matrix.columns[i]
                asset2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                correlations.append((asset1, asset2, corr_value))
        
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return {
            'correlation_matrix': correlation_matrix.round(3).to_dict(),
            'highest_correlation': correlations[0] if correlations else None,
            'lowest_correlation': correlations[-1] if correlations else None,
            'diversification_benefit': self._assess_diversification(correlation_matrix)
        }
    
    def _assess_diversification(self, correlation_matrix):
        """Assess diversification benefits"""
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        
        if avg_correlation < 0.3:
            return "Excellent diversification benefits"
        elif avg_correlation < 0.6:
            return "Moderate diversification benefits"
        else:
            return "Limited diversification benefits"
    
    def _generate_performance_comparison(self, metrics_df):
        """Generate performance comparison"""
        comparison = {
            'rankings': {},
            'performance_metrics': {},
            'relative_analysis': {}
        }
        
        # Rank assets by different metrics
        comparison['rankings']['sharpe_ratio'] = metrics_df.sort_values('sharpe_ratio', ascending=False)['symbol'].tolist()
        comparison['rankings']['lowest_volatility'] = metrics_df.sort_values('annualized_volatility')['symbol'].tolist()
        comparison['rankings']['highest_return'] = metrics_df.sort_values('annual_return', ascending=False)['symbol'].tolist()
        comparison['rankings']['best_risk_adjusted'] = metrics_df.sort_values('sharpe_ratio', ascending=False)['symbol'].tolist()
        
        # Performance metrics summary
        comparison['performance_metrics'] = {
            'best_performer': metrics_df.loc[metrics_df['sharpe_ratio'].idxmax(), 'symbol'],
            'most_volatile': metrics_df.loc[metrics_df['annualized_volatility'].idxmax(), 'symbol'],
            'least_volatile': metrics_df.loc[metrics_df['annualized_volatility'].idxmin(), 'symbol'],
            'highest_beta': metrics_df.loc[metrics_df['beta'].idxmax(), 'symbol'],
            'lowest_beta': metrics_df.loc[metrics_df['beta'].idxmin(), 'symbol']
        }
        
        return comparison
    
    def _generate_recommendations(self, metrics_df):
        """Generate investment recommendations"""
        recommendations = {
            'portfolio_suggestions': [],
            'risk_management': [],
            'monitoring_points': []
        }
        
        # Portfolio suggestions
        best_risk_adjusted = metrics_df.loc[metrics_df['sharpe_ratio'].idxmax()]
        low_volatility_assets = metrics_df[metrics_df['risk_level'].isin(['Low Risk', 'Medium Risk'])]
        
        recommendations['portfolio_suggestions'].append(
            f"Consider higher allocation to {best_risk_adjusted['symbol']} for best risk-adjusted returns"
        )
        
        if len(low_volatility_assets) > 0:
            recommendations['portfolio_suggestions'].append(
                f"Use {', '.join(low_volatility_assets['symbol'].tolist())} for portfolio stability"
            )
        
        # Risk management
        high_volatility = metrics_df[metrics_df['risk_level'] == 'Very High Risk']
        if len(high_volatility) > 0:
            recommendations['risk_management'].append(
                f"Implement strict stop-losses for {', '.join(high_volatility['symbol'].tolist())}"
            )
        
        recommendations['risk_management'].append("Consider position sizing based on volatility")
        recommendations['risk_management'].append("Diversify across assets with low correlation")
        
        # Monitoring points
        recommendations['monitoring_points'].append("Monitor Sharpe ratio trends")
        recommendations['monitoring_points'].append("Watch for volatility spikes")
        recommendations['monitoring_points'].append("Track correlation changes")
        
        return recommendations
    
    def _generate_appendix(self, viz_data, metrics_df):
        """Generate appendix with technical details"""
        appendix = {
            'methodology': {
                'volatility_calculation': 'Daily standard deviation of log returns, annualized with √365',
                'sharpe_ratio': '(Annual Return - Risk-Free Rate) / Annual Volatility',
                'beta_calculation': 'Covariance(Asset, Market) / Variance(Market)',
                'risk_classification': 'Based on annualized volatility thresholds'
            },
            'data_quality': {
                'data_points_per_asset': {symbol: len(data['returns_data']) for symbol, data in viz_data.items()},
                'missing_data_handling': 'Forward fill for gaps, exclusion for insufficient data',
                'outlier_treatment': 'Winsorization at 1st and 99th percentiles'
            },
            'assumptions': [
                'Risk-free rate assumed to be 2% annually',
                '365 trading days per year for cryptocurrency markets',
                'Normal distribution assumptions for VaR calculations',
                'Historical correlations may not predict future correlations'
            ]
        }
        
        return appendix
    
    def format_report_as_text(self, report):
        """Format report as readable text"""
        if not report:
            return "No report data available"
        
        text = []
        
        # Title and metadata
        text.append("=" * 80)
        text.append(report['metadata']['report_title'].upper())
        text.append("=" * 80)
        text.append(f"Generated: {report['metadata']['generated_at']}")
        text.append(f"Analysis Period: {report['metadata']['analysis_period']}")
        text.append(f"Assets: {', '.join(report['metadata']['assets_analyzed'])}")
        text.append(f"Benchmark: {report['metadata']['benchmark']}")
        text.append("")
        
        # Executive Summary
        text.append("EXECUTIVE SUMMARY")
        text.append("-" * 40)
        for finding in report['executive_summary']['key_findings']:
            text.append(f"• {finding}")
        text.append("")
        
        # Market Overview
        market = report['executive_summary']['market_overview']
        text.append("MARKET OVERVIEW")
        text.append("-" * 40)
        text.append(f"Market Condition: {market['condition']}")
        text.append(f"Outlook: {market['outlook']}")
        text.append(f"Average Return: {market['average_return']}")
        text.append(f"Average Volatility: {market['average_volatility']}")
        text.append("")
        
        # Detailed Analysis
        text.append("DETAILED ASSET ANALYSIS")
        text.append("-" * 40)
        for symbol, analysis in report['detailed_analysis'].items():
            text.append(f"\n{symbol}")
            text.append("Basic Metrics:")
            for metric, value in analysis['basic_metrics'].items():
                text.append(f"  {metric}: {value}")
            
            text.append("Risk Metrics:")
            for metric, value in analysis['risk_metrics'].items():
                text.append(f"  {metric}: {value}")
        
        # Risk Assessment
        text.append("\nRISK ASSESSMENT")
        text.append("-" * 40)
        for symbol, risk in report['risk_assessment'].items():
            text.append(f"\n{symbol}:")
            text.append(f"  Risk Level: {risk['overall_risk']}")
            text.append(f"  Risk Score: {risk['risk_score']:.1f}/100")
            text.append(f"  Recommendation: {risk['recommendation']}")
        
        # Recommendations
        text.append("\nRECOMMENDATIONS")
        text.append("-" * 40)
        text.append("Portfolio Suggestions:")
        for suggestion in report['recommendations']['portfolio_suggestions']:
            text.append(f"• {suggestion}")
        
        text.append("\nRisk Management:")
        for risk_mgmt in report['recommendations']['risk_management']:
            text.append(f"• {risk_mgmt}")
        
        # Correlation Analysis
        if 'correlation_analysis' in report and 'error' not in report['correlation_analysis']:
            text.append("\nCORRELATION ANALYSIS")
            text.append("-" * 40)
            corr = report['correlation_analysis']
            if corr['highest_correlation']:
                asset1, asset2, value = corr['highest_correlation']
                text.append(f"Highest Correlation: {asset1}-{asset2} ({value:.3f})")
            if corr['lowest_correlation']:
                asset1, asset2, value = corr['lowest_correlation']
                text.append(f"Lowest Correlation: {asset1}-{asset2} ({value:.3f})")
            text.append(f"Diversification Benefit: {corr['diversification_benefit']}")
        
        # Methodology
        text.append("\nMETHODOLOGY")
        text.append("-" * 40)
        for method, description in report['appendix']['methodology'].items():
            text.append(f"{method}: {description}")
        
        return "\n".join(text)
    
    def format_report_as_html(self, report):
        """Format report as HTML"""
        if not report:
            return "<p>No report data available</p>"
        
        html = []
        
        # HTML header
        html.append(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report['metadata']['report_title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; 
                         background: #f8f9fa; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .risk-low {{ color: #28a745; }}
                .risk-medium {{ color: #ffc107; }}
                .risk-high {{ color: #fd7e14; }}
                .risk-very-high {{ color: #dc3545; }}
            </style>
        </head>
        <body>
        """)
        
        # Header
        html.append(f"""
        <div class="header">
            <h1>{report['metadata']['report_title']}</h1>
            <p>Generated: {report['metadata']['generated_at']} | 
               Period: {report['metadata']['analysis_period']} | 
               Assets: {', '.join(report['metadata']['assets_analyzed'])}</p>
        </div>
        """)
        
        # Executive Summary
        html.append("""
        <div class="section">
            <h2>Executive Summary</h2>
        """)
        
        for finding in report['executive_summary']['key_findings']:
            html.append(f"<p>• {finding}</p>")
        
        html.append(f"""
        <h3>Market Overview</h3>
        <p><strong>Condition:</strong> {report['executive_summary']['market_overview']['condition']}</p>
        <p><strong>Outlook:</strong> {report['executive_summary']['market_overview']['outlook']}</p>
        <p><strong>Average Return:</strong> {report['executive_summary']['market_overview']['average_return']}</p>
        <p><strong>Average Volatility:</strong> {report['executive_summary']['market_overview']['average_volatility']}</p>
        </div>
        """)
        
        # Detailed Analysis
        html.append("""
        <div class="section">
            <h2>Detailed Asset Analysis</h2>
            <table>
                <tr>
                    <th>Asset</th>
                    <th>Current Price</th>
                    <th>24h Change</th>
                    <th>Volatility</th>
                    <th>Sharpe Ratio</th>
                    <th>Beta</th>
                    <th>Risk Level</th>
                </tr>
        """)
        
        for symbol, analysis in report['detailed_analysis'].items():
            risk_class = analysis['risk_metrics']['risk_level'].lower().replace(' ', '-')
            html.append(f"""
            <tr>
                <td><strong>{symbol}</strong></td>
                <td>{analysis['basic_metrics']['current_price']}</td>
                <td>{analysis['basic_metrics']['24h_change']}</td>
                <td>{analysis['basic_metrics']['annualized_volatility']}</td>
                <td>{analysis['basic_metrics']['sharpe_ratio']}</td>
                <td>{analysis['basic_metrics']['beta']}</td>
                <td class="risk-{risk_class}">{analysis['risk_metrics']['risk_level']}</td>
            </tr>
            """)
        
        html.append("</table></div>")
        
        # Risk Assessment
        html.append("""
        <div class="section">
            <h2>Risk Assessment</h2>
        """)
        
        for symbol, risk in report['risk_assessment'].items():
            html.append(f"""
            <div class="metric">
                <h4>{symbol}</h4>
                <p>Risk Level: {risk['overall_risk']}</p>
                <p>Risk Score: {risk['risk_score']:.1f}/100</p>
                <p>Recommendation: {risk['recommendation']}</p>
            </div>
            """)
        
        html.append("</div>")
        
        # Recommendations
        html.append("""
        <div class="section">
            <h2>Investment Recommendations</h2>
            <h3>Portfolio Suggestions</h3>
            <ul>
        """)
        
        for suggestion in report['recommendations']['portfolio_suggestions']:
            html.append(f"<li>{suggestion}</li>")
        
        html.append("""
            </ul>
            <h3>Risk Management</h3>
            <ul>
        """)
        
        for risk_mgmt in report['recommendations']['risk_management']:
            html.append(f"<li>{risk_mgmt}</li>")
        
        html.append("</ul></div>")
        
        # Footer
        html.append("""
        <div class="section">
            <h2>Methodology</h2>
            <p>This report uses statistical analysis of historical price data to assess risk and return characteristics.</p>
            <p>Volatility is calculated as the standard deviation of daily log returns, annualized over 365 days.</p>
            <p>Sharpe ratio measures risk-adjusted returns relative to a 2% risk-free rate.</p>
            <p>Beta measures sensitivity to market movements (BTC as benchmark).</p>
        </div>
        </body>
        </html>
        """)
        
        return "\n".join(html)
    
    def generate_csv_report(self, report):
        """Generate CSV report with key metrics"""
        if not report or 'detailed_analysis' not in report:
            return None
        
        # Create summary CSV
        data = []
        for symbol, analysis in report['detailed_analysis'].items():
            row = {
                'Symbol': symbol,
                'Current Price': analysis['basic_metrics']['current_price'],
                '24h Change': analysis['basic_metrics']['24h_change'],
                'Annualized Volatility': analysis['basic_metrics']['annualized_volatility'],
                'Sharpe Ratio': analysis['basic_metrics']['sharpe_ratio'],
                'Beta': analysis['basic_metrics']['beta'],
                'Max Drawdown': analysis['risk_metrics']['max_drawdown'],
                'VaR (95%)': analysis['risk_metrics']['var_95'],
                'Risk Level': analysis['risk_metrics']['risk_level'],
                'Risk Score': report['risk_assessment'][symbol]['risk_score']
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
