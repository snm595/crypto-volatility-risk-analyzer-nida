# Crypto Volatility & Risk Analyzer

A comprehensive Streamlit application for analyzing cryptocurrency volatility and risk using real-time data from CoinGecko and Binance APIs.

## Features

### 🔐 Dynamic Authentication System
- **User Registration**: Create new accounts with username, email, and password
- **Secure Login**: Password hashing with SHA-256
- **Session Management**: Persistent user sessions
- **User Profiles**: Display user information in dashboard sidebar
- **Account Validation**: Email validation, password strength requirements

### 📊 Interactive Dashboard
- Real-time cryptocurrency price data
- Volatility analysis and risk assessment
- Interactive charts using Plotly
- Risk gauge visualization
- Detailed statistics and metrics
- User profile sidebar with account information

### 🎯 Key Functionality
- **Search**: Search for any cryptocurrency
- **Analysis**: Analyze volatility over different time periods (7, 30, 90 days)
- **Risk Assessment**: Automatic risk level classification (Low, Medium, High)
- **Visualizations**: Price charts, volatility trends, and risk indicators
- **Metrics**: Current price, 24h changes, volatility metrics

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crypto-volatility-risk-analyzer-nida
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

### Registration & Login
1. **Create Account**: Click "Register" to create a new account
   - Enter username (min 3 characters)
   - Enter valid email address
   - Create password (min 6 characters)
   - Confirm password
2. **Login**: Use your credentials to access the dashboard

### Dashboard
1. Search for a cryptocurrency or select from popular options
2. Choose time period (7, 30, or 90 days)
3. Click "Analyze" to get comprehensive risk analysis
4. View interactive charts and risk assessments
5. Check your user profile in the sidebar

### Default Accounts (for testing)
- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`

## API Integration

### CoinGecko API
- Real-time price data
- Historical price charts
- Market statistics

### Binance API
- Alternative data source
- Kline/candlestick data
- Trading volume information

## Risk Assessment

The application calculates risk based on volatility metrics:

- **🟢 Low Risk**: Volatility < 2%
- **🟡 Low-Medium Risk**: Volatility 2-4%
- **🟠 Medium Risk**: Volatility 4-8%
- **🔴 High Risk**: Volatility > 8%

## Technical Details

### Volatility Calculation
- Daily returns calculation
- Rolling standard deviation (14-day window)
- Statistical analysis and trend identification

### Data Processing
- Pandas for data manipulation
- NumPy for numerical calculations
- Plotly for interactive visualizations

## File Structure

```
crypto-volatility-risk-analyzer-nida/
├── app.py              # Main application entry point
├── auth.py             # Authentication system
├── dashboard.py        # Main dashboard functionality
├── crypto_api.py       # API integration and data processing
├── requirements.txt    # Python dependencies
├── users.json          # User credentials (auto-generated)
└── README.md          # This file
```

## Dependencies

- `streamlit`: Web application framework
- `requests`: HTTP client for API calls
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `plotly`: Interactive charts
- `yfinance`: Financial data (backup source)

## Security Notes

- Passwords are hashed using SHA-256
- Session state management for authentication
- No sensitive data stored in plain text
- API rate limiting implemented

## Future Enhancements

- Portfolio tracking
- Price alerts
- Advanced technical indicators
- Machine learning predictions
- Multi-user support with roles
- Database integration for historical data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
