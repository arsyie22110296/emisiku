# ================= app.py =================
# EmisiKu - Wizard Tanpa Sidebar, dengan Card & Hover
# Skripsi - Ariel Adrienne Setiawan

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import base64
import warnings
warnings.filterwarnings('ignore')
import plotly.graph_objects as go

# ========== IMPORT MODUL ==========
from emission_calculator import calculate_emissions, get_emission_summary, FUEL_FACTORS, get_fuel_info, calculate_carbon_credit, calculate_carbon_credit_per_row
from clustering_engine import EmissionClusterAnalyzer
import visualizer as viz
import report_exporter as rex
from forecasting_linear import EmissionForecaster, validate_forecast_data
from anomaly_detector import AnomalyDetector, validate_anomaly_data
from utils.header import show_header
import sys
sys.stderr = sys.stdout
# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="EmisiKu - Monitoring Emisi Karbon UMKM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= ASSETS / BACKGROUND IMAGE =================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


def image_to_base64(image_path):
    """
    Membaca gambar dari folder assets dan mengubahnya
    menjadi Data URI agar dapat digunakan langsung
    sebagai background-image di HTML.
    """
    if not image_path.exists():
        return None

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }

    mime_type = mime_types.get(image_path.suffix.lower())

    if mime_type is None:
        return None

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


# Load background images
slide_images = {}

for i in range(1, 6):
    image_path = ASSETS_DIR / f"slide{i}.png"
    image_data = image_to_base64(image_path)

    if image_data:
        slide_images[i] = image_data
    else:
        slide_images[i] = ""
        print(f"⚠️ Background tidak ditemukan: {image_path}")

# Load logo
logo_path = ASSETS_DIR / "logo.png"
logo_base64 = image_to_base64(logo_path)
if not logo_base64:
    logo_base64 = ""
    print("⚠️ Logo tidak ditemukan: assets/logo.png")
        
# ================= LANDING PAGE =================
# ================= LANDING PAGE =================
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

