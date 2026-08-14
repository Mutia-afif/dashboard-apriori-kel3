import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_processing import load_and_clean_data, compute_stability

st.set_page_config(page_title="Validasi Stabilitas | Apriori", page_icon="✅", layout="wide")

df = st.session_state.get("df")
if df is None:
    df = load_and_clean_data()

st.title("✅ Validasi Stabilitas Pola Pembelian")
st.markdown(
    """
    Algoritma Apriori bersifat **unsupervised** (association rule mining) dan tidak
    memiliki target/label untuk diprediksi, sehingga pembagian data di sini **bukan**
    dipakai untuk mengukur akurasi seperti pada model klasifikasi/regresi.

    Sebagai gantinya, data dibagi berdasarkan waktu untuk menguji **konsistensi pola
    pembelian**:
    - **Data Training** — transaksi Januari–April 2025
    - **Data Testing** — transaksi Mei 2025

    Jika rule yang ditemukan pada periode Training juga muncul kembali di periode
    Testing, ini menjadi indikasi bahwa pola tersebut bukan kebetulan sesaat,
    melainkan kecenderungan pembelian yang benar-benar berulang.
    """
)

st.divider()

st.sidebar.header("⚙️ Parameter Validasi")
min_support = st.sidebar.slider("Minimum Support", 0.01, 0.10, 0.03, 0.01, key="stab_support")
min_confidence = st.sidebar.slider("Minimum Confidence", 0.01, 0.80, 0.03, 0.01, key="stab_confidence")
st.sidebar.caption("Default 0.03 / 0.03 mengikuti parameter model utama pada notebook.")

with st.spinner("Menjalankan Apriori terpisah untuk periode Training & Testing..."):
    result = compute_stability(df, min_support=min_support, min_confidence=min_confidence)

df_train, df_test = result["df_train"], result["df_test"]
rules_train, rules_test = result["rules_train"], result["rules_test"]
rule_konsisten = result["rule_konsisten"]
stability_rate = result["stability_rate"]

# ---------------------------------------------------------------------------
# Ringkasan pembagian data
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Transaksi Training (Jan–Apr)", f"{df_train.shape[0]:,}",
          f"{df_train.shape[0]/df.shape[0]*100:.1f}% dari total")
c2.metric("Transaksi Testing (Mei)", f"{df_test.shape[0]:,}",
          f"{df_test.shape[0]/df.shape[0]*100:.1f}% dari total")
c3.metric("Tingkat Stabilitas Rules", f"{stability_rate:.1f}%")

st.divider()

# ---------------------------------------------------------------------------
# Perbandingan jumlah rules
# ---------------------------------------------------------------------------
st.subheader("Perbandingan Jumlah Rules per Periode")

count_df = pd.DataFrame({
    "Periode": ["Training (Jan–Apr)", "Testing (Mei)", "Konsisten di Keduanya"],
    "Jumlah Rules": [len(rules_train), len(rules_test), len(rule_konsisten)],
})
fig = px.bar(
    count_df, x="Periode", y="Jumlah Rules", color="Periode",
    color_discrete_sequence=["#B7E4C7", "#4CAF93", "#0E7C7B"],
    text="Jumlah Rules",
)
fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig, width='stretch')

if len(rules_train) == 0:
    st.warning(
        "Tidak ada rule yang ditemukan pada periode Training dengan parameter ini. "
        "Coba turunkan Minimum Support atau Minimum Confidence di sidebar."
    )
    st.stop()

st.info(
    f"Dari **{len(rules_train)} rule** yang ditemukan pada periode Training, "
    f"sebanyak **{len(rule_konsisten)} rule ({stability_rate:.1f}%)** tetap konsisten "
    f"muncul pada periode Testing — menunjukkan pola pembelian ini cenderung stabil "
    f"dari waktu ke waktu, bukan kebetulan musiman semata."
)

st.divider()

# ---------------------------------------------------------------------------
# Tabel rule yang konsisten
# ---------------------------------------------------------------------------
st.subheader("Rules yang Konsisten Muncul di Training & Testing")

if not rule_konsisten:
    st.write("Tidak ada rule yang konsisten muncul di kedua periode pada parameter ini.")
else:
    data_perbandingan = []
    for ant, con in rule_konsisten:
        baris_train = rules_train[
            (rules_train["antecedents"] == ant) & (rules_train["consequents"] == con)
        ].iloc[0]
        baris_test = rules_test[
            (rules_test["antecedents"] == ant) & (rules_test["consequents"] == con)
        ].iloc[0]
        data_perbandingan.append({
            "Antecedent": ", ".join(sorted(ant)),
            "Consequent": ", ".join(sorted(con)),
            "Confidence (Training)": f"{baris_train['confidence']*100:.1f}%",
            "Confidence (Testing)": f"{baris_test['confidence']*100:.1f}%",
            "Lift (Training)": round(baris_train["lift"], 2),
            "Lift (Testing)": round(baris_test["lift"], 2),
        })

    df_perbandingan = pd.DataFrame(data_perbandingan).sort_values(
        "Lift (Training)", ascending=False
    )
    st.dataframe(df_perbandingan, width='stretch', hide_index=True)
