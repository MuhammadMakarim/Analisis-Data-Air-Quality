import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob

st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

st.title("Dashboard Analisis Data Kualitas Udara - Proyek Akhir")

# --- DATA LOADING ---

# Pencarian otomatis file CSV di folder yang sama
csv_files = glob("*.csv") 
if len(csv_files) == 0:
    st.error("Tidak ditemukan file CSV di folder ini. Pastikan dataset sudah diekstrak.")
    st.stop()
else:
    main_file = None
    for file in csv_files:
        if 'air' in file.lower() or 'quality' in file.lower():
            main_file = file
            break
    if main_file is None:
        main_file = csv_files[0]  # fallback: ambil file pertama
    st.success(f"Menggunakan dataset: **{main_file}**")
    air_df = pd.read_csv(main_file, parse_dates=['datetime'])

# --- FILTER MARET 2013 ---
march_df = air_df[(air_df['year'] == 2013) & (air_df['month'] == 3)].copy()

# --- PERTANYAAN 1: RATA-RATA PM2.5 PER STASIUN ---
st.header("Rata-rata Harian PM2.5 per Stasiun (Maret 2013)")
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

st.markdown("""
**Insight:**
- Semua stasiun mengalami rata-rata PM2.5 yang tinggi di bulan Maret 2013.
- Stasiun Aotizhongxin tertinggi (hampir 120 µg/m³), diikuti Dongsi, Wanliu, Tiantan.
- Tidak ada stasiun dengan rata-rata di bawah 100 µg/m³.
""")

# --- PERTANYAAN 2: DISTRIBUSI KATEGORI PM2.5 PER STASIUN ---
st.header("Distribusi Kategori Kualitas Udara (PM2.5) per Stasiun (Maret 2013)")
bins = [0, 12, 35.4, 55.4, 150.4, float('inf')]
labels = ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy', 'Very Unhealthy']
march_df['PM2.5_category'] = pd.cut(march_df['PM2.5'], bins=bins, labels=labels)

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

st.markdown("""
**Insight:**
- Kategori “Unhealthy for Sensitive” dan “Unhealthy” mendominasi di hampir semua stasiun.
- Kategori “Very Unhealthy” juga signifikan, kategori “Good” dan “Moderate” jauh lebih sedikit.
""")

st.header("Clustering Rata-rata PM2.5 per Stasiun (Binning Manual, Maret 2013)")
mean_pm25_station['Cluster_PM2.5'] = pd.cut(mean_pm25_station['pm25_mean'], bins=bins, labels=labels)

fig3, ax3 = plt.subplots(figsize=(14, 7))
sns.barplot(x='station', y='pm25_mean', hue='Cluster_PM2.5', data=mean_pm25_station, palette='Reds', ax=ax3)
ax3.set_title('Cluster Rata-rata PM2.5 per Stasiun (Maret 2013)')
ax3.set_xlabel('Stasiun')
ax3.set_ylabel('Rata-rata PM2.5')
plt.xticks(rotation=45)
plt.legend(title='Cluster')
plt.tight_layout()
st.pyplot(fig3)

st.markdown("""
**Conclution:**

Conclution pertanyaan 1

Dari hasil analisis ini, saya menyimpulkan bahwa polusi udara selama bulan Maret 2013 merupakan masalah serius di seluruh stasiun pemantauan, tanpa terkecuali. Dengan rata-rata PM2.5 yang tinggi di setiap lokasi, masyarakat di sekitar stasiun-stasiun tersebut sangat berpotensi terpapar udara yang tidak sehat setiap harinya. Hal ini memperjelas perlunya intervensi dan kebijakan yang serius dari pemerintah maupun pihak terkait untuk menekan sumber polusi, terutama di stasiun-stasiun dengan rata-rata PM2.5 tertinggi seperti Aotizhongxin dan Dongsi. Selain itu, hasil ini juga merupakan alarm bagi masyarakat untuk lebih peduli terhadap kualitas udara di lingkungan tempat tinggal mereka.

Conclution pertanyaan 2

Berdasarkan distribusi kategori kualitas udara, saya menyadari bahwa masyarakat di sekitar stasiun-stasiun pemantauan tidak hanya sesekali, tetapi hampir setiap hari dihadapkan pada risiko polusi udara yang tinggi. Kategori “Unhealthy” bahkan menjadi yang paling dominan, baik di stasiun dengan rata-rata PM2.5 tertinggi maupun yang lebih rendah. Ini artinya, masalah kualitas udara tidak hanya terjadi di lokasi tertentu saja, tetapi merupakan masalah bersama di seluruh wilayah pemantauan. Dengan kondisi seperti ini, sangat penting untuk melakukan edukasi publik tentang bahaya polusi udara dan mendorong pemerintah untuk memperkuat kebijakan pengendalian emisi, terutama di sektor transportasi dan industri.
""")

with st.expander("Lihat Data Rata-rata & Kategori per Stasiun"):
    st.dataframe(mean_pm25_station)

st.write("Dashboard ini menampilkan analisis kualitas udara berdasarkan data yang telah dibersihkan.")

st.markdown("""
---
© 2025 | Muhammad Makarim,  Analisis Data Air Quality | MC006D5Y1427 |
""")