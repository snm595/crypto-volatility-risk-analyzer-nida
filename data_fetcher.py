import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests
from crypto_api import CryptoAPI
from data_storage import DataStorage

class DataFetcher:
    def __init__(self):
        self.api = CryptoAPI()
        self.storage = DataStorage()
        self.cryptocurrencies = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
            {"id": "solana", "symbol": "SOL", "name": "Solana"},
            {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
            {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"}
        ]
    
    def fetch_current_prices(self):
        """Fetch current prices from multiple sources - real-time only"""
        data = []
        
        # Try multiple sources for real-time data
        sources = [
            self._fetch_from_coingecko,
            self._fetch_from_binance,
            self._fetch_from_alternative_source
        ]
        
        for source_func in sources:
            try:
                result = source_func()
                if result:
                    data = result
                    break
            except Exception as e:
                print(f"Source {source_func.__name__} failed: {e}")
                continue
        
        if not data:
            st.error("All real-time data sources are currently unavailable. Please try again in 2-5 minutes.")
            return None
        
        df = pd.DataFrame(data)
        return df
    
    def _fetch_from_coingecko(self):
        """Fetch from CoinGecko API"""
        coin_ids = [crypto["id"] for crypto in self.cryptocurrencies]
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        price_data = response.json()
        
        data = []
        for crypto in self.cryptocurrencies:
            if crypto["id"] in price_data:
                info = price_data[crypto["id"]]
                data.append({
                    "Cryptocurrency": crypto["name"],
                    "Symbol": crypto["symbol"],
                    "Price (USD)": info["usd"],
                    "24h Change": info.get("usd_24h_change", 0),
                    "Volume (24h)": info.get("usd_24h_vol", 0),
                    "Last Updated": datetime.now()
                })
        return data
    
    def _fetch_from_binance(self):
        """Fetch from Binance API"""
        data = []
        binance_pairs = {
            "bitcoin": "BTCUSDT",
            "ethereum": "ETHUSDT", 
            "solana": "SOLUSDT",
            "cardano": "ADAUSDT",
            "dogecoin": "DOGEUSDT"
        }
        
        for crypto in self.cryptocurrencies:
            if crypto["id"] in binance_pairs:
                symbol = binance_pairs[crypto["id"]]
                try:
                    url = f"https://api.binance.com/api/v3/ticker/24hr"
                    params = {'symbol': symbol}
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    ticker_data = response.json()
                    
                    data.append({
                        "Cryptocurrency": crypto["name"],
                        "Symbol": crypto["symbol"],
                        "Price (USD)": float(ticker_data['lastPrice']),
                        "24h Change": float(ticker_data['priceChangePercent']),
                        "Volume (24h)": float(ticker_data['volume']),
                        "Last Updated": datetime.now()
                    })
                except Exception as e:
                    print(f"Binance error for {crypto['name']}: {e}")
                    continue
        
        return data if len(data) > 0 else None
    
    def _fetch_from_alternative_source(self):
        """Fetch from alternative free API"""
        try:
            # Using CryptoCompare API as backup
            data = []
            symbols = {
                "bitcoin": "BTC",
                "ethereum": "ETH",
                "solana": "SOL", 
                "cardano": "ADA",
                "dogecoin": "DOGE"
            }
            
            for crypto in self.cryptocurrencies:
                if crypto["id"] in symbols:
                    symbol = symbols[crypto["id"]]
                    url = f"https://min-api.cryptocompare.com/data/price"
                    params = {
                        'fsym': symbol,
                        'tsyms': 'USD'
                    }
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    price_data = response.json()
                    
                    data.append({
                        "Cryptocurrency": crypto["name"],
                        "Symbol": crypto["symbol"],
                        "Price (USD)": price_data["USD"],
                        "24h Change": 0,  # Basic price API doesn't include 24h change
                        "Volume (24h)": 0,
                        "Last Updated": datetime.now()
                    })
            
            return data if len(data) > 0 else None
        except Exception as e:
            print(f"Alternative source error: {e}")
            return None
    
    def fetch_historical_data(self, days=7):
        """Fetch historical price data for trend analysis - optimized"""
        historical_data = {}
        
        # Only fetch historical data if we don't have recent cached data
        for crypto in self.cryptocurrencies:
            try:
                # Check if we have recent cached data
                cached_data = self.storage.load_from_csv(f"{crypto['symbol']}_historical")
                if cached_data is not None and len(cached_data) > 0:
                    # Check if data is recent (within last hour)
                    last_update = cached_data.index[-1]
                    if (datetime.now() - last_update).total_seconds() < 3600:  # 1 hour
                        historical_data[crypto["symbol"]] = cached_data
                        continue
                
                # Fetch new data if cache is old or doesn't exist
                df = self.api.get_coingecko_price_history(crypto["id"], days)
                if df is not None:
                    historical_data[crypto["symbol"]] = df
                    # Save to storage
                    self.storage.save_to_csv(df, f"{crypto['symbol']}_historical")
            except Exception as e:
                print(f"Error fetching historical data for {crypto['name']}: {e}")
                # Try to load from cache as fallback
                cached_data = self.storage.load_from_csv(f"{crypto['symbol']}_historical")
                if cached_data is not None:
                    historical_data[crypto["symbol"]] = cached_data
        
        return historical_data
    
    def create_price_trend_chart(self, historical_data):
        """Create 7-day price trend chart"""
        fig = go.Figure()
        
        for symbol, df in historical_data.items():
            if df is not None and len(df) > 0:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['price'],
                    mode='lines',
                    name=symbol,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="7-Day Price Trend",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    def verify_api_connectivity(self):
        """Verify API connectivity and data consistency"""
        results = {
            "coingecko": False,
            "binance": False,
            "data_consistency": False,
            "last_check": datetime.now()
        }
        
        # Test CoinGecko API
        try:
            bitcoin_data = self.api.get_current_price("bitcoin")
            if bitcoin_data and "bitcoin" in bitcoin_data:
                results["coingecko"] = True
        except Exception as e:
            print(f"CoinGecko API test failed: {e}")
        
        # Test Binance API
        try:
            binance_data = self.api.get_binance_klines("BTCUSDT", "1d", 1)
            if binance_data is not None:
                results["binance"] = True
        except Exception as e:
            print(f"Binance API test failed: {e}")
        
        # Test data consistency
        try:
            current_prices = self.fetch_current_prices()
            if len(current_prices) == len(self.cryptocurrencies):
                results["data_consistency"] = True
        except Exception as e:
            print(f"Data consistency test failed: {e}")
        
        return results
    
    def display_data_fetcher_ui(self):
        """Display the Data Fetcher component UI"""
        st.markdown("### 🔄 Crypto Data Fetcher")
        
        # Initialize session state for data
        if 'crypto_data' not in st.session_state:
            st.session_state.crypto_data = None
        if 'last_updated' not in st.session_state:
            st.session_state.last_updated = None
        if 'historical_data' not in st.session_state:
            st.session_state.historical_data = None
        
        # Refresh button with options
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("🔄 Refresh Data", type="primary"):
                with st.spinner("Fetching real-time data..."):
                    # Fetch current prices (real-time only)
                    st.session_state.crypto_data = self.fetch_current_prices()
                    st.session_state.last_updated = datetime.now()
                    
                    if st.session_state.crypto_data is not None:
                        # Fetch historical data (only if needed)
                        st.session_state.historical_data = self.fetch_historical_data(7)
                        st.success("Real-time data refreshed successfully!")
                    else:
                        st.error("Failed to fetch real-time data. Please wait a few minutes before retrying.")
        
        with col2:
            if st.button("⚡ Quick Refresh", type="secondary"):
                with st.spinner("Quick refresh..."):
                    # Only refresh current prices (real-time only)
                    st.session_state.crypto_data = self.fetch_current_prices()
                    st.session_state.last_updated = datetime.now()
                    
                    if st.session_state.crypto_data is not None:
                        st.success("Real-time prices updated!")
                    else:
                        st.error("Failed to fetch real-time data. Please wait a few minutes before retrying.")
        
        with col3:
            if st.session_state.last_updated:
                time_diff = datetime.now() - st.session_state.last_updated
                seconds_ago = int(time_diff.total_seconds())
                if seconds_ago < 60:
                    st.markdown(f"**{seconds_ago}s ago**")
                else:
                    minutes_ago = seconds_ago // 60
                    st.markdown(f"**{minutes_ago}m ago**")
            else:
                st.markdown("**Never**")
        
        # Rate limit warning
        st.info("🔄 **Multi-Source Data**: App tries CoinGecko → Binance → CryptoCompare APIs for real-time data. If all sources are rate limited, please wait 2-5 minutes before refreshing.")
        
        # Display current prices table
        if st.session_state.crypto_data is not None:
            st.markdown("#### 📊 Current Prices")
            
            # Format the data for display
            display_df = st.session_state.crypto_data.copy()
            
            # Check if the expected columns exist
            if "Price (USD)" in display_df.columns:
                display_df["Price (USD)"] = display_df["Price (USD)"].apply(lambda x: f"${x:,.2f}")
            if "24h Change" in display_df.columns:
                display_df["24h Change"] = display_df["24h Change"].apply(lambda x: f"{x:+.2f}%")
            if "Volume (24h)" in display_df.columns:
                display_df["Volume (24h)"] = display_df["Volume (24h)"].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
            
            # Remove the Last Updated column from display if it exists
            if "Last Updated" in display_df.columns:
                display_df = display_df.drop("Last Updated", axis=1)
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No data available. Please refresh to get real-time prices.")
        
        # Display 7-day price trend chart
        if st.session_state.historical_data is not None:
            st.markdown("#### 📈 7-Day Price Trend")
            chart = self.create_price_trend_chart(st.session_state.historical_data)
            st.plotly_chart(chart, use_container_width=True)

def display_milestone_1():
    """Display Milestone 1: Data Acquisition dashboard"""
    st.markdown("# 🎯 Milestone 1: Data Acquisition")
    
    # Initialize and display data fetcher
    fetcher = DataFetcher()
    fetcher.display_data_fetcher_ui()
