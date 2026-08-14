import streamlit as st

st.set_page_config(page_title="Paket Bundling | Apriori", page_icon="📦", layout="wide")

st.title("📦 Rancangan Paket Bundling")
st.markdown(
    "Berdasarkan aturan asosiasi dengan **Lift tertinggi** pada model data penuh, "
    "disusun tiga rancangan paket produk yang dapat dijadikan strategi *cross-selling* "
    "oleh apotek."
)

st.divider()

paket_list = [
    {
        "nama": "Paket Hemat Pelega Tenggorokan Aneka Rasa",
        "icon": "🍬",
        "items": [
            "Woods Lozenges Cherry 6'S",
            "Woods Lozenges Orange Vitamin C",
            "Woods Loz Honey Lemon",
        ],
        "dasar": "Lift tinggi (> 20) antar-varian rasa Woods Lozenges",
        "strategi": "Cross-selling varian rasa dalam satu paket hemat — customer yang "
                    "membeli satu rasa cenderung tertarik mencoba rasa lain.",
    },
    {
        "nama": "Paket Herbal Sehat Pertolongan Pertama",
        "icon": "🌿",
        "items": [
            "Bejo Jahe Merah Herbal 12 SC",
            "Komix Herbal 15 ML",
            "Promag Herbal 15 ML",
        ],
        "dasar": "Kombinasi 3 item herbal terlaris utama yang sering muncul bersamaan "
                 "dalam transaksi yang sama",
        "strategi": "Bundling produk herbal pendukung daya tahan tubuh & pencernaan "
                    "sebagai paket 'jaga-jaga' rumah tangga.",
    },
    {
        "nama": "Paket Nutrisi & Vitamin Anak",
        "icon": "🧃",
        "items": [
            "Cerebrofort Gold Orange 100 ML",
            "Cerebrofort M.G. Aggr Sch",
            "Cerebrofort Mg Jrk Sch",
        ],
        "dasar": "Lift sangat tinggi antar-varian rasa/kemasan Cerebrofort",
        "strategi": "Konsumen membeli beberapa varian rasa/kemasan Cerebrofort sekaligus "
                    "— berpotensi untuk paket keluarga atau stok bulanan.",
    },
]

cols = st.columns(3)
for i, paket in enumerate(paket_list):
    with cols[i]:
        items_html = "".join(f"<li>{it}</li>" for it in paket["items"])
        st.markdown(
            f"""
            <div style="background:#F4F9F9; border-radius:14px; padding:1.4rem;
                        border-top:5px solid #0E7C7B; min-height:520px;">
                <p style="font-size:2rem; margin-bottom:0.2rem;">{paket['icon']}</p>
                <p style="font-weight:700; font-size:1.05rem; color:#0E7C7B; margin-bottom:0.8rem;">
                    {paket['nama']}
                </p>
                <p style="font-size:0.82rem; font-weight:600; color:#3A4A4A; margin-bottom:0.3rem;">
                    Komposisi Item:
                </p>
                <ul style="font-size:0.85rem; color:#3A4A4A; padding-left:1.1rem; margin-bottom:0.9rem;">
                    {items_html}
                </ul>
                <p style="font-size:0.82rem; font-weight:600; color:#3A4A4A; margin-bottom:0.2rem;">
                    Dasar Aturan:
                </p>
                <p style="font-size:0.83rem; color:#5A6A6A; margin-bottom:0.9rem;">
                    {paket['dasar']}
                </p>
                <p style="font-size:0.82rem; font-weight:600; color:#3A4A4A; margin-bottom:0.2rem;">
                    Strategi:
                </p>
                <p style="font-size:0.83rem; color:#5A6A6A; margin:0;">
                    {paket['strategi']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.info(
    "💡 **Catatan:** ketiga paket ini dirancang manual berdasarkan interpretasi rules "
    "ber-Lift tertinggi pada halaman *Association Rules Explorer*. Untuk eksplorasi "
    "rekomendasi yang lebih fleksibel dan berbasis kombinasi produk apa pun, gunakan "
    "halaman **💊 Simulasi Rekomendasi**."
)
