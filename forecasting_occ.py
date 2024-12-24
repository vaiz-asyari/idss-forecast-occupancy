import pickle
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

model = pickle.load(open('forecasting_occ.sav', 'rb'))

df = pd.read_excel("hotelx2.xlsx")
df['Month'] = pd.to_datetime(df['Bulan'], format='%Y-%m')
df.set_index(['Month'], inplace=True)

st.title('Forecasting Occupancy Rate')
months = st.slider("Determine the months", 1, 24, step=1)

forecasted_months = pd.date_range(df.index[-1], periods=months+1, freq='M')[1:]

future_predictions = []

# Normalisasi nilai terakhir sebelum prediksi
last_value = (df['Occ (%)'].values[-1] - df['Occ (%)'].min()) / (df['Occ (%)'].max() - df['Occ (%)'].min())

# Melakukan prediksi untuk setiap bulan ke depan
for month in range(months):
    # Menggunakan model untuk memprediksi
    prediction = model.predict(np.array([[last_value]]))
    future_predictions.append(prediction[0][0])
    last_value = prediction[0][0]  # Update input untuk prediksi berikutnya

# Denormalisasi hasil prediksi
future_predictions = np.array(future_predictions) * (df['Occ (%)'].max() - df['Occ (%)'].min()) + df['Occ (%)'].min()

# Menggabungkan data asli dan prediksi
predictions_df = pd.DataFrame(future_predictions, index=forecasted_months, columns=['Occ (%)'])

# Menampilkan DataFrame jika tombol ditekan
if st.button("Forecast"):
    col1, col2 = st.columns([2, 3])

    # Menggabungkan data asli dan prediksi
    combined_df = pd.concat([df, predictions_df])

    # Menambahkan kolom 'Bulan' dari index dan memformat sebagai 'MM-YYYY'
    combined_df['Bulan'] = combined_df.index.strftime('%m-%Y')

    # Mengatur urutan kolom agar 'Bulan' di awal
    combined_df = combined_df[['Bulan', 'Occ (%)']]

    # Format kolom 'Occ (%)' menjadi persen
    combined_df['Occ (%)'] = combined_df['Occ (%)'] * 100
    combined_df['Occ (%)'] = combined_df['Occ (%)'].map('{:,.3f}%'.format)

    # Styling tabel
    def highlight_forecast(row):
        if row['Bulan'] in predictions_df.index.strftime('%m-%Y'):
            return ['background-color: lightblue'] * len(row)
        return [''] * len(row)

    # Terapkan styling
    styled_table = combined_df.style.apply(highlight_forecast, axis=1)

    with col1:
        # Menampilkan tabel dengan styling tanpa index
        st.dataframe(styled_table, hide_index=True, width=1000)  # Menambah ukuran lebar tabel

    with col2:
        # Membuat plot dengan data asli dan data prediksi
        fig, ax = plt.subplots()

        # Plot data asli dengan garis abu-abu
        df['Occ (%)'].plot(ax=ax, style='--', color='gray', legend=True, label='Known Data')

        # Plot data prediksi dengan garis biru
        predictions_df['Occ (%)'].plot(ax=ax, color='blue', legend=True, label='Forecasted Data')

        # Menampilkan grafik
        st.pyplot(fig)