if st.session_state.show_landing:
    # Sembunyikan elemen Streamlit
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }

    .stApp {
        background-color: #0d1117;
        overflow: hidden;
    }

    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        z-index: 9999 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    bg1 = slide_images.get(1, "")
    bg2 = slide_images.get(2, "")
    bg3 = slide_images.get(3, "")
    bg4 = slide_images.get(4, "")
    bg5 = slide_images.get(5, "")

    html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EmisiKu - Landing</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #0d1117;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .slideshow-container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
            opacity: 0;
            transition: opacity 1.2s ease;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #0d1117;
        }}
        .slide::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.25);
            z-index: 0;
        }}
        .slide > * {{
            position: relative;
            z-index: 1;
        }}
        .slide.active {{
            opacity: 1;
        }}

        .slide-1 {{ background-image: url('{bg1}'); }}
        .slide-2 {{ background-image: url('{bg2}'); }}
        .slide-3 {{ background-image: url('{bg3}'); }}
        .slide-4 {{ background-image: url('{bg4}'); }}
        .slide-5 {{ background-image: url('{bg5}'); }}

        .slide .emoji {{ font-size: 6rem; margin-bottom: 1rem; }}
        .slide .title {{ font-size: 2.5rem; font-weight: 700; color: #2ecc71; margin-bottom: 0.5rem; }}
        .slide .desc {{ font-size: 1.2rem; color: #f0f6fc; max-width: 600px; }}
        
        .logo-img {{
            max-width: 300px;
            width: 75%;
            height: auto;
            margin-bottom: 0.2rem;
            filter: drop-shadow(0 6px 18px rgba(0,0,0,0.45));
        }}
        
        .logo-small {{
            font-size: 1.2rem;
            color: #c9d1d9;
            margin-top: 0.2rem;
            margin-bottom: 1.2rem;
        }}
        
        .btn-start {{
            display: inline-block;
            margin-top: 2rem;
            padding: 0.8rem 2.5rem;
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(46,204,113,0.3);
            transition: all 0.3s ease;
            text-decoration: none;
        }}
        .btn-start:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 30px rgba(46,204,113,0.5);
        }}
        .dots {{
            position: absolute;
            bottom: 2rem;
            width: 100%;
            display: flex;
            justify-content: center;
            gap: 0.8rem;
            z-index: 10;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #30363d;
            transition: background 0.3s;
            cursor: pointer;
        }}
        .dot.active {{ background: #2ecc71; }}
        @media (max-width: 768px) {{
            .slide .emoji {{ font-size: 4rem; }}
            .slide .title {{ font-size: 1.8rem; }}
            .slide .desc {{ font-size: 1rem; }}
            .logo-img {{ max-width: 280px; }}
        }}
    </style>
</head>
<body>
<div class="slideshow-container">
    <div class="slide slide-1 active" data-index="0">
        <img src="{logo_base64}" alt="EmisiKu Logo" class="logo-img">
        <div class="logo-small">Sistem Analisis Pola Emisi Karbon untuk UMKM</div>
        <div class="emoji">📊</div>
        <div class="title">Dashboard Analitik</div>
        <div class="desc">Pantau emisi karbon usaha Anda secara real-time</div>
        <button class="btn-start" onclick="goToApp()">🚀 Mulai Analisis</button>
    </div>
    <div class="slide slide-2" data-index="1">
        <img src="{logo_base64}" alt="EmisiKu Logo" class="logo-img">
        <div class="logo-small">Sistem Analisis Pola Emisi Karbon untuk UMKM</div>
        <div class="emoji">🧩</div>
        <div class="title">K-Means Clustering</div>
        <div class="desc">Kelompokkan pola emisi menjadi Tinggi, Sedang, Rendah</div>
        <button class="btn-start" onclick="goToApp()">🚀 Mulai Analisis</button>
    </div>
    <div class="slide slide-3" data-index="2">
        <img src="{logo_base64}" alt="EmisiKu Logo" class="logo-img">
        <div class="logo-small">Sistem Analisis Pola Emisi Karbon untuk UMKM</div>
        <div class="emoji">🔮</div>
        <div class="title">Forecasting 30 Hari</div>
        <div class="desc">Prediksi emisi dengan Linear Time Series Regression</div>
        <button class="btn-start" onclick="goToApp()">🚀 Mulai Analisis</button>
    </div>
    <div class="slide slide-4" data-index="3">
        <img src="{logo_base64}" alt="EmisiKu Logo" class="logo-img">
        <div class="logo-small">Sistem Analisis Pola Emisi Karbon untuk UMKM</div>
        <div class="emoji">⚠️</div>
        <div class="title">Deteksi Anomali</div>
        <div class="desc">Identifikasi pola emisi tidak wajar dengan Isolation Forest</div>
        <button class="btn-start" onclick="goToApp()">🚀 Mulai Analisis</button>
    </div>
    <div class="slide slide-5" data-index="4">
        <img src="{logo_base64}" alt="EmisiKu Logo" class="logo-img">
        <div class="logo-small">Sistem Analisis Pola Emisi Karbon untuk UMKM</div>
        <div class="emoji">💰</div>
        <div class="title">Carbon Credit</div>
        <div class="desc">Hitung potensi pendapatan dari perdagangan karbon</div>
        <button class="btn-start" onclick="goToApp()">🚀 Mulai Analisis</button>
    </div>
    <div class="dots">
        <span class="dot active" data-index="0"></span>
        <span class="dot" data-index="1"></span>
        <span class="dot" data-index="2"></span>
        <span class="dot" data-index="3"></span>
        <span class="dot" data-index="4"></span>
    </div>
</div>
<script>
    (function() {{
        var slides = document.querySelectorAll('.slide');
        var dots = document.querySelectorAll('.dot');
        
        if (slides.length === 0) return;
        
        var currentIndex = 0;
        var interval = setInterval(changeSlide, 4000);

        function changeSlide() {{
            var nextIndex = (currentIndex + 1) % slides.length;
            goToSlide(nextIndex);
        }}

        function goToSlide(index) {{
            slides.forEach(function(s) {{ s.classList.remove('active'); }});
            dots.forEach(function(d) {{ d.classList.remove('active'); }});
            
            slides[index].classList.add('active');
            dots[index].classList.add('active');
            
            currentIndex = index;
            clearInterval(interval);
            interval = setInterval(changeSlide, 4000);
        }}

        dots.forEach(function(dot) {{
            dot.addEventListener('click', function() {{
                var index = parseInt(this.getAttribute('data-index'));
                goToSlide(index);
            }});
        }});

        window.goToApp = function() {{
            // Cara lebih cepat: langsung ubah URL tanpa reload penuh jika memungkinkan
            try {{
                window.top.location.href = window.top.location.pathname + '?start=true';
            }} catch(e) {{
                window.location.href = window.location.pathname + '?start=true';
            }}
        }};
    }})();
</script>
</body>
</html>
    """

    st.iframe(
    src="data:text/html;charset=utf-8," + html_code,
    height=800,
    width=1200
)

    # Tangkap sinyal lebih cepat
    if st.query_params.get("start") == "true":
        st.session_state.show_landing = False
        # Langsung clear biar tidak double proses
        st.query_params.clear()
        st.rerun()

    st.stop()
    
# ================= SETELAH LANDING PAGE =================
# Hapus query parameter agar tidak mengganggu
if st.query_params.get("start") == "true":
    st.query_params.clear()
    st.rerun()

# ================= HEADER & KONTEN UTAMA =================
show_header()

# ========== CSS CUSTOM ==========
st.markdown("""
<style>
/* Dark theme */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff;
}
p, li, label, .stMarkdown {
    color: #e6edf3 !important;
}

/* Sticky header */
.sticky-header {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(13, 17, 23, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #30363d;
    padding: 0.5rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

/* Card style dengan hover */
.card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.5rem 0;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    border-color: #2ecc71;
}

/* Tombol navigasi footer */
.nav-btn {
    background: transparent;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #e6edf3;
    font-weight: 500;
    transition: all 0.2s;
    width: 100%;
}
.nav-btn:hover {
    background: rgba(46,204,113,0.15);
    border-color: #2ecc71;
    color: #2ecc71;
}
.nav-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* Metric card */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.2s;
}
.metric-card:hover {
    border-color: #2ecc71;
    transform: scale(1.02);
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #2ecc71;
}
.metric-label {
    font-size: 0.8rem;
    color: #8b949e;
}

/* Footer */
.footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #30363d;
    text-align: center;
    color: #8b949e;
    font-size: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# ========== INIT SESSION STATE ==========
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df_processed' not in st.session_state:
    st.session_state.df_processed = None
if 'df_clustered' not in st.session_state:
    st.session_state.df_clustered = None
if 'clustering_done' not in st.session_state:
    st.session_state.clustering_done = False
if 'cluster_metrics' not in st.session_state:
    st.session_state.cluster_metrics = {}
if 'forecast_df' not in st.session_state:
    st.session_state.forecast_df = None
if 'anomaly_df' not in st.session_state:
    st.session_state.anomaly_df = None
if 'carbon_summary' not in st.session_state:
    st.session_state.carbon_summary = None

# ========== HELPER FUNCTIONS ==========
def show_card(content):
    """Bungkus konten dengan card"""
    st.markdown(f'<div class="card">{content}</div>', unsafe_allow_html=True)

# ========== CONTENT PER STEP ==========

# --- STEP 1: DASHBOARD ---
def step_dashboard():
    st.title("📊 Dashboard")
    st.markdown("*Ringkasan kinerja emisi karbon usaha Anda*")
    
    if st.session_state.df_clustered is not None:
        df = st.session_state.df_clustered
        summary = get_emission_summary(df)
        
        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["total_emisi_kg"]:,.0f}</div><div class="metric-label">Total CO₂ (kg)</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["rata_rata_emisi_per_periode"]:.0f}</div><div class="metric-label">Rata-rata/hari (kg)</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["emisi_tertinggi"]:.0f}</div><div class="metric-label">Tertinggi (kg)</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["emisi_terendah"]:.0f}</div><div class="metric-label">Terendah (kg)</div></div>', unsafe_allow_html=True)
        
        # === TAMBAHAN: Green Champion Badge ===
        if summary['total_emisi_kg'] < 10000:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 20px; padding: 0.6rem 1rem; text-align: center; margin: 1rem 0;">
                🏆 <strong>Green Champion!</strong> Total emisi di bawah 10 ton — Luar biasa!
            </div>
            """, unsafe_allow_html=True)
        
        # Grafik Tren
        fig = viz.plot_emission_trend(df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📂 Belum ada data. Silakan upload dan proses data terlebih dahulu.")
        
# --- STEP 2: UPLOAD DATA ---
def step_upload():
    st.title("📂 Upload Data Emisi")
    st.markdown("*Unggah file aktivitas energi harian Anda*")
    
    with st.container():
        col1, col2 = st.columns([2,1])
        with col1:
            fuel_type = st.radio(
                "Pilih jenis bahan bakar:",
                options=['solar', 'bensin', 'kayu', 'lpg'],
                format_func=lambda x: f"{FUEL_FACTORS[x]['icon']} {FUEL_FACTORS[x]['sumber'].split()[0]} - {x.upper()}",
                horizontal=True
            )
        with col2:
            st.caption(f"Faktor emisi: {FUEL_FACTORS[fuel_type]['value']} {FUEL_FACTORS[fuel_type]['unit']}")
    
    uploaded_file = st.file_uploader("Upload CSV atau Excel", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        if 'tanggal' in df.columns:
            df['tanggal'] = pd.to_datetime(df['tanggal'])
        st.session_state.df_raw = df
        st.session_state.fuel_type = fuel_type
        st.success(f"✅ Data berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
        st.dataframe(df, use_container_width=True)
        if st.button("Lanjut ke Perhitungan Emisi"):
            st.session_state.step = 3
            st.rerun()
    else:
        st.info("Silakan upload file CSV/Excel.")

# --- STEP 3: PERHITUNGAN EMISI ---
def step_emission():
    st.title("📊 Perhitungan Emisi Karbon")
    
    # Cek apakah data mentah tersedia
    if 'df_raw' not in st.session_state or st.session_state.df_raw is None:
        st.warning("Belum ada data. Upload data dulu di Step 2.")
        return
    
    # Ambil data dari session_state
    df_raw = st.session_state.df_raw
    fuel_type = st.session_state.get('fuel_type', 'solar')
    
    # Hitung emisi
    df = calculate_emissions(df_raw, fuel_type=fuel_type)
    st.session_state.df_processed = df
    summary = get_emission_summary(df)
    
    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["total_emisi_kg"]:,.0f}</div><div class="metric-label">Total CO₂ (kg)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["rata_rata_emisi_per_periode"]:.0f}</div><div class="metric-label">Rata-rata/hari (kg)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["emisi_tertinggi"]:.0f}</div><div class="metric-label">Tertinggi (kg)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["emisi_terendah"]:.0f}</div><div class="metric-label">Terendah (kg)</div></div>', unsafe_allow_html=True)
    
    # === BAR CHART Total Emisi per Sumber ===
    sumber_emisi = ['Listrik', 'BBM', 'Transportasi']
    nilai_emisi = [
        df['emisi_listrik_kg'].sum(),
        df['emisi_bbm_kg'].sum(),
        df['emisi_transport_kg'].sum()
    ]
    
    fig_bar = go.Figure(data=[go.Bar(
        x=sumber_emisi,
        y=nilai_emisi,
        text=[f'{val:,.0f} kg' for val in nilai_emisi],
        textposition='auto',
        marker_color=['#3498db', '#e74c3c', '#2ecc71'],
        textfont=dict(color='white')
    )])
    fig_bar.update_layout(
        title='Total Emisi per Sumber (kg CO₂)',
        xaxis_title='Sumber Emisi',
        yaxis_title='Total Emisi (kg CO₂)',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3')
    )
    fig_bar.update_xaxes(tickfont=dict(color='#e6edf3'))
    fig_bar.update_yaxes(tickfont=dict(color='#e6edf3'), gridcolor='#30363d')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detail Kontribusi (teks)
    st.markdown(f"""
    📋 **Detail Kontribusi:**
    - ⚡ Listrik: {summary['kontribusi_listrik_persen']:.1f}%
    - 🔥 {fuel_type.upper()}: {summary['kontribusi_bbm_persen']:.1f}%
    - 🚚 Transportasi: {summary['kontribusi_transport_persen']:.1f}%
    """)
    
# --- STEP 4: CLUSTERING ---
def step_clustering():
    st.title("🧩 K-Means Clustering")
    
    if st.session_state.df_processed is None:
        st.warning("Proses emisi dulu.")
        return
    
    df = st.session_state.df_processed
    n_clusters = st.selectbox("Jumlah Cluster (K)", [2,3,4,5], index=1)
    analyzer = EmissionClusterAnalyzer(n_clusters=n_clusters, random_state=42)
    
    # Elbow Method
    if st.button("🔍 Tentukan K Optimal"):
        with st.spinner("Menghitung Elbow Method..."):
            elbow_result = analyzer.find_optimal_k(df, max_k=10)
            fig = viz.plot_elbow_curve(elbow_result['wss'], elbow_result['k_range'], elbow_result['optimal_k'])
            st.plotly_chart(fig, use_container_width=True)
            st.info(f"Rekomendasi K optimal: **{elbow_result['optimal_k']}**")
    
    # Jalankan Clustering
    if st.button("🚀 Jalankan Clustering", type="primary"):
        with st.spinner("Sedang melakukan clustering..."):
            df_clustered = analyzer.fit(df)
            metrics = analyzer.get_evaluation_metrics()
            st.session_state.df_clustered = df_clustered
            st.session_state.cluster_metrics = metrics
            st.session_state.clustering_done = True
            st.success("✅ Clustering selesai!")
            st.balloons()
    
    # === TAMPILKAN HASIL LENGKAP (jika clustering sudah dilakukan) ===
    if st.session_state.clustering_done:
        dfc = st.session_state.df_clustered
        metrics = st.session_state.cluster_metrics
        emission_summary = get_emission_summary(dfc)
        fuel_type = st.session_state.get('fuel_type', 'solar')
        fuel_info = get_fuel_info(fuel_type)
        
        # --- Evaluasi Kualitas Cluster ---
        st.markdown("#### 📊 Evaluasi Kualitas Cluster")
        col1, col2, col3 = st.columns(3)
        col1.metric("Silhouette Score", f"{metrics.get('silhouette_score',0):.4f}")
        col2.metric("Calinski-Harabasz", f"{metrics.get('calinski_harabasz_score',0):.2f}")
        col3.metric("Davies-Bouldin", f"{metrics.get('davies_bouldin_score',0):.4f}")
        
        # --- Distribusi Cluster ---
        st.markdown("#### 📋 Distribusi Cluster")
        cluster_counts = dfc['cluster_label'].value_counts()
        for cluster, count in cluster_counts.items():
            emoji = "🟢" if cluster == "Rendah" else ("🟡" if cluster == "Sedang" else "🔴")
            st.write(f"{emoji} **{cluster}**: {count} periode ({(count/len(dfc))*100:.1f}%)")
        
        # --- Rekomendasi Pengurangan Emisi ---
        st.subheader("💡 Rekomendasi Pengurangan Emisi")
        if 'Tinggi' in cluster_counts.index:
            st.warning("🔴 **Periode Emisi Tinggi Terdeteksi!** Evaluasi aktivitas pada periode tersebut.")
            st.markdown("""
            **Langkah yang bisa dilakukan:**
            - ✅ Periksa jadwal produksi di periode emisi tinggi
            - ✅ Cek apakah ada mesin/alat yang boros energi
            - ✅ Pertimbangkan perawatan rutin peralatan produksi
            """)
        
        if emission_summary['kontribusi_listrik_persen'] > 40:
            st.info("💡 **Sumber emisi terbesar: Listrik**")
            st.markdown("""
            **Rekomendasi hemat listrik:**
            - Ganti lampu ke LED (hemat 60-80%)
            - Matikan peralatan saat tidak digunakan
            - Pertimbangkan panel surya untuk kebutuhan siang hari
            """)
        elif emission_summary['kontribusi_bbm_persen'] > 40:
            st.info(f"💡 **Sumber emisi terbesar: {fuel_type.upper()}**")
            st.markdown(f"""
            **Rekomendasi hemat bahan bakar:**
            - Lakukan perawatan rutin mesin 
            - Catat konsumsi {fuel_type} harian untuk evaluasi
            - Jika pakai kayu bakar, pastikan kayu kering (efisiensi lebih tinggi)
            """)
        elif emission_summary['kontribusi_transport_persen'] > 40:
            st.info("💡 **Sumber emisi terbesar: Transportasi**")
            st.markdown("""
            **Rekomendasi efisiensi transportasi:**
            - Optimalisasi rute distribusi
            - Tingkatkan muatan per perjalanan
            - Kelompokkan pelanggan berdasarkan zona
            """)
        
        # --- Visualisasi (3 Tabs) ---
        st.subheader("📈 Dashboard Visualisasi")
        tab1, tab2, tab3 = st.tabs(["📈 Tren Emisi", "🥧 Kontribusi Sumber", "🎯 Hasil Clustering"])
        with tab1:
            fig_trend = viz.plot_emission_trend(dfc)
            st.plotly_chart(fig_trend, use_container_width=True)
        with tab2:
            fig_pie = viz.plot_emission_breakdown_pie(dfc)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown(f"""
            📋 **Detail Kontribusi:**
            - ⚡ Listrik: {emission_summary['kontribusi_listrik_persen']:.1f}%
            - {fuel_info['icon']} {fuel_type.upper()}: {emission_summary['kontribusi_bbm_persen']:.1f}%
            - 🚚 Transportasi: {emission_summary['kontribusi_transport_persen']:.1f}%
            """)
        with tab3:
            fig_scatter = viz.plot_cluster_scatter(dfc)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # --- Data Lengkap ---
        with st.expander("📋 Data Lengkap con Label Cluster", expanded=False):
            st.dataframe(dfc, use_container_width=True)

# --- STEP 5: FORECASTING ---
def step_forecasting():
    st.title("🔮 Forecasting Emisi (30 Hari)")
    st.markdown("*Prediksi emisi karbon 30 hari ke depan menggunakan Linear Regression*")
    
    if st.session_state.df_clustered is None:
        st.warning("⚠️ Clustering belum dilakukan. Jalankan clustering dulu di Step 4.")
        return
    
    df = st.session_state.df_clustered
    
    # Validasi data
    is_valid, msg = validate_forecast_data(df)
    if not is_valid:
        st.warning(f"⚠️ {msg}")
        return
    
    if st.button("🚀 Jalankan Forecasting", type="primary"):
        with st.spinner("⏳ Menghitung prediksi..."):
            forecaster = EmissionForecaster()
            result = forecaster.forecast(df, periods=30)
            
            if result['status'] == 'success':
                st.session_state.forecast_df = result['forecast_df']
                st.session_state.forecast_metrics = result['metrics']
                st.success("✅ Forecasting selesai!")
                st.balloons()
            else:
                st.error(f"❌ Error: {result.get('error_message', 'Unknown error')}")
    
    # Tampilkan hasil jika sudah ada
    if st.session_state.forecast_df is not None:
        fdf = st.session_state.forecast_df
        metrics = st.session_state.get('forecast_metrics', {})
        
        # Metrik Akurasi
        st.markdown("#### 📊 Metrik Akurasi")
        col1, col2, col3 = st.columns(3)
        col1.metric("MAE", f"{metrics.get('mae', 0):.2f} kg")
        col2.metric("RMSE", f"{metrics.get('rmse', 0):.2f} kg")
        col3.metric("MAPE", f"{metrics.get('mape', 0):.2f}%")
        
        # Grafik Prediksi
        st.markdown("#### 📈 Grafik Prediksi 30 Hari")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fdf['tanggal'],
            y=fdf['yhat'],
            mode='lines+markers',
            name='Prediksi',
            line=dict(color='#2ecc71', width=2),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=fdf['tanggal'],
            y=fdf['yhat_lower'],
            mode='lines',
            name='Lower Bound (80%)',
            line=dict(dash='dash', color='#8b949e'),
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=fdf['tanggal'],
            y=fdf['yhat_upper'],
            mode='lines',
            name='Upper Bound (80%)',
            line=dict(dash='dash', color='#8b949e'),
            fill='tonexty',
            fillcolor='rgba(46,204,113,0.1)',
            showlegend=True
        ))
        fig.update_layout(
            title='Prediksi Emisi Harian',
            xaxis_title='Tanggal',
            yaxis_title='Emisi (kg CO₂)',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3')
        )
        fig.update_xaxes(tickfont=dict(color='#e6edf3'))
        fig.update_yaxes(tickfont=dict(color='#e6edf3'), gridcolor='#30363d')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Prediksi
        st.markdown("#### 📋 Tabel Prediksi Detail")
        st.dataframe(
            fdf[['tanggal', 'yhat', 'yhat_lower', 'yhat_upper']].round(2),
            use_container_width=True
        )
        
        # Ringkasan Tren
        avg_forecast = fdf['yhat'].mean()
        last_10_avg = fdf['yhat'].tail(10).mean()
        first_10_avg = fdf['yhat'].head(10).mean()
        pct_change = ((last_10_avg - first_10_avg) / first_10_avg * 100) if first_10_avg > 0 else 0
        
        if pct_change > 5:
            trend_text = "📈 **Cenderung NAIK**"
            trend_color = "#e74c3c"
        elif pct_change < -5:
            trend_text = "📉 **Cenderung TURUN**"
            trend_color = "#2ecc71"
        else:
            trend_text = "➡️ **Cenderung STABIL**"
            trend_color = "#f1c40f"
        
        st.markdown(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 1rem; margin-top: 1rem;">
            <b>📌 Ringkasan:</b><br>
            • Rata-rata prediksi: <b>{avg_forecast:.1f} kg CO₂/hari</b><br>
            • Tren: <span style="color:{trend_color};">{trend_text}</span><br>
            • Perubahan 10 hari pertama vs 10 hari terakhir: <b>{pct_change:+.1f}%</b>
        </div>
        """, unsafe_allow_html=True)
        
