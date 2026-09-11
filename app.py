import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Macro Policy Dashboard", layout="wide")
st.title("🌍 Global Macroeconomic & Policy Dashboard")
st.markdown("Analyzing Interest Rate Parity and Yield Curve Dynamics across major global economies.")

# --- SIDEBAR & NAVIGATION ---
st.sidebar.header("Dashboard Controls")
selected_region = st.sidebar.selectbox(
    "Select Economic Region",
    ("Australia", "Canada", "Eurozone", "Singapore")
)

# Currency Ticker Mapping
tickers = {
    "Australia": "AUDUSD=X",
    "Canada": "CADUSD=X",
    "Eurozone": "EURUSD=X",
    "Singapore": "SGDUSD=X"
}

# --- DATA FETCHING FUNCTIONS ---
@st.cache_data
def fetch_fx_data(ticker):
    """Fetches 1 year of live FX data."""
    end = datetime.today()
    start = end - timedelta(days=365)
    data = yf.download(ticker, start=start, end=end)
    return data

def generate_yield_curve(region):
    """
    Generates representative yield curve data. 
    Note: In a production environment, this would connect to a paid macro API (like Bloomberg or Alpha Vantage).
    """
    maturities = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '30Y']
    
    # Baseline current central bank rates (approximate for modeling)
    base_rates = {"Australia": 4.35, "Canada": 5.00, "Eurozone": 4.50, "Singapore": 3.50}
    base = base_rates[region]
    
    # Simulating the curve shape (slightly inverted/flat reflecting current global regimes)
    yields = [
        base, base + 0.05, base + 0.10, base + 0.05, 
        base - 0.15, base - 0.20, base - 0.35, 
        base - 0.40, base - 0.45, base - 0.20
    ]
    return maturities, yields

# --- LAYOUT: ROW 1 (Key Metrics) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

fx_data = fetch_fx_data(tickers[selected_region])
current_fx = fx_data['Close'].iloc[-1].item()
fx_change = ((current_fx - fx_data['Close'].iloc[-2].item()) / fx_data['Close'].iloc[-2].item()) * 100

col1.metric(label=f"Current FX Rate ({tickers[selected_region][:3]}/USD)", value=f"{current_fx:.4f}", delta=f"{fx_change:.2f}%")
col2.metric(label="Target Policy Rate", value=f"{generate_yield_curve(selected_region)[1][0]:.2f}%", delta="0.00%")
col3.metric(label="10Y Bond Yield", value=f"{generate_yield_curve(selected_region)[1][8]:.2f}%", delta=None)

# --- LAYOUT: ROW 2 (Interactive Charts) ---
st.markdown("---")
chart_col1, chart_col2 = st.columns(2)

# Chart 1: The Yield Curve
with chart_col1:
    st.subheader(f"Sovereign Yield Curve: {selected_region}")
    maturities, yields = generate_yield_curve(selected_region)
    
    fig_yc = go.Figure()
    fig_yc.add_trace(go.Scatter(x=maturities, y=yields, mode='lines+markers', name='Yield', line=dict(color='royalblue', width=3)))
    fig_yc.update_layout(xaxis_title="Maturity", yaxis_title="Yield (%)", template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_yc, use_container_width=True)

# Chart 2: FX Trajectory
with chart_col2:
    st.subheader(f"1-Year FX Trajectory ({tickers[selected_region][:3]}/USD)")
    
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=fx_data.index, y=fx_data['Close'].squeeze(), mode='lines', fill='tozeroy', line=dict(color='seagreen')))
    fig_fx.update_layout(xaxis_title="Date", yaxis_title="Exchange Rate", template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_fx, use_container_width=True)

# --- ECONOMIC THEORY SECTION ---
st.markdown("---")
st.header("The Economic Engine: Interest Rate Parity")
st.markdown(f"""
This dashboard operationalizes **Uncovered Interest Rate Parity (UIRP)**. The theory postulates that the difference in interest rates between two countries should equal the expected change in exchange rates between their currencies. 

If the {selected_region} central bank raises its target policy rate relative to the US Federal Reserve, we typically observe a tightening in the short end of the yield curve displayed above. Capital flows toward the higher yield, theoretically causing the {tickers[selected_region][:3]} to appreciate against the USD in the short term, which you can track in the FX Trajectory chart.
""")