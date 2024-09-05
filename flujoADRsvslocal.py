import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch the latest available date on or before the selected date
def get_valid_date(ticker, selected_date):
    """
    Fetches the latest available trading date for the ticker on or before the selected date.
    """
    start_date = selected_date - timedelta(days=7)
    end_date = selected_date + timedelta(days=1)  # Include the selected date
    try:
        ticker_data = ticker.history(start=start_date, end=end_date)
        if ticker_data.empty:
            return None, None
        latest_valid_date = ticker_data.index.max()
        price = ticker_data['Adj Close'].loc[latest_valid_date]
        volume = ticker_data['Volume'].loc[latest_valid_date]
        return price, volume
    except KeyError as e:
        st.warning(f"Error fetching data for {ticker.ticker}: Missing {e}")
        return None, None
    except Exception as e:
        st.warning(f"Error fetching data for {ticker.ticker}: {e}")
        return None, None

# Function to fetch price and volume for a list of tickers
def fetch_price_volume(tickers, selected_date):
    """
    Fetches the price and volume for each ticker on the selected date or the closest previous date.
    Returns a DataFrame with tickers, prices, and volumes.
    """
    data = []
    failed_tickers = []
    for ticker_symbol in tickers:
        ticker = yf.Ticker(ticker_symbol)
        price, volume = get_valid_date(ticker, selected_date)
        if price is not None and volume is not None:
            data.append({'Ticker': ticker_symbol, 'Price': price, 'Volume': volume})
        else:
            failed_tickers.append(ticker_symbol)
    df = pd.DataFrame(data)
    return df, failed_tickers

# Function to calculate the sum of price * volume
def calculate_sum(df):
    if not df.empty:
        return (df['Price'] * df['Volume']).sum()
    return 0

# Function to fetch YPFD/YPF ratio
def fetch_ypf_ratio(selected_date):
    """
    Fetches the YPFD and YPF prices on the selected date or the closest previous date and calculates the ratio.
    """
    ypf_ticker = yf.Ticker('YPF')
    ypfd_ticker = yf.Ticker('YPFD.BA')
    
    ypf_price, _ = get_valid_date(ypf_ticker, selected_date)
    ypfd_price, _ = get_valid_date(ypfd_ticker, selected_date)
    
    if ypf_price is None or ypfd_price is None:
        st.error("Could not retrieve YPF or YPFD.BA data for the selected date.")
        return None
    if ypf_price == 0:
        st.error("YPF price is zero, cannot compute ratio.")
        return None
    return ypfd_price / ypf_price

