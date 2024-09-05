import streamlit as st
import yfinance as yf
import plotly.express as px
import datetime

# Function to fetch latest price and volume for a list of tickers
def fetch_price_volume(tickers):
    data = yf.download(tickers, period="1d")
    prices = data['Adj Close'].iloc[0]
    volumes = data['Volume'].iloc[0]
    return prices, volumes

# Function to calculate the sum of price * volume for a set of tickers
def calculate_sum(tickers):
    prices, volumes = fetch_price_volume(tickers)
    return (prices * volumes).sum()

# Function to calculate YPFD/YPF ratio
def fetch_ypf_ratio():
    tickers = ['YPF', 'YPFD.BA']
    data = yf.download(tickers, period="1d")
    try:
        ratio = data['Adj Close']['YPFD.BA'].iloc[0] / data['Adj Close']['YPF'].iloc[0]
    except IndexError:
        st.error("No data available for YPF or YPFD.BA. Please select another date.")
        return None
    return ratio

# Main function for the app
def main():
    st.title("Stock Volume-Weighted Price Comparison")

    # Date picker
    today = datetime.date.today()
    user_date = st.date_input("Choose a date", today)

    # ADRs tickers
    adrs_tickers = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS', 'LOMA', 'PAM', 'SUPV', 'TEO', 'TGS', 'YPF']
    # Panel Líder tickers
    panel_lider_tickers = ['GGAL.BA', 'YPFD.BA', 'PAMP.BA', 'TXAR.BA', 'ALUA.BA', 'CRES.BA', 'SUPV.BA', 'CEPU.BA',
                           'BMA.BA', 'TGSU2.BA', 'TRAN.BA', 'EDN.BA', 'LOMA.BA', 'MIRG.BA', 'BBAR.BA', 'TGNO4.BA',
                           'COME.BA', 'IRSA.BA', 'BYMA.BA', 'TECO2.BA', 'VALO.BA']
    # Panel General tickers
    panel_general_tickers = ['DGCU2.BA', 'MOLI.BA', 'CGPA2.BA', 'METR.BA', 'CECO2.BA', 'BHIP.BA', 'AGRO.BA', 'LEDE.BA',
                             'CVH.BA', 'HAVA.BA', 'AUSO.BA', 'SEMI.BA', 'INVJ.BA', 'CTIO.BA', 'MORI.BA', 'HARG.BA',
                             'GCLA.BA', 'SAMI.BA', 'BOLT.BA', 'MOLA.BA', 'CAPX.BA', 'OEST.BA', 'LONG.BA', 'GCDI.BA',
                             'GBAN.BA', 'CELU.BA', 'FERR.BA', 'CADO.BA', 'GAMI.BA', 'PATA.BA', 'CARC.BA', 'BPAT.BA',
                             'RICH.BA', 'INTR.BA', 'GARO.BA', 'FIPL.BA', 'GRIM.BA', 'DYCA.BA', 'POLL.BA', 'DOME.BA',
                             'ROSE.BA', 'RIGO.BA', 'DGCE.BA', 'MTR.BA', 'HSAT.BA']

    # Fetch ADRs value
    st.subheader("Fetching ADRs data...")
    adrs_value = calculate_sum(adrs_tickers)

    # Fetch Panel Líder value and apply YPFD/YPF ratio
    st.subheader("Fetching Panel Líder data...")
    panel_lider_value = calculate_sum(panel_lider_tickers)
    ypfd_ratio = fetch_ypf_ratio()
    if ypfd_ratio is not None:
        panel_lider_value /= ypfd_ratio

    # Fetch Panel General value and apply YPFD/YPF ratio
    st.subheader("Fetching Panel General data...")
    panel_general_value = calculate_sum(panel_general_tickers)
    if ypfd_ratio is not None:
        panel_general_value /= ypfd_ratio

    # Display results as a tree map
    st.subheader("Tree Map of Values")
    data = {
        'Category': ['ADRs', 'Panel Líder', 'Panel General'],
        'Value (USD)': [adrs_value, panel_lider_value, panel_general_value]
    }
    
    fig = px.treemap(data, path=['Category'], values='Value (USD)', 
                     title="Comparison of ADRs, Panel Líder, and Panel General",
                     color='Value (USD)', color_continuous_scale='Blues')
    st.plotly_chart(fig)

# Run the Streamlit app
if __name__ == "__main__":
    main()
