import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_processing import load_and_clean_data

st.set_page_config(page_title="Eksplorasi Data | Apriori", page_icon="📊", layout="wide")

df = st.session_state.get("df")
if df is None:
    df = load_and_clean_data()

st.title("📊 Eksplorasi Data (EDA)")
st.markdown(
    "Sebelum masuk ke pemodelan, kita gali dulu karakteristik data transaksi: "
    "seberapa banyak item yang biasanya dibeli sekaligus, produk apa yang paling "
    "laris, dan bagaimana pola transaksi berjalan sepanjang periode data."
)

st.divider()

# ---------------------------------------------------------------------------
# Statistik ringkas
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Transaksi", f"{df.shape[0]:,}")
c2.metric("Rata-rata Item/Transaksi", f"{df['Jumlah_Item'].mean():.2f}")
c3.metric("Maksimum Item/Transaksi", f"{df['Jumlah_Item'].max()}")
c4.metric("Median Item/Transaksi", f"{df['Jumlah_Item'].median():.0f}")

st.divider()

# ---------------------------------------------------------------------------
# Distribusi jumlah item per transaksi
# ---------------------------------------------------------------------------
st.subheader("Distribusi Jumlah Item per Transaksi")
st.caption(
    "Menunjukkan seberapa besar kecenderungan customer membeli banyak produk "
    "sekaligus dalam satu transaksi — semakin banyak transaksi multi-item, "
    "semakin relevan analisis pola pembelian ini dilakukan."
)

fig_hist = px.histogram(
    df, x="Jumlah_Item", nbins=30,
    color_discrete_sequence=["#0E7C7B"],
    labels={"Jumlah_Item": "Jumlah Item per Transaksi"},
)
fig_hist.update_layout(
    yaxis_title="Jumlah Transaksi", bargap=0.05,
    plot_bgcolor="white", paper_bgcolor="white",
)
st.plotly_chart(fig_hist, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Top-N produk terlaris (interaktif)
# ---------------------------------------------------------------------------
st.subheader("Produk Terlaris (Fast-Moving)")

top_n = st.slider("Tampilkan berapa produk teratas?", min_value=5, max_value=30, value=10, step=5)

semua_item = [item for sublist in df["Items_list"] for item in sublist]
item_counts = pd.Series(semua_item).value_counts().head(top_n).sort_values(ascending=True)

fig_bar = px.bar(
    x=item_counts.values, y=item_counts.index, orientation="h",
    color=item_counts.values, color_continuous_scale=["#B7E4C7", "#0E7C7B"],
    labels={"x": "Jumlah Transaksi", "y": ""},
)
fig_bar.update_layout(
    showlegend=False, coloraxis_showscale=False,
    plot_bgcolor="white", paper_bgcolor="white",
    height=max(400, top_n * 28),
)
st.plotly_chart(fig_bar, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Tren transaksi bulanan
# ---------------------------------------------------------------------------
st.subheader("Tren Jumlah Transaksi per Bulan")
st.caption("Melihat apakah ada pola musiman pada volume transaksi selama periode data.")

df_monthly = df.copy()
df_monthly["Bulan"] = df_monthly["Tanggal"].dt.to_period("M").astype(str)
monthly_counts = df_monthly.groupby("Bulan").size().reset_index(name="Jumlah Transaksi")

fig_line = px.line(
    monthly_counts, x="Bulan", y="Jumlah Transaksi", markers=True,
    color_discrete_sequence=["#0E7C7B"],
)
fig_line.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig_line, width='stretch')

with st.expander("Lihat tabel jumlah transaksi per bulan"):
    st.dataframe(monthly_counts, width='stretch', hide_index=True)
