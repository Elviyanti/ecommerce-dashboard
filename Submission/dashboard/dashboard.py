# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filter Data")

semua_region = ['Semua'] + sorted(df['region'].dropna().unique().tolist())
pilih_region = st.sidebar.selectbox("Pilih Wilayah:", semua_region)

top_n    = st.sidebar.slider("Top N Negara Bagian:", min_value=5, max_value=27, value=10)
top_kota = st.sidebar.slider("Top N Kota:", min_value=5, max_value=20, value=10)

st.sidebar.divider()
st.sidebar.markdown("**Tentang Dashboard**")
st.sidebar.markdown("Dataset: Olist E-Commerce Brasil")
st.sidebar.markdown("Dibuat oleh: Elviyanti")

if pilih_region == 'Semua':
    df_filtered = df.copy()
else:
    df_filtered = df[df['region'] == pilih_region]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("Dashboard Analisis Pelanggan E-Commerce Brasil")
st.divider()

# ── METRIC CARDS ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan",  f"{len(df_filtered):,}")
col2.metric("Pelanggan Unik",   f"{df_filtered['customer_unique_id'].nunique():,}")
col3.metric("Jumlah Kota",      f"{df_filtered['customer_city'].nunique():,}")

st.divider()

# ── VISUALISASI 1 & 2 : 2 KOLOM ───────────────────────────────────────────────
st.subheader("Distribusi Pelanggan per Negara Bagian dan Wilayah")

col1, col2 = st.columns(2)

with col1:
    state_dist = (df_filtered['customer_state']
                  .value_counts()
                  .reset_index()
                  .rename(columns={'customer_state': 'state', 'count': 'jumlah'})
                  .head(top_n))

    fig1 = px.bar(
        state_dist,
        x='state', y='jumlah',
        labels={'state': 'Negara Bagian', 'jumlah': 'Jumlah Pelanggan'},
        title=f'Top {top_n} Negara Bagian',
        color='jumlah',
        color_continuous_scale='Blues',
        text='jumlah'
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Lihat Insight"):
        st.markdown("""
        - **São Paulo (SP)** memiliki pelanggan terbanyak dengan lebih dari 41.000 pelanggan.
        - Lima negara bagian teratas menyumbang sekitar **73%** dari total pelanggan.
        - Terdapat kesenjangan besar antara SP dan negara bagian lainnya.
        """)

with col2:
    region_dist = (df_filtered['region']
                   .value_counts()
                   .reset_index()
                   .rename(columns={'region': 'wilayah', 'count': 'jumlah'}))

    fig2 = px.bar(
        region_dist,
        x='wilayah', y='jumlah',
        labels={'wilayah': 'Wilayah', 'jumlah': 'Jumlah Pelanggan'},
        title='Distribusi per Wilayah',
        color='wilayah',
        text='jumlah'
    )
    fig2.update_traces(textposition='outside')
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Lihat Insight"):
        st.markdown("""
        - Wilayah **Sudeste** mendominasi dengan lebih dari **68%** total pelanggan.
        - Wilayah **Norte** hanya memiliki sekitar **1.86%** pelanggan.
        - Peluang ekspansi besar di wilayah Norte dan Nordeste.
        """)

st.divider()

# ── VISUALISASI 3: CLUSTERING KOTA — 2 KOLOM ─────────────────────────────────
st.subheader("Clustering Kota Berdasarkan Jumlah Pelanggan")

city_df = (df_filtered.groupby('customer_city')['customer_unique_id']
           .nunique()
           .reset_index()
           .rename(columns={'customer_unique_id': 'jumlah_pelanggan'})
           .sort_values('jumlah_pelanggan', ascending=False))

city_df['kategori'] = pd.cut(
    city_df['jumlah_pelanggan'],
    bins=[0, 50, 500, city_df['jumlah_pelanggan'].max()],
    labels=['Kecil', 'Menengah', 'Besar']
)

col1, col2 = st.columns(2)

with col1:
    kategori_count = (city_df['kategori']
                      .value_counts()
                      .reindex(['Kecil', 'Menengah', 'Besar'])
                      .reset_index()
                      .rename(columns={'kategori': 'Kategori', 'count': 'Jumlah Kota'}))

    fig3 = px.bar(
        kategori_count,
        x='Kategori', y='Jumlah Kota',
        title='Jumlah Kota per Kategori',
        color='Kategori',
        color_discrete_map={'Kecil': '#EF5350', 'Menengah': '#FFA726', 'Besar': '#1565C0'},
        text='Jumlah Kota'
    )
    fig3.update_traces(textposition='outside')
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = px.bar(
        city_df.head(top_kota),
        x='customer_city', y='jumlah_pelanggan',
        title=f'Top {top_kota} Kota Terbanyak',
        labels={'customer_city': 'Kota', 'jumlah_pelanggan': 'Jumlah Pelanggan'},
        color='jumlah_pelanggan',
        color_continuous_scale='Blues',
        text='jumlah_pelanggan'
    )
    fig4.update_traces(textposition='outside')
    fig4.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

with st.expander("Lihat Insight"):
    st.markdown("""
    - Sebanyak **93.7%** kota masuk kategori *Kecil* (0–50 pelanggan).
    - Hanya **21 kota** yang masuk kategori *Besar* (>500 pelanggan).
    - **São Paulo** memimpin jauh dengan hampir 15.000 pelanggan unik.
    """)

st.divider()
st.caption("Dashboard dibuat oleh Elviyanti | Olist E-Commerce Dataset")
