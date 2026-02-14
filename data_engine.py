import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import numpy as np
from scipy import stats
from functools import lru_cache
import gc

class DataEngine:
    """Background data acquisition engine - runs silently"""
    
    def __init__(self):
        self.cryptocurrencies = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
            {"id": "solana", "symbol": "SOL", "name": "Solana"},
            {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
            {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"}
        ]
        self.last_update = None
        self.data_cache = {}
        self.status = "idle"  # idle, syncing, error, ready
    
    def get_data_status(self):
        """Get current data engine status"""
        if self.last_update:
            time_diff = datetime.now() - self.last_update
            if time_diff.total_seconds() < 60:
                self.status = "ready"
            else:
                self.status = "stale"
        return self.status
    
    def sync_data(self, force=False):
        """Sync data from multiple sources"""
        if not force and self.get_data_status() == "ready":
            return self.data_cache
        
        self.status = "syncing"
        
        # Try multiple sources
        sources = [
            self._fetch_coingecko,
            self._fetch_binance,
            self._fetch_cryptocompare
        ]
        
        for source_func in sources:
            try:
                data = source_func()
                if data:
                    self.data_cache = data
                    self.last_update = datetime.now()
                    self.status = "ready"
                    return data
            except Exception as e:
                print(f"Source {source_func.__name__} failed: {e}")
                continue
        
        self.status = "error"
        return None
    
    def _fetch_coingecko(self):
        """Fetch from CoinGecko API"""
        coin_ids = [crypto["id"] for crypto in self.cryptocurrencies]
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        price_data = response.json()
        
        data = {}
        for crypto in self.cryptocurrencies:
            if crypto["id"] in price_data:
                info = price_data[crypto["id"]]
                data[crypto["symbol"]] = {
                    "name": crypto["name"],
                    "symbol": crypto["symbol"],
                    "price": info["usd"],
                    "change_24h": info.get("usd_24h_change", 0),
                    "volume_24h": info.get("usd_24h_vol", 0),
                    "timestamp": datetime.now()
                }
        return data
    
    def _fetch_binance(self):
        """Fetch from Binance API"""
        data = {}
        binance_pairs = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT", 
            "SOL": "SOLUSDT",
            "ADA": "ADAUSDT",
            "DOGE": "DOGEUSDT"
        }
        
        for crypto in self.cryptocurrencies:
            symbol = crypto["symbol"]
            if symbol in binance_pairs:
                try:
                    url = "https://api.binance.com/api/v3/ticker/24hr"
                    params = {'symbol': binance_pairs[symbol]}
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    ticker_data = response.json()
                    
                    data[symbol] = {
                        "name": crypto["name"],
                        "symbol": crypto["symbol"],
                        "price": float(ticker_data['lastPrice']),
                        "change_24h": float(ticker_data['priceChangePercent']),
                        "volume_24h": float(ticker_data['volume']),
                        "timestamp": datetime.now()
                    }
                except Exception as e:
                    print(f"Binance error for {crypto['name']}: {e}")
                    continue
        
        return data if len(data) > 0 else None
    
    def _fetch_cryptocompare(self):
        """Fetch from CryptoCompare API"""
        data = {}
        symbols = {
            "BTC": "BTC",
            "ETH": "ETH",
            "SOL": "SOL", 
            "ADA": "ADA",
            "DOGE": "DOGE"
        }
        
        for crypto in self.cryptocurrencies:
            symbol = crypto["symbol"]
            if symbol in symbols:
                try:
                    url = "https://min-api.cryptocompare.com/data/price"
                    params = {
                        'fsym': symbols[symbol],
                        'tsyms': 'USD'
                    }
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    price_data = response.json()
                    
                    data[symbol] = {
                        "name": crypto["name"],
                        "symbol": crypto["symbol"],
                        "price": price_data["USD"],
                        "change_24h": 0,
                        "volume_24h": 0,
                        "timestamp": datetime.now()
                    }
                except Exception as e:
                    print(f"CryptoCompare error for {crypto['name']}: {e}")
                    continue
        
        return data if len(data) > 0 else None
    
    @lru_cache(maxsize=32)
    def get_historical_data(self, symbol, days=30):
        """Get historical data for a symbol - tries Binance first, then CoinGecko"""
        # Implement caching to reduce API calls
        cache_key = f"{symbol}_{days}"
        
        # Try Binance first
        binance_pairs = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT", 
            "SOL": "SOLUSDT",
            "ADA": "ADAUSDT",
            "DOGE": "DOGEUSDT"
        }
        
        if symbol in binance_pairs:
            try:
                print(f"Trying Binance for {symbol}...")
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    'symbol': binance_pairs[symbol],
                    'interval': '1d',
                    'limit': min(days, 100)  # Limit to 100 days for performance
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data:
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
                    
                    print(f"Successfully fetched {len(df)} records from Binance for {symbol}")
                    return df[['price']]
                    
            except Exception as e:
                print(f"Binance failed for {symbol}: {e}")
        
        # Fallback to CoinGecko
        try:
            print(f"Trying CoinGecko for {symbol}...")
            crypto = next((c for c in self.cryptocurrencies if c["symbol"] == symbol), None)
            if not crypto:
                return None
            
            url = f"https://api.coingecko.com/api/v3/coins/{crypto['id']}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90),  # Limit to 90 days for performance
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
            
            # Limit data points for performance
            if len(df) > 1000:
                df = df.tail(1000)
            
            print(f"Successfully fetched {len(df)} records from CoinGecko for {symbol}")
            return df
        except Exception as e:
            print(f"CoinGecko failed for {symbol}: {e}")
            return None
    
    def calculate_log_returns(self, price_data):
        """Calculate daily log returns - optimized for performance"""
        if price_data is None or len(price_data) < 2:
            return None
        
        # Use numpy for faster calculations
        prices = price_data['price'].values
        
        # Vectorized log returns calculation
        log_returns = np.log(prices[1:] / prices[:-1])
        simple_returns = np.diff(prices) / prices[:-1]
        
        # Create DataFrame with optimized memory usage
        df = pd.DataFrame({
            'log_return': log_returns,
            'simple_return': simple_returns
        }, index=price_data.index[1:])
        
        # Limit data points for performance
        if len(df) > 1000:
            df = df.tail(1000)
        
        return df
    
    def calculate_volatility(self, returns_data, annualize=True):
        """Calculate daily and annualized volatility"""
        if returns_data is None or len(returns_data) == 0:
            return None
        
        log_returns = returns_data['log_return']
        
        # Daily volatility (standard deviation of log returns)
        daily_vol = log_returns.std()
        
        # Annualized volatility (assuming 365 trading days for crypto)
        if annualize:
            annual_vol = daily_vol * np.sqrt(365)
        else:
            annual_vol = daily_vol
        
        return {
            'daily_volatility': daily_vol,
            'annualized_volatility': annual_vol,
            'volatility_data': log_returns
        }
    
    def calculate_sharpe_ratio(self, returns_data, risk_free_rate=0.02):
        """Calculate Sharpe ratio (annualized)"""
        if returns_data is None or len(returns_data) == 0:
            return None
        
        log_returns = returns_data['log_return']
        
        # Annualized return
        annual_return = log_returns.mean() * 365
        
        # Annualized volatility
        annual_vol = log_returns.std() * np.sqrt(365)
        
        # Sharpe ratio
        if annual_vol == 0:
            sharpe_ratio = 0
        else:
            sharpe_ratio = (annual_return - risk_free_rate) / annual_vol
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'risk_free_rate': risk_free_rate
        }
    
    def calculate_beta(self, asset_returns, benchmark_returns):
        """Calculate beta coefficient vs benchmark"""
        if asset_returns is None or benchmark_returns is None:
            return None
        
        if len(asset_returns) != len(benchmark_returns):
            return None
        
        # Remove any NaN values
        valid_mask = ~(np.isnan(asset_returns) | np.isnan(benchmark_returns))
        asset_clean = asset_returns[valid_mask]
        benchmark_clean = benchmark_returns[valid_mask]
        
        if len(asset_clean) < 2:
            return None
        
        # Calculate beta using covariance/variance formula
        covariance = np.cov(asset_clean, benchmark_clean)[0][1]
        benchmark_variance = np.var(benchmark_clean)
        
        if benchmark_variance == 0:
            return 0
        
        beta = covariance / benchmark_variance
        
        # Also calculate correlation and R-squared
        correlation = np.corrcoef(asset_clean, benchmark_clean)[0][1]
        r_squared = correlation ** 2 if not np.isnan(correlation) else 0
        
        return {
            'beta': beta,
            'correlation': correlation,
            'r_squared': r_squared,
            'covariance': covariance,
            'benchmark_variance': benchmark_variance
        }
    
    def calculate_moving_averages(self, price_data, windows=[7, 14, 30]):
        """Calculate moving averages for specified windows"""
        if price_data is None or len(price_data) == 0:
            return None
        
        df = price_data.copy()
        
        for window in windows:
            if len(df) >= window:
                df[f'MA_{window}'] = df['price'].rolling(window=window).mean()
                df[f'Price_vs_MA_{window}'] = (df['price'] / df[f'MA_{window}'] - 1) * 100
        
        return df
    
    def calculate_rolling_volatility(self, returns_data, windows=[7, 14, 30]):
        """Calculate rolling window volatility"""
        if returns_data is None or len(returns_data) == 0:
            return None
        
        df = returns_data.copy()
        log_returns = df['log_return']
        
        for window in windows:
            if len(df) >= window:
                rolling_vol = log_returns.rolling(window=window).std()
                df[f'rolling_vol_{window}'] = rolling_vol
                df[f'rolling_vol_annual_{window}'] = rolling_vol * np.sqrt(365)
        
        return df
    
    def generate_metrics_table(self, benchmark_symbol='BTC'):
        """Generate comprehensive metrics table for all assets"""
        metrics_data = []
        
        # Get benchmark data first
        benchmark_data = self.get_historical_data(benchmark_symbol, days=90)
        benchmark_returns = None
        
        if benchmark_data is not None:
            benchmark_returns = self.calculate_log_returns(benchmark_data)
            print(f"✅ Benchmark {benchmark_symbol} data loaded")
        else:
            print(f"❌ Failed to load benchmark {benchmark_symbol} data")
        
        for crypto in self.cryptocurrencies:
            symbol = crypto["symbol"]
            print(f"Processing {symbol}...")
            
            # Get historical data
            price_data = self.get_historical_data(symbol, days=90)
            
            if price_data is None:
                print(f"❌ No price data for {symbol}")
                continue
            
            # Calculate returns
            returns_data = self.calculate_log_returns(price_data)
            
            if returns_data is None:
                print(f"❌ No returns data for {symbol}")
                continue
            
            # Calculate metrics
            volatility = self.calculate_volatility(returns_data)
            sharpe = self.calculate_sharpe_ratio(returns_data)
            
            # Calculate beta if we have benchmark data
            beta_metrics = None
            if benchmark_returns is not None and symbol != benchmark_symbol:
                beta_metrics = self.calculate_beta(
                    returns_data['log_return'].values,
                    benchmark_returns['log_return'].values
                )
            
            # Current price and basic stats
            current_price = price_data['price'].iloc[-1]
            price_change_24h = returns_data['simple_return'].iloc[-1] * 100
            
            # Compile metrics
            metrics = {
                'symbol': symbol,
                'name': crypto['name'],
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'daily_volatility': volatility['daily_volatility'] if volatility else 0,
                'annualized_volatility': volatility['annualized_volatility'] if volatility else 0,
                'sharpe_ratio': sharpe['sharpe_ratio'] if sharpe else 0,
                'annual_return': sharpe['annual_return'] if sharpe else 0,
                'beta': beta_metrics['beta'] if beta_metrics else 1.0,
                'correlation_vs_btc': beta_metrics['correlation'] if beta_metrics else 0,
                'r_squared': beta_metrics['r_squared'] if beta_metrics else 0,
                'data_points': len(returns_data),
                'last_updated': datetime.now()
            }
            
            metrics_data.append(metrics)
            print(f"✅ {symbol} metrics calculated")
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame(metrics_data)
        
        if len(metrics_df) > 0:
            # Sort by Sharpe ratio (descending)
            metrics_df = metrics_df.sort_values('sharpe_ratio', ascending=False)
            
            # Add risk classification
            metrics_df['risk_level'] = metrics_df['annualized_volatility'].apply(self._classify_risk)
            
            print(f"✅ Metrics table generated with {len(metrics_df)} assets")
        else:
            print("❌ No metrics data available")
        
        return metrics_df
    
    def _classify_risk(self, volatility):
        """Classify risk level based on volatility"""
        if volatility < 0.3:  # < 30%
            return "Low Risk"
        elif volatility < 0.6:  # 30-60%
            return "Medium Risk"
        elif volatility < 1.0:  # 60-100%
            return "High Risk"
        else:  # > 100%
            return "Very High Risk"
    
    def prepare_visualization_data(self, symbols=None, days=90):
        """Prepare intermediate dataset for visualization"""
        if symbols is None:
            symbols = [crypto["symbol"] for crypto in self.cryptocurrencies]
        
        viz_data = {}
        
        for symbol in symbols:
            print(f"Preparing viz data for {symbol}...")
            
            # Get historical data using the updated method
            price_data = self.get_historical_data(symbol, days)
            
            if price_data is None:
                print(f"❌ No price data for {symbol}")
                continue
            
            # Calculate all metrics
            returns_data = self.calculate_log_returns(price_data)
            if returns_data is None:
                print(f"❌ No returns data for {symbol}")
                continue
            
            volatility = self.calculate_volatility(returns_data)
            sharpe = self.calculate_sharpe_ratio(returns_data)
            
            # Add moving averages
            price_with_ma = self.calculate_moving_averages(price_data)
            
            # Add rolling volatility
            returns_with_rolling = self.calculate_rolling_volatility(returns_data)
            
            # Get crypto info
            crypto = next((c for c in self.cryptocurrencies if c["symbol"] == symbol), None)
            
            viz_data[symbol] = {
                'price_data': price_with_ma,
                'returns_data': returns_with_rolling,
                'current_metrics': {
                    'volatility': volatility,
                    'sharpe_ratio': sharpe,
                    'current_price': price_data['price'].iloc[-1],
                    'latest_return': returns_data['simple_return'].iloc[-1]
                },
                'metadata': {
                    'name': crypto['name'] if crypto else symbol,
                    'symbol': symbol,
                    'data_points': len(returns_data),
                    'date_range': {
                        'start': price_data.index[0],
                        'end': price_data.index[-1]
                    }
                }
            }
            print(f"✅ {symbol} viz data prepared")
        
        return viz_data
