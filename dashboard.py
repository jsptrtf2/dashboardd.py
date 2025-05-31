import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# --------------------------------------------
# 1. Muat dataset harian dan per-jam
# --------------------------------------------
df_harian = pd.read_csv('data/day.csv')
df_per_jam = pd.read_csv('data/hour.csv')

# Ubah kolom tanggal ('dteday') menjadi tipe datetime
df_harian['dteday'] = pd.to_datetime(df_harian['dteday'])

# --------------------------------------------
# 2. Judul Aplikasi Streamlit
# --------------------------------------------
st.title("Dashboard Analisis Penyewaan Sepeda")

# --------------------------------------------
# 3. Menu Pilihan Visualisasi di Sidebar
# --------------------------------------------
st.sidebar.header("Visualisasi yang Tersedia")
pilihan_grafik = st.sidebar.selectbox(
    "Silakan pilih tipe grafik:",
    [
        "Distribusi Penyewaan Sepeda",
        "Pola Berdasarkan Cuaca",
        "Tren Harian & Bulanan",
        "RFM Analysis",
        "Clustering"
    ]
)

# --------------------------------------------
# 4. Filter Interaktif di Sidebar
# --------------------------------------------
st.sidebar.header("Filter Data")

# Opsi musim (dengan tambahan pilihan "Semua Musim")
opsi_musim = ['Semua Musim'] + list(df_harian['season'].unique())
# Opsi kondisi cuaca (dengan tambahan pilihan "Semua Cuaca")
opsi_cuaca = ['Semua Cuaca'] + list(df_harian['weathersit'].unique())

# Dropdown untuk memilih musim
filter_musim = st.sidebar.selectbox("Pilih Musim:", opsi_musim, key="pilih_musim")
# Dropdown untuk memilih kondisi cuaca
filter_cuaca = st.sidebar.selectbox("Pilih Cuaca:", opsi_cuaca, key="pilih_cuaca")

# --------------------------------------------
# 5. Filter Berdasarkan Rentang Tanggal
# --------------------------------------------
# Tentukan batas terendah dan tertinggi tanggal pada data
tanggal_min = df_harian['dteday'].min().date()
tanggal_maks = df_harian['dteday'].max().date()

# Opsi pemilihan tanggal awal dan akhir
tanggal_awal = st.sidebar.date_input("Mulai Tanggal:", tanggal_min, key="picker_tanggal_awal")
tanggal_akhir = st.sidebar.date_input("Sampai Tanggal:", tanggal_maks, key="picker_tanggal_akhir")

# Validasi: jika tanggal_awal > tanggal_akhir, tampilkan pesan error
if tanggal_awal > tanggal_akhir:
    st.sidebar.error("⛔ Tanggal awal tidak boleh setelah tanggal akhir!")

# Ubah kembali ke tipe datetime untuk difilter
tanggal_awal = pd.to_datetime(tanggal_awal)
tanggal_akhir = pd.to_datetime(tanggal_akhir)

# --------------------------------------------
# 6. Proses Filtering Data
# --------------------------------------------
# Ambil data di antara tanggal_awal dan tanggal_akhir
df_terfilter = df_harian[
    (df_harian['dteday'] >= tanggal_awal) &
    (df_harian['dteday'] <= tanggal_akhir)
]

# Jika dipilih musim tertentu (bukan "Semua Musim"), saring lagi
if filter_musim != 'Semua Musim':
    df_terfilter = df_terfilter[df_terfilter['season'] == filter_musim]

# Jika dipilih cuaca tertentu (bukan "Semua Cuaca"), saring lagi
if filter_cuaca != 'Semua Cuaca':
    df_terfilter = df_terfilter[df_terfilter['weathersit'] == filter_cuaca]

# Jika hasil filter kosong, tampilkan peringatan; jika tidak, tampilkan potongan data
if df_terfilter.empty:
    st.warning("⚠️ Tidak ada data sesuai dengan filter yang dipilih.")
else:
    st.header("Data Setelah Proses Filtering")
    st.write(df_terfilter.head())

# --------------------------------------------
# 7. Pilihan Visualisasi Berdasarkan menu
# --------------------------------------------
# 7.a. Distribusi Jumlah Penyewaan Sepeda
if pilihan_grafik == "Distribusi Penyewaan Sepeda":
    st.subheader("Distribusi Jumlah Penyewaan Sepeda (Harian)")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(
        df_terfilter['cnt'],
        bins=30,
        kde=True,
        color='blue',
        ax=ax
    )
    ax.set_title("Distribusi Jumlah Penyewaan Sepeda per Hari")
    ax.set_xlabel("Jumlah Penyewaan")
    ax.set_ylabel("Frekuensi")
    st.pyplot(fig)

