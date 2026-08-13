import os
import tempfile
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# ============================================================
# SETUP HALAMAN STREAMLIT
# ============================================================
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
# 3. PENAMPILAN METRIK STREAMLIT (NILAI PLUS DIBOARD)
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Produk (Nodes)", value=G.number_of_nodes())
with col2:
    st.metric(label="Total Aturan Atas Pasangan (Edges)", value=G.number_of_edges())
with col3:
    st.metric(label="Kepadatan Network (Density)", value=f"{nx.density(G):.3f}")

st.markdown("---")

# ============================================================
# 4. INISIALISASI PYVIS NETWORK (TAMPILAN KHUSUS WEB)
# ============================================================
# Menggunakan cdn_resources='remote' wajib untuk deployment di Streamlit Cloud
net = Network(
    height="750px", 
    width="100%", 
    bgcolor="#FFFFFF", 
    font_color="#1A1A1A",
    notebook=False,
    cdn_resources='remote'
)

# Import Graph dari NetworkX ke Pyvis
net.from_nx(G)

# ============================================================
# 5. STYLING NODE & LABEL DENGAN AUTO-TEXT WRAPPING
# ============================================================
for node in net.nodes:
    node_id = node["id"]
    
    # Bungkus teks nama produk yang panjang agar tidak terlalu melebar (maks 15 karakter per baris)
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
    
    # Kustomisasi Properti Tampilan Node
    node["label"] = wrapped_label
    node["shape"] = "ellipse"                  # Bentuk node elips/lingkaran rapi
    node["color"] = {
        "background": "#89CFF0",               # Warna background isi
        "border": "#1F4E79",                   # Warna garis pinggir
        "highlight": {
            "background": "#5FA8D3",
            "border": "#002B49"
        }
    }
    node["borderWidth"] = 2                    # Ketebalan garis pinggir
    node["borderWidthSelected"] = 4
    node["size"] = 30                          # Ukuran node proporsional
    node["font"] = {
        "size": 13, 
        "face": "Arial", 
        "bold": True,
        "multi": "md"                          # Mendukung multiline (\n)
    }

# ============================================================
# 6. ATUR FISIKA (PHYSICS) ANTI-BERANTAKAN & STABILISASI
# ============================================================
# Menggunakan 'forceAtlas2Based' agar penyebaran titik saling mendorong secara seimbang
net.set_options("""
var options = {
  "nodes": {
    "shadow": true
  },
  "edges": {
    "color": {
      "color": "#707070",
      "highlight": "#1F4E79"
    },
    "width": 2,
    "smooth": {
      "type": "continuous"
    }
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -100,
      "centralGravity": 0.01,
      "springLength": 160,
      "springConstant": 0.08,
      "damping": 0.4
    },
    "maxVelocity": 50,
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based",
    "stabilization": {
      "enabled": true,
      "iterations": 1000,
      "updateInterval": 25
    }
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  }
}
""")

# ============================================================
# 7. RENDER DI STREAMLIT VIA TEMPORARY FILE HTML
# ============================================================
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
    path_html = tmp_file.name
    net.save_graph(path_html)

# BACA FILE HTML UNTUK DITAMPILKAN DI COMPONENTS STREAMLIT
with open(path_html, 'r', encoding='utf-8') as f:
    html_data = f.read()

# Tampilkan di Streamlit dengan tinggi 760px
components.html(html_data, height=760, scrolling=True)

# Hapus file temporary setelah ditampilkan agar tidak memenuhi RAM server
if os.path.exists(path_html):
    os.remove(path_html)

st.success("✅ Diagram Network berhasil ditampilkan secara rapi & interaktif!")
