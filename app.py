import streamlit as st
from utils.data_processing import (
    load_and_clean_data, encode_transactions, run_apriori, compute_stability
)

st.set_page_config(
    page_title="Rekomendasi Paket Obat & Suplemen | Apriori",
    page_icon="💊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Load data (cached — hanya dihitung ulang kalau file sumber berubah)
# ---------------------------------------------------------------------------
with st.spinner("Memuat & membersihkan data transaksi..."):
    df = load_and_clean_data()
    df_encoded = encode_transactions(df)
    frequent_itemsets, rules = run_apriori(df_encoded, min_support=0.03, min_confidence=0.03, min_lift=1.0)

# Simpan ke session_state supaya halaman lain tidak perlu load ulang
st.session_state["df"] = df
st.session_state["df_encoded"] = df_encoded

# ---------------------------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0E7C7B 0%, #4CAF93 100%);
                padding: 2.2rem 2rem; border-radius: 14px; margin-bottom: 1.8rem;">
        <p style="color:#E6F5F3; font-size:0.95rem; letter-spacing:1.5px;
                   text-transform:uppercase; margin-bottom:0.4rem;">
            Proyek Akhir Data Mining · Market Basket Analysis
        </p>
        <h1 style="color:white; font-size:2rem; margin-bottom:0.6rem; line-height:1.3;">
            💊 Rekomendasi Paket Penjualan Obat & Suplemen
            <br>Berdasarkan Pola Pembelian dengan Algoritma Apriori
        </h1>
        <p style="color:#E6F5F3; font-size:1rem; max-width:700px;">
            Menemukan kombinasi produk yang sering dibeli bersamaan dari data transaksi
            apotek, sebagai dasar penyusunan strategi <i>product bundling</i>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# METRIC CARDS
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Transaksi", f"{df.shape[0]:,}")
with col2:
    st.metric("Item Unik", f"{df_encoded.shape[1]}")
with col3:
    st.metric("Rentang Data", "Jan – Mei 2025")
with col4:
    st.metric("Rata-rata Item/Transaksi", f"{df['Jumlah_Item'].mean():.2f}")
with col5:
    st.metric("Rules Ditemukan", f"{len(rules)}")

st.divider()

# ---------------------------------------------------------------------------
# RINGKASAN ALUR PROJECT
# ---------------------------------------------------------------------------
st.subheader("Alur Analisis (CRISP-DM)")

steps = [
    ("1. Data Understanding", "Memuat 6.952 transaksi penjualan obat & suplemen (2 Jan – 30 Mei 2025)."),
    ("2. Data Cleansing", "Standarisasi nama item, parsing tanggal, pengecekan duplikat & missing value."),
    ("3. EDA", "Menggali distribusi jumlah item per transaksi & produk terlaris."),
    ("4. Modeling — Apriori", "Membentuk frequent itemsets & association rules (Support, Confidence, Lift)."),
    ("5. Validasi Stabilitas", "Membandingkan rules periode Training (Jan–Apr) vs Testing (Mei)."),
    ("6. Rekomendasi Bundling", "Menyusun paket produk berdasarkan rules ber-Lift tertinggi."),
]

cols = st.columns(3)
for i, (title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(
            f"""
            <div style="background:#F4F9F9; border-left:4px solid #0E7C7B;
                        border-radius:8px; padding:1rem; margin-bottom:1rem; min-height:130px;">
                <p style="font-weight:600; color:#0E7C7B; margin-bottom:0.3rem;">{title}</p>
                <p style="font-size:0.88rem; color:#3A4A4A; margin:0;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

st.subheader("Jelajahi Aplikasi")
st.markdown(
    """
    Gunakan menu di sidebar (kiri) untuk menjelajahi setiap tahapan analisis:

    - **📊 Eksplorasi Data** — statistik & visualisasi karakteristik transaksi
    - **🔗 Association Rules** — eksplorasi aturan asosiasi dengan parameter yang bisa diatur
    - **💊 Simulasi Rekomendasi** — coba sendiri fitur rekomendasi berbasis keranjang belanja
    - **📦 Paket Bundling** — rancangan paket produk hasil analisis
    - **✅ Validasi Stabilitas** — pengujian konsistensi pola pembelian dari waktu ke waktu
    - **ℹ️ Tentang** — metodologi & batasan penelitian
    """
)
