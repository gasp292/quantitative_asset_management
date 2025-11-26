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
        
        # Fetch data using Yahoo Finance
        # auto_adjust=True handles dividends/splits correctly
        try:
            df = yf.download(tickers, period=period, auto_adjust=True)['Close']
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
        
        # Handle single ticker case (returns Series instead of DataFrame)
        if len(tickers) == 1:
            df = df.to_frame(name=tickers[0])
            
        # Clean data: Fill weekends/holidays to avoid gaps (NaNs)
        # Forward fill first (copy Friday to Saturday), then Backward fill
        df = df.ffill().bfill()
        
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

    def simulate_portfolio(self, weights, rebalance=False):
        """
        Calculates portfolio performance.
        If rebalance=True, weights are reset to target allocation at the start of each month.
        """
        if self.data.empty:
            return None

        # Normalize data to start at 100 (base 100) for comparison
        normalized_data = self.data / self.data.iloc[0] * 100
        
        # STRATEGY 1: BUY AND HOLD (No Rebalancing) 
        if not rebalance:
            # Simple weighted sum. Returns run freely.
            portfolio_value = pd.Series(0.0, index=normalized_data.index)
            for ticker, weight in weights.items():
                if ticker in normalized_data.columns:
                    portfolio_value += normalized_data[ticker] * weight
            
            result_df = normalized_data.copy()
            result_df['Portfolio'] = portfolio_value
            return result_df

        # STRATEGY 2: MONTHLY REBALANCING 
        else:
            # We calculate day by day to apply rebalancing logic
            daily_returns = self.data.pct_change().fillna(0)
            
            # Start at 100
            portfolio_value = pd.Series(100.0, index=daily_returns.index)
            
            # Initial allocation of money (e.g., 25€ in each stock)
            current_positions = {t: 100.0 * w for t, w in weights.items()}
            
            dates = daily_returns.index
            for i in range(1, len(dates)):
                current_date = dates[i]
                prev_date = dates[i-1]
                
                # Check for new month -> TRIGGER REBALANCE
                if current_date.month != prev_date.month:
                    total_value = sum(current_positions.values())
                    # Reset positions to target weights (selling winners, buying losers)
                    current_positions = {t: total_value * w for t, w in weights.items()}
                
                # Apply daily return to positions
                daily_total = 0
                for ticker in weights.keys():
                    if ticker in daily_returns.columns:
                        ret = daily_returns.at[current_date, ticker]
                        current_positions[ticker] *= (1 + ret)
                        daily_total += current_positions[ticker]
                
                portfolio_value.at[current_date] = daily_total

            result_df = normalized_data.copy()
            result_df['Portfolio'] = portfolio_value
            return result_df

    def get_portfolio_metrics(self, weights, portfolio_series):
        """
        Calculates risk/return metrics AND Diversification Effect.
        """
        # 1. Standard Metrics
        ret_port = portfolio_series.pct_change().dropna()
        if portfolio_series.iloc[0] == 0: 
            total_return = 0
        else:
            total_return = (portfolio_series.iloc[-1] - portfolio_series.iloc[0]) / portfolio_series.iloc[0]
            
        vol_port = ret_port.std() * np.sqrt(252) # Annualized Volatility
        
        # 2. Diversification Effect (The "Free Lunch" of Finance)
        # Compare "Sum of Weighted Volatilities" vs "Portfolio Volatility"
        individual_rets = self.data.pct_change().dropna()
        individual_vols = individual_rets.std() * np.sqrt(252)
        
        weighted_vol_sum = 0
        for ticker, weight in weights.items():
            if ticker in individual_vols.index:
                weighted_vol_sum += individual_vols[ticker] * weight
        
        # If result > 0, diversification is working (risk is reduced)
        diversification_benefit = weighted_vol_sum - vol_port

        return {
            "Total Return": total_return,
            "Volatility (Ann.)": vol_port,
            "Diversification Effect": diversification_benefit
        }