import yfinance as yf
import pandas as pd
import numpy as np 
import streamlit as sl

class AssetAnalyzer():
    def __init__ (self,ticker):
        self.ticker=ticker 
        self.data = None

    def get_data(self): 
        """
        Get the data (Close Price and Returns) using the ticker of the instance and using yfinance
        """
        df = yf.download(self.ticker, period = "3y", interval = "1d", progress = False,auto_adjust=True )
        df['Returns'] = df['Close'].pct_change()
        df.dropna(inplace=True)

        self.data = df

    def run_strategy(self,strategy_name, short_window,long_window):
        if self.data is None or self.data.empty :
            return None
        df = self.data.copy()

        if strategy_name == "Buy and Hold":
            df['Strategy_Retuns'] = self.data['Returns']

        elif strategy_name == "Momentum":
            # .rolling(X).mean() compute the mean of the X last days
            df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
            df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()

            df['Signal'] = np.where(df['SMA_Short'] > df ['SMA_Long'], 1, 0)
            #strategy_return = signal of day n-1 * return of day n 
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']

        df['Cumulative_strategy'] = (1 + df['Strategy_Returns'].fillna(0)).cumprod() * 100
        return df
    


# ----------------------------------- Test of AssetAnalyzer Class ---------------------------------------

Test = AssetAnalyzer('GOOG')
Test.get_data()

df_result = Test.run_strategy("Momentum",20,50)
cols_to_check = ['Close', 'SMA_Short', 'SMA_Long', 'Signal', 'Strategy_Returns']
print(df_result[cols_to_check].tail(30))

last_signal = df_result['Signal'].iloc[-1]
print("Signal for today : ", last_signal, "| 1 = Buy, 0 = Sell")