# 7.b. Pola Berdasarkan Kondisi Cuaca
elif pilihan_grafik == "Pola Berdasarkan Cuaca":
    st.subheader("Pengaruh Cuaca, Suhu, dan Kelembaban terhadap Jumlah Penyewaan")

    # Tampilkan informasi jumlah baris setelah filtering
    st.write("Jumlah data setelah filter:", df_terfilter.shape)

    if df_terfilter.empty:
        st.warning("❌ Data kosong setelah filter. Ubah pilihan musim/cuaca.")
    else:
        # Ubah kolom 'weathersit' menjadi tipe string untuk memudahkan plotting
        df_terfilter['weathersit'] = df_terfilter['weathersit'].astype(str)

        # Tampilkan nilai unik di kolom weathersit (untuk debugging/interaktif)
        st.write("✅ Nilai unik weathersit:", df_terfilter['weathersit'].unique())

        # Buat dropdown baru khusus untuk memilih kode cuaca yang ada di df_terfilter
        opsi_cuaca_unik = ['Semua Cuaca'] + sorted(df_terfilter['weathersit'].unique())
        cuaca_terpilih = st.sidebar.selectbox(
            "Pilih Kode Cuaca:", opsi_cuaca_unik, key="dropdown_cuaca_unik"
        )

        # Tampilkan pilihan cuaca yang diambil (debugging)
        st.write("✅ Cuaca terpilih:", cuaca_terpilih)

        # Jika cuaca_terpilih bukan "Semua Cuaca", saring kembali
        if cuaca_terpilih != "Semua Cuaca":
            df_terfilter = df_terfilter[df_terfilter['weathersit'] == cuaca_terpilih]

        # Tampilkan ukuran dataset setelah saringan cuaca
        st.write("Jumlah data pasca filter cuaca:", df_terfilter.shape)

        if df_terfilter.empty:
            st.warning("❌ Data kosong setelah filter cuaca. Coba opsi lain.")
        else:
            # Tampilkan jumlah nilai NaN di kolom 'cnt', lalu buang baris jika ada NaN
            st.write("Jumlah NaN pada 'cnt':", df_terfilter['cnt'].isnull().sum())
            df_terfilter = df_terfilter.dropna(subset=['cnt'])

            # Tentukan urutan kategori cuaca (kode 1–4)
            urutan_cuaca = ['1', '2', '3', '4']

            # ----- Visualisasi Boxplot: Cuaca vs Jumlah Penyewaan -----
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(
                x='weathersit',
                y='cnt',
                data=df_terfilter,
                hue='weathersit',
                palette='viridis',
                legend=False,
                ax=ax,
                order=urutan_cuaca
            )
            ax.set_title("Pola Penyewaan Sepeda berdasarkan Kode Cuaca")
            ax.set_xlabel("Kode Cuaca (1=Cerah, 2=Berkabut, 3=Hujan, 4=Salju)")
            ax.set_ylabel("Jumlah Penyewaan")
            st.pyplot(fig)

            # ----- Visualisasi Regresi: Suhu vs Jumlah Penyewaan -----
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.regplot(
                x='temp',
                y='cnt',
                data=df_terfilter,
                scatter_kws={'alpha': 0.5},
                line_kws={'color': 'red'},
                ax=ax
            )
            ax.set_title("Hubungan Suhu (Ternormalisasi) dan Jumlah Penyewaan")
            ax.set_xlabel("Suhu (Normalized)")
            ax.set_ylabel("Jumlah Penyewaan")
            st.pyplot(fig)

            # ----- Visualisasi Regresi: Kelembaban vs Jumlah Penyewaan -----
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.regplot(
                x='hum',
                y='cnt',
                data=df_terfilter,
                scatter_kws={'alpha': 0.5},
                line_kws={'color': 'blue'},
                ax=ax
            )
            ax.set_title("Hubungan Kelembaban dan Jumlah Penyewaan")
            ax.set_xlabel("Kelembaban")
            ax.set_ylabel("Jumlah Penyewaan")
            st.pyplot(fig)

