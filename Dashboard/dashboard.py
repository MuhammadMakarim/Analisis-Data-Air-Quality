import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gdown

st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("Dashboard Analisis Data Kualitas Udara")

st.markdown("""

Dashboard ini menyajikan analisis dan visualisasi data kualitas udara yang mencakup pengukuran berbagai polutan seperti PM2.5, PM10, SO2, NO2, CO, dan O3.  
Pengguna dapat melakukan filter berdasarkan waktu, lokasi (stasiun), dan kategori kualitas udara untuk mengeksplorasi pola konsentrasi polutan secara mendalam.  
""")

# --- DATA LOADING ---
url = 'https://drive.google.com/uc?id=16FEIHlXfVrWpTiRg_dVfvtUw8x4cg1pJ'
gdown.download(url, 'dataset.csv', quiet=True)
air_df = pd.read_csv('dataset.csv', parse_dates=['datetime'])

# --- HEATMAP KORELASI TARUH DI BAGIAN ATAS ---
st.header("Heatmap Korelasi Antar Variabel")

cols_corr = ['year','month','day','hour','PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
corr_matrix = air_df[cols_corr].corr()

fig_corr, ax_corr = plt.subplots(figsize=(14, 12))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": .75},
    ax=ax_corr
)
ax_corr.set_title("Heatmap Korelasi Antar Variabel")
st.pyplot(fig_corr)

st.write("""
**Insight:** Heatmap ini memperlihatkan kekuatan dan arah hubungan antar variabel utama dalam dataset.  
Warna merah menunjukkan korelasi positif kuat, biru menunjukkan korelasi negatif kuat, dan putih mendekati nol (tidak berkorelasi).  
Anotasi angka membantu melihat nilai korelasi secara kuantitatif.
""")

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data")

min_date = air_df['datetime'].dt.date.min()
max_date = air_df['datetime'].dt.date.max()
start_date = st.sidebar.date_input("Tanggal Mulai", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Tanggal Akhir", max_date, min_value=min_date, max_value=max_date)
if start_date > end_date:
    st.sidebar.error("Tanggal mulai harus sebelum atau sama dengan tanggal akhir")

stations = air_df['station'].unique()
selected_stations = st.sidebar.multiselect("Pilih Stasiun", stations, default=stations.tolist())

categories = air_df['PM2.5_category'].unique()
selected_categories = st.sidebar.multiselect("Pilih Kategori PM2.5", categories, default=categories.tolist())

param_options = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
selected_param = st.sidebar.selectbox("Pilih Parameter untuk Visualisasi", param_options)

# Filter data sesuai input tanpa filter jam
filtered_df = air_df[
    (air_df['datetime'].dt.date >= start_date) &
    (air_df['datetime'].dt.date <= end_date) &
    (air_df['station'].isin(selected_stations)) &
    (air_df['PM2.5_category'].isin(selected_categories))
].copy()

# Tambah kolom year & month untuk heatmap dan analisis
filtered_df['year'] = filtered_df['datetime'].dt.year
filtered_df['month'] = filtered_df['datetime'].dt.month

# --- Rata-rata Tahunan ---
st.header(f"Rata-rata Tahunan {selected_param}")
param_yearly_mean = filtered_df.groupby('year')[selected_param].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(param_yearly_mean['year'], param_yearly_mean[selected_param], marker='o', linestyle='-')
ax.set_title(f"Rata-rata Tahunan {selected_param}")
ax.set_xlabel("Tahun")
ax.set_ylabel(f"Rata-rata {selected_param} (µg/m³)")
ax.grid(True)
st.pyplot(fig)

st.write("""
**Insight:** Grafik ini menampilkan tren rata-rata tahunan konsentrasi parameter polutan yang dipilih berdasarkan filter tanggal, stasiun, dan kategori kualitas udara.  
Pengguna dapat melihat apakah polusi udara parameter tersebut cenderung meningkat, menurun, atau stabil selama tahun-tahun yang tersedia.
""")

# --- Heatmap Rata-rata per Bulan & Tahun ---
st.header(f"Heatmap Rata-rata {selected_param} per Bulan dan Tahun")

pivot_table_month_year = filtered_df.pivot_table(
    index='year',
    columns='month',
    values=selected_param,
    aggfunc='mean'
)

fig_heatmap_month_year, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(
    pivot_table_month_year,
    ax=ax,
    cmap="YlOrRd",
    linewidths=0.3,
    linecolor='gray',
    cbar_kws={'label': f'Rata-rata {selected_param}'},
    annot=True,
    fmt=".1f"
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Tahun")
ax.set_title(f"Heatmap Rata-rata {selected_param} per Bulan dan Tahun")
plt.yticks(rotation=0)
plt.xticks(rotation=0)
st.pyplot(fig_heatmap_month_year)

st.write("""
**Insight:** Heatmap ini memperlihatkan variasi rata-rata konsentrasi parameter polutan yang dipilih sepanjang bulan dan tahun.  
Pengguna bisa mengamati pola musiman (per bulan) serta tren tahunan secara visual.
""")

# --- Pertanyaan 1 ---
st.header("Pertanyaan 1: Rata-rata Harian PM2.5 per Stasiun (Maret 2013)")

march_df = filtered_df[
    (filtered_df['datetime'].dt.year == 2013) & (filtered_df['datetime'].dt.month == 3)
].copy()

mean_pm25_station = (
    march_df.groupby('station')['PM2.5']
    .mean()
    .reset_index()
    .rename(columns={'PM2.5': 'pm25_mean'})
)

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x='station', y='pm25_mean', data=mean_pm25_station, palette='Blues_r', ax=ax1)
ax1.set_title('Rata-rata harian PM2.5 per Stasiun pada bulan Maret 2013')
ax1.set_xlabel('Stasiun')
ax1.set_ylabel('Rata-rata PM2.5')
ax1.grid(axis='y', linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
st.pyplot(fig1)

st.write("""
**Insight:** Grafik ini menunjukkan rata-rata konsentrasi PM2.5 selama bulan Maret 2013 untuk tiap stasiun sesuai dengan filter yang diterapkan.  
Dari sini, dapat diketahui stasiun mana yang memiliki tingkat polusi PM2.5 tertinggi selama periode tersebut.
""")

# --- Pertanyaan 2 ---
st.header("Pertanyaan 2: Distribusi Kategori Kualitas Udara (PM2.5) per Stasiun")

fig2, ax2 = plt.subplots(figsize=(14, 8))
sns.countplot(
    data=march_df,
    x='station',
    hue='PM2.5_category',
    palette='YlOrRd',
    ax=ax2
)
ax2.set_title('Distribusi Kategori Kualitas Udara (PM2.5) per Stasiun pada bulan Maret 2013')
ax2.set_xlabel('Stasiun')
ax2.set_ylabel('Jumlah Observasi')
plt.xticks(rotation=45)
plt.legend(title='Kategori PM2.5')
plt.tight_layout()
st.pyplot(fig2)

st.write("""
**Insight:** Diagram batang bertumpuk ini memperlihatkan distribusi jumlah pengamatan tiap kategori kualitas udara berdasarkan PM2.5 per stasiun selama bulan Maret 2013.  
Ini membantu memahami frekuensi kejadian kualitas udara baik hingga tidak sehat di setiap lokasi.
""")
