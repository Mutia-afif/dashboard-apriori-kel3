import os
import tempfile
import pandas as pd
import numpy as np
import networkx as nx
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from mlxtend.frequent_patterns import apriori, association_rules

# ============================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Dashboard Market Basket Analysis (Apriori)",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #1F4E79;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 16px;
        color: #555555;
        text-align: center;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛒 Dashboard Market Basket Analysis (Apriori)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Aplikasi Analisis Pola Pembelian Produk & Aturan Asosiasi Interaktif</div>', unsafe_allow_html=True)

# ============================================================
# FUNGSI MEMBACA CSV AMAN (ANTI PARSER ERROR)
# ============================================================
def load_csv_safely(file_source):
    """Mencoba membaca CSV dengan berbagai macam separator (koma, titik koma, tab)"""
    separators = [',', ';', '\t', '|']
    for sep in separators:
        try:
            if hasattr(file_source, 'seek'):
                file_source.seek(0)
            df = pd.read_csv(file_source, sep=sep, on_bad_lines='skip', engine='python')
            if df.shape[1] > 1:
                return df
        except Exception:
            continue
    if hasattr(file_source, 'seek'):
        file_source.seek(0)
    return pd.read_csv(file_source, on_bad_lines='skip', engine='python')

# ============================================================
# 2. FUNGSI KHUSUS RENDER NETWORK DIAGRAM (PYVIS RAPI)
# ============================================================
def render_pyvis_network(df_rules):
    """Fungsi menggambar Network Diagram Apriori secara Interaktif & Rapi"""
    try:
        from pyvis.network import Network
        import streamlit.components.v1 as components

        G = nx.Graph()
        
        for _, row in df_rules.iterrows():
            antecedents = list(row['antecedents'])[0] if isinstance(row['antecedents'], (set, frozenset)) else str(row['antecedents'])
            consequents = list(row['consequents'])[0] if isinstance(row['consequents'], (set, frozenset)) else str(row['consequents'])
            G.add_edge(antecedents, consequents)

        net = Network(
            height="650px", 
            width="100%", 
            bgcolor="#FFFFFF", 
            font_color="#1A1A1A",
            notebook=False,
            cdn_resources='remote'
        )
        net.from_nx(G)

        for node in net.nodes:
            node_id = node["id"]
            words = str(node_id).split(' ')
            wrapped_label = ""
            line = ""
            for w in words:
                if len(line + w) > 12:
                    wrapped_label += line.strip() + "\n"
                    line = w + " "
                else:
                    line += w + " "
            wrapped_label += line.strip()
            
            node["label"] = wrapped_label
            node["shape"] = "ellipse"
            node["color"] = {
                "background": "#89CFF0",
                "border": "#1F4E79",
                "highlight": {"background": "#5FA8D3", "border": "#002B49"}
            }
            node["borderWidth"] = 2
            node["size"] = 26
            node["font"] = {"size": 13, "face": "Arial", "bold": True}

        net.set_options("""
        var options = {
          "edges": { "color": {"color": "#707070"}, "width": 2 },
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -100,
              "centralGravity": 0.01,
              "springLength": 160,
              "springConstant": 0.08,
              "damping": 0.4
            },
            "solver": "forceAtlas2Based",
            "stabilization": { "enabled": true, "iterations": 1000 }
          },
          "interaction": { "hover": true, "navigationButtons": true }
        }
        """)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            path_html = tmp_file.name
            net.save_graph(path_html)

        with open(path_html, 'r', encoding='utf-8') as f:
            html_data = f.read()

        components.html(html_data, height=660, scrolling=True)

        if os.path.exists(path_html):
            os.remove(path_html)

    except Exception as e:
        st.warning("Menampilkan versi alternatif statis (Matplotlib):")
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
        pos = nx.kamada_kawai_layout(G)
        nx.draw_networkx_edges(G, pos, edge_color='#666666', width=1.5, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_size=600, node_color='#6BAED6', edgecolors='#1F4E79', ax=ax)
        for node, (x, y) in pos.items():
            label_text = "\n".join(str(node).split(' ', 2)) if len(str(node)) > 12 else str(node)
            ax.text(x, y + 0.05, label_text, fontsize=7, fontweight='bold', ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#B0C4DE", lw=1))
        ax.axis('off')
        st.pyplot(fig)

# ============================================================
# 3. SIDEBAR PARAMETER & INPUT DATA
# ============================================================
st.sidebar.header("⚙️ Pengaturan Analysis")

uploaded_file = st.sidebar.file_uploader("Upload File CSV Penjualan", type=["csv"])

df_raw = None
if uploaded_file is not None:
    df_raw = load_csv_safely(uploaded_file)
elif os.path.exists('Sales_Final_Unique.csv'):
    df_raw = load_csv_safely('Sales_Final_Unique.csv')

if df_raw is not None:
    st.sidebar.subheader("🎛️ Parameter Apriori")
    
    # ADJUSTABLE PER 0.01 (Bisa digeser halus tanpa lompat jauh)
    min_support = st.sidebar.slider(
        "Minimum Support", 
        min_value=0.001, 
        max_value=0.5, 
        value=0.01, 
        step=0.01, 
        format="%.2f"
    )
    
    min_confidence = st.sidebar.slider(
        "Minimum Confidence", 
        min_value=0.01, 
        max_value=1.0, 
        value=0.10, 
        step=0.01, 
        format="%.2f"
    )
    
    min_lift = st.sidebar.slider(
        "Minimum Lift Ratio", 
        min_value=1.0, 
        max_value=10.0, 
        value=1.0, 
        step=0.1, 
        format="%.1f"
    )

    cols = df_raw.columns.tolist()
    col_trans = st.sidebar.selectbox("Pilih Kolom ID Transaksi / Invoice", cols, index=0)
    col_prod = st.sidebar.selectbox("Pilih Kolom Nama Produk", cols, index=1 if len(cols) > 1 else 0)

    # ============================================================
    # 4. PREPROCESSING DATA & ALGORITMA APRIORI
    # ============================================================
    with st.spinner("Memproses Data & Menghitung Apriori..."):
        basket = (df_raw.groupby([col_trans, col_prod])[col_prod]
                  .count().unstack().reset_index().fillna(0)
                  .set_index(col_trans))
        
        def encode_units(x):
            return 1 if x >= 1 else 0

        basket_sets = basket.map(encode_units) if hasattr(basket, 'map') else basket.applymap(encode_units)

        frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)
        
        if not frequent_itemsets.empty:
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
            rules = rules[rules['lift'] >= min_lift]
        else:
            rules = pd.DataFrame()

    # ============================================================
    # 5. TAMPILAN FITUR DASHBOARD UTAMA
    # ============================================================
    st.subheader("📊 Ringkasan Transaksi Penjualan")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transaksi", basket_sets.shape[0])
    c2.metric("Total Jenis Produk", basket_sets.shape[1])
    c3.metric("Itemsets Ditemukan", len(frequent_itemsets))
    c4.metric("Aturan Asosiasi", len(rules))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📜 Tabel Aturan Asosiasi", "🕸️ Diagram Network Interaktif", "📈 Grafik Evaluasi Rules"])

    with tab1:
        st.subheader("📋 Daftar Aturan Asosiasi (Association Rules)")
        if not rules.empty:
            rules_display = rules.copy()
            rules_display['antecedents'] = rules_display['antecedents'].apply(lambda x: ', '.join(list(x)))
            rules_display['consequents'] = rules_display['consequents'].apply(lambda x: ', '.join(list(x)))
            
            st.dataframe(
                rules_display[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
                .sort_values(by='lift', ascending=False),
                use_container_width=True
            )
            
            csv = rules_display.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Hasil Rules (CSV)", csv, "hasil_apriori_rules.csv", "text/csv")
        else:
            st.warning("Aturan Asosiasi tidak ditemukan! Coba turunkan nilai Minimum Support atau Minimum Confidence di sidebar.")

    with tab2:
        st.subheader("🕸️ Diagram Network Asosiasi Produk (PyVis Interaktif)")
        st.write("Titik lingkaran merepresentasikan produk, dan garis menunjukkan aturan hubungan antar produk.")
        
        if not rules.empty:
            render_pyvis_network(rules)
        else:
            st.info("Tidak ada diagram untuk ditampilkan karena aturan asosiasi kosong.")

    with tab3:
        st.subheader("📈 Scatter Plot Support vs Confidence (Color by Lift)")
        if not rules.empty:
            fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
            scatter = ax.scatter(rules['support'], rules['confidence'], c=rules['lift'], cmap='viridis', alpha=0.8, s=100)
            plt.colorbar(scatter, label='Lift Ratio')
            ax.set_xlabel('Support')
            ax.set_ylabel('Confidence')
            ax.set_title('Evaluasi Aturan Asosiasi (Support vs Confidence)')
            ax.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig)
        else:
            st.info("Grafik evaluasi akan muncul jika aturan asosiasi ditemukan.")

else:
    st.error("⚠️ Data tidak ditemukan! Silakan upload file CSV transaksi penjualan kamu lewat sidebar di sebelah kiri.")
