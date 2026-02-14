"""
Cloud-optimized data fetcher for Streamlit Cloud deployment
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os

class CloudDataFetcher:
    """Optimized data fetcher for cloud environments"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.max_retries = 3
        self.timeout = 10
        
        # API endpoints
        self.binance_base = "https://api.binance.com/api/v3"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
        # Symbol mappings
        self.binance_pairs = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT", 
            "SOL": "SOLUSDT",
            "ADA": "ADAUSDT",
            "DOGE": "DOGEUSDT"
        }
        
        self.coin_ids = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "ADA": "cardano",
            "DOGE": "dogecoin"
        }
    
    def get_cache_key(self, symbol, days):
        """Generate cache key"""
        return f"{symbol}_{days}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    def is_cache_valid(self, cache_key):
        """Check if cache is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        current_time = datetime.now()
        return (current_time - cache_time).total_seconds() < self.cache_timeout
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data with cloud optimizations"""
        cache_key = self.get_cache_key(symbol, days)
        
        # Check cache first
        if self.is_cache_valid(cache_key):
            print(f"✅ Using cached data for {symbol}")
            return self.cache[cache_key]['data'].copy()
        
        # Fetch fresh data
        for attempt in range(self.max_retries):
            try:
                # Try Binance first
                data = self._fetch_from_binance(symbol, days)
                if data is not None:
                    self.cache[cache_key] = {
                        'data': data.copy(),
                        'timestamp': datetime.now()
                    }
                    return data
                
                # Fallback to CoinGecko
                print(f"Trying CoinGecko for {symbol}...")
                data = self._fetch_from_coingecko(symbol, days)
                if data is not None:
                    self.cache[cache_key] = {
                        'data': data.copy(),
                        'timestamp': datetime.now()
                    }
                    return data
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    print(f"❌ All attempts failed for {symbol}")
                    return None
        
        return None
    
    def _fetch_from_binance(self, symbol, days):
        """Fetch data from Binance API"""
        try:
            binance_symbol = self.binance_pairs.get(symbol)
            if not binance_symbol:
                return None
            
            url = f"{self.binance_base}/klines"
            params = {
                'symbol': binance_symbol,
                'interval': '1d',
                'limit': min(days, 100)  # Limit for cloud performance
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            df['price'] = pd.to_numeric(df['close'])
            
            # Limit data points for performance
            if len(df) > 1000:
                df = df.tail(1000)
            
            print(f"✅ Successfully fetched {len(df)} records from Binance for {symbol}")
            return df[['price']]
            
        except Exception as e:
            print(f"Binance error for {symbol}: {e}")
            return None
    
    def _fetch_from_coingecko(self, symbol, days=30):
        """Fetch data from CoinGecko API"""
        try:
            coin_id = self.coin_ids.get(symbol)
            if not coin_id:
                return None
            
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90),  # Limit for cloud performance
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            # Limit data points for performance
            if len(df) > 1000:
                df = df.tail(1000)
            
            print(f"✅ Successfully fetched {len(df)} records from CoinGecko for {symbol}")
            return df
            
        except Exception as e:
            print(f"CoinGecko error for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price with cloud optimizations"""
        cache_key = f"current_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        # Check cache first (shorter cache for current prices)
        if cache_key in self.cache:
            cache_time = self.cache[cache_key]['timestamp']
            current_time = datetime.now()
            if (current_time - cache_time).total_seconds() < 60:  # 1 minute cache
                return self.cache[cache_key]['data']
        
        # Fetch fresh data
        try:
            # Try Binance first
            binance_symbol = self.binance_pairs.get(symbol)
            if binance_symbol:
                url = f"{self.binance_base}/ticker/price"
                params = {'symbol': binance_symbol}
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                result = {symbol: {'usd': float(data['price'])}
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
                return result
            
            # Fallback to CoinGecko
            coin_id = self.coin_ids.get(symbol)
            if coin_id:
                url = f"{self.coingecko_base}/simple/price"
                params = {
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                }
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                result = {symbol: {'usd': float(data[coin_id]['usd'])}
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now()
                }
                return result
            
        except Exception as e:
            print(f"Current price fetch failed for {symbol}: {e}")
            return None
    
    def test_connectivity(self):
        """Test API connectivity"""
        results = {
            'binance': False,
            'coingecko': False,
            'internet': False
        }
        
        # Test internet connectivity
        try:
            response = requests.get('https://httpbin.org/get', timeout=5)
            if response.status_code == 200:
                results['internet'] = True
        except:
            results['internet'] = False
        
        # Test Binance API
        try:
            response = requests.get(f"{self.binance_base}/ping", timeout=5)
            if response.status_code == 200:
                results['binance'] = True
        except:
            results['binance'] = False
        
        # Test CoinGecko API
        try:
            response = requests.get(f"{self.coingecko_base}/ping", timeout=5)
            if response.status_code == 200:
                results['coingecko'] = True
        except:
            results['coingecko'] = False
        
        return results
    
    def get_status_report(self):
        """Get detailed status report"""
        connectivity = self.test_connectivity()
        
        cache_size = len(self.cache)
        cache_memory = len(json.dumps(self.cache)) / 1024  # KB
        
        return {
            'connectivity': connectivity,
            'cache_size': cache_size,
            'cache_memory_kb': cache_memory,
            'cache_timeout': f"{self.cache_timeout}s",
            'max_retries': self.max_retries,
            'timeout': f"{self.timeout}s",
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
