import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta

# --- 0. PAGE CONFIG & FUNKY CURVY RED THEME ---
st.set_page_config(page_title="Global Macro Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state so the popup ONLY injects on the very first load
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

st.markdown("""
<style>
/* 1. Deep Black Background */
.stApp { background-color: #050505; }

/* 2. Funky Crimson Red Text & Headers */
h1, h2, h3, h4, .st-emotion-cache-10trblm { 
    color: #DC143C !important; 
    font-family: 'Verdana', sans-serif; 
    font-weight: 900; 
    text-shadow: 0px 0px 10px rgba(220, 20, 60, 0.4); 
}

/* Funky Curvy Dividers */
hr { border-top: 3px dashed #DC143C !important; margin: 25px 0; border-radius: 10px; }

/* 3. Super Curvy & Glowing Metric Boxes */
[data-testid="stMetric"] { 
    background-color: #000000; 
    border: 3px solid #DC143C; 
    padding: 20px; 
    border-radius: 30px; 
    box-shadow: 0px 5px 20px rgba(220, 20, 60, 0.3); 
}

/* 4. OVERRIDE STREAMLIT BLUE: Crimson Information Boxes */
[data-testid="stAlert"] { 
    background-color: #4a0404 !important; /* Deep Crimson Red Background */
    border: 2px solid #DC143C !important; 
    border-radius: 25px !important; 
    box-shadow: 0px 4px 15px rgba(220, 20, 60, 0.5) !important;
    color: #ffffff !important;
}
[data-testid="stAlert"] p { color: #ffffff !important; font-size: 16px; }

/* 5. Mobile-Friendly Curvy Selectboxes */
div[data-baseweb="select"] > div { 
    background-color: #000000; 
    border: 2px solid #DC143C; 
    color: white; 
    border-radius: 25px; 
}

/* 6. MASSIVE Curvy Expander Tabs (Advanced Analysis) */
div[data-testid="stExpander"] details summary { 
    background-color: #000000; 
    color: #DC143C !important; 
    border: 2px solid #DC143C !important; 
    border-radius: 25px !important; 
    font-size: 22px !important; /* BIGGER TEXT */
    padding: 20px !important;   /* BIGGER BUTTON */
}
div[data-testid="stExpander"] { border-radius: 25px; overflow: hidden; }

/* 7. MASSIVE Download Button */
button[data-testid="baseButton-secondary"] {
    font-size: 22px !important; /* BIGGER TEXT */
    padding: 25px 40px !important; /* BIGGER BUTTON */
    border-radius: 35px !important;
    background-color: #DC143C !important;
    color: #ffffff !important;
    border: 2px solid #DC143C !important;
    width: 100%; /* Makes button stretch across screen */
    box-shadow: 0px 5px 20px rgba(220, 20, 60, 0.6) !important;
    font-weight: bold !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background-color: #000000 !important;
    color: #DC143C !important;
    box-shadow: 0px 5px 25px rgba(220, 20, 60, 1) !important;
}
</style>
""", unsafe_allow_html=True)

# --- 1. EXPANDED FUNKY INTRODUCTION ---
st.title("🌍 Global Macroeconomic Pulse")
st.markdown("""
**Welcome to the command center of the global economy.** Money never sleeps, and neither do these metrics. 
This platform isn't just a dashboard—it is a live heartbeat of international trade, tracking the raw chaos of the financial markets in real-time. We are visualizing the hidden forces that dictate our world: live foreign exchange rates, sovereign debt yields, and central bank maneuvers. 

Whether it is inflation eating away at a nation's purchasing power or a shifting yield curve predicting the next global recession, this tool decodes the math behind global power dynamics. Select your target economy below and watch the data unfold.
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
    }
}

# --- 3. MAIN PAGE MOBILE CONTROLS ---
st.subheader("🔍 Lock In Your Target")
selected_region = st.selectbox("Step 1: Choose Economic Region", list(regions.keys()))
selected_country = st.selectbox("Step 2: Select Country", list(regions[selected_region].keys()))
data_dict = regions[selected_region][selected_country]
currency_name = selected_country.split(" ")[1]

with st.expander("⚙️ Advanced Analysis Tools (Moving Averages & Comparisons)"):
    show_ma = st.checkbox("📈 Show 50 & 200-Day Moving Averages")
    show_events = st.checkbox("🏛️ Overlay Geopolitical Events")
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

# --- 5. RECESSION PREDICTOR ---
with st.expander("🚨 Global Recession Predictor (Yield Spread)", expanded=True):
    col_y1, col_y2 = st.columns([2,1])
    us_10y = get_data("^TNX")
    us_3m = get_data("^IRX")
    if not us_10y.empty and not us_3m.empty:
        current_spread = us_10y.iloc[-1].item() - us_3m.iloc[-1].item()
        status = "⚠️ INVERTED (Recession Risk)" if current_spread < 0 else "✅ NORMAL (Expansion)"
        color = "#DC143C" if current_spread < 0 else "green"
        
        with col_y1:
            st.markdown(f"**Current Spread:** <span style='color:{color}; font-size:24px; font-weight:bold;'>{current_spread:.2f}%</span>", unsafe_allow_html=True)
            st.markdown(f"**Status:** {status}")
        with col_y2:
            st.metric("US 10-Year Yield", f"{us_10y.iloc[-1].item():.2f}%")
            
    st.info(f"""
    📖 **HOW THIS WORKS NORMALLY:** The yield spread subtracts short-term government borrowing rates from long-term rates. An inverted curve (dropping below 0%) is historically the most accurate predictor of a global economic recession.
    
    🌍 **WHAT THIS MEANS FOR {selected_country.upper()}:** Because the US Dollar is the world's reserve currency, an inverted curve here spells danger everywhere. If the US enters a recession, {selected_country}'s export markets and foreign investments could face severe turbulence, directly impacting the value of the {currency_name}.
    """)

st.markdown("<hr>", unsafe_allow_html=True)

# --- 6. MACRO INDICATORS ---
st.subheader(f"Macroeconomic Snapshot: {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("GDP Growth", data_dict["gdp"])
col2.metric("Inflation (CPI)", data_dict["cpi"])
col3.metric("Base vs USD", currency_name)

st.info(f"""
📖 **HOW THIS WORKS NORMALLY:** Gross Domestic Product (GDP) tracks the total economic output and growth of a country, while the Consumer Price Index (CPI) tracks how fast prices (inflation) are rising for citizens.

🌍 **WHAT THIS MEANS FOR {selected_country.upper()}:** {selected_country} is currently seeing a GDP growth of {data_dict['gdp']} and inflation at {data_dict['cpi']}. If this inflation gets too hot, {selected_country}'s central bank will be forced to raise interest rates, which could aggressively strengthen the {currency_name} on the world stage!
""")

# --- 7. ADVANCED CHARTING ---
fx_data = get_data(data_dict["fx"])
yield_data = get_data(data_dict["yield"])

if not fx_data.empty:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader(f"Currency Trajectory: {selected_country}")
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=fx_data.index, y=fx_data.squeeze(), mode='lines', name=selected_country, line=dict(color='#DC143C', width=3)))

    if show_ma:
        ma_50 = fx_data.rolling(window=50).mean()
        ma_200 = fx_data.rolling(window=200).mean()
        fig_fx.add_trace(go.Scatter(x=fx_data.index, y=ma_50.squeeze(), mode='lines', name='50-Day MA', line=dict(color='white', dash='dot')))
        fig_fx.add_trace(go.Scatter(x=fx_data.index, y=ma_200.squeeze(), mode='lines', name='200-Day MA', line=dict(color='gray', dash='dash')))

    fig_fx.update_layout(plot_bgcolor="#050505", paper_bgcolor="#050505", font=dict(color="white"), hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_fx, use_container_width=True)

    st.info(f"""
    📖 **HOW THIS WORKS NORMALLY:** This chart visualizes the exchange rate of a currency against the US Dollar over the last 365 days. 
    
    🌍 **WHAT THIS MEANS FOR {selected_country.upper()}:** You are watching the live battle between the {currency_name} and the USD. If the red line is trending downwards, {selected_country} is actively losing international purchasing power. If it spikes up, foreign capital is flooding into their economy!
    """)

# --- 8. CORRELATION & EXPORT ---
if not yield_data.empty and not fx_data.empty:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Statistical Correlation Matrix")
    df_combined = pd.DataFrame({'FX Rate': fx_data.squeeze(), '10Y Yield': yield_data.squeeze()}).dropna()
    st.dataframe(df_combined.corr(), use_container_width=True)
    
    st.info(f"""
    📖 **HOW THIS WORKS NORMALLY:** A Pearson correlation calculates the statistical relationship between a country's bond yields and its currency value, scoring it from -1 (opposites) to +1 (moving perfectly together).
    
    🌍 **WHAT THIS MEANS FOR {selected_country.upper()}:** This matrix proves mathematically whether {selected_country}'s domestic bond yields are actually dictating the {currency_name}'s value, or if external geopolitical chaos is taking the wheel.
    """)
    
    csv = df_combined.to_csv(index=True).encode('utf-8')
    st.download_button(label="📥 Download Raw Financial Data (CSV)", data=csv, file_name=f'{selected_country}_macro_data.csv', mime='text/csv')

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Developed by Tanish Singh | Contact: tanishsingh671@gmail.com</p>", unsafe_allow_html=True)

# --- 9. ONE-TIME 15-SECOND DELAY FEEDBACK POPUP ---
if st.session_state.first_load:
    st.markdown("""
    <style>
    /* Popup Animation - Delays for 15s, then zooms in */
    @keyframes funkyPopup {
        0% { opacity: 0; pointer-events: none; transform: scale(0.8); }
        99% { opacity: 0; pointer-events: none; transform: scale(0.8); }
        100% { opacity: 1; pointer-events: auto; transform: scale(1); }
    }

    #close-modal { display: none; }
    #close-modal:checked ~ .feedback-overlay { display: none !important; }

    .feedback-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.85); backdrop-filter: blur(5px);
        z-index: 999999; display: flex; justify-content: center; align-items: center;
        animation: funkyPopup 15s forwards; 
    }

    .feedback-box {
        background: #000000; border: 4px solid #DC143C; padding: 40px;
        border-radius: 40px; text-align: center; color: white;
        box-shadow: 0px 0px 40px rgba(220, 20, 60, 0.8); width: 90%; max-width: 550px;
    }

    .feedback-emojis {
        font-size: 60px; margin: 30px 0; display: flex; justify-content: space-between; cursor: pointer;
    }

    .feedback-emojis label {
        cursor: pointer; transition: 0.3s; filter: drop-shadow(0px 0px 5px rgba(255,255,255,0.2));
    }
    
    .feedback-emojis label:hover {
        transform: scale(1.3) translateY(-10px);
        filter: drop-shadow(0px 10px 10px rgba(220,20,60,0.8));
    }
    </style>

    <input type="checkbox" id="close-modal">
    <div class="feedback-overlay">
       <div class="feedback-box">
          <h2 style="color: #DC143C !important; font-size: 28px;">How satisfied are you with our website?</h2>
          <div class="feedback-emojis">
              <label for="close-modal">🤬</label> 
              <label for="close-modal">🙁</label> 
              <label for="close-modal">😐</label> 
              <label for="close-modal">🙂</label> 
              <label for="close-modal">🤩</label>
          </div>
          <p style="font-size:16px; color:gray; font-style: italic;">(Tap an emoji to submit & close)</p>
       </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.session_state.first_load = False
