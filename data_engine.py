import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import numpy as np

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
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data for a symbol"""
        try:
            crypto = next((c for c in self.cryptocurrencies if c["symbol"] == symbol), None)
            if not crypto:
                return None
            
            url = f"https://api.coingecko.com/api/v3/coins/{crypto['id']}/market_chart"
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
            print(f"Historical data error: {e}")
            return None
