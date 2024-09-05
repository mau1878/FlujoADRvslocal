import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def get_valid_date(ticker, selected_date):
    start_date = selected_date - timedelta(days=7)
    end_date = selected_date + timedelta(days=1)
    try:
        ticker_data = ticker.history(start=start_date, end=end_date)
        if ticker_data.empty:
            st.warning(f"No hay datos disponibles para {ticker.ticker} entre {start_date} y {end_date}.")
            return None, None
        
        price_col = 'Adj Close' if 'Adj Close' in ticker_data.columns else 'Close'
        
        latest_valid_date = ticker_data.index.max()
        price = ticker_data[price_col].loc[latest_valid_date]
        volume = ticker_data['Volume'].loc[latest_valid_date]
        return price, volume
    except Exception as e:
        st.warning(f"Error al obtener datos para {ticker.ticker}: {e}")
        return None, None

def fetch_price_volume(tickers, selected_date):
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
    ypf_ticker = yf.Ticker('YPF')
    ypfd_ticker = yf.Ticker('YPFD.BA')
    
    ypf_price, _ = get_valid_date(ypf_ticker, selected_date)
    ypfd_price, _ = get_valid_date(ypfd_ticker, selected_date)
    
    if ypf_price is None or ypfd_price is None:
        st.error("No se pudo recuperar datos de YPF o YPFD.BA para la fecha seleccionada.")
        return None
    return ypfd_price / ypf_price

def add_watermark(fig, text="MTaurus - X:mtaurus_ok"):
    fig.update_layout(
        annotations=[
            dict(
                text=text,
                xref="paper", yref="paper",
                x=0.99, y=0.01,
                showarrow=False,
                font=dict(size=12, color="grey"),
                align="right"
            )
        ]
    )
    return fig

def main():
    st.title("Comparación de Volumen en Dólares por Acción")

    today = datetime.today().date()
    selected_date = st.date_input("Selecciona una fecha", today)
    
    if selected_date > today:
        st.error("La fecha seleccionada no puede estar en el futuro.")
        return

    title_font_size = st.slider("Tamaño de fuente del título", 10, 50, 24)
    axis_font_size = st.slider("Tamaño de fuente de los ejes", 10, 50, 18)
    label_font_size = st.slider("Tamaño de fuente de las etiquetas", 10, 50, 14)

    if st.button("Obtener Datos"):
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

        st.markdown("### Obtención de datos ADRs...")
        adrs_df, adrs_failed = fetch_price_volume(adrs_tickers, selected_date)
        if not adrs_df.empty:
            adrs_value = calculate_sum(adrs_df)
            st.success(f"Suma ADRs: USD {adrs_value:,.2f}")
        else:
            adrs_value = 0
            st.warning("No hay datos disponibles para ADRs en la fecha seleccionada.")
        
        if adrs_failed:
            st.warning(f"Fallo al obtener datos de ADRs: {', '.join(adrs_failed)}")

        st.markdown("### Obtención de datos Panel Líder...")
        panel_lider_df, panel_lider_failed = fetch_price_volume(panel_lider_tickers, selected_date)
        if not panel_lider_df.empty:
            panel_lider_sum = calculate_sum(panel_lider_df)
            ypfd_ratio = fetch_ypf_ratio(selected_date)
            if ypfd_ratio:
                panel_lider_value = panel_lider_sum / ypfd_ratio
                st.success(f"Suma Panel Líder: USD {panel_lider_value:,.2f}")
            else:
                panel_lider_value = 0
                st.error("No se pudo calcular el Panel Líder debido a un problema con la razón YPFD/YPF.")
        else:
            panel_lider_value = 0
            st.warning("No hay datos disponibles para Panel Líder en la fecha seleccionada.")
        
        if panel_lider_failed:
            st.warning(f"Fallo al obtener datos de Panel Líder: {', '.join(panel_lider_failed)}")

        st.markdown("### Obtención de datos Panel General...")
        panel_general_df, panel_general_failed = fetch_price_volume(panel_general_tickers, selected_date)
        if not panel_general_df.empty:
            panel_general_sum = calculate_sum(panel_general_df)
            ypfd_ratio = fetch_ypf_ratio(selected_date)
            if ypfd_ratio:
                panel_general_value = panel_general_sum / ypfd_ratio
                st.success(f"Suma Panel General: USD {panel_general_value:,.2f}")
            else:
                panel_general_value = 0
                st.error("No se pudo calcular el Panel General debido a un problema con la razón YPFD/YPF.")
        else:
            panel_general_value = 0
            st.warning("No hay datos disponibles para Panel General en la fecha seleccionada.")
        
        if panel_general_failed:
            st.warning(f"Fallo al obtener datos de Panel General: {', '.join(panel_general_failed)}")

        if adrs_df.empty and panel_lider_df.empty and panel_general_df.empty:
            st.warning("No hay datos disponibles para ninguna categoría.")
            return

        fig = px.bar(
            x=["ADRs", "Panel Líder", "Panel General"],
            y=[adrs_value, panel_lider_value, panel_general_value],
            labels={"x": "Categoría", "y": "Volumen en USD"},
            title="Comparación de Volumen en Dólares por Acción",
            color=["ADRs", "Panel Líder", "Panel General"],
            color_discrete_map={"ADRs": "blue", "Panel Líder": "green", "Panel General": "red"}
        )
        fig.update_layout(
            title_text='Comparación de Volumen en Dólares por Acción',
            title_font_size=title_font_size,
            xaxis_title='Categoría',
            xaxis_title_font_size=label_font_size,
            yaxis_title='Volumen en USD',
            yaxis_title_font_size=label_font_size,
            xaxis_tickfont_size=axis_font_size,
            yaxis_tickfont_size=axis_font_size,
            xaxis_title_font=dict(size=label_font_size),
            yaxis_title_font=dict(size=label_font_size)
        )
        fig = add_watermark(fig)
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
