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
    },
    "dark": {
        "bg_primary": "#0F172A",
        "bg_secondary": "#1E293B",
        "bg_tertiary": "#334155",
        "text_primary": "#F1F5F9",
        "text_secondary": "#CBD5E1",
        "text_muted": "#94A3B8",
        "border": "#334155",
        "border_light": "#475569",
        "accent": "#10B981",
        "accent_hover": "#34D399",
        "accent_light": "#064E3B",
        "accent_text": "#A7F3D0",
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
       GLOBAL RESETS & BASE
       ============================================ */
    .stApp {{
        background-color: {c['bg_primary']} !important;
    }}
    
    .main .block-container {{
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }}
    
    /* Force all text to use our fonts */
    html, body, [class*="st-"], .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {c['text_primary']} !important;
    }}
    
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        color: {c['text_primary']} !important;
        text-align: center !important;
    }}
    
    /* Center paragraph text */
    .stMarkdown p {{
        text-align: center !important;
    }}
    
    /* But left-align lists */
    .stMarkdown ul, .stMarkdown ol {{
        text-align: left !important;
        display: inline-block !important;
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
        text-align: center !important;
        padding: 3rem 1rem 2rem 1rem;
        max-width: 800px;
        margin: 0 auto;
    }}
    
    .hero-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
    }}
    
    .hero-title {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        color: {c['text_primary']} !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }}
    
    .hero-subtitle {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.5rem !important;
        font-style: italic;
        color: {c['text_secondary']} !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
    }}
    
    .hero-description {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1.125rem !important;
        color: {c['text_secondary']} !important;
        line-height: 1.75 !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
    }}
    
    /* ============================================
       CONTENT SECTIONS - THEMED BOXES
       ============================================ */
    .theory-box, .content-box {{
        background-color: {c['bg_secondary']} !important;
        color: {c['text_primary']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        margin-bottom: 1.5rem !important;
        line-height: 1.7 !important;
        border: 1px solid {c['border']} !important;
        text-align: left !important;
    }}
    
    .theory-box h3, .content-box h3 {{
        color: {c['accent']} !important;
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        text-align: left !important;
    }}
    
    .theory-box p, .content-box p {{
        color: {c['text_primary']} !important;
        margin-bottom: 0.75rem !important;
        text-align: left !important;
    }}
    
    .theory-box ul, .content-box ul {{
        margin: 0.5rem 0 1rem 1.5rem !important;
        color: {c['text_primary']} !important;
    }}
    
    .theory-box li, .content-box li {{
        color: {c['text_primary']} !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .theory-box b, .theory-box strong,
    .content-box b, .content-box strong {{
        color: {c['accent']} !important;
    }}
    
    .theory-box a, .content-box a {{
        color: {c['accent']} !important;
        text-decoration: none !important;
    }}
    
    .theory-box a:hover, .content-box a:hover {{
        text-decoration: underline !important;
    }}
    
    /* ============================================
       QUOTE BOX
       ============================================ */
    .quote-box {{
        background: {c['bg_secondary']} !important;
        border-left: 4px solid {c['accent']} !important;
        padding: 1.25rem 1.5rem !important;
        margin: 1.5rem auto !important;
        border-radius: 0 8px 8px 0 !important;
        max-width: 700px !important;
    }}
    
    .quote-box p {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.1rem !important;
        font-style: italic !important;
        color: {c['text_primary']} !important;
        margin: 0 !important;
        line-height: 1.6 !important;
        text-align: left !important;
    }}
    
    .quote-box .attribution {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.875rem !important;
        font-style: normal !important;
        color: {c['text_muted']} !important;
        margin-top: 0.75rem !important;
    }}
    
    /* ============================================
       SECTION HEADERS
       ============================================ */
    .section-header {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: {c['text_primary']} !important;
        text-align: center !important;
        margin: 2rem 0 1rem 0 !important;
        padding-bottom: 0.5rem !important;
    }}
    
    .section-header::after {{
        content: '';
        display: block;
        width: 60px;
        height: 3px;
        background: {c['accent']};
        margin: 0.5rem auto 0 auto;
        border-radius: 2px;
    }}
    
    /* ============================================
       METRIC CARDS
       ============================================ */
    .metric-card {{
        background: {c['bg_secondary']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }}
    
    .metric-card:hover {{
        border-color: {c['accent']} !important;
        transform: translateY(-2px) !important;
    }}
    
    .metric-icon {{
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .metric-value {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: {c['accent']} !important;
        line-height: 1.2 !important;
    }}
    
    .metric-label {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: {c['text_muted']} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-top: 0.25rem !important;
    }}
    
    .metric-delta {{
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.8rem !important;
        color: {c['text_secondary']} !important;
        margin-top: 0.5rem !important;
    }}
    
    /* ============================================
       PAGE HEADER (big-header class)
       ============================================ */
    .big-header {{
        font-family: 'IBM Plex Serif', Georgia, serif !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: {c['text_primary']} !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
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
    
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background-color: {c['accent']} !important;
        color: white !important;
        border: none !important;
    }}
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {{
        background-color: {c['accent_hover']} !important;
    }}
    
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {{
        background-color: {c['bg_secondary']} !important;
        color: {c['text_primary']} !important;
        border: 1px solid {c['border']} !important;
    }}
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {{
        background-color: {c['bg_tertiary']} !important;
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
    
    .streamlit-expanderContent {{
        background-color: {c['bg_secondary']} !important;
        border: 1px solid {c['border']} !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }}
    
    /* Selectbox & Inputs */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {{
        background-color: {c['bg_secondary']} !important;
        border-color: {c['border']} !important;
        color: {c['text_primary']} !important;
        border-radius: 8px !important;
    }}
    
    .stSelectbox label,
    .stTextInput label,
    .stSlider label {{
        color: {c['text_primary']} !important;
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
    
    .stDataFrame [data-testid="stDataFrameResizable"] {{
        background-color: {c['bg_secondary']} !important;
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
    
    [data-testid="stMetricDelta"] {{
        color: {c['text_muted']} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {c['bg_secondary']} !important;
        border-right: 1px solid {c['border']} !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: {c['text_primary']} !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label {{
        color: {c['text_primary']} !important;
    }}
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {c['text_primary']} !important;
        text-align: left !important;
    }}
    
    /* Info/Success/Warning boxes */
    .stAlert {{
        border-radius: 8px !important;
        background-color: {c['bg_secondary']} !important;
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
        border-collapse: collapse !important;
        width: 100% !important;
        margin: 1rem auto !important;
    }}
    
    .stMarkdown th {{
        background-color: {c['bg_tertiary']} !important;
        color: {c['text_primary']} !important;
        padding: 0.75rem !important;
        text-align: left !important;
        border-bottom: 2px solid {c['border']} !important;
    }}
    
    .stMarkdown td {{
        padding: 0.75rem !important;
        border-bottom: 1px solid {c['border_light']} !important;
        color: {c['text_primary']} !important;
        background-color: {c['bg_secondary']} !important;
    }}

    /* Radio buttons */
    .stRadio > div {{
        background-color: transparent !important;
    }}
    
    .stRadio label {{
        color: {c['text_primary']} !important;
    }}
    
    .stRadio [data-testid="stMarkdownContainer"] p {{
        text-align: left !important;
    }}
    
    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {c['text_muted']} !important;
        text-align: center !important;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: {c['accent']} !important;
    }}
    
    /* Download buttons */
    .stDownloadButton > button {{
        background-color: {c['bg_secondary']} !important;
        color: {c['text_primary']} !important;
        border: 1px solid {c['border']} !important;
    }}
    
    .stDownloadButton > button:hover {{
        background-color: {c['bg_tertiary']} !important;
        border-color: {c['accent']} !important;
    }}
    
    /* LaTeX / Math */
    .katex {{
        color: {c['text_primary']} !important;
    }}
    
    /* Columns - ensure they don't overlap */
    [data-testid="column"] {{
        padding: 0 0.5rem !important;
    }}
    
    </style>
    """

def apply_styles():
    """Apply all custom styles."""
    st.markdown(get_css(), unsafe_allow_html=True)

# =============================================================================
# REUSABLE COMPONENTS
# =============================================================================

def render_section_header(title):
    """Render a centered section header with accent underline."""
    return f'<div class="section-header">{title}</div>'

def render_quote_box(quote, attribution=None):
    """Render a styled quote box."""
    attr_html = f'<div class="attribution">— {attribution}</div>' if attribution else ""
    return f"""
    <div class="quote-box">
        <p>{quote}</p>
        {attr_html}
    </div>
    """

def render_metric_cards(metrics):
    """
    Render custom metric cards in a row.
    metrics: list of dicts with keys: icon, value, label, delta (optional)
    """
    c = get_colors()
    cards_html = '<div style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; margin: 1.5rem 0;">'
    for m in metrics:
        delta_html = f'<div class="metric-delta">{m.get("delta", "")}</div>' if m.get("delta") else ""
        cards_html += f"""
        <div class="metric-card" style="flex: 1; min-width: 150px; max-width: 250px;">
            <div class="metric-icon">{m['icon']}</div>
            <div class="metric-value">{m['value']}</div>
            <div class="metric-label">{m['label']}</div>
            {delta_html}
        </div>
        """
    cards_html += '</div>'
    return cards_html

def render_footer():
    """Render the site footer."""
    c = get_colors()
    theme = get_theme()
    
    footer_html = f"""
    <div style="
        margin-top: 4rem;
        padding: 2.5rem 2rem;
        background-color: {c['bg_secondary']};
        border-top: 1px solid {c['border']};
    ">
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 3rem;
            max-width: 1000px;
            margin: 0 auto;
            justify-content: space-between;
        ">
            <!-- Brand Column -->
            <div style="flex: 2; min-width: 250px;">
                <div style="display: flex; align-items: flex-start; gap: 1rem;">
                    <img src="https://brand.chapman.edu/wp-content/uploads/2023/04/window-icon-1.png" 
                         alt="Chapman University" 
                         style="width: 48px; height: 48px; {'filter: invert(1);' if theme == 'dark' else ''}">
                    <div>
                        <div style="font-family: 'IBM Plex Serif', Georgia, serif; font-size: 1.125rem; font-weight: 600; color: {c['text_primary']};">
                            The Dartboard Experiment
                        </div>
                        <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; margin-top: 0.25rem;">
                            Built by Scott T. Switzer
                        </div>
                        <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']};">
                            Finance & Economics @ Chapman University
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Data Column -->
            <div style="flex: 1; min-width: 150px;">
                <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: {c['text_muted']}; margin-bottom: 0.75rem;">
                    Data
                </div>
                <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; padding: 0.25rem 0;">CRSP via WRDS</div>
                <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; padding: 0.25rem 0;">Survivorship bias-free</div>
                <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; padding: 0.25rem 0;">Jan 2000 – Dec 2024</div>
            </div>
            
            <!-- Links Column -->
            <div style="flex: 1; min-width: 150px;">
                <div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: {c['text_muted']}; margin-bottom: 0.75rem;">
                    Links
                </div>
                <a href="https://github.com/Scott-Switzer/Random-Portfolio" target="_blank" 
                   style="display: block; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; text-decoration: none; padding: 0.25rem 0;">
                    GitHub Repository
                </a>
                <a href="https://www.linkedin.com/in/scottswitzer-/" target="_blank" 
                   style="display: block; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; text-decoration: none; padding: 0.25rem 0;">
                    LinkedIn
                </a>
                <a href="mailto:scott.t.switzer@gmail.com" 
                   style="display: block; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.875rem; color: {c['text_secondary']}; text-decoration: none; padding: 0.25rem 0;">
                    Email
                </a>
            </div>
        </div>
        
        <!-- Disclaimer -->
        <div style="
            text-align: center;
            padding-top: 1.5rem;
            margin-top: 1.5rem;
            border-top: 1px solid {c['border']};
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.75rem;
            color: {c['text_muted']};
        ">
            ⚠️ This is an educational tool only. Not financial advice. Past performance does not guarantee future results.
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_page_sidebar(sections, current_section=None):
    """
    Render a sidebar navigation for page sections.
    sections: list of tuples (section_id, section_label)
    """
    c = get_colors()
    
    st.sidebar.markdown(f"""
    <div style="
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {c['text_muted']};
        margin-bottom: 0.75rem;
        padding-left: 0.5rem;
    ">
        On This Page
    </div>
    """, unsafe_allow_html=True)
    
    selected = st.sidebar.radio(
        "Jump to section:",
        options=[s[0] for s in sections],
        format_func=lambda x: dict(sections)[x],
        label_visibility="collapsed"
    )
    
    return selected