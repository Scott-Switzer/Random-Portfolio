"""
styles.py - Design System for The Dartboard Experiment
"""

import streamlit as st

# =============================================================================
# DESIGN TOKENS
# =============================================================================

COLORS = {
    "light": {
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F9FAFB",
        "bg_tertiary": "#F3F4F6",
        "text_primary": "#111827",
        "text_secondary": "#4B5563",
        "text_muted": "#6B7280",
        "border": "#E5E7EB",
        "border_light": "#F3F4F6",
        "accent": "#10B981",
        "accent_hover": "#059669",
        "accent_light": "#D1FAE5",
        "accent_text": "#065F46",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6",
    },
    "dark": {
        "bg_primary": "#111827",
        "bg_secondary": "#1F2937",
        "bg_tertiary": "#374151",
        "text_primary": "#F9FAFB",
        "text_secondary": "#D1D5DB",
        "text_muted": "#9CA3AF",
        "border": "#374151",
        "border_light": "#4B5563",
        "accent": "#10B981",
        "accent_hover": "#34D399",
        "accent_light": "#064E3B",
        "accent_text": "#A7F3D0",
        "error": "#F87171",
        "warning": "#FBBF24",
        "info": "#60A5FA",
    }
}

CHAPMAN_RED = "#A50034"

# =============================================================================
# THEME MANAGEMENT
# =============================================================================

def init_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

def get_theme():
    init_theme()
    return st.session_state.theme

def toggle_theme():
    init_theme()
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

def get_colors():
    return COLORS[get_theme()]

# =============================================================================
# MAIN CSS
# =============================================================================

def get_css():
    c = get_colors()
    theme = get_theme()
    
    return f"""
    <style>
    /* ============================================
       FONTS
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Serif:wght@400;500;600;700&display=swap');
    
    /* ============================================
       GLOBAL OVERRIDES
       ============================================ */
    html, body, [class*="st-"] {{
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    
    .stApp {{
        background-color: {c['bg_primary']} !important;
    }}
    
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        color: {c['text_primary']} !important;
    }}
    
    p, li, span, label, .stMarkdown p, .stMarkdown li {{
        color: {c['text_primary']} !important;
    }}
    
    /* ============================================
       HIDE STREAMLIT DEFAULTS
       ============================================ */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ============================================
       HERO SECTION
       ============================================ */
    .hero-container {{
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
        max-width: 800px;
        margin: 0 auto;
    }}
    
    .hero-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
    }}
    
    .hero-title {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        color: {c['text_primary']} !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
    }}
    
    .hero-subtitle {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.5rem !important;
        font-style: italic;
        color: {c['text_secondary']} !important;
        margin-bottom: 1.5rem !important;
    }}
    
    .hero-description {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1.125rem !important;
        color: {c['text_secondary']} !important;
        line-height: 1.75 !important;
        margin-bottom: 2rem !important;
    }}
    
    /* ============================================
       SECTION STYLING (Minimal - no boxes)
       ============================================ */
    .section-header {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: {c['text_primary']} !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {c['accent']};
        margin-bottom: 1rem;
        margin-top: 2rem;
    }}
    
    .section-content {{
        color: {c['text_primary']} !important;
        line-height: 1.7;
    }}
    
    .section-content p {{
        margin-bottom: 1rem;
    }}
    
    .section-content ul {{
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    .section-content li {{
        margin-bottom: 0.5rem;
    }}
    
    .section-content b, .section-content strong {{
        color: {c['accent']} !important;
    }}
    
    .section-content a {{
        color: {c['accent']} !important;
        text-decoration: none;
    }}
    
    .section-content a:hover {{
        text-decoration: underline;
    }}
    
    /* ============================================
       QUOTE BOX
       ============================================ */
    .quote-box {{
        background: {c['bg_secondary']};
        border-left: 4px solid {c['accent']};
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 8px 8px 0;
    }}
    
    .quote-box p {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.1rem;
        font-style: italic;
        color: {c['text_primary']} !important;
        margin: 0 !important;
        line-height: 1.6;
    }}
    
    .quote-box .attribution {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.875rem;
        font-style: normal;
        color: {c['text_muted']} !important;
        margin-top: 0.75rem !important;
    }}
    
    /* ============================================
       METRIC CARDS
       ============================================ */
    .metric-row {{
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }}
    
    .metric-card {{
        flex: 1;
        min-width: 150px;
        background: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.2s ease;
    }}
    
    .metric-card:hover {{
        border-color: {c['accent']};
        transform: translateY(-2px);
    }}
    
    .metric-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: {c['accent']};
        line-height: 1.2;
    }}
    
    .metric-label {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: {c['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }}
    
    .metric-delta {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.8rem;
        color: {c['text_secondary']};
        margin-top: 0.5rem;
    }}
    
    /* ============================================
       FOOTER
       ============================================ */
    .site-footer {{
        margin-top: 4rem;
        padding: 2rem;
        background: {c['bg_secondary']};
        border-top: 1px solid {c['border']};
    }}
    
    .footer-grid {{
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto;
    }}
    
    .footer-brand {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }}
    
    .footer-logo {{
        width: 48px;
        height: 48px;
        filter: {'invert(1)' if theme == 'dark' else 'none'};
    }}
    
    .footer-title {{
        font-family: 'IBM Plex Serif', Georgia, serif;
        font-size: 1.125rem;
        font-weight: 600;
        color: {c['text_primary']};
        margin-bottom: 0.25rem;
    }}
    
    .footer-subtitle {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.875rem;
        color: {c['text_secondary']};
    }}
    
    .footer-section-title {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {c['text_muted']};
        margin-bottom: 0.75rem;
    }}
    
    .footer-link {{
        display: block;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.875rem;
        color: {c['text_secondary']};
        text-decoration: none;
        padding: 0.25rem 0;
        transition: color 0.15s ease;
    }}
    
    .footer-link:hover {{
        color: {c['accent']};
    }}
    
    .footer-disclaimer {{
        grid-column: 1 / -1;
        text-align: center;
        padding-top: 1.5rem;
        margin-top: 1.5rem;
        border-top: 1px solid {c['border']};
        font-size: 0.75rem;
        color: {c['text_muted']};
    }}
    
    /* ============================================
       STREAMLIT COMPONENT OVERRIDES
       ============================================ */
    
    /* Buttons */
    .stButton > button {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }}
    
    .stButton > button[kind="primary"] {{
        background-color: {c['accent']} !important;
        color: white !important;
        border: none !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {c['accent_hover']} !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        color: {c['text_primary']} !important;
        border: 1px solid {c['border']} !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: {c['bg_secondary']} !important;
        border-color: {c['text_muted']} !important;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        color: {c['text_primary']} !important;
        background-color: {c['bg_secondary']} !important;
        border-radius: 8px !important;
    }}
    
    /* Selectbox & Inputs */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {{
        background-color: {c['bg_secondary']} !important;
        border-color: {c['border']} !important;
        color: {c['text_primary']} !important;
        border-radius: 8px !important;
    }}
    
    /* Slider */
    .stSlider > div > div > div > div {{
        background-color: {c['accent']} !important;
    }}
    
    /* Dataframe */
    .stDataFrame {{
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: {c['accent']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: {c['text_secondary']} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {c['bg_secondary']} !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: {c['text_primary']} !important;
    }}
    
    /* Info/Success/Warning boxes */
    .stAlert {{
        border-radius: 8px !important;
    }}
    
    /* Divider */
    hr {{
        border-color: {c['border']} !important;
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        border-radius: 8px !important;
    }}
    
    /* Links */
    a {{
        color: {c['accent']} !important;
    }}
    
    /* Tables in markdown */
    .stMarkdown table {{
        border-collapse: collapse;
        width: 100%;
    }}
    
    .stMarkdown th {{
        background-color: {c['bg_tertiary']} !important;
        color: {c['text_primary']} !important;
        padding: 0.75rem !important;
        text-align: left;
        border-bottom: 2px solid {c['border']};
    }}
    
    .stMarkdown td {{
        padding: 0.75rem !important;
        border-bottom: 1px solid {c['border_light']};
        color: {c['text_primary']} !important;
    }}

    /* Radio buttons styling */
    .stRadio > div {{
        background-color: transparent !important;
    }}
    
    .stRadio label {{
        color: {c['text_primary']} !important;
    }}
    
    /* Tab styling for top nav */
    .nav-container {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1rem;
        border-bottom: 1px solid {c['border']};
        margin-bottom: 1.5rem;
    }}
    
    </style>
    """

