import yfinance as yf
import pandas as pd
import numpy as np 
import streamlit as sl
from statsmodels.tsa.arima.model import ARIMA

class AssetAnalyzer():
    def __init__ (self,ticker):
        self.ticker=ticker 
        self.data = None

    def get_data(self,period="1y"): 
        """
        Get the data (Close Price and Returns) using the ticker of the instance and using yfinance
        """
        df = yf.download(self.ticker, period = period, interval = "1d", progress = False,auto_adjust=True )
        df['Returns'] = df['Close'].pct_change()
        df.dropna(inplace=True)

        self.data = df
    
    def _compute_rsi(self, window=14):
        # Calculate price changes
        delta = self.data['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate rolling averages
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def run_strategy(self,strategy_name, short_window=20,long_window=50,rsi_window=14, rsi_buy=30, rsi_sell=70):
        if self.data is None or self.data.empty :
            return ValueError("Invalid data")
        df = self.data.copy()

        if strategy_name == "Buy and Hold":
            df['Strategy_Returns'] = self.data['Returns']

        elif strategy_name == "Momentum":
            # .rolling(X).mean() compute the mean of the X last days
            df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
            df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()

            df['Signal'] = np.where(df['SMA_Short'] > df ['SMA_Long'], 1, 0)
            #strategy_return = signal of day n-1 * return of day n 
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']

        elif strategy_name == "RSI Strategy":
            # Compute the indicator
            df['RSI'] = self._compute_rsi(window=rsi_window)
            
            # Initialize signal column with NaN to handle the hold state
            df['Signal'] = np.nan
            
            # Enter position (buy) when asset is oversold
            df.loc[df['RSI'] < rsi_buy, 'Signal'] = 1
            
            # Exit position (sell) when asset is overbought
            df.loc[df['RSI'] > rsi_sell, 'Signal'] = 0
            
            # Fill NaN values with the previous valid signal (hold logic)
            df['Signal'] = df['Signal'].ffill()
            
            # Fill initial NaNs with 0 (not invested at start)
            df['Signal'] = df['Signal'].fillna(0)
            
            # Calculate returns (shifted by 1 day)
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']

        df['Cumulative_strategy'] = (1 + df['Strategy_Returns'].fillna(0)).cumprod() * 100
        return df
    
    def get_metrics(self,df):
        """
        Compute advanced KPIs: Sharpe, Drawdown, CAGR, Win Rate, Volatility.        
        """
        if df is None or 'Strategy_Returns' not in df.columns:
            return ValueError("df empty")
        
        # 1. Prepare data
        # Fill NaN with 0 to avoid calculation errors
        returns = df['Strategy_Returns'].fillna(0)
        
        # 2. Total Return & CAGR (Annualized Return)
        # We calculate how many years the data covers
        days = (df.index[-1] - df.index[0]).days
        years = max(days / 365.25, 0.01) # Avoid division by zero

        # Cumulative Return (Final Value / Initial Value)
        cum_ret_series = (1 + returns).cumprod()
        total_return = cum_ret_series.iloc[-1] - 1

        # CAGR Formula: (End/Start)^(1/Years) - 1
        cagr = (1 + total_return) ** (1 / years) - 1
        
        # 3. Volatility (Annualized Standard Deviation)
        volatility = returns.std() * np.sqrt(252)
        
        # 4. Sharpe Ratio (Risk Free Rate assumed 0 for simplicity)
        if volatility == 0:
            sharpe = 0
        else:
            sharpe = cagr / volatility
            
        # 5. Max Drawdown
        running_max = cum_ret_series.cummax()
        drawdown = (cum_ret_series - running_max) / running_max
        max_dd = drawdown.min()
        
        # 6. Win Rate (Percentage of positive days)
        # Let's check all days where strategy made money > 0
        positive_days = returns[returns > 0].count()
        total_days = returns[returns != 0].count() # Ignore flat days
        
        if total_days > 0:
            win_rate = positive_days / total_days
        else:
            win_rate = 0

        # Return a dictionary with all metrics (raw floats)
        return {
            "Total Return": total_return,
            "CAGR": cagr,
            "Volatility": volatility,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_dd,
            "Win Rate": win_rate
        }

    def get_forecast(self, steps=30):
        """
        Generates a price forecast using an ARIMA model.
        Returns a DataFrame with the forecasted prices for the next 'steps' days.
        """
        if self.data is None or self.data.empty:
            return None
            
        try:
            # 1. Prepare data (use Close price)
            # We use a simple (1,1,1) order which is robust for financial data
            # p=1 (AutoRegressive), d=1 (Integrated/Trend), q=1 (Moving Average)
            model = ARIMA(self.data['Close'], order=(1, 1, 1))
            model_fit = model.fit()
            
            # 2. Generate Forecast
            forecast_res = model_fit.get_forecast(steps=steps)
            forecast_data = forecast_res.predicted_mean
            
            # 3. Create Future Dates Index
            last_date = self.data.index[-1]
            # Create a range of business days starting after the last known date
            future_dates = pd.date_range(start=last_date, periods=steps + 1, freq='B')[1:]
            
            # 4. Format as DataFrame
            forecast_df = pd.DataFrame(forecast_data.values, index=future_dates, columns=['Forecast'])
            
            return forecast_df
            
        except Exception as e:
            print(f"ARIMA Error: {e}")
            return None    

    


# ----------------------------------- Test of AssetAnalyzer Class ---------------------------------------

Test = AssetAnalyzer('GOOG')
Test.get_data()

print("--- Test Momentum ---")
df_res = Test.run_strategy("Momentum", 20, 50)
print(df_res[['Close', 'Signal']].tail())

print("\n--- Test RSI ---")
df_rsi = Test.run_strategy("RSI Strategy", rsi_window=14, rsi_buy=30, rsi_sell=70)
print(df_rsi[['Close', 'RSI', 'Signal']].tail())

print("\n--- Test Prévision IA (ARIMA) ---")
try:
        # On demande une prévision sur 5 jours pour voir si ça marche vite
        forecast = Test.get_forecast(steps=5)
        
        if forecast is not None and not forecast.empty:
            print("✅ Succès ! Voici les prévisions :")
            print(forecast)
            
            # Petit check visuel des valeurs
            last_price = float(Test.data['Close'].values[-1])
            next_price = float(forecast['Forecast'].values[0])
            print(f"\nDernier prix connu : {last_price:.2f}")
            print(f"Prix prévu demain  : {next_price:.2f}")
        else:
            print("Erreur : Le modèle a retourné vide.")
            
except Exception as e:
    print(f"Crash du test : {e}")




