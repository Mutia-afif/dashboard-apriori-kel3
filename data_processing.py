"""
Modul inti pemrosesan data untuk aplikasi Rekomendasi Paket Penjualan
Obat & Suplemen Berdasarkan Pola Pembelian (Algoritma Apriori).

Semua fungsi di sini di-cache oleh Streamlit (@st.cache_data / @st.cache_resource)
supaya proses cleaning & mining tidak berulang setiap kali user pindah halaman
atau menggeser slider.
"""

import pandas as pd
import streamlit as st
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

DATA_PATH = "Sales_Final_Unique.csv"
SPLIT_DATE = "2025-05-01"  # batas Training (Jan-Apr) vs Testing (Mei), mengikuti notebook


# ---------------------------------------------------------------------------
# 1. LOAD & CLEANING
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_clean_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load CSV transaksi, bersihkan, dan parsing kolom Items menjadi list.
    Mengikuti tahapan Data Cleansing pada notebook DAMING_Apriori.ipynb.
    """
    df = pd.read_csv(path, sep=";")

    # Parsing tanggal (format: "Januari 02, 2025" -> perlu locale mapping manual
    # karena pandas default tidak kenal nama bulan Bahasa Indonesia)
    bulan_map = {
        "Januari": "January", "Februari": "February", "Maret": "March",
        "April": "April", "Mei": "May", "Juni": "June", "Juli": "July",
        "Agustus": "August", "September": "September", "Oktober": "October",
        "November": "November", "Desember": "December",
    }
    tanggal_en = df["Tanggal"].copy()
    for idn, eng in bulan_map.items():
        tanggal_en = tanggal_en.str.replace(idn, eng, regex=False)
    df["Tanggal"] = pd.to_datetime(tanggal_en, format="%B %d, %Y")

    # Standarisasi nama item: uppercase, rapikan spasi
    def clean_items(item_string: str):
        items = item_string.split(",")
        items = [" ".join(i.strip().upper().split()) for i in items]
        return items

    df["Items_list"] = df["Items"].apply(clean_items)
    df["Jumlah_Item"] = df["Items_list"].apply(len)

    return df


# ---------------------------------------------------------------------------
# 2. ONE-HOT ENCODING (format Apriori)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def encode_transactions(_df: pd.DataFrame):
    """Transformasi list item per transaksi menjadi matriks boolean one-hot.
    Prefix underscore pada _df supaya Streamlit tidak mencoba hashing DataFrame besar.
    """
    transactions = _df["Items_list"].tolist()
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)
    return df_encoded


# ---------------------------------------------------------------------------
# 3. APRIORI + ASSOCIATION RULES (dengan parameter fleksibel untuk explorer)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_apriori(_df_encoded: pd.DataFrame, min_support: float = 0.03,
                 min_confidence: float = 0.03, min_lift: float = 1.0,
                 max_len: int = 2):
    """Jalankan Apriori + association_rules dengan parameter yang bisa diatur user.
    Mengembalikan (frequent_itemsets, rules) — rules sudah difilter & diurutkan
    berdasarkan Lift menurun, mengikuti pendekatan pada notebook.
    """
    frequent_itemsets = apriori(
        _df_encoded, min_support=min_support, use_colnames=True, max_len=max_len
    )
    if frequent_itemsets.empty:
        return frequent_itemsets, pd.DataFrame()

    rules = association_rules(
        frequent_itemsets, metric="confidence", min_threshold=min_confidence
    )
    rules = rules[rules["lift"] > min_lift].copy()
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
    return frequent_itemsets, rules


def format_rules_for_display(rules: pd.DataFrame) -> pd.DataFrame:
    """Ubah kolom frozenset antecedents/consequents menjadi string yang mudah dibaca,
    plus persentase Support & Confidence untuk ditampilkan di tabel/UI.
    """
    if rules.empty:
        return rules

    out = rules.copy()
    out["Antecedent"] = out["antecedents"].apply(lambda s: ", ".join(sorted(s)))
    out["Consequent"] = out["consequents"].apply(lambda s: ", ".join(sorted(s)))
    out["Support (%)"] = (out["support"] * 100).round(2)
    out["Confidence (%)"] = (out["confidence"] * 100).round(1)
    out["Lift"] = out["lift"].round(2)
    return out[["Antecedent", "Consequent", "Support (%)", "Confidence (%)", "Lift"]]


# ---------------------------------------------------------------------------
# 4. VALIDASI STABILITAS (Training Jan-Apr vs Testing Mei)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_apriori_on_transactions(transactions: list, min_support: float = 0.01,
                                 min_confidence: float = 0.30, max_len: int = 2):
    """Helper: jalankan Apriori langsung dari list transaksi (dipakai untuk
    membandingkan periode Training vs Testing secara terpisah)."""
    te_local = TransactionEncoder()
    arr = te_local.fit(transactions).transform(transactions)
    df_enc_local = pd.DataFrame(arr, columns=te_local.columns_)

    freq = apriori(df_enc_local, min_support=min_support, use_colnames=True, max_len=max_len)
    if freq.empty:
        return pd.DataFrame()

    r = association_rules(freq, metric="confidence", min_threshold=min_confidence)
    r = r[r["lift"] > 1.0].sort_values("lift", ascending=False).reset_index(drop=True)
    return r


@st.cache_data(show_spinner=False)
def compute_stability(_df: pd.DataFrame, min_support: float = 0.01,
                       min_confidence: float = 0.30):
    """Bandingkan rules yang muncul di periode Training (< SPLIT_DATE) vs
    Testing (>= SPLIT_DATE). Mengembalikan dict berisi rules_train, rules_test,
    rule_konsisten (set), dan stability_rate (%).
    """
    df_train = _df[_df["Tanggal"] < SPLIT_DATE]
    df_test = _df[_df["Tanggal"] >= SPLIT_DATE]

    rules_train = run_apriori_on_transactions(
        df_train["Items_list"].tolist(), min_support, min_confidence
    )
    rules_test = run_apriori_on_transactions(
        df_test["Items_list"].tolist(), min_support, min_confidence
    )

    def kunci_rule(row):
        return (frozenset(row["antecedents"]), frozenset(row["consequents"]))

    set_train = set(rules_train.apply(kunci_rule, axis=1)) if not rules_train.empty else set()
    set_test = set(rules_test.apply(kunci_rule, axis=1)) if not rules_test.empty else set()
    rule_konsisten = set_train & set_test
    stability_rate = (len(rule_konsisten) / len(set_train) * 100) if set_train else 0.0

    return {
        "df_train": df_train,
        "df_test": df_test,
        "rules_train": rules_train,
        "rules_test": rules_test,
        "rule_konsisten": rule_konsisten,
        "stability_rate": stability_rate,
    }


# ---------------------------------------------------------------------------
# 5. REKOMENDASI (untuk fitur Simulasi Cart multi-item)
# ---------------------------------------------------------------------------
def get_recommendations(selected_items: list, rules: pd.DataFrame, top_n: int = 10):
    """Cari produk yang direkomendasikan berdasarkan item yang dipilih user.

    Strategi (mendukung multi-item cart):
    1. EXACT/SUBSET MATCH  -> antecedent adalah subset dari item yang dipilih user
       (rule paling relevan, karena semua syarat antecedent terpenuhi).
    2. PARTIAL OVERLAP     -> kalau tidak ada exact match, cari rule yang
       antecedent-nya beririsan sebagian dengan pilihan user, diurutkan
       berdasarkan jumlah overlap lalu Lift.

    Mengembalikan DataFrame hasil rekomendasi (tanpa item yang sudah dipilih user)
    beserta kolom 'match_type' untuk transparansi ke user.
    """
    if rules.empty or not selected_items:
        return pd.DataFrame()

    selected_set = set(selected_items)
    rules = rules.copy()
    rules["overlap"] = rules["antecedents"].apply(lambda a: len(a & selected_set))
    rules["is_subset"] = rules["antecedents"].apply(lambda a: a.issubset(selected_set))

    # 1. Exact/subset match
    subset_matches = rules[rules["is_subset"] & (rules["overlap"] > 0)].copy()
    subset_matches = subset_matches.sort_values(
        ["overlap", "lift", "confidence"], ascending=False
    )

    if not subset_matches.empty:
        result = subset_matches.copy()
        result["match_type"] = "Sesuai kombinasi produk yang dipilih"
    else:
        # 2. Partial overlap fallback
        partial = rules[rules["overlap"] > 0].copy()
        partial = partial.sort_values(["overlap", "lift"], ascending=False)
        result = partial.copy()
        result["match_type"] = "Kemiripan sebagian (partial match)"

    # Buang consequent yang sudah ada di keranjang user
    result = result[result["consequents"].apply(lambda c: len(c & selected_set) == 0)]

    if result.empty:
        return pd.DataFrame()

    result = result.head(top_n)
    display = format_rules_for_display(result)
    display["Match Type"] = result["match_type"].values
    return display


@st.cache_data(show_spinner=False)
def get_all_items(_df_encoded: pd.DataFrame) -> list:
    """Daftar semua item unik (untuk dropdown/multiselect di halaman Simulasi)."""
    return sorted(_df_encoded.columns.tolist())
