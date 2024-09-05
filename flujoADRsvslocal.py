import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def get_valid_date(ticker, selected_date):
    """
    Fetches the latest available trading date for the ticker on or before the selected date.
    """
    start_date = selected_date - timedelta(days=7)
    end_date = selected_date + timedelta(days=1)
    try:
        ticker_data = ticker.history(start=start_date, end=end_date)
        if ticker_data.empty:
            st.warning(f"No data available for {ticker.ticker} between {start_date} and {end_date}.")
            return None, None
        latest_valid_date = ticker_data.index.max()
        price = ticker_data['Adj Close'].loc[latest_valid_date]
        volume = ticker_data['Volume'].loc[latest_valid_date]
        return price, volume
    except Exception as e:
        st.warning(f"Error fetching data for {ticker.ticker}: {e}")
        return None, None

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

        st.markdown("### Fetching ADRs data...")
        adrs_df, adrs_failed = fetch_price_volume(adrs_tickers, selected_date)
        st.write(f"ADRs Data: {adrs_df}")  # Debugging line
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
        st.write(f"Panel Líder Data: {panel_lider_df}")  # Debugging line
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
        st.write(f"Panel General Data: {panel_general_df}")  # Debugging line
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
        fig = px.treemap(
            treemap_df, 
            path=['Category'], 
            values='Value (USD)', 
            title="Comparison of ADRs, Panel Líder, and Panel General",
            color='Value (USD)', 
            color_continuous_scale='Blues',
            hover_data={'Value (USD)': ':.2f'}
        )
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig, use_container_width=True)

        # Plot data for comparison
        st.markdown("### Historical Comparison")
        comparison_data = {
            'Category': ['ADRs', 'Panel Líder', 'Panel General'],
            'Value (USD)': [adrs_value, panel_lider_value, panel_general_value]
        }
        comparison_df = pd.DataFrame(comparison_data)
        
        # Bar plot
        fig = px.bar(
            comparison_df, 
            x='Category', 
            y='Value (USD)', 
            title="Comparison of ADRs, Panel Líder, and Panel General",
            text='Value (USD)',
            color='Value (USD)',
            color_continuous_scale='Blues'
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
