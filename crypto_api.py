import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class CryptoAPI:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.binance_base = "https://api.binance.com/api/v3"
    
    def get_price_history(self, coin_id, days=30):
        """Get price history - tries Binance first, then CoinGecko"""
        print(f"Attempting to fetch price history for {coin_id} ({days} days)")
        
        # Try Binance first (more reliable)
        binance_symbol = self.get_binance_symbol(coin_id)
        print(f"Binance symbol for {coin_id}: {binance_symbol}")
        
        if binance_symbol:
            binance_data = self.get_binance_klines(binance_symbol, '1d', days)
            if binance_data is not None:
                print(f"Successfully got data from Binance for {coin_id}")
                return binance_data
            else:
                print(f"Binance failed for {coin_id}, trying CoinGecko")
        else:
            print(f"No Binance symbol found for {coin_id}, trying CoinGecko")
        
        # Fallback to CoinGecko
        print(f"Trying CoinGecko for {coin_id}")
        return self.get_coingecko_price_history(coin_id, days)
    
    def get_coingecko_price_history(self, coin_id, days=30):
        """Get price history from CoinGecko - real-time only"""
        try:
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            return df
        except Exception as e:
            print(f"Error fetching CoinGecko data: {e}")
            return None
    
    def get_binance_symbol(self, coin_id):
        """Convert CoinGecko ID to Binance symbol"""
        symbol_map = {
            'bitcoin': 'BTCUSDT',
            'ethereum': 'ETHUSDT',
            'cardano': 'ADAUSDT',
            'polkadot': 'DOTUSDT',
            'chainlink': 'LINKUSDT',
            'binancecoin': 'BNBUSDT',
            'ripple': 'XRPUSDT',
            'solana': 'SOLUSDT',
            'dogecoin': 'DOGEUSDT',
            'avalanche-2': 'AVAXUSDT'
        }
        return symbol_map.get(coin_id)
    
    def get_binance_klines(self, symbol, interval='1d', limit=30):
        """Get kline data from Binance"""
        try:
            url = f"{self.binance_base}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print(f"No data returned from Binance for {symbol}")
                return None
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            df['price'] = pd.to_numeric(df['close'])
            
            print(f"Successfully fetched {len(df)} records from Binance for {symbol}")
            return df[['price']]
        except Exception as e:
            print(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    def get_current_price(self, coin_id):
        """Get current price - tries Binance first, then CoinGecko"""
        # Try Binance first
        binance_symbol = self.get_binance_symbol(coin_id)
        if binance_symbol:
            try:
                url = f"{self.binance_base}/ticker/price"
                params = {'symbol': binance_symbol}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                return {coin_id: {'usd': float(data['price'])}}
            except Exception as e:
                print(f"Binance price fetch failed: {e}")
        
        # Fallback to CoinGecko
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None
    
    def calculate_volatility(self, df, window=14):
        """Calculate volatility metrics"""
        if df is None or len(df) < 2:
            return None
        
        df['returns'] = df['price'].pct_change() * 100
        df['volatility'] = df['returns'].rolling(window=window).std()
        df['avg_volatility'] = df['volatility'].mean()
        
        latest_vol = df['volatility'].iloc[-1]
        avg_vol = df['volatility'].mean()
        max_vol = df['volatility'].max()
        
        return {
            'current_volatility': latest_vol,
            'average_volatility': avg_vol,
            'max_volatility': max_vol,
            'price_change_24h': df['returns'].iloc[-1] if len(df) > 0 else 0,
            'data': df
        }
    
    def get_risk_assessment(self, volatility_data):
        """Assess risk based on volatility"""
        if volatility_data is None:
            return "Unknown", "Insufficient data"
        
        current_vol = volatility_data['current_volatility']
        
        if current_vol > 8:
            risk_level = "🔴 High Risk"
            explanation = "Extreme volatility detected. Prices can change dramatically in short periods. Only suitable for experienced traders with high risk tolerance."
        elif current_vol > 4:
            risk_level = "🟠 Medium Risk"
            explanation = "Moderate to high volatility. Suitable for investors with balanced risk appetite and good understanding of crypto markets."
        elif current_vol > 2:
            risk_level = "🟡 Low-Medium Risk"
            explanation = "Moderate volatility. Generally manageable for most investors with some crypto knowledge."
        else:
            risk_level = "🟢 Low Risk"
            explanation = "Low volatility. Relatively stable compared to other cryptocurrencies."
        
        return risk_level, explanation

def search_crypto(query):
    """Search for cryptocurrencies"""
    try:
        url = "https://api.coingecko.com/api/v3/search"
        params = {'query': query}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        coins = []
        for coin in data['coins'][:10]:  # Top 10 results
            coins.append({
                'id': coin['id'],
                'name': coin['name'],
                'symbol': coin['symbol'].upper()
            })
        return coins
    except Exception as e:
        print(f"Error searching crypto: {e}")
        return []
