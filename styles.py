"""
styles.py - Design System for The Dartboard Experiment
Handles theming, CSS, and reusable style components.
"""

import streamlit as st

# DESIGN TOKENS


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
        "accent": "#10B981",  # Money green
        "accent_hover": "#059669",
        "accent_light": "#D1FAE5",
        "accent_text": "#065F46",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6",
        "card_shadow": "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)",
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
        "accent": "#10B981",  # Money green (same in dark)
        "accent_hover": "#34D399",
        "accent_light": "#064E3B",
        "accent_text": "#A7F3D0",
        "error": "#F87171",
        "warning": "#FBBF24",
        "info": "#60A5FA",
        "card_shadow": "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)",
    }
}

CHAPMAN_RED = "#A50034"


# THEME MANAGEMENT


def init_theme():
    """Initialize theme in session state."""
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

def get_theme():
    """Get current theme."""
    init_theme()
    return st.session_state.theme

def toggle_theme():
    """Toggle between light and dark mode."""
    init_theme()
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

def get_colors():
    """Get color palette for current theme."""
    return COLORS[get_theme()]

# CSS GENERATION


def get_base_css():
    """Generate base CSS with current theme colors."""
    c = get_colors()
    theme = get_theme()
    
    return f"""
    <style>
    /* ===========================================
       FONTS - IBM Plex Sans & Serif
       =========================================== */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Serif:wght@400;500;600;700&display=swap');
    
    /* ===========================================
       ROOT VARIABLES
       =========================================== */
    :root {{
        --bg-primary: {c['bg_primary']};
        --bg-secondary: {c['bg_secondary']};
        --bg-tertiary: {c['bg_tertiary']};
        --text-primary: {c['text_primary']};
        --text-secondary: {c['text_secondary']};
        --text-muted: {c['text_muted']};
        --border: {c['border']};
        --border-light: {c['border_light']};
        --accent: {c['accent']};
        --accent-hover: {c['accent_hover']};
        --accent-light: {c['accent_light']};
        --accent-text: {c['accent_text']};
        --card-shadow: {c['card_shadow']};
        --chapman-red: {CHAPMAN_RED};
        
        --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-serif: 'IBM Plex Serif', Georgia, serif;
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        
        --transition: 150ms ease;
    }}
    
    /* ===========================================
       GLOBAL STYLES
       =========================================== */
    .stApp {{
        background-color: var(--bg-primary) !important;
    }}
    
    /* Override Streamlit's default font */
    html, body, [class*="st-"] {{
        font-family: var(--font-sans) !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-serif) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    
    p, li, span, div {{
        color: var(--text-primary);
    }}
    
    /* ===========================================
       TOP NAVIGATION BAR
       =========================================== */
    .top-nav {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border);
        margin: -1rem -1rem 2rem -1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }}
    
    .nav-brand {{
        font-family: var(--font-serif);
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .nav-tabs {{
        display: flex;
        gap: 0.5rem;
    }}
    
    .nav-tab {{
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        font-family: var(--font-sans);
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        background: transparent;
        border: none;
        cursor: pointer;
        transition: all var(--transition);
        text-decoration: none;
    }}
    
    .nav-tab:hover {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }}
    
    .nav-tab.active {{
        background: var(--accent-light);
        color: var(--accent-text);
    }}
    
    .nav-right {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    /* Theme toggle button */
    .theme-toggle {{
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.5rem;
        cursor: pointer;
        font-size: 1.25rem;
        line-height: 1;
        transition: all var(--transition);
    }}
    
    .theme-toggle:hover {{
        background: var(--border);
    }}
    
    /* ===========================================
       SECTION DIVIDERS (Minimal style)
       =========================================== */
    .section-divider {{
        border: none;
        border-top: 1px solid var(--border);
        margin: 2.5rem 0;
    }}
    
    .section-title {{
        font-family: var(--font-serif) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--accent);
        display: inline-block;
    }}
    
    .section-subtitle {{
        font-family: var(--font-sans);
        font-size: 1rem;
        color: var(--text-secondary);
        margin-top: 0;
        margin-bottom: 1.5rem;
    }}
    
    /* ===========================================
       METRIC CARDS
       =========================================== */
    .metric-card {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        transition: all var(--transition);
    }}
    
    .metric-card:hover {{
        box-shadow: var(--card-shadow);
        border-color: var(--accent);
    }}
    
    .metric-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-family: var(--font-sans);
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent);
        line-height: 1.2;
    }}
    
    .metric-label {{
        font-family: var(--font-sans);
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .metric-delta {{
        font-family: var(--font-sans);
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }}
    
    .metric-delta.positive {{
        color: var(--accent);
    }}
    
    .metric-delta.negative {{
        color: var(--error);
    }}
    
    /* ===========================================
       HERO SECTION
       =========================================== */
    .hero {{
        text-align: center;
        padding: 4rem 2rem;
        max-width: 800px;
        margin: 0 auto;
    }}
    
    .hero-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
    }}
    
    .hero-title {{
        font-family: var(--font-serif) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
        line-height: 1.2 !important;
    }}
    
    .hero-subtitle {{
        font-family: var(--font-serif);
        font-size: 1.5rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        font-style: italic;
    }}
    
    .hero-description {{
        font-family: var(--font-sans);
        font-size: 1.125rem;
        color: var(--text-secondary);
        line-height: 1.7;
        margin-bottom: 2rem;
    }}
    
    .hero-buttons {{
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }}
    
    /* ===========================================
       BUTTONS
       =========================================== */
    .btn {{
        font-family: var(--font-sans);
        font-size: 1rem;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all var(--transition);
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border: none;
    }}
    
    .btn-primary {{
        background: var(--accent);
        color: white;
    }}
    
    .btn-primary:hover {{
        background: var(--accent-hover);
    }}
    
    .btn-secondary {{
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border);
    }}
    
    .btn-secondary:hover {{
        background: var(--bg-secondary);
        border-color: var(--text-muted);
    }}
    
    /* ===========================================
       IN-PAGE SIDEBAR NAVIGATION
       =========================================== */
    .page-sidebar {{
        position: sticky;
        top: 100px;
        max-height: calc(100vh - 120px);
        overflow-y: auto;
        padding-right: 1rem;
    }}
    
    .page-sidebar-title {{
        font-family: var(--font-sans);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
    }}
    
    .page-sidebar-link {{
        display: block;
        font-family: var(--font-sans);
        font-size: 0.875rem;
        color: var(--text-secondary);
        padding: 0.375rem 0;
        padding-left: 0.75rem;
        border-left: 2px solid transparent;
        text-decoration: none;
        transition: all var(--transition);
    }}
    
    .page-sidebar-link:hover {{
        color: var(--text-primary);
        border-left-color: var(--border);
    }}
    
    .page-sidebar-link.active {{
        color: var(--accent);
        border-left-color: var(--accent);
        font-weight: 500;
    }}
    
    /* ===========================================
       FOOTER
       =========================================== */
    .footer {{
        margin-top: 4rem;
        padding: 2.5rem 2rem;
        background: var(--bg-secondary);
        border-top: 1px solid var(--border);
    }}
    
    .footer-content {{
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 3rem;
    }}
    
    .footer-brand {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }}
    
    .footer-logo {{
        width: 48px;
        height: 48px;
    }}
    
    .footer-title {{
        font-family: var(--font-serif);
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }}
    
    .footer-author {{
        font-family: var(--font-sans);
        font-size: 0.875rem;
        color: var(--text-secondary);
    }}
    
    .footer-section-title {{
        font-family: var(--font-sans);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
    }}
    
    .footer-link {{
        display: block;
        font-family: var(--font-sans);
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-decoration: none;
        padding: 0.25rem 0;
        transition: color var(--transition);
    }}
    
    .footer-link:hover {{
        color: var(--accent);
    }}
    
    .footer-disclaimer {{
        grid-column: 1 / -1;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border);
        font-family: var(--font-sans);
        font-size: 0.75rem;
        color: var(--text-muted);
        text-align: center;
    }}
    
    /* ===========================================
       INFO/QUOTE BOXES
       =========================================== */
    .quote-box {{
        background: var(--bg-secondary);
        border-left: 4px solid var(--accent);
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
    }}
    
    .quote-box p {{
        font-family: var(--font-serif);
        font-size: 1.125rem;
        font-style: italic;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.6;
    }}
    
    .quote-box .attribution {{
        font-family: var(--font-sans);
        font-size: 0.875rem;
        font-style: normal;
        color: var(--text-muted);
        margin-top: 0.75rem;
    }}
    
    /* ===========================================
       DATA TABLES
       =========================================== */
    .styled-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: var(--font-sans);
        font-size: 0.875rem;
    }}
    
    .styled-table th {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
        font-weight: 600;
        text-align: left;
        padding: 0.75rem 1rem;
        border-bottom: 2px solid var(--border);
    }}
    
    .styled-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-light);
        color: var(--text-primary);
    }}
    
    .styled-table tr:hover td {{
        background: var(--bg-secondary);
    }}
    
    /* ===========================================
       STREAMLIT OVERRIDES
       =========================================== */
    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Style Streamlit buttons */
    .stButton > button {{
        font-family: var(--font-sans) !important;
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all var(--transition) !important;
    }}
    
    .stButton > button:hover {{
        background: var(--accent-hover) !important;
        border: none !important;
    }}
    
    /* Style Streamlit expanders */
    .streamlit-expanderHeader {{
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-md) !important;
    }}
    
    /* Style Streamlit selectbox/inputs */
    .stSelectbox > div > div {{
        background: var(--bg-secondary) !important;
        border-color: var(--border) !important;
        border-radius: var(--radius-md) !important;
    }}
    
    .stSlider > div > div > div {{
        background: var(--accent) !important;
    }}
    
    /* Style dataframes */
    .stDataFrame {{
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }}
    
    /* Style metrics - override default */
    [data-testid="stMetricValue"] {{
        font-family: var(--font-sans) !important;
        color: var(--accent) !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-family: var(--font-sans) !important;
        color: var(--text-secondary) !important;
    }}
    
    /* Radio buttons (for any remaining) */
    .stRadio > div {{
        background: transparent !important;
    }}
    
    .stRadio label {{
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: var(--text-primary) !important;
    }}
    
    /* Link buttons */
    .stLinkButton > a {{
        font-family: var(--font-sans) !important;
        border-radius: var(--radius-md) !important;
    }}
    
    </style>
    """


