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
        return None


# ----------------------------------- Test of AssetAnalyzer Class ---------------------------------------
Test = AssetAnalyzer('BTC-USD')
Test.get_data()
print(Test.data['Returns'].head())
print(Test.data['Close'].head())