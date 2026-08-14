import streamlit as st
import plotly.express as px
from utils.data_processing import (
    load_and_clean_data, encode_transactions, run_apriori, format_rules_for_display
)

st.set_page_config(page_title="Association Rules | Apriori", page_icon="🔗", layout="wide")

df = st.session_state.get("df") or load_and_clean_data()
df_encoded = st.session_state.get("df_encoded") or encode_transactions(df)

st.title("🔗 Association Rules Explorer")
st.markdown(
    "Algoritma **Apriori** bekerja dengan tiga metrik utama untuk menilai kekuatan "
    "sebuah aturan asosiasi (`A → B`):"
)

with st.expander("ℹ️ Penjelasan metrik Support, Confidence, dan Lift", expanded=False):
    st.markdown(
        """
        - **Support** — seberapa sering kombinasi item tersebut muncul di seluruh transaksi.
          Support tinggi = kombinasi tersebut umum terjadi.
        - **Confidence** — dari semua transaksi yang mengandung item **A**, berapa persen
          yang juga mengandung item **B**. Ini mengukur keandalan aturan.
        - **Lift** — membandingkan confidence aturan dengan probabilitas B muncul secara
          acak. Lift > 1 berarti A dan B benar-benar cenderung dibeli bersama (bukan kebetulan);
          semakin tinggi, semakin kuat asosiasinya.
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Kontrol parameter (sidebar)
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Parameter Apriori")
min_support = st.sidebar.slider("Minimum Support", 0.01, 0.20, 0.03, 0.01)
min_confidence = st.sidebar.slider("Minimum Confidence", 0.01, 0.80, 0.03, 0.01)
min_lift = st.sidebar.slider("Minimum Lift", 1.0, 5.0, 1.0, 0.1)
st.sidebar.caption(
    "Geser slider untuk melihat bagaimana jumlah & kekuatan aturan berubah "
    "seiring perubahan ambang batas parameter."
)

with st.spinner("Menjalankan Apriori dengan parameter terpilih..."):
    frequent_itemsets, rules = run_apriori(
        df_encoded, min_support=min_support,
        min_confidence=min_confidence, min_lift=min_lift,
    )

if rules.empty:
    st.warning(
        "Tidak ada rule yang memenuhi kombinasi parameter ini. "
        "Coba turunkan nilai Minimum Support atau Minimum Confidence."
    )
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Frequent Itemsets", f"{len(frequent_itemsets)}")
c2.metric("Association Rules", f"{len(rules)}")
c3.metric("Lift Tertinggi", f"{rules['lift'].max():.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Scatter plot: Support vs Confidence, bubble size/color = Lift
# ---------------------------------------------------------------------------
st.subheader("Sebaran Association Rules")
st.caption("Sumbu X = Support, Sumbu Y = Confidence, ukuran & warna bubble = Lift Ratio.")

plot_df = rules.copy()
plot_df["Antecedent"] = plot_df["antecedents"].apply(lambda s: ", ".join(sorted(s)))
plot_df["Consequent"] = plot_df["consequents"].apply(lambda s: ", ".join(sorted(s)))

fig_scatter = px.scatter(
    plot_df, x="support", y="confidence", size="lift", color="lift",
    hover_data={"Antecedent": True, "Consequent": True, "lift": ":.2f"},
    color_continuous_scale=["#B7E4C7", "#0E7C7B", "#1A4D4D"],
    labels={"support": "Support", "confidence": "Confidence", "lift": "Lift"},
)
fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig_scatter, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Top 10 rules berdasarkan Lift
# ---------------------------------------------------------------------------
st.subheader("Top 10 Rules Berdasarkan Lift Ratio")

top10 = rules.head(10).copy()
top10["Rule"] = (
    top10["antecedents"].apply(lambda s: ", ".join(sorted(s)))
    + " → "
    + top10["consequents"].apply(lambda s: ", ".join(sorted(s)))
)
fig_bar = px.bar(
    top10.sort_values("lift"), x="lift", y="Rule", orientation="h",
    color="lift", color_continuous_scale=["#B7E4C7", "#0E7C7B"],
    labels={"lift": "Lift Ratio", "Rule": ""},
)
fig_bar.update_layout(
    showlegend=False, coloraxis_showscale=False,
    plot_bgcolor="white", paper_bgcolor="white", height=450,
)
st.plotly_chart(fig_bar, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Tabel lengkap
# ---------------------------------------------------------------------------
st.subheader("Tabel Seluruh Association Rules")
display_df = format_rules_for_display(rules)
st.dataframe(display_df, width='stretch', hide_index=True)

csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Unduh tabel rules (CSV)", data=csv,
    file_name="association_rules.csv", mime="text/csv",
)