# COMPONENT HELPERS


def render_metric_card(icon: str, value: str, label: str, delta: str = None, delta_type: str = "neutral"):
    """Render a custom metric card."""
    delta_html = ""
    if delta:
        delta_class = "positive" if delta_type == "positive" else "negative" if delta_type == "negative" else ""
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """

def render_section_title(title: str, subtitle: str = None):
    """Render a section title with optional subtitle."""
    subtitle_html = f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <h2 class="section-title">{title}</h2>
    {subtitle_html}
    """

def render_quote_box(quote: str, attribution: str = None):
    """Render a styled quote box."""
    attr_html = f'<div class="attribution">— {attribution}</div>' if attribution else ""
    return f"""
    <div class="quote-box">
        <p>{quote}</p>
        {attr_html}
    </div>
    """

def render_footer():
    """Render the expanded footer."""
    c = get_colors()
    return f"""
    <div class="footer">
        <div class="footer-content">
            <div>
                <div class="footer-brand">
                    <img src="https://brand.chapman.edu/wp-content/uploads/2023/04/window-icon-1.png" 
                         alt="Chapman University" class="footer-logo" 
                         style="filter: {'invert(1)' if get_theme() == 'dark' else 'none'};">
                    <div>
                        <div class="footer-title">The Dartboard Experiment</div>
                        <div class="footer-author">Built by Scott T. Switzer</div>
                        <div class="footer-author">Finance & Economics @ Chapman University</div>
                    </div>
                </div>
            </div>
            
            <div>
                <div class="footer-section-title">Data</div>
                <div class="footer-link">CRSP via WRDS</div>
                <div class="footer-link">Survivorship bias-free</div>
                <div class="footer-link">Jan 2000 – Dec 2024</div>
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

def apply_styles():
    """Apply all styles to the Streamlit app."""
    st.markdown(get_base_css(), unsafe_allow_html=True)