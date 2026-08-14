import streamlit as st

st.set_page_config(page_title="Tentang | Apriori", page_icon="ℹ️", layout="wide")

st.title("ℹ️ Tentang & Metodologi")

st.subheader("Judul Penelitian")
st.markdown(
    "**Rekomendasi Paket Penjualan Obat dan Suplemen Berdasarkan Pola Pembelian "
    "Menggunakan Algoritma Apriori**"
)

st.divider()

st.subheader("Ringkasan")
st.markdown(
    """
    Aplikasi ini mengimplementasikan *Market Basket Analysis* menggunakan algoritma
    **Apriori** untuk menemukan pola kombinasi produk obat & suplemen yang sering
    dibeli bersamaan, sebagai dasar penyusunan strategi *product bundling* pada
    apotek/toko obat.

    Dataset yang digunakan berisi **6.952 transaksi** penjualan sepanjang periode
    **2 Januari – 30 Mei 2025**.
    """
)

st.divider()

st.subheader("Alur Analisis (CRISP-DM)")
st.markdown(
    """
    1. **Data Understanding** — memuat data transaksi mentah (`Transaction`, `Tanggal`, `Items`)
    2. **Data Cleansing** — pengecekan missing value & duplikat, parsing tanggal,
       standarisasi nama item (uppercase, rapikan spasi) agar produk yang sama tidak
       terhitung berbeda akibat variasi penulisan
    3. **Exploratory Data Analysis** — distribusi jumlah item per transaksi & produk terlaris
    4. **Data Preprocessing** — transformasi ke matriks *one-hot encoding* menggunakan `TransactionEncoder`
    5. **Modeling** — algoritma **Apriori** untuk frequent itemsets, dilanjutkan
       `association_rules` untuk membentuk aturan asosiasi
    6. **Evaluasi** — analisis Support, Confidence, dan Lift, serta validasi stabilitas
       temporal (Training Jan–Apr vs Testing Mei)
    7. **Formulasi Rekomendasi** — penyusunan rancangan paket bundling berdasarkan
       rule ber-Lift tertinggi
    """
)

st.divider()

st.subheader("Parameter Model (Data Penuh)")
col1, col2, col3 = st.columns(3)
col1.metric("Minimum Support", "3%")
col2.metric("Minimum Confidence", "3%")
col3.metric("Minimum Lift", "> 1.0")

st.divider()

st.subheader("Batasan Penelitian")
st.markdown(
    """
    - Apriori bersifat **unsupervised** — tidak ada label/target, sehingga tidak
      ada metrik akurasi prediksi seperti pada klasifikasi/regresi. Pembagian data
      Training/Testing di sini digunakan untuk **validasi stabilitas pola**, bukan
      pengukuran akurasi.
    - `max_len=2` digunakan pada pembentukan frequent itemsets, sehingga rule yang
      dihasilkan berupa hubungan antar **pasangan item** (belum mencakup kombinasi
      3 item atau lebih).
    - Rule dengan Lift sangat tinggi banyak ditemukan pada **varian rasa/kemasan
      produk yang sama** (misalnya antar-rasa Woods Lozenges atau Cerebrofort),
      yang secara bisnis wajar terjadi namun perlu diinterpretasikan secara berhati-hati
      dalam penyusunan strategi bundling lintas kategori produk.
    - Hasil analisis bergantung pada kelengkapan & kualitas pencatatan data transaksi
      sumber.
    """
)

st.divider()

st.subheader("Tim Penyusun")
st.markdown(
    """
    - Mutia Afif Ramadhani
    - Nabilatus Salamah
    - Raihan Gibran Arla Putra

    **Dosen Pembimbing:** Dr. Damayanti, S.Kom., M.Kom.

    Fakultas Teknik dan Ilmu Komputer, Universitas Teknokrat Indonesia
    """
)
