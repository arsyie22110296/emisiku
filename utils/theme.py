# utils/theme.py
import streamlit as st

def apply_dark_theme():
    """
    Menerapkan dark theme premium:
    - Background hitam pekat (#0d1117)
    - Sidebar abu gelap (#161b22)
    - Aksen hijau (#2ecc71)
    - Font modern (Inter)
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── BACKGROUND UTAMA ── */
    .stApp {
        background-color: #0d1117 !important;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f0f6fc !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #2ecc71 !important;
    }

    /* ── TEKS ── */
    .stApp p, .stApp li, .stApp label,
    .stApp .stMarkdown, .stApp span {
        color: #e6edf3 !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #ffffff !important;
    }

    /* ── METRIC CARD ── */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #2ecc71;
        box-shadow: 0 8px 24px rgba(46,204,113,0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #2ecc71;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #8b949e;
        margin-top: 0.3rem;
    }

    /* ── TOMBOL ── */
    .stButton > button {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(46,204,113,0.35);
        color: white;
    }

    /* ── EXPANDER ── */
    div[data-testid="stExpander"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        transition: 0.2s;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(46,204,113,0.4);
    }

    /* ── TAB ── */
    button[data-baseweb="tab"] {
        color: #8b949e !important;
        font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2ecc71 !important;
        border-bottom: 2px solid #2ecc71 !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        background: #161b22 !important;
    }

    /* ── ALERT / INFO / SUCCESS ── */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border-left-width: 4px;
    }

    /* ── DOWNLOAD BUTTON ── */
    .stDownloadButton button {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46,204,113,0.25) !important;
    }
    .stDownloadButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(46,204,113,0.4) !important;
    }

    /* ── FOOTER ── */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #8b949e;
        font-size: 0.75rem;
        border-top: 1px solid #30363d;
        margin-top: 2rem;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0d1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #2ecc71;
    }

    /* ── STICKY HEADER (tambahan untuk header agar tidak bentrok) ── */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(13, 17, 23, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #30363d;
        padding: 0.6rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)