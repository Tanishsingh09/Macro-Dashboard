import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# --- 0. PAGE CONFIG & CUSTOM THEME ---
st.set_page_config(page_title="Global Macro Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* Tertiary: Black Main Background */
.stApp {
    background-color: #050505; 
}

/* Secondary: Dark Blue Sidebar */
[data-testid="stSidebar"] {
    background-color: #0a1128 !important;
    border-right: 2px solid #DC143C;
}

/* Primary: Crimson Accents for Headers */
h1, h2, h3, h4, .st-emotion-cache-10trblm {
    color: #DC143C !important;
    font-family: 'Arial', sans-serif;
    font-weight: bold;
}

/* UI Designs: Metric Snapshot Boxes */
[data-testid="stMetric"] {
    background-color: #0a1128; 
    border-left: 5px solid #DC143C; 
    padding: 15px;
    border-radius: 8px;
    box-shadow: 2px 2px 10px rgba(220, 20, 60, 0.1);
}

/* UI Designs: Customizing the Blue Info Boxes */
div.stInfo {
    background-color: #0a1128;
    color: #f4f4f4;
    border-left: 5px solid #DC143C;
}

/* General Text Color to White for readability */
p, li, .stMarkdown {
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# --- 1. CONSTANT INTRODUCTION ---
st.title("🌍 Global Macroeconomic & Policy Dashboard")
st.markdown("""
**About This Platform:**
This interactive dashboard tracks real-time foreign exchange (FX) rates, sovereign bond yields, and macroeconomic indicators across major global economies. It is designed to visualize capital flows and the effects of central bank monetary policy on currency valuations using Uncovered Interest Rate Parity (UIRP) frameworks.
""")
st.divider()

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

# --- 3. TWO-STEP DROPDOWN UI ---
st.sidebar.title("Navigation")
selected_region = st.sidebar.selectbox("🌍 Step 1: Choose a Region", list(regions.keys()))
selected_country = st.sidebar.selectbox(f"🏳️ Step 2: Select Country", list(regions[selected_region].keys()))

data_dict = regions[selected_region][selected_country]

# --- 4. MACRO INDICATORS ---
st.subheader(f"Macroeconomic Snapshot: {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("GDP Growth (Annual)", data_dict["gdp"])
col2.metric("Inflation Rate (CPI)", data_dict["cpi"])
col3.metric("Base Currency vs USD", selected_country.split(" ")[1])
st.divider()

# --- 5. DATA FETCHING ---
@st.cache_data
def get_data(ticker):
    if ticker == "N/A":
        return pd.DataFrame()
    try:
        data = yf.download(ticker, period="1y", interval="1d")
        return data['Close'] if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

fx_data = get_data(data_dict["fx"])
yield_data = get_data(data_dict["yield"])

# --- 6. VISUALIZATIONS & EXPLANATIONS ---
if not fx_data.empty:
    st.subheader("1-Year Foreign Exchange Trajectory")
    fig_fx = go.Figure(data=go.Scatter(x=fx_data.index, y=fx_data.squeeze(), mode='lines', line=dict(color='#DC143C')))
    fig_fx.update_layout(
        title=f"{selected_country} FX Rate vs USD", 
        xaxis_title="Date", 
        yaxis_title="Exchange Rate",
        plot_bgcolor="#050505",
        paper_bgcolor="#050505",
        font=dict(color="white")
    )
    st.plotly_chart(fig_fx, use_container_width=True)
    st.info("📉 **Graph Analysis:** This chart tracks the currency's strength against the US Dollar over the last 365 days. A downward slope indicates the local currency is weakening (depreciating), while an upward slope indicates strengthening (appreciating) against the USD.")

if not yield_data.empty and not fx_data.empty:
    st.divider()
    st.subheader("Statistical Correlation Matrix")
    df_combined = pd.DataFrame({'FX Rate': fx_data.squeeze(), '10Y Yield': yield_data.squeeze()}).dropna()
    correlation = df_combined.corr()
    st.dataframe(correlation, use_container_width=True)
    st.info("🧮 **Graph Analysis:** This matrix calculates the Pearson correlation coefficient between the country's currency and its bond yields. A value close to 1 implies they move closely together, while a negative value implies they move in opposite directions, reflecting capital flow behavior.")

    # --- 7. CSV DOWNLOAD BUTTON ---
    csv = df_combined.to_csv(index=True).encode('utf-8')
    st.download_button(
        label="📥 Download Raw Financial Data (CSV)",
        data=csv,
        file_name=f'{selected_country}_macro_data.csv',
        mime='text/csv',
    )

# --- 8. GLOSSARY & FOOTER ---
st.divider()
st.subheader("📚 Economic Glossary")
st.markdown("""
*   **Foreign Exchange (FX):** The value of one nation's currency versus the currency of another nation.
*   **Sovereign Bond Yield:** The interest rate that a national government pays to borrow money. 
*   **Uncovered Interest Rate Parity (UIRP):** An economic theory stating that the difference in interest rates between two countries should equal the expected change in exchange rates between their currencies.
*   **Gross Domestic Product (GDP):** The total monetary value of all finished goods and services produced within a country's borders.
*   **Consumer Price Index (CPI):** A measure of inflation that tracks the changing prices of a basket of consumer goods and services.
*   **Correlation Coefficient:** A statistical measure (from -1 to 1) calculating how closely two variables (like FX and Yields) move together.
""")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>Developed by Tanish Singh | Contact: tanishsingh671@gmail.com</p>", unsafe_allow_html=True)
