import streamlit as st


def apply_custom_styles():
    """Aplica CSS customizado para design Clean Minimal"""
    st.markdown("""
    <style>
    /* ==================== GLOBAL ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #fafafa;
        padding: 2rem 3rem;
    }
    
    /* ==================== HEADER ==================== */
    h1 {
        font-weight: 700;
        font-size: 2.5rem;
        color: #0a0a0a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main > div:first-child p {
        color: #6b6b6b;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* ==================== SIDEBAR ==================== */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e5;
        padding: 2rem 1.5rem;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #0a0a0a;
        margin-bottom: 1rem;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #3a3a3a;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e5e5e5;
    }
    
    /* ==================== BUTTONS ==================== */
    .stButton > button {
        background-color: #0a0a0a;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #2a2a2a;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stDownloadButton > button {
        background-color: #ffffff;
        color: #0a0a0a;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background-color: #f5f5f5;
        border-color: #d4d4d4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* ==================== INPUTS ==================== */
    .stSelectbox > div > div,
    .stSlider > div > div > div {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
    }
    
    .stFileUploader {
        background-color: #ffffff;
        border: 2px dashed #d4d4d4;
        border-radius: 8px;
        padding: 2rem;
        transition: all 0.2s ease;
    }
    
    .stFileUploader:hover {
        border-color: #a3a3a3;
        background-color: #fafafa;
    }
    
    /* ==================== ALERTS ==================== */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem 1.25rem;
        font-size: 0.9375rem;
    }
    
    .stSuccess {
        background-color: #f0fdf4;
        color: #166534;
    }
    
    .stInfo {
        background-color: #eff6ff;
        color: #1e40af;
    }
    
    .stWarning {
        background-color: #fffbeb;
        color: #92400e;
    }
    
    .stError {
        background-color: #fef2f2;
        color: #991b1b;
    }
    
    /* ==================== PROGRESS BAR ==================== */
    .stProgress > div > div > div {
        background-color: #0a0a0a;
        border-radius: 4px;
    }
    
    /* ==================== VIDEO PREVIEW ==================== */
    [data-testid="stVideo"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    [data-testid="stCaptionContainer"] {
        font-size: 0.875rem;
        color: #6b6b6b;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* ==================== SUBHEADER ==================== */
    h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0a0a0a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }
    
    /* ==================== SPINNER ==================== */
    .stSpinner > div {
        border-top-color: #0a0a0a !important;
    }
    
    /* ==================== COLUMNS ==================== */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    /* ==================== TOGGLE ==================== */
    .stCheckbox {
        font-weight: 500;
    }
    
    </style>
    """, unsafe_allow_html=True)
