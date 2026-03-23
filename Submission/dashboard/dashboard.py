# dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard E-Commerce Brasil", layout="wide")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    df = pd.read_csv(os.path.join(dir_path, 'main_data.csv'))

    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    df['customer_city']  = df['customer_city'].str.strip().str.lower()

    region_map = {
        'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
        'RS': 'Sul',     'PR': 'Sul',     'SC': 'Sul',
        'BA': 'Nordeste','CE': 'Nordeste','PE': 'Nordeste','MA': 'Nordeste',
        'PB': 'Nordeste','RN': 'Nordeste','AL': 'Nordeste','SE': 'Nordeste','PI': 'Nordeste',
        'PA': 'Norte',   'AM': 'Norte',   'RO': 'Norte',   'AC': 'Norte',
        'AP': 'Norte',   'RR': 'Norte',   'TO': 'Norte',
        'GO': 'Centro-Oeste','MT': 'Centro-Oeste','MS': 'Centro-Oeste','DF': 'Centro-Oeste'
    }
    df['region'] = df['customer_state'].map(region_map)
    return df

df = load_data()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🛒 Dashboard Analisis Pelanggan E-Commerce Brasil")
st.divider()

# ── VISUALISASI 1: PER STATE ──────────────────────────────────────────────────
st.subheader("Distribusi Pelanggan per Negara Bagian")

top_n = st.slider("Tampilkan Top N State:", min_value=5, max_value=27, value=10)

state_dist = df['customer_state'].value_counts().reset_index()
state_dist.columns = ['state', 'jumlah']

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(state_dist.head(top_n)['state'], state_dist.head(top_n)['jumlah'],
       color='steelblue', edgecolor='white')
ax.set_xlabel('Negara Bagian')
ax.set_ylabel('Jumlah Pelanggan')
ax.set_title(f'Top {top_n} Negara Bagian dengan Pelanggan Terbanyak')
ax.grid(axis='y', alpha=0.4)
st.pyplot(fig)

st.divider()

# ── VISUALISASI 2: PER REGION ─────────────────────────────────────────────────
st.subheader("Distribusi Pelanggan per Wilayah")

region_dist = df['region'].value_counts().reset_index()
region_dist.columns = ['wilayah', 'jumlah']

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(region_dist['wilayah'], region_dist['jumlah'],
       color='steelblue', edgecolor='white')
ax.set_xlabel('Wilayah')
ax.set_ylabel('Jumlah Pelanggan')
ax.set_title('Jumlah Pelanggan per Wilayah di Brasil')
ax.grid(axis='y', alpha=0.4)
st.pyplot(fig)

st.divider()

# ── VISUALISASI 3: CLUSTERING KOTA ───────────────────────────────────────────
st.subheader("Clustering Kota Berdasarkan Jumlah Pelanggan")

city_df = df.groupby('customer_city')['customer_unique_id'].nunique().reset_index()
city_df.columns = ['kota', 'jumlah_pelanggan']
city_df = city_df.sort_values('jumlah_pelanggan', ascending=False)

city_df['kategori'] = pd.cut(
    city_df['jumlah_pelanggan'],
    bins=[0, 50, 500, city_df['jumlah_pelanggan'].max()],
    labels=['Kecil', 'Menengah', 'Besar']
)

col1, col2 = st.columns(2)

with col1:
    kategori_count = city_df['kategori'].value_counts().reindex(['Kecil', 'Menengah', 'Besar'])
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(kategori_count.index, kategori_count.values,
           color=['#EF5350', '#FFA726', '#1565C0'], edgecolor='white')
    ax.set_xlabel('Kategori')
    ax.set_ylabel('Jumlah Kota')
    ax.set_title('Jumlah Kota per Kategori')
    ax.grid(axis='y', alpha=0.4)
    for i, val in enumerate(kategori_count.values):
        ax.text(i, val + 5, str(val), ha='center', fontweight='bold')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(5, 4))
    top10 = city_df.head(10)
    ax.bar(top10['kota'], top10['jumlah_pelanggan'], color='steelblue', edgecolor='white')
    ax.set_xlabel('Kota')
    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_title('Top 10 Kota Terbanyak')
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.grid(axis='y', alpha=0.4)
    st.pyplot(fig)

st.caption("Dashboard dibuat oleh Elviyanti | Olist E-Commerce Dataset")
