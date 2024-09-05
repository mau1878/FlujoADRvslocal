import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Toggle debug mode
DEBUG_MODE = False  # Set to True to enable debug information

def get_valid_date(ticker, selected_date):
    """
    Fetches the latest available trading date for the ticker on or before the selected date.
    """
    start_date = selected_date - timedelta(days=7)
    end_date = selected_date + timedelta(days=1)
    try:
        ticker_data = ticker.history(start=start_date, end=end_date)
        if DEBUG_MODE:
            st.write(f"Fetched data for {ticker.ticker}: {ticker_data.head()}")  # Debugging line
        
        if ticker_data.empty:
            st.warning(f"No data available for {ticker.ticker} between {start_date} and {end_date}.")
            return None, None
        
        # Debug: Print available columns
        if DEBUG_MODE:
            st.write(f"Available columns for {ticker.ticker}: {ticker_data.columns}")
        
        # Check if 'Adj Close' exists, if not use the 'Close' column
        price_col = 'Adj Close' if 'Adj Close' in ticker_data.columns else 'Close'
        
        latest_valid_date = ticker_data.index.max()
        price = ticker_data[price_col].loc[latest_valid_date]
        volume = ticker_data['Volume'].loc[latest_valid_date]
        return price, volume
    except Exception as e:
        st.warning(f"Error fetching data for {ticker.ticker}: {e}")
        return None, None

def fetch_price_volume(tickers, selected_date, group_name):
    """
    Fetches the price and volume for each ticker on the selected date or the closest previous date.
    Returns a DataFrame with tickers, prices, and volumes.
    """
    data = []
    failed_tickers = []
    for ticker_symbol in tickers:
        ticker = yf.Ticker(ticker_symbol)
        if DEBUG_MODE:
            st.write(f"Processing ticker: {ticker_symbol}")  # Debugging line
        price, volume = get_valid_date(ticker, selected_date)
        if price is not None and volume is not None:
            data.append({'Ticker': ticker_symbol, 'Price': price, 'Volume': volume, 'Group': group_name})
        else:
            failed_tickers.append(ticker_symbol)
    df = pd.DataFrame(data)
    return df, failed_tickers

def calculate_sum(df):
    return (df['Price'] * df['Volume']).sum()

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
    return ypfd_price / ypf_price

def main():
    st.title("Stock Volume-Weighted Price Comparison")

    today = datetime.today().date()
    selected_date = st.date_input("Choose a date", today)
    
    if selected_date > today:
        st.error("Selected date cannot be in the future.")
        return

    if st.button("Fetch Data"):
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

        # Fetch data
        st.markdown("### Fetching ADRs data...")
        adrs_df, adrs_failed = fetch_price_volume(adrs_tickers, selected_date, 'ADRs')
        
        st.markdown("### Fetching Panel Lider data...")
        panel_lider_df, panel_lider_failed = fetch_price_volume(panel_lider_tickers, selected_date, 'Panel Lider')
        
        st.markdown("### Fetching Panel General data...")
        panel_general_df, panel_general_failed = fetch_price_volume(panel_general_tickers, selected_date, 'Panel General')

        # Concatenate all dataframes for treemaps
        all_data = pd.concat([adrs_df, panel_lider_df, panel_general_df], ignore_index=True)

        # Display first treemap
        if not all_data.empty:
            st.markdown("### Tree Map of Groups")
            fig_group = px.treemap(
                all_data, 
                path=['Group'], 
                values='Price', 
                title="Tree Map of Groups",
                color='Price', 
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_group, use_container_width=True)

            # Detailed data for second treemap
            detailed_data = []
            for group_name in all_data['Group'].unique():
                group_df = all_data[all_data['Group'] == group_name]
                if not group_df.empty:
                    detailed_data.append(group_df)
            
            if detailed_data:
                detailed_df = pd.concat(detailed_data, ignore_index=True)
                st.markdown("### Detailed Tree Map of Tickers within Groups")
                fig_detailed = px.treemap(
                    detailed_df, 
                    path=['Group', 'Ticker'], 
                    values='Price', 
                    title="Detailed View of Tickers within Groups",
                    color='Price', 
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_detailed, use_container_width=True)
            else:
                st.warning("No detailed data available for the tickers.")
        else:
            st.warning("No data available for the selected date.")

if __name__ == "__main__":
    main()
