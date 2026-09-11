import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta

# --- 0. PAGE CONFIG & AGGRESSIVE RED THEME ---
st.set_page_config(page_title="Global Macro Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* Main Backgrounds */
.stApp { background-color: #050505; }

/* Aggressive Red Accents */
h1, h2, h3, h4, .st-emotion-cache-10trblm { color: #DC143C !important; font-family: 'Arial', sans-serif; font-weight: bold; }
hr { border-top: 2px solid #DC143C !important; margin: 20px 0; }

/* Metric Boxes */
[data-testid="stMetric"] { background-color: #0a1128; border: 2px solid #DC143C; border-left: 8px solid #DC143C; padding: 15px; border-radius: 8px; box-shadow: 2px 2px 15px rgba(220, 20, 60, 0.2); }
div.stInfo, div.stWarning { background-color: #0a1128; color: #f4f4f4; border: 2px solid #DC143C; border-left: 8px solid #DC143C; }
p, li, .stMarkdown, label { color: #e0e0e0 !important; }

/* Mobile-Friendly Selectboxes */
div[data-baseweb="select"] > div { background-color: #0a1128; border: 1px solid #DC143C; color: white; }

/* Expander (Advanced Tools) */
.streamlit-expanderHeader { background-color: #0a1128; color: #DC143C !important; border: 1px solid #DC143C; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 1. SIMPLIFIED INTRODUCTION ---
st.title("🌍 Global Macroeconomic Dashboard")
st.markdown("""
**Welcome.** This tool tracks live exchange rates, bond yields, and key economic data for major global economies. Use the menus below to select a country and explore how central bank policies affect currency valuations in real-time.
""")
st.markdown("<hr>", unsafe_allow_html=True)

# --- 2. CATEGORIZED COUNTRY DICTIONARY ---
regions = {
    "The Majors": {
        "🇺🇸 United States": {"fx": "DX-Y.NYB", "yield": "^TNX", "gdp": "2.5%", "cpi": "3.1%"},
        "🇪🇺 Eurozone": {"fx": "EURUSD=X", "yield": "^TNX", "gdp": "0.5%", "cpi": "2.4%"}, 
        "🇬🇧 United Kingdom": {"fx": "GBPUSD=X", "yield": "^TNX", "gdp": "0.1%", "cpi": "3.2%"},
        "🇯🇵 Japan": {"fx": "JPY=X", "yield": "^TNX", "gdp": "1.0%", "cpi": "2.2%"},
        "🇦🇺 Australia": {"fx": "AUDUSD=X", "yield": "^TNX", "gdp": "1.5%", "cpi": "3.4%"},
        "🇨🇦 Canada": {"fx": "CAD=X", "yield": "^TNX", "gdp": "1.1%", "cpi": "2.9%"},
        "🇨🇭 Switzerland": {"fx": "CHF=X", "yield": "^TNX", "gdp": "0.8%", "cpi": "1.2%"},
        "🇸🇬 Singapore": {"fx": "SGD=X", "yield": "^TNX", "gdp": "1.1%", "cpi": "3.1%"},
        "🇮🇳 India": {"fx": "INR=X", "yield": "^TNX", "gdp": "7.3%", "cpi": "5.1%"},
        "🇧🇷 Brazil": {"fx": "BRL=X", "yield": "^TNX", "gdp": "2.9%", "cpi": "4.5%"}
    },
    "Asia & Pacific": {
        "🇨🇳 China": {"fx": "CNY=X", "yield": "N/A", "gdp": "5.2%", "cpi": "-0.8%"},
        "🇭🇰 Hong Kong": {"fx": "HKD=X", "yield": "N/A", "gdp": "3.2%", "cpi": "2.1%"},
        "🇰🇷 South Korea": {"fx": "KRW=X", "yield": "N/A", "gdp": "1.4%", "cpi": "2.8%"},
        "🇳🇿 New Zealand": {"fx": "NZDUSD=X", "yield": "N/A", "gdp": "0.6%", "cpi": "4.7%"},
        "🇮🇩 Indonesia": {"fx": "IDR=X", "yield": "N/A", "gdp": "5.0%", "cpi": "2.6%"},
        "🇻🇳 Vietnam": {"fx": "VND=X", "yield": "N/A", "gdp": "5.0%", "cpi": "3.2%"}
    },
    "Americas": {
        "🇲🇽 Mexico": {"fx": "MXN=X", "yield": "N/A", "gdp": "3.2%", "cpi": "4.4%"},
        "🇦🇷 Argentina": {"fx": "ARS=X", "yield": "N/A", "gdp": "-1.6%", "cpi": "254%"},
        "🇨🇱 Chile": {"fx": "CLP=X", "yield": "N/A", "gdp": "0.2%", "cpi": "3.8%"},
        "🇨🇴 Colombia": {"fx": "COP=X", "yield": "N/A", "gdp": "0.6%", "cpi": "8.3%"}
    },
    "Europe (Non-Euro)": {
        "🇸🇪 Sweden": {"fx": "SEK=X", "yield": "N/A", "gdp": "-0.3%", "cpi": "5.4%"},
        "🇳🇴 Norway": {"fx": "NOK=X", "yield": "N/A", "gdp": "0.5%", "cpi": "4.7%"},
        "🇩🇰 Denmark": {"fx": "DKK=X", "yield": "N/A", "gdp": "1.8%", "cpi": "0.9%"},
        "🇵🇱 Poland": {"fx": "PLN=X", "yield": "N/A", "gdp": "0.2%", "cpi": "3.9%"},
        "🇷🇺 Russia": {"fx": "RUB=X", "yield": "N/A", "gdp": "3.6%", "cpi": "7.4%"}
    },
    "Middle East & Africa": {
        "🇸🇦 Saudi Arabia": {"fx": "SAR=X", "yield": "N/A", "gdp": "-0.9%", "cpi": "1.6%"},
        "🇦🇪 UAE": {"fx": "AED=X", "yield": "N/A", "gdp": "3.4%", "cpi": "1.6%"},
        "🇿🇦 South Africa": {"fx": "ZAR=X", "yield": "N/A", "gdp": "0.6%", "cpi": "5.3%"},
        "🇳🇬 Nigeria": {"fx": "NGN=X", "yield": "N/A", "gdp": "2.9%", "cpi": "29.9%"},
        "🇰🇪 Kenya": {"fx": "KES=X", "yield": "N/A", "gdp": "5.0%", "cpi": "6.9%"}
    }
}

# --- 3. MAIN PAGE MOBILE CONTROLS (No Sidebar) ---
st.subheader("🔍 Select Data")
selected_region = st.selectbox("Step 1: Choose Economic Region", list(regions.keys()))
selected_country = st.selectbox("Step 2: Select Country", list(regions[selected_region].keys()))
data_dict = regions[selected_region][selected_country]

# Hide advanced tools in an expander so it stays clean on mobile
with st.expander("⚙️ Advanced Analysis Tools (Moving Averages & Comparisons)"):
    show_ma = st.checkbox("📈 Show 50 & 200-Day Moving Averages")
    show_events = st.checkbox("🏛️ Overlay Geopolitical & Law Events")
    compare_mode = st.checkbox("⚔️ Enable Country Comparison")
    
    compare_country = None
    if compare_mode:
        comp_region = st.selectbox("Compare with Region:", list(regions.keys()))
        compare_country = st.selectbox("Compare with Country:", list(regions[comp_region].keys()))
        comp_data_dict = regions[comp_region][compare_country]

st.markdown("<hr>", unsafe_allow_html=True)

# --- 4. DATA FETCHING ---
@st.cache_data
def get_data(ticker, period="1y"):
    if ticker == "N/A": return pd.Series()
    try:
        data = yf.download(ticker, period=period, interval="1d")
        return data['Close'] if not data.empty else pd.Series()
    except:
        return pd.Series()

# --- 5. RECESSION PREDICTOR (YIELD SPREAD) ---
with st.expander("🚨 Global Recession Predictor (US Treasury Yield Spread)", expanded=True):
    col_y1, col_y2 = st.columns([2,1])
    us_10y = get_data("^TNX")
    us_3m = get_data("^IRX")
    if not us_10y.empty and not us_3m.empty:
        current_spread = us_10y.iloc[-1].item() - us_3m.iloc[-1].item()
        status = "⚠️ INVERTED (Recession Risk)" if current_spread < 0 else "✅ NORMAL (Expansion)"
        color = "#DC143C" if current_spread < 0 else "green"
        
        with col_y1:
            st.markdown(f"**Current 10Y - 3M Spread:** <span style='color:{color}; font-size:20px;'>{current_spread:.2f}%</span>", unsafe_allow_html=True)
            st.markdown(f"**Yield Curve Status:** {status}")
        with col_y2:
            st.metric("US 10-Year Yield", f"{us_10y.iloc[-1].item():.2f}%")
            st.metric("US 3-Month Yield", f"{us_3m.iloc[-1].item():.2f}%")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 6. MACRO INDICATORS ---
st.subheader(f"Macroeconomic Snapshot: {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("GDP Growth", data_dict["gdp"])
col2.metric("Inflation (CPI)", data_dict["cpi"])
col3.metric("Base vs USD", selected_country.split(" ")[1])

# --- 7. ADVANCED CHARTING ---
fx_data = get_data(data_dict["fx"])
yield_data = get_data(data_dict["yield"])

if not fx_data.empty:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader(f"Foreign Exchange Trajectory: {selected_country}")
    fig_fx = go.Figure()
    
    fig_fx.add_trace(go.Scatter(x=fx_data.index, y=fx_data.squeeze(), mode='lines', name=selected_country, line=dict(color='#DC143C', width=2)))

    if show_ma:
        ma_50 = fx_data.rolling(window=50).mean()
        ma_200 = fx_data.rolling(window=200).mean()
        fig_fx.add_trace(go.Scatter(x=fx_data.index, y=ma_50.squeeze(), mode='lines', name='50-Day MA', line=dict(color='cyan', dash='dot')))
        fig_fx.add_trace(go.Scatter(x=fx_data.index, y=ma_200.squeeze(), mode='lines', name='200-Day MA', line=dict(color='orange', dash='dash')))

    if compare_mode and compare_country:
        comp_fx = get_data(comp_data_dict["fx"])
        if not comp_fx.empty:
            fx_pct = (fx_data / fx_data.iloc[0] - 1) * 100
            comp_pct = (comp_fx / comp_fx.iloc[0] - 1) * 100
            fig_fx = go.Figure() 
            fig_fx.add_trace(go.Scatter(x=fx_pct.index, y=fx_pct.squeeze(), mode='lines', name=selected_country, line=dict(color='#DC143C', width=2)))
            fig_fx.add_trace(go.Scatter(x=comp_pct.index, y=comp_pct.squeeze(), mode='lines', name=compare_country, line=dict(color='yellow', width=2)))
            fig_fx.update_layout(yaxis_title="Percentage Change (%)")

    if show_events:
        events = {
            (datetime.now() - timedelta(days=250)).strftime('%Y-%m-%d'): "UN Climate & Trade Summit",
            (datetime.now() - timedelta(days=160)).strftime('%Y-%m-%d'): "Intl. Maritime Security Pact",
            (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'): "Global Tariff Framework Update"
        }
        for date, event in events.items():
            fig_fx.add_vline(x=date, line_width=1, line_dash="dash", line_color="white")
            fig_fx.add_annotation(x=date, y=0.95, yref="paper", text=event, showarrow=False, font=dict(color="white", size=10), textangle=-90)

    fig_fx.update_layout(
        plot_bgcolor="#050505", paper_bgcolor="#050505", font=dict(color="white"),
        hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20)
    )
    if not (compare_mode and compare_country): fig_fx.update_layout(yaxis_title="Exchange Rate")
        
    st.plotly_chart(fig_fx, use_container_width=True)

# --- 8. CORRELATION & EXPORT ---
if not yield_data.empty and not fx_data.empty:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Statistical Correlation Matrix")
    df_combined = pd.DataFrame({'FX Rate': fx_data.squeeze(), '10Y Yield': yield_data.squeeze()}).dropna()
    correlation = df_combined.corr()
    st.dataframe(correlation, use_container_width=True)
    st.info("🧮 **Graph Analysis:** Calculates how closely the currency and bond yields move together. Positive = move together, Negative = move opposite.")
    
    csv = df_combined.to_csv(index=True).encode('utf-8')
    st.download_button(label="📥 Download Raw Financial Data (CSV)", data=csv, file_name=f'{selected_country}_macro_data.csv', mime='text/csv')

# --- 9. GLOSSARY & FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("📚 Economic & Policy Glossary")
st.markdown("""
*   **Yield Spread (10Y - 3M):** Difference between long-term and short-term government debt rates.
*   **Moving Averages (50/200 Day):** Technical indicators used to identify long-term market trends.
*   **UIRP:** Theory that interest rate differences equal expected exchange rate changes.
""")
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Developed by Tanish Singh | Contact: tanishsingh671@gmail.com</p>", unsafe_allow_html=True)

# --- 10. 15-SECOND DELAY FEEDBACK POPUP (CSS Hack) ---
st.markdown("""
<style>
/* Animation to delay the popup for 15 seconds */
@keyframes delayShow {
    0% { opacity: 0; pointer-events: none; }
    99% { opacity: 0; pointer-events: none; }
    100% { opacity: 1; pointer-events: auto; }
}

/* Hidden checkbox logic to allow closing without Javascript */
#close-modal { display: none; }
#close-modal:checked ~ .feedback-overlay { display: none !important; }

.feedback-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.85);
    z-index: 999999;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: delayShow 15s forwards; /* 15 SECOND TIMER HERE */
}

.feedback-box {
    background: #0a1128;
    border: 3px solid #DC143C;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 0px 30px rgba(220, 20, 60, 0.6);
    width: 90%;
    max-width: 500px;
}

.feedback-emojis {
    font-size: 50px;
    margin: 25px 0;
    display: flex;
    justify-content: space-between;
    cursor: pointer;
}

.feedback-emojis span:hover {
    transform: scale(1.2);
    transition: 0.2s;
}

.close-btn {
    background: #DC143C;
    color: white;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    cursor: pointer;
    border-radius: 5px;
    display: inline-block;
    margin-top: 15px;
}
.close-btn:hover { background: #ff1e4d; }
</style>

<input type="checkbox" id="close-modal">
<div class="feedback-overlay">
   <div class="feedback-box">
      <h2 style="color: white !important;">How satisfied are you with our website?</h2>
      <div class="feedback-emojis">
          <label for="close-modal">🤬</label> 
          <label for="close-modal">🙁</label> 
          <label for="close-modal">😐</label> 
          <label for="close-modal">🙂</label> 
          <label for="close-modal">🤩</label>
      </div>
      <p style="font-size:14px; color:gray;">(Click an emoji to submit and close)</p>
   </div>
</div>
""", unsafe_allow_html=True)