# Main function for the Streamlit app
def main():
    st.title("Stock Volume-Weighted Price Comparison")

    # Date picker
    today = datetime.today().date()
    selected_date = st.date_input("Choose a date", today)
    
    if selected_date > today:
        st.error("Selected date cannot be in the future.")
        return

    # "Enter" button for data fetching
    if st.button("Enter to Fetch Data"):
        # Define ticker groups
        adrs_tickers = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS', 'LOMA', 'PAM', 'SUPV', 'TEO', 'TGS', 'YPF']
        panel_lider_tickers = [
            'GGAL.BA', 'YPFD.BA', 'PAMP.BA', 'TXAR.BA', 'ALUA.BA', 'CRES.BA', 'SUPV.BA', 'CEPU.BA',
            'BMA.BA', 'TGSU2.BA', 'TRAN.BA', 'EDN.BA', 'LOMA.BA', 'MIRG.BA', 'BBAR.BA', 'TGNO4.BA',
            'COME.BA', 'IRSA.BA', 'BYMA.BA', 'TECO2.BA', 'VALO.BA'
        ]
        panel_general_tickers = [
            'DGCU2.BA', 'MOLI.BA', 'CGPA2.BA', 'METR.BA', 'CECO2.BA', 'BHIP.BA', 'AGRO.BA', 'LEDE.BA',
            'CVH.BA', 'HAVA.BA', 'AUSO.BA', 'SEMI.BA', 'INVJ.BA', 'CTIO.BA', 'MORI.BA', 'HARG.BA',
            'GCLA.BA', 'SAMI.BA', 'BOLT.BA', 'MOLA.BA', 'CAPX.BA', 'OEST.BA', 'LONG.BA', 'GCDI.BA',
            'GBAN.BA', 'CELU.BA', 'FERR.BA', 'CADO.BA', 'GAMI.BA', 'PATA.BA', 'CARC.BA', 'BPAT.BA',
            'RICH.BA', 'INTR.BA', 'GARO.BA', 'FIPL.BA', 'GRIM.BA', 'DYCA.BA', 'POLL.BA', 'DOME.BA',
            'ROSE.BA', 'RIGO.BA', 'DGCE.BA', 'MTR.BA', 'HSAT.BA'
        ]

        st.markdown("### Fetching ADRs data...")
        adrs_df, adrs_failed = fetch_price_volume(adrs_tickers, selected_date)
        if not adrs_df.empty:
            adrs_value = calculate_sum(adrs_df)
            st.success(f"ADRs Sum: USD {adrs_value:,.2f}")
        else:
            adrs_value = 0
            st.warning("No ADRs data available for the selected date.")
        
        if adrs_failed:
            st.warning(f"Failed to fetch ADRs tickers: {', '.join(adrs_failed)}")

        st.markdown("### Fetching Panel Líder data...")
        panel_lider_df, panel_lider_failed = fetch_price_volume(panel_lider_tickers, selected_date)
        if not panel_lider_df.empty:
            panel_lider_sum = calculate_sum(panel_lider_df)
            ypfd_ratio = fetch_ypf_ratio(selected_date)
            if ypfd_ratio:
                panel_lider_value = panel_lider_sum / ypfd_ratio
                st.success(f"Panel Líder Sum: USD {panel_lider_value:,.2f}")
            else:
                panel_lider_value = 0
                st.error("Could not calculate Panel Líder due to YPFD/YPF ratio issue.")
        else:
            panel_lider_value = 0
            st.warning("No Panel Líder data available for the selected date.")
        
        if panel_lider_failed:
            st.warning(f"Failed to fetch Panel Líder tickers: {', '.join(panel_lider_failed)}")

        st.markdown("### Fetching Panel General data...")
        panel_general_df, panel_general_failed = fetch_price_volume(panel_general_tickers, selected_date)
        if not panel_general_df.empty:
            panel_general_sum = calculate_sum(panel_general_df)
            ypfd_ratio = fetch_ypf_ratio(selected_date)
            if ypfd_ratio:
                panel_general_value = panel_general_sum / ypfd_ratio
                st.success(f"Panel General Sum: USD {panel_general_value:,.2f}")
            else:
                panel_general_value = 0
                st.error("Could not calculate Panel General due to YPFD/YPF ratio issue.")
        else:
            panel_general_value = 0
            st.warning("No Panel General data available for the selected date.")
        
        if panel_general_failed:
            st.warning(f"Failed to fetch Panel General tickers: {', '.join(panel_general_failed)}")

        # Prepare data for treemap
        treemap_data = {
            'Category': ['ADRs', 'Panel Líder', 'Panel General'],
            'Value (USD)': [adrs_value, panel_lider_value, panel_general_value]
        }
        treemap_df = pd.DataFrame(treemap_data)

        # Display treemap
        st.markdown("### Tree Map of Values")
        try:
            fig = px.treemap(
                treemap_df, 
                path=['Category'], 
                values='Value (USD)', 
                title="Comparison of ADRs, Panel Líder, and Panel General",
                color='Value (USD)', 
                color_continuous_scale='Blues',
                hover_data={'Value (USD)': ':.2f'}
            )
            fig.update_traces(root_color='lightblue', selector=dict(type='treemap'))
            st.plotly_chart(fig)
        except ZeroDivisionError:
            st.error("Error displaying tree map. Division by zero occurred.")

if __name__ == "__main__":
    main()