def apply_styles():
    """Apply all custom styles."""
    st.markdown(get_css(), unsafe_allow_html=True)

# =============================================================================
# REUSABLE COMPONENTS
# =============================================================================

def render_footer():
    """Render the site footer."""
    c = get_colors()
    theme = get_theme()
    
    footer_html = f"""
    <div class="site-footer">
        <div class="footer-grid">
            <div>
                <div class="footer-brand">
                    <img src="https://brand.chapman.edu/wp-content/uploads/2023/04/window-icon-1.png" 
                         alt="Chapman University" 
                         class="footer-logo">
                    <div>
                        <div class="footer-title">The Dartboard Experiment</div>
                        <div class="footer-subtitle">Built by Scott T. Switzer</div>
                        <div class="footer-subtitle">Finance & Economics @ Chapman University</div>
                    </div>
                </div>
            </div>
            
            <div>
                <div class="footer-section-title">Data</div>
                <span class="footer-link">CRSP via WRDS</span>
                <span class="footer-link">Survivorship bias-free</span>
                <span class="footer-link">Jan 2000 – Dec 2024</span>
            </div>
            
            <div>
                <div class="footer-section-title">Links</div>
                <a href="https://github.com/Scott-Switzer/Random-Portfolio" target="_blank" class="footer-link">GitHub Repository</a>
                <a href="https://www.linkedin.com/in/scottswitzer-/" target="_blank" class="footer-link">LinkedIn</a>
                <a href="mailto:scott.t.switzer@gmail.com" class="footer-link">Email</a>
            </div>
            
            <div class="footer-disclaimer">
                ⚠️ This is an educational tool only. Not financial advice. Past performance does not guarantee future results.
            </div>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_metric_cards(metrics):
    """
    Render custom metric cards.
    metrics: list of dicts with keys: icon, value, label, delta (optional)
    """
    cards_html = '<div class="metric-row">'
    for m in metrics:
        delta_html = f'<div class="metric-delta">{m.get("delta", "")}</div>' if m.get("delta") else ""
        cards_html += f"""
        <div class="metric-card">
            <div class="metric-icon">{m['icon']}</div>
            <div class="metric-value">{m['value']}</div>
            <div class="metric-label">{m['label']}</div>
            {delta_html}
        </div>
        """
    cards_html += '</div>'
    return cards_html

def render_quote_box(quote, attribution=None):
    """Render a styled quote box."""
    attr_html = f'<div class="attribution">— {attribution}</div>' if attribution else ""
    return f"""
    <div class="quote-box">
        <p>{quote}</p>
        {attr_html}
    </div>
    """

def render_section_header(title):
    """Render a section header with accent underline."""
    return f'<div class="section-header">{title}</div>'