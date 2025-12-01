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
        
        try:
            # Download adjusted close prices
            df = yf.download(tickers, period=period, auto_adjust=True)['Close']
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
        
        # Handle single ticker case
        if len(tickers) == 1:
            df = df.to_frame(name=tickers[0])
            
        # Clean data (Forward fill then Backward fill)
        df = df.ffill().bfill()
        
        self.data = df
        return self.data

    def get_correlation_matrix(self):
        """
        Returns the correlation matrix of daily returns.
        """
        if self.data.empty:
            return pd.DataFrame()
        
        returns = self.data.pct_change().dropna()
        return returns.corr()

    def simulate_portfolio(self, weights, rebalance_freq="None"):
        """
        Calculates portfolio performance with advanced rebalancing options.
        rebalance_freq: "None", "Monthly", "Quarterly", "Yearly"
        """
        if self.data.empty:
            return None

        # Normalize data to start at 100
        normalized_data = self.data / self.data.iloc[0] * 100
        
        # --- STRATEGY: BUY AND HOLD (No Rebalancing) ---
        if rebalance_freq == "None" or rebalance_freq is None or rebalance_freq is False:
            portfolio_value = pd.Series(0.0, index=normalized_data.index)
            for ticker, weight in weights.items():
                if ticker in normalized_data.columns:
                    portfolio_value += normalized_data[ticker] * weight
            
            result_df = normalized_data.copy()
            result_df['Portfolio'] = portfolio_value
            return result_df

        # --- STRATEGY: PERIODIC REBALANCING ---
        else:
            daily_returns = self.data.pct_change().fillna(0)
            portfolio_value = pd.Series(100.0, index=daily_returns.index)
            current_positions = {t: 100.0 * w for t, w in weights.items()}
            
            dates = daily_returns.index
            for i in range(1, len(dates)):
                current_date = dates[i]
                prev_date = dates[i-1]
                
                # Check Rebalancing Trigger
                should_rebalance = False
                if rebalance_freq == "Monthly" and current_date.month != prev_date.month:
                    should_rebalance = True
                elif rebalance_freq == "Quarterly" and current_date.quarter != prev_date.quarter:
                    should_rebalance = True
                elif rebalance_freq == "Yearly" and current_date.year != prev_date.year:
                    should_rebalance = True
                
                # Apply Rebalancing
                if should_rebalance:
                    total_value = sum(current_positions.values())
                    current_positions = {t: total_value * w for t, w in weights.items()}
                
                # Apply Daily Performance
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
        if len(portfolio_series) > 0 and portfolio_series.iloc[0] != 0:
            total_return = (portfolio_series.iloc[-1] - portfolio_series.iloc[0]) / portfolio_series.iloc[0]
        else:
            total_return = 0
            
        vol_port = ret_port.std() * np.sqrt(252)
        
        # 2. Diversification Effect
        individual_rets = self.data.pct_change().dropna()
        individual_vols = individual_rets.std() * np.sqrt(252)
        
        weighted_vol_sum = 0
        for ticker, weight in weights.items():
            if ticker in individual_vols.index:
                weighted_vol_sum += individual_vols[ticker] * weight
        
        diversification_benefit = weighted_vol_sum - vol_port

        return {
            "Total Return": total_return,
            "Volatility (Ann.)": vol_port,
            "Diversification Effect": diversification_benefit
        }