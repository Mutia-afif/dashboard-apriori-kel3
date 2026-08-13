import os
import tempfile
import streamlit as st
import networkx as nx

# Setup Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Visualisasi Network Asosiasi Produk",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🕸️ Visualisasi Network Asosiasi Produk (Market Basket Analysis)")
st.caption("Diagram interaktif hubungan antar produk berdasarkan aturan asosiasi.")

# ============================================================
# 1. DEFINISI DATA HUBUNGAN ASOSIASI (EDGES)
# ============================================================
edges = [
    ("WOODS EXPECTORANT 60 ML", "WOODS COUGH SYR ATT  60ML"),
    ("CEREBROFORT M.G. AGGR SCH", "WOODS EXPECTORANT 60 ML"),
    ("CEREBROFORT M.G. AGGR SCH", "CEREBROFORT MG MGA SCH"),
    ("CEREBROFORT MG MGA SCH", "CEREBROFORT MG JRK SCH"),
    ("CEREBROFORT MG JRK SCH", "CEREBROFORT MG STRAW SCH"),
    ("CEREBROFORT MG STRAW SCH", "KOMIX HERBAL 15 ML"),
    ("KOMIX HERBAL 15 ML", "BEJO JAHE MERAH HERBAL 12'SC"),
    ("KOMIX HERBAL 15 ML", "KOMIX HERBAL ORI PACK"),
    ("MIXAGRIP HERBAL GREGES", "KOMIX HERBAL ORI PACK"),
    ("BEJO JAHE MERAH HERBAL 12'SC", "ENTROSTOP HERBAL ANAK"),
    ("ENTROSTOP HERBAL ANAK", "PROMAG HERBAL 15 ML"),
    ("PROMAG SUSPENSI 10ML/6", "PROMAG HERBAL 15 ML"),
    ("PROMAG HERBAL 15 ML", "KOMIX HERBAL ORI PACK"),
    ("PROMAG HERBAL 15 ML", "SAKATONIK ABC ORANGE 30TAB"),
    ("SAKATONIK ABC ORANGE 30TAB", "SAKATONIK ABC STRAW 30TAB"),
    ("SAKATONIK ABC ORANGE 30TAB", "SAKATONIK ABC ANGGUR 30TAB"),
    ("SAKATONIK ABC ORANGE 30TAB", "SAKATONIK ABC ANTARIKSA")
]

# ============================================================
# 2. MEMBUAT NETWORKX GRAPH
# ============================================================
G = nx.Graph()
G.add_edges_from(edges)

# ============================================================
# 3. STATISTIK METRIK DASHBOARD
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Produk (Nodes)", value=G.number_of_nodes())
with col2:
    st.metric(label="Total Pasangan Aturan (Edges)", value=G.number_of_edges())
with col3:
    st.metric(label="Kepadatan Network (Density)", value=f"{nx.density(G):.3f}")

st.markdown("---")

# ============================================================
# 4. RENDER UTAMA MENGGUNAKAN PYVIS KHUSUS WEB
# ============================================================
try:
    from pyvis.network import Network
    import streamlit.components.v1 as components

    # Inisialisasi Pyvis Network
    net = Network(
        height="750px", 
        width="100%", 
        bgcolor="#FFFFFF", 
        font_color="#1A1A1A",
        notebook=False,
        cdn_resources='remote'
    )
    net.from_nx(G)

    # Styling Node & Auto Text-Wrapping (Pemotongan Kata Agar Tidak Melar)
    for node in net.nodes:
        node_id = node["id"]
        words = node_id.split(' ')
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
        node["size"] = 28
        node["font"] = {"size": 13, "face": "Arial", "bold": True}

    # Atur Fisika/Layout Anti-Berantakan
    net.set_options("""
    var options = {
      "edges": {
        "color": {"color": "#707070"},
        "width": 2
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.01,
          "springLength": 160,
          "springConstant": 0.08,
          "damping": 0.4
        },
        "solver": "forceAtlas2Based",
        "stabilization": {
          "enabled": true,
          "iterations": 1000
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true
      }
    }
    """)

    # Render via temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        path_html = tmp_file.name
        net.save_graph(path_html)

    with open(path_html, 'r', encoding='utf-8') as f:
        html_data = f.read()

    components.html(html_data, height=760, scrolling=True)

    if os.path.exists(path_html):
        os.remove(path_html)

except ModuleNotFoundError:
    st.error("⚠️ Module 'pyvis' belum terinstall di server. Pastikan 'pyvis' sudah ditambahkan di file requirements.txt di GitHub!")
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_edges(G, pos, edge_color='#666666', width=1.8, alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#6BAED6', edgecolors='#1F4E79', linewidths=1.5, ax=ax)
    
    for node, (x, y) in pos.items():
        label_text = "\n".join(node.split(' ', 2)) if len(node) > 12 else node
        ax.text(x, y + 0.05, label_text, fontsize=7, fontweight='bold', ha='center', va='bottom',
                bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#B0C4DE", lw=1, alpha=0.95))
    
    ax.axis('off')
    st.pyplot(fig)
