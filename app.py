import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
import networkx as nx

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Rekomendasi Apriori", layout="wide")

st.title("🛒 Market Basket Analysis & Rekomendasi Bundling")
st.markdown("Aplikasi interaktif untuk menemukan pola pembelian obat/suplemen menggunakan **Algoritma Apriori**.")

@st.cache_data
def load_data():
    # Membaca dataset asli milikmu
    df = pd.read_csv("Sales_Final_Unique.csv", delimiter=";")
    
    # Mengubah kolom teks 'Items' menjadi format One-Hot Encoding (True/False)
    encoded_df = df['Items'].str.get_dummies(sep=', ')
    encoded_df = encoded_df.astype(bool)
    
    return encoded_df

df = load_data()

# --- PENGATURAN SLIDER DI SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan Apriori")
# Nilai default Minimum Support diset ke 0.03
min_support_val = st.sidebar.slider("Minimum Support", 0.01, 0.50, 0.03, 0.01)
# Nilai default Minimum Confidence diset ke 0.03
min_confidence_val = st.sidebar.slider("Minimum Confidence", 0.01, 1.00, 0.03, 0.01)

# Menjalankan algoritma apriori
frequent_itemsets = apriori(df, min_support=min_support_val, use_colnames=True)

if frequent_itemsets.empty:
    st.warning("Tidak ada item yang memenuhi Minimum Support. Silakan turunkan nilai Support di Sidebar.")
    rules = pd.DataFrame()
else:
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence_val)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Ringkasan Data (EDA)", "📋 Association Rules", "💡 Simulator Bundling", "🕸️ Network Graph"])

with tab1:
    st.header("Ringkasan Data Transaksi")
    st.write(f"Total Transaksi: **{len(df)}**")
    
with tab2:
    st.header("Tabel Association Rules")
    if not rules.empty:
        st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
    else:
        st.info("Tidak ada aturan (rules) yang terbentuk dengan parameter ini.")

with tab3:
    st.header("Simulator Rekomendasi Bundling")
    if not rules.empty:
        all_antecedents = set()
        for antecedents in rules['antecedents']:
            all_antecedents.update(list(antecedents))
            
        selected_item = st.selectbox("Pilih Produk:", list(all_antecedents))
        recommendations = rules[rules['antecedents'].apply(lambda x: selected_item in list(x))]
        
        if not recommendations.empty:
            st.success(f"Rekomendasi untuk **{selected_item}** ditemukan!")
            st.dataframe(recommendations[['consequents', 'confidence', 'lift']])
        else:
            st.info("Tidak ada rekomendasi bundling untuk produk ini pada ambang batas saat ini.")
    else:
        st.warning("Rules kosong, simulator tidak dapat dijalankan.")

with tab4:
    st.header("Visualisasi Jaringan Hubungan Produk")
    if not rules.empty and len(rules) > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        G = nx.DiGraph()
        for i in range(len(rules)):
            ant = list(rules.iloc[i]['antecedents'])[0]
            con = list(rules.iloc[i]['consequents'])[0]
            G.add_edge(ant, con, weight=rules.iloc[i]['lift'])
        pos = nx.spring_layout(G, k=1)
        nx.draw_networkx_nodes(G, pos, node_size=1500, node_color="skyblue", ax=ax)
        nx.draw_networkx_edges(G, pos, width=2.0, alpha=0.5, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        plt.axis("off")
        st.pyplot(fig)
    else:
        st.info("Aturan asosiasi terlalu sedikit untuk divisualisasikan.")
