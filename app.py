import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
import networkx as nx

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Rekomendasi Apriori", layout="wide")

st.title("🛒 Dashboard Market Basket Analysis (Apriori)")
st.markdown("Aplikasi Analisis Pola Pembelian Produk & Aturan Asosiasi Interaktif")

# --- SIDEBAR: UPLOAD FILE ---
st.sidebar.header("⚙️ Pengaturan Analysis")
uploaded_file = st.sidebar.file_uploader("Upload File CSV Penjualan", type=["csv"])

@st.cache_data
def load_data(file):
    if file is not None:
        try:
            df = pd.read_csv(file, delimiter=";")
        except:
            df = pd.read_csv(file, delimiter=",")
        return df
    return None

# Jika belum upload, pakai file default lokal
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    try:
        df = pd.read_csv("Sales_Final_Unique.csv", delimiter=";")
    except:
        st.error("File dataset tidak ditemukan. Silakan upload file CSV di sidebar.")
        st.stop()

# --- SIDEBAR: PILIH KOLOM ID & PARAMETER ---
st.sidebar.subheader("Parameter Apriori")
columns = df.columns.tolist()

id_column = st.sidebar.selectbox("Pilih Kolom ID Transaksi / Invoice", columns, index=0)
item_column = st.sidebar.selectbox("Pilih Kolom Daftar Item / Produk", columns, index=2 if len(columns)>2 else 0)

min_support_val = st.sidebar.slider("Minimum Support", 0.01, 0.50, 0.03, 0.01)
min_confidence_val = st.sidebar.slider("Minimum Confidence", 0.01, 1.00, 0.03, 0.01)
min_lift_val = st.sidebar.slider("Minimum Lift Ratio", 1.0, 5.0, 1.0, 0.1)

# --- PROSES PEMBENTUKAN KERANJANG (BASKET MATRIX) ---
@st.cache_data
def process_market_basket(data, id_col, item_col):
    data = data.dropna(subset=[id_col, item_col])
    
    basket_sets = (data.groupby([id_col, item_col])[item_col]
                   .count().unstack().reset_index().fillna(0)
                   .set_index(id_col))
    
    def encode_units(x):
        return 0 if x <= 0 else 1

    # Diperbaiki menggunakan .map() agar kompatibel dengan pandas versi baru
    basket_encoded = basket_sets.map(encode_units)
    basket_encoded = basket_encoded.astype(bool)
    return basket_encoded

df_encoded = process_market_basket(df, id_column, item_column)

# Menjalankan Algoritma Apriori
frequent_itemsets = apriori(df_encoded, min_support=min_support_val, use_colnames=True)

if not frequent_itemsets.empty:
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence_val)
    if not rules.empty and min_lift_val > 1.0:
        rules = rules[rules['lift'] >= min_lift_val]
else:
    rules = pd.DataFrame()

# --- TAMPILAN DASHBOARD UTAMA (METRIK) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Transaksi", df[id_column].nunique())
with col2:
    st.metric("Total Jenis Produk", df_encoded.shape[1])
with col3:
    st.metric("Itemsets Ditemukan", len(frequent_itemsets))
with col4:
    st.metric("Aturan Asosiasi", len(rules))

st.markdown("---")

# --- NAVIGASI TAB ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Tabel Aturan Asosiasi", 
    "💡 Simulator Bundling", 
    "🕸️ Diagram Network Interaktif", 
    "📈 Grafik Evaluasi Rules"
])

with tab1:
    st.header("Daftar Aturan Asosiasi (Association Rules)")
    if not rules.empty:
        rules_display = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
        rules_display['antecedents'] = rules_display['antecedents'].apply(lambda x: ', '.join(list(x)))
        rules_display['consequents'] = rules_display['consequents'].apply(lambda x: ', '.join(list(x)))
        st.dataframe(rules_display.sort_values('lift', ascending=False), use_container_width=True)
    else:
        st.warning("Aturan Asosiasi tidak ditemukan! Coba sesuaikan nilai Minimum Support, Confidence, atau Lift di sidebar.")

with tab2:
    st.header("Simulator Rekomendasi Bundling")
    st.write("Cari tahu produk apa saja yang paling potensial direkomendasikan jika pelanggan membeli produk tertentu.")
    
    if not rules.empty:
        all_antecedents = set()
        for antecedents in rules['antecedents']:
            all_antecedents.update(list(antecedents))
            
        selected_item = st.selectbox("Pilih Produk yang Dibeli Pelanggan:", sorted(list(all_antecedents)))
        
        recommendations = rules[rules['antecedents'].apply(lambda x: selected_item in list(x))]
        
        if not recommendations.empty:
            st.success(f"Pelanggan yang membeli **{selected_item}** juga cenderung membeli produk berikut:")
            for index, row in recommendations.sort_values('lift', ascending=False).iterrows():
                consec = ', '.join(list(row['consequents']))
                st.markdown(f"- 📦 **{consec}** *(Confidence: {row['confidence']*100:.1f}%, Lift: {row['lift']:.2f})*")
        else:
            st.info(f"Belum ada rekomendasi bundling yang kuat untuk produk **{selected_item}** pada parameter saat ini.")
    else:
        st.warning("Simulator tidak dapat dijalankan karena belum ada aturan asosiasi yang terbentuk.")

with tab3:
    st.header("Visualisasi Network Graph Produk")
    if not rules.empty and len(rules) > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        G = nx.DiGraph()
        top_rules = rules.sort_values('lift', ascending=False).head(30)
        for i in range(len(top_rules)):
            ant = list(top_rules.iloc[i]['antecedents'])[0]
            con = list(top_rules.iloc[i]['consequents'])[0]
            G.add_edge(ant, con, weight=top_rules.iloc[i]['lift'])
            
        pos = nx.spring_layout(G, k=1.5, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=600, node_color="skyblue", alpha=0.9, ax=ax)
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.4, edge_color="gray", ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=7, font_family="sans-serif", ax=ax)
        plt.axis("off")
        st.pyplot(fig)
    else:
        st.info("Aturan asosiasi terlalu sedikit untuk divisualisasikan.")

with tab4:
    st.header("Grafik Scatter Support vs Confidence")
    if not rules.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x="support", y="confidence", size="lift", hue="lift", data=rules, palette="viridis", ax=ax)
        ax.set_title("Support vs Confidence (Ukuran & Warna berdasarkan Lift)")
        st.pyplot(fig)
    else:
        st.info("Belum ada data untuk grafik.")