# --- STEP 6: ANOMALI ---
def step_anomaly():
    st.title("⚠️ Deteksi Anomali Emisi")
    st.markdown("*Identifikasi hari-hari dengan pola emisi yang tidak biasa*")
    
    if st.session_state.df_clustered is None:
        st.warning("⚠️ Clustering belum dilakukan. Jalankan clustering dulu di Step 4.")
        return
    
    df = st.session_state.df_clustered
    
    # Validasi data
    is_valid, msg = validate_anomaly_data(df)
    if not is_valid:
        st.warning(f"⚠️ {msg}")
        return
    
    # Slider contamination
    contamination = st.slider(
        "🎯 Tingkat Kontaminasi (Sensitivity)",
        min_value=0.01,
        max_value=0.20,
        value=st.session_state.get('anomaly_contamination', 0.05),
        step=0.01,
        help="Semakin tinggi nilai, semakin sensitif deteksi anomali (default 5%)"
    )
    st.caption(f"📊 Asumsikan ~{int(contamination*100)}% data sebagai anomali")
    
    if st.button("🔍 Deteksi Anomali", type="primary"):
        with st.spinner("⏳ Mendeteksi anomali..."):
            detector = AnomalyDetector(contamination=contamination)
            result = detector.detect_anomalies(df)
            st.session_state.anomaly_df = result
            summary = detector.get_anomaly_details(result)
            st.session_state.anomaly_summary = summary
            st.success(f"✅ Deteksi selesai! Ditemukan {summary['total_anomalies']} anomali.")
            st.balloons()
    
    # Tampilkan hasil jika sudah ada
    if st.session_state.anomaly_df is not None:
        adf = st.session_state.anomaly_df
        summary = st.session_state.get('anomaly_summary', {})
        
        # Metrik
        col1, col2 = st.columns(2)
        col1.metric("🚨 Total Anomali", summary.get('total_anomalies', 0))
        col2.metric("📊 Persentase", f"{summary.get('anomaly_percentage', 0):.1f}%")
        
        # Grafik Anomali
        st.markdown("#### 📈 Visualisasi Anomali")
        try:
            fig_anomaly = viz.plot_emission_trend_with_anomalies(adf)
            st.plotly_chart(fig_anomaly, use_container_width=True)
        except AttributeError:
            # Fallback jika fungsi tidak ada di visualizer
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=adf['tanggal'],
                y=adf['total_emisi_kgco2'],
                mode='lines+markers',
                name='Emisi Normal',
                line=dict(color='#2ecc71'),
                marker=dict(size=6, color='#2ecc71')
            ))
            # Tandai anomali
            anomaly_data = adf[adf['is_anomaly'] == 1]
            if len(anomaly_data) > 0:
                fig.add_trace(go.Scatter(
                    x=anomaly_data['tanggal'],
                    y=anomaly_data['total_emisi_kgco2'],
                    mode='markers',
                    name='🔴 Anomali',
                    marker=dict(size=12, color='#e74c3c', symbol='x')
                ))
            fig.update_layout(
                title='Emisi Harian dengan Anomali',
                xaxis_title='Tanggal',
                yaxis_title='Emisi (kg CO₂)',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e6edf3')
            )
            fig.update_xaxes(tickfont=dict(color='#e6edf3'))
            fig.update_yaxes(tickfont=dict(color='#e6edf3'), gridcolor='#30363d')
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Anomali
        st.markdown("#### 📋 Daftar Anomali")
        anomaly_table = adf[adf['is_anomaly'] == 1][['tanggal', 'total_emisi_kgco2']]
        if len(anomaly_table) > 0:
            st.dataframe(anomaly_table, use_container_width=True)
        else:
            st.success("✅ Tidak ada anomali terdeteksi! Semua emisi normal.")

