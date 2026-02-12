import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AnalyticsEngine:
    """Real-time analytics and risk assessment engine"""
    
    def __init__(self):
        pass
    
    def calculate_volatility(self, df, window=14):
        """Calculate volatility metrics"""
        if df is None or len(df) < 2:
            return None
        
        df = df.copy()
        df['returns'] = df['price'].pct_change() * 100
        df['volatility'] = df['returns'].rolling(window=window).std()
        df['avg_volatility'] = df['volatility'].mean()
        
        latest_vol = df['volatility'].iloc[-1]
        avg_vol = df['volatility'].mean()
        max_vol = df['volatility'].max()
        price_change_24h = df['returns'].iloc[-1] if len(df) > 0 else 0
        
        return {
            'current_volatility': latest_vol,
            'average_volatility': avg_vol,
            'max_volatility': max_vol,
            'price_change_24h': price_change_24h,
            'data': df
        }
    
    def get_risk_assessment(self, volatility_data):
        """Assess risk based on volatility"""
        if volatility_data is None:
            return "Unknown", "Insufficient data", 50
        
        current_vol = volatility_data['current_volatility']
        
        if current_vol > 8:
            risk_level = "High Risk"
            risk_score = min(90, 50 + current_vol * 5)
            explanation = "Extreme volatility detected. Prices can change dramatically in short periods."
            color = "#ef4444"
        elif current_vol > 4:
            risk_level = "Medium Risk"
            risk_score = min(70, 40 + current_vol * 3)
            explanation = "Moderate to high volatility. Suitable for balanced risk appetite."
            color = "#f59e0b"
        elif current_vol > 2:
            risk_level = "Low-Medium Risk"
            risk_score = min(50, 30 + current_vol * 2)
            explanation = "Moderate volatility. Generally manageable for most investors."
            color = "#3b82f6"
        else:
            risk_level = "Low Risk"
            risk_score = min(30, 20 + current_vol)
            explanation = "Low volatility. Relatively stable compared to other cryptocurrencies."
            color = "#10b981"
        
        return risk_level, explanation, risk_score, color
    
    def calculate_market_sentiment(self, data):
        """Calculate market sentiment based on price movements"""
        if not data:
            return "Neutral", 50, "#6b7280"
        
        positive_changes = 0
        negative_changes = 0
        
        for symbol, info in data.items():
            if info.get('change_24h', 0) > 0:
                positive_changes += 1
            elif info.get('change_24h', 0) < 0:
                negative_changes += 1
        
        total = positive_changes + negative_changes
        if total == 0:
            return "Neutral", 50, "#6b7280"
        
        bullish_ratio = positive_changes / total
        
        if bullish_ratio > 0.7:
            sentiment = "Very Bullish"
            score = 80 + (bullish_ratio - 0.7) * 50
            color = "#10b981"
        elif bullish_ratio > 0.5:
            sentiment = "Bullish"
            score = 60 + (bullish_ratio - 0.5) * 80
            color = "#22c55e"
        elif bullish_ratio > 0.3:
            sentiment = "Bearish"
            score = 40 - (0.5 - bullish_ratio) * 80
            color = "#f59e0b"
        else:
            sentiment = "Very Bearish"
            score = 20 - (0.3 - bullish_ratio) * 50
            color = "#ef4444"
        
        return sentiment, min(100, max(0, score)), color
    
    def get_price_trend(self, df, period=7):
        """Analyze price trend over period"""
        if df is None or len(df) < period:
            return "Neutral", 0, "#6b7280"
        
        recent_data = df.tail(period)
        start_price = recent_data.iloc[0]['price']
        end_price = recent_data.iloc[-1]['price']
        
        change_pct = ((end_price - start_price) / start_price) * 100
        
        if change_pct > 5:
            trend = "Strong Uptrend"
            color = "#10b981"
        elif change_pct > 2:
            trend = "Uptrend"
            color = "#22c55e"
        elif change_pct > -2:
            trend = "Sideways"
            color = "#6b7280"
        elif change_pct > -5:
            trend = "Downtrend"
            color = "#f59e0b"
        else:
            trend = "Strong Downtrend"
            color = "#ef4444"
        
        return trend, change_pct, color
    
    def calculate_metrics(self, data):
        """Calculate comprehensive market metrics"""
        if not data:
            return {}
        
        prices = [info.get('price', 0) for info in data.values()]
        volumes = [info.get('volume_24h', 0) for info in data.values()]
        changes = [info.get('change_24h', 0) for info in data.values()]
        
        return {
            'total_market_cap': sum(prices),  # Simplified
            'total_volume_24h': sum(volumes),
            'avg_change_24h': np.mean(changes),
            'positive_movers': len([c for c in changes if c > 0]),
            'negative_movers': len([c for c in changes if c < 0]),
            'biggest_gainer': max(data.items(), key=lambda x: x[1].get('change_24h', 0)) if data else None,
            'biggest_loser': min(data.items(), key=lambda x: x[1].get('change_24h', 0)) if data else None
        }
