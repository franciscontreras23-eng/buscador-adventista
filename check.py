import streamlit as st
import pandas as pd
import os
from google import genai
from st_copy_to_clipboard import st_copy_to_clipboard


# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Biblioteca Digital Francis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= =========================
# ESTILOS PREMIUM (Vanilla CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
    }
    
    .dashboard-header {
        font-family: 'Manrope', sans-serif;
        text-align: center;
        padding: 2.5rem 1rem 0.5rem 1rem;
        color: #ffffff;
        font-weight: 800;
        font-size: 2.8rem !important;
        letter-spacing: -1px;
    }
    
    .dashboard-subheader {
        text-align: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 1rem;
        font-style: italic;
        margin-bottom: 2rem;
    }

    /* Estilos Dark para Inputs para unificar */
    div[data-baseweb="input"], input, textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="input"] input {
        color: #ffffff !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #2563eb !important;
        background-color: rgba(255, 255, 255, 0.07) !important;
    }

    div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    
    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* Cards - Estilo Digital Archive */
    .book-card {
        background: #141414;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.4s ease;
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    
    .book-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0px 15px 40px rgba(0, 0, 0, 0.7);
    }
    
    .book-title {
        font-family: 'Manrope', sans-serif;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.3;
        transition: color 0.3s;
    }
    
    .book-card:hover .book-title {
        color: #3b82f6;
    }
    
    .drive-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #2563eb !important;
        color: #ffffff !important;
        text-decoration: none !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        transition: background 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .drive-btn:hover {
        background: #1d4ed8 !important;
    }
    
    .stat-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 2.5rem;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem 2rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        text-align: center;
        min-width: 140px;
    }
    
    .stat-value {
        font-family: 'Manrope', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }
    
    .book-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.04);
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.7rem;
        padding: 0.25rem 0.55rem;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        font-weight: 500;
    }

    .icon-box {
        width: 2.5rem;
        height: 2.5rem;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3b82f6;
    }
    
    .icon-box span { font-size: 1.4rem; }
    
    .collection-pill {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .file-stats {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.3);
    }
    
    .stButton>button {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.02);
        color: #ffffff;
    }
    .stCheckbox label { color: rgba(255,255,255,0.7) !important; }
</style>
"""), unsafe_allow_html=True)

