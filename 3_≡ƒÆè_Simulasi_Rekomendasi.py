import streamlit as st
from utils.data_processing import (
    load_and_clean_data, encode_transactions, run_apriori,
    get_all_items, get_recommendations,
)

st.set_page_config(page_title="Simulasi Rekomendasi | Apriori", page_icon="💊", layout="wide")

df = st.session_state.get("df") or load_and_clean_data()
df_encoded = st.session_state.get("df_encoded") or encode_transactions(df)

st.title("💊 Simulasi Rekomendasi Produk")
st.markdown(
    "Fitur ini mensimulasikan skenario kasir: pilih produk yang sedang dibeli "
    "customer (bisa lebih dari satu), lalu sistem akan menyarankan produk "
    "tambahan berdasarkan **association rules** yang telah ditemukan dari pola "
    "pembelian historis."
)

# Rules dihasilkan dengan parameter yang lebih longgar (recall lebih tinggi)
# supaya simulasi tetap bisa memberi saran untuk lebih banyak kombinasi produk.
with st.spinner("Menyiapkan model rekomendasi..."):
    _, rules = run_apriori(df_encoded, min_support=0.01, min_confidence=0.05, min_lift=1.0)

all_items = get_all_items(df_encoded)

st.divider()

col_input, col_result = st.columns([1, 1.4])

with col_input:
    st.subheader("🛒 Keranjang Belanja")
    selected = st.multiselect(
        "Pilih produk yang dibeli customer:",
        options=all_items,
        placeholder="Cari & pilih produk...",
    )

    top_n = st.slider("Jumlah rekomendasi ditampilkan", 3, 15, 5)

    if selected:
        st.success(f"{len(selected)} produk dipilih di keranjang.")
        for item in selected:
            st.markdown(f"- {item}")
    else:
        st.info("Belum ada produk dipilih. Silakan pilih minimal satu produk di atas.")

with col_result:
    st.subheader("✨ Rekomendasi Produk Tambahan")

    if not selected:
        st.write("Rekomendasi akan muncul di sini setelah kamu memilih produk.")
    else:
        recs = get_recommendations(selected, rules, top_n=top_n)

        if recs.empty:
            st.warning(
                "Belum ditemukan pola pembelian terkait untuk kombinasi produk ini "
                "pada dataset. Coba pilih produk lain atau kurangi jumlah produk "
                "di keranjang."
            )
        else:
            is_exact = recs.iloc[0]["Match Type"] == "Sesuai kombinasi produk yang dipilih"
            badge = "✅ Sesuai kombinasi keranjang" if is_exact else "🔶 Kemiripan sebagian (partial match)"
            badge_color = "#0E7C7B" if is_exact else "#C98A2C"
            st.markdown(
                f"<span style='color:{badge_color}; font-weight:600; font-size:0.85rem;'>{badge}</span>",
                unsafe_allow_html=True,
            )
            for _, row in recs.iterrows():
                st.markdown(
                    f"""
                    <div style="background:#F4F9F9; border-left:4px solid #4CAF93;
                                border-radius:8px; padding:0.9rem 1rem; margin-bottom:0.7rem;">
                        <p style="margin:0; font-weight:600; color:#0E7C7B;">
                            {row['Consequent']}
                        </p>
                        <p style="margin:0.2rem 0 0 0; font-size:0.85rem; color:#3A4A4A;">
                            Berdasarkan pembelian: <i>{row['Antecedent']}</i><br>
                            Confidence: <b>{row['Confidence (%)']}%</b> ·
                            Lift: <b>{row['Lift']}</b> ·
                            Support: <b>{row['Support (%)']}%</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.divider()
with st.expander("ℹ️ Cara kerja rekomendasi ini"):
    st.markdown(
        """
        1. **Exact/subset match** — sistem mencari aturan di mana seluruh produk
           di sisi *antecedent* (syarat) sudah ada di keranjang customer. Ini
           rekomendasi paling relevan karena kombinasinya benar-benar cocok.
        2. **Partial match (fallback)** — jika tidak ada aturan yang cocok
           sepenuhnya, sistem mencari aturan dengan **irisan produk terbanyak**
           dengan keranjang, lalu mengurutkannya berdasarkan Lift tertinggi.
        3. Produk yang sudah ada di keranjang tidak akan direkomendasikan ulang.

        Model rekomendasi ini menggunakan parameter Apriori yang lebih longgar
        (Min. Support 1%, Min. Confidence 5%) dibanding halaman *Association
        Rules Explorer*, supaya tetap bisa memberi saran untuk lebih banyak
        variasi kombinasi produk pada simulasi.
        """
    )
