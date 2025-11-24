import yfinance as yf
import pandas as pd
import numpy as np

class PortfolioManager:
    """
    Handles data fetching and portfolio calculations.
    """
    def __init__(self):
        self.data = pd.DataFrame()

    def fetch_data(self, tickers, period="1y"):
        """
        Fetches historical data for the given tickers using yfinance.
        """
        if not tickers:
            return None
        
        # Download adjusted close prices
        # auto_adjust=True ensures we account for dividends/splits
        df = yf.download(tickers, period=period, auto_adjust=True)['Close']
        
        # Handle single ticker case (returns Series instead of DataFrame)
        if len(tickers) == 1:
            df = df.to_frame(name=tickers[0])
            
        self.data = df
        return self.data

    def get_correlation_matrix(self):
        """
        Returns the correlation matrix of daily returns.
        """
        if self.data.empty:
            return pd.DataFrame()
        
        # Calculate daily percentage change
        returns = self.data.pct_change().dropna()
        return returns.corr()

    def simulate_portfolio(self, weights):
        """
        Calculates portfolio performance based on user-defined weights.
        Returns a DataFrame with 'Portfolio' value and individual normalized assets.
        """
        if self.data.empty:
            return None

        # Normalize data to start at 100 (base 100) for comparison
        normalized_data = self.data / self.data.iloc[0] * 100
        
        # Calculate weighted portfolio value
        # weights dict example: {'AAPL': 0.5, 'MSFT': 0.5}
        portfolio_value = pd.Series(0, index=normalized_data.index)
        
        for ticker, weight in weights.items():
            if ticker in normalized_data.columns:
                portfolio_value += normalized_data[ticker] * weight

        # Combine for visualization
        result_df = normalized_data.copy()
        result_df['Portfolio'] = portfolio_value
        
        return result_df

    def get_portfolio_metrics(self, portfolio_series):
        """
        Calculates basic risk/return metrics for the portfolio.
        """
        # Daily returns
        returns = portfolio_series.pct_change().dropna()
        
        # Total Cumulative Return
        total_return = (portfolio_series.iloc[-1] - portfolio_series.iloc[0]) / portfolio_series.iloc[0]
        
        # Annualized Volatility (assuming 252 trading days)
        volatility = returns.std() * np.sqrt(252)
        
        return {
            "Total Return": total_return,
            "Volatility (Ann.)": volatility
        }