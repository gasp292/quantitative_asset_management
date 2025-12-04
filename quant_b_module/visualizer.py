import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

class Visualizer:
    """
    Handles all chart plotting using Plotly.
    """
    
    @staticmethod
    def plot_performance(df):
        """
        Plots the main multi-line chart comparing assets and portfolio.
        """
        # Create a line chart
        fig = px.line(
            df, 
            x=df.index, 
            y=df.columns, 
            title="Portfolio vs Individual Assets (Rebased to 100)",
            labels={"value": "Normalized Price (Base 100)", "variable": "Asset"}
        )
        try:
            theme = st.get_option("theme.base")
        except:
            theme = 'dark'
        fig.update_traces(line=dict(width=1)) 
        fig.update_traces(
            selector=dict(name='Portfolio'), 
            line=dict(width=4) 
        )
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def plot_correlation_heatmap(corr_matrix):
        """
        Plots the correlation matrix as a heatmap.
        """
        fig = px.imshow(
            corr_matrix, 
            text_auto=True, 
            aspect="auto",
            color_continuous_scale="RdBu_r", # Red to Blue (diverging)
            title="Asset Correlation Matrix"
        )
        st.plotly_chart(fig, use_container_width=True)