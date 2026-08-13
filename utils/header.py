# utils/header.py
import streamlit as st
import base64
from pathlib import Path

def show_header():
    logo_path = Path("emisiku_logo.png")
    
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:200px; width:auto; display:block; margin:0 0 -18px 0; padding:0; line-height:0;">'
    else:
        logo_html = '<div style="font-size:4rem; line-height:1;">🌿</div>'

    st.markdown(f"""
    <div style="
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(13, 17, 23, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #30363d;
        padding: 2px 1rem 4px 0.3rem;
        min-height: 110px;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    ">
        <div style="display: flex; flex-direction: column; align-items: flex-start; margin: 0; padding: 0; gap: 0;">
            {logo_html}
            <div style="line-height: 1.1; margin: 0; padding: 0 0 0 2px;">
                <span style="font-size:1.15rem; font-weight:600; color:#FFFFFF; letter-spacing:-0.5px;">EmisiKu</span><br>
                <span style="font-size:0.72rem; color:#8b949e; font-weight:400;">Carbon Tracking for SMEs</span>
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; margin-top: 70px;">
            <span style="background:rgba(46,204,113,0.12); color:#2ecc71; font-size:0.65rem; padding:3px 10px; border-radius:20px; border:1px solid rgba(46,204,113,0.25);">
                🟢 Perpres 110/2025
            </span>
            <span style="background:rgba(255,215,0,0.08); color:#FFD700; font-size:0.65rem; padding:3px 10px; border-radius:20px; border:1px solid rgba(255,215,0,0.15);">
                ⚡ MRV Ready
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)