# --- STEP 7: CARBON CREDIT ---
def step_carbon():
    st.title("💰 Estimasi Carbon Credit")
    st.markdown("*Hitung potensi pendapatan dari perdagangan karbon*")
    
    if st.session_state.df_clustered is None:
        st.warning("⚠️ Clustering belum dilakukan. Jalankan clustering dulu di Step 4.")
        return
    
    df = st.session_state.df_clustered
    
    # Pilihan harga karbon
    st.markdown("### ⚙️ Pengaturan Harga Karbon")
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input(
            "💰 Harga per ton (IDR)",
            min_value=30000,
            max_value=150000,
            value=st.session_state.get('carbon_price_idr', 30000),
            step=5000,
            help="Default Rp 30.000 (Perpres 110/2025) | Pasar ~Rp 70.000"
        )
    with col2:
        st.caption("📌 **Referensi:**")
        st.caption("• Perpres: Rp 30.000/ton")
        st.caption("• IDXCarbon: Rp 70.000/ton")
    
    if st.button("💚 Hitung Carbon Credit", type="primary"):
        with st.spinner("⏳ Menghitung..."):
            try:
                # Pastikan fungsi calculate_carbon_credit tersedia
                from emission_calculator import calculate_carbon_credit, calculate_carbon_credit_per_row
                
                summary = calculate_carbon_credit(df, carbon_price_idr_per_ton=price)
                df_with_credit = calculate_carbon_credit_per_row(
                    df,
                    summary['baseline_emisi_kg'],
                    carbon_price_idr=price
                )
                
                st.session_state.carbon_summary = summary
                st.session_state.df_with_credit = df_with_credit
                st.success("✅ Perhitungan carbon credit selesai!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Tampilkan hasil jika sudah ada
    if st.session_state.carbon_summary is not None:
        cs = st.session_state.carbon_summary
        
        # Metrik Utama
        st.markdown("#### 📊 Ringkasan Carbon Credit")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌍 Total Emisi", f"{cs['total_emisi_kg']/1000:.2f} ton")
        col2.metric("💳 Carbon Credit", f"{cs['carbon_credit_ton']:.4f} ton")
        col3.metric("🌳 Pohon Diperlukan", f"{cs['trees_to_plant']} pohon")
        col4.metric("💰 Potensi Pendapatan", f"Rp {cs['potential_revenue_idr_perpres']/1e6:.1f} jt")
        
        # Potensi Pendapatan (2 skenario)
        st.markdown("#### 💰 Potensi Pendapatan (2 Skenario)")
        ref_col1, ref_col2 = st.columns(2)
        with ref_col1:
            st.info(f"**Perpres 110/2025**\nRp {cs['potential_revenue_idr_perpres']/1e6:.1f} juta")
        with ref_col2:
            market_revenue = cs['carbon_credit_ton'] * 70000
            st.info(f"**IDXCarbon (Market)**\nRp {market_revenue/1e6:.1f} juta")
        
        # Tabel Detail
        st.markdown("#### 📋 Detail Credit per Periode")
        if 'df_with_credit' in st.session_state:
            df_credit = st.session_state.df_with_credit
            st.dataframe(
                df_credit[['tanggal', 'total_emisi_kgco2', 'carbon_credit_kg', 
                           'offset_trees', 'revenue_per_day_idr']].round(2),
                use_container_width=True
            )
        else:
            st.info("Data detail tidak tersedia.")

# --- STEP 8: LAPORAN MRV ---
def step_report():
    st.title("📄 Laporan MRV")
    if st.session_state.df_clustered is None:
        st.warning("Belum ada data untuk laporan.")
        return
    df = st.session_state.df_clustered
    excel_data = rex.export_to_excel(df)
    st.download_button("📊 Download Excel", excel_data, "laporan.xlsx")
    html_report = rex.generate_html_report(df, st.session_state.cluster_metrics, get_emission_summary(df))
    st.download_button("📄 Download HTML", html_report, "laporan.html")

# ========== NAVIGASI ==========
def navigate():
    st.markdown("---")
    col_back, col_step, col_next = st.columns([1, 2, 1])
    
    with col_back:
        if st.button("⬅ Kembali", disabled=(st.session_state.step == 1), use_container_width=True):
            if st.session_state.step > 1:
                st.session_state.step -= 1
                st.rerun()
    
    with col_step:
        st.markdown(f"<div style='text-align:center; color:#8b949e;'>Langkah {st.session_state.step} dari 8</div>", unsafe_allow_html=True)
    
    with col_next:
        if st.button("Lanjut ➡", disabled=(st.session_state.step == 8), use_container_width=True):
            if st.session_state.step < 8:
                st.session_state.step += 1
                st.rerun()

# ========== MAIN SWITCH ==========
step_functions = {
    1: step_dashboard,
    2: step_upload,
    3: step_emission,
    4: step_clustering,
    5: step_forecasting,
    6: step_anomaly,
    7: step_carbon,
    8: step_report,
}

# Jalankan step yang aktif
step_functions[st.session_state.step]()

# Tampilkan navigasi di bawah
navigate()

# Footer
st.markdown('<div class="footer">© 2026 EmisiKu • Skripsi Ariel Adrienne Setiawan</div>', unsafe_allow_html=True)