# 7.c. Tren Harian & Tren Bulanan
elif pilihan_grafik == "Tren Harian & Bulanan":
    st.subheader("Tren Penyewaan Sepeda Berdasarkan Waktu")

    # Ambil kolom numerik dari df_per_jam, lalu hitung rata-rata 'cnt' per jam (hr)
    df_jam_numerik = df_per_jam.select_dtypes(include=['number'])
    rata_per_jam = df_jam_numerik.groupby('hr').mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        x='hr',
        y='cnt',
        data=rata_per_jam,
        marker='o',
        color='purple',
        ax=ax
    )
    ax.set_title("Rata-Rata Penyewaan per Jam")
    ax.set_xlabel("Jam (0–23)")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

    # Hitung rata-rata 'cnt' per bulan (mnth) dari df_harian
    rata_per_bulan = df_harian.groupby('mnth').mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        x='mnth',
        y='cnt',
        data=rata_per_bulan,
        marker='o',
        color='orange',
        ax=ax
    )
    ax.set_title("Tren Penyewaan Sepeda per Bulan")
    ax.set_xlabel("Bulan (1–12)")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

# 7.d. RFM Analysis
elif pilihan_grafik == "RFM Analysis":
    st.subheader("RFM Analysis untuk Segmentasi Pengguna")

    # Hitung recency: selisih hari antara tanggal terakhir di data dengan setiap baris
    tanggal_terakhir = pd.to_datetime(df_harian['dteday']).max()
    df_harian['Recency'] = (tanggal_terakhir - pd.to_datetime(df_harian['dteday'])).dt.days

    # Grup berdasarkan hari dalam seminggu (weekday), lalu hitung:
    #   - Recency minimum (terbaru)
    #   - Frequency (jumlah baris/pengamatan)
    #   - Monetary (total penyewaan 'cnt')
    df_rfm = df_harian.groupby('weekday').agg({
        'Recency': 'min',
        'cnt': ['count', 'sum']
    }).reset_index()

    # Perbaiki nama kolom agar lebih sederhana
    df_rfm.columns = ['weekday', 'Recency', 'Frequency', 'Monetary']

    # Tampilkan korelasi antar metrik RFM
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        df_rfm[['Recency', 'Frequency', 'Monetary']].corr(),
        annot=True,
        cmap='coolwarm',
        linewidths=0.5,
        ax=ax
    )
    ax.set_title("Heatmap Korelasi RFM")
    st.pyplot(fig)

    # Insight dasar yang muncul dari analisis RFM
    st.write("""
    **Catatan RFM Analysis:**
    - Pengguna dengan nilai Frequency tinggi biasanya memiliki Recency yang rendah.
    - Pengguna dengan Monetary tinggi cenderung lebih setia (stable).
    - Rekomendasi: Program reward/loyalty untuk pengguna ber-Frequency tinggi agar retensi meningkat.
    """)

    st.write(df_rfm)

# 7.e. Clustering (Sederhana dengan Kategori Waktu)
elif pilihan_grafik == "Clustering":
    st.subheader("Clustering: Pola Penggunaan Berdasarkan Waktu")

    # Bagi kolom 'hr' menjadi kategori waktu (Malam, Pagi, Siang, Sore)
    df_per_jam['kategori_waktu'] = pd.cut(
        df_per_jam['hr'],
        bins=[0, 6, 12, 18, 24],
        labels=['Malam', 'Pagi', 'Siang', 'Sore']
    )

    # Hitung total penyewaan per kategori waktu
    klaster_waktu = df_per_jam.groupby('kategori_waktu').agg({'cnt': 'sum'}).reset_index()

    # Buat barplot untuk melihat distribusi penyewaan berdasarkan kategori waktu
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x='kategori_waktu',
        y='cnt',
        data=klaster_waktu,
        palette='coolwarm',
        ax=ax
    )
    ax.set_title("Jumlah Penyewaan per Kategori Waktu (Harian)")
    ax.set_xlabel("Kategori Waktu")
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)

    st.write("""
    **Wawasan Clustering:**
    - Pagi dan sore hari menunjukkan puncak penyewaan tertinggi.
    - Jam malam (00–06) cenderung paling sepi.
    - Saran strategi: Diskon khusus jam malam atau tambahan armada pada jam sibuk.
    """)

# 8. Footer/Info Pembuat di Sidebar
st.sidebar.text("Dashboard by Jaya Saputra")
