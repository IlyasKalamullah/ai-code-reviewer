"""
Styling kustom untuk AI Code Reviewer: palet warna, CSS, dan toggle dark/light
mode yang terpisah dari tema bawaan Streamlit (supaya tampilannya konsisten
di semua browser/device, tidak tergantung setting sistem operasi user).
"""

import streamlit as st

THEMES = {
    "light": {
        "bg": "#f5f6fa",
        "surface": "#ffffff",
        "surface_alt": "#f0f1f6",
        "text": "#1a1d29",
        "text_muted": "#6b7280",
        "border": "#e5e7eb",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
        "shadow": "0 1px 3px rgba(16, 24, 40, 0.06), 0 1px 2px rgba(16, 24, 40, 0.04)",
        "shadow_hover": "0 4px 12px rgba(16, 24, 40, 0.10)",
    },
    "dark": {
        "bg": "#0e1117",
        "surface": "#181c25",
        "surface_alt": "#1f2430",
        "text": "#e8eaf0",
        "text_muted": "#9199a8",
        "border": "#2a2f3d",
        "accent": "#818cf8",
        "accent_hover": "#a5b4fc",
        "shadow": "0 1px 3px rgba(0, 0, 0, 0.4)",
        "shadow_hover": "0 4px 16px rgba(0, 0, 0, 0.5)",
    },
}

SEVERITY_STYLES = {
    "critical": {"bg": "#fef2f2", "bg_dark": "#3f1d1d", "text": "#dc2626", "text_dark": "#f87171", "icon": "🔴"},
    "high":     {"bg": "#fff7ed", "bg_dark": "#3f2a12", "text": "#ea580c", "text_dark": "#fb923c", "icon": "🟠"},
    "medium":   {"bg": "#fefce8", "bg_dark": "#3f3712", "text": "#ca8a04", "text_dark": "#fbbf24", "icon": "🟡"},
    "low":      {"bg": "#eff6ff", "bg_dark": "#1a2f4f", "text": "#2563eb", "text_dark": "#60a5fa", "icon": "🔵"},
}


def get_theme_mode() -> str:
    """Ambil mode saat ini dari session_state ('light' atau 'dark'), default light."""
    return st.session_state.get("theme_mode", "light")


def inject_css():
    """Suntikkan CSS kustom sesuai mode yang aktif."""
    mode = get_theme_mode()
    t = THEMES[mode]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {t["bg"]};
        }}

        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        [data-testid="stSidebar"] {{
            background-color: {t["surface"]};
            border-right: 1px solid {t["border"]};
        }}

        [data-testid="stSidebar"] * {{
            color: {t["text"]} !important;
        }}

        .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
            color: {t["text"]};
        }}

        /* Hero header */
        .acr-hero {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 22px 26px;
            border-radius: 18px;
            background: linear-gradient(135deg, {t["accent"]}22 0%, {t["surface"]} 60%);
            border: 1px solid {t["border"]};
            margin-bottom: 22px;
        }}
        .acr-hero-icon {{
            font-size: 34px;
            line-height: 1;
        }}
        .acr-hero-title {{
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            color: {t["text"]};
            letter-spacing: -0.02em;
        }}
        .acr-hero-subtitle {{
            font-size: 14px;
            color: {t["text_muted"]};
            margin: 4px 0 0 0;
        }}

        /* Section card wrapper */
        .acr-card {{
            background-color: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: {t["shadow"]};
            margin-bottom: 18px;
        }}

        .acr-section-title {{
            font-size: 17px;
            font-weight: 700;
            color: {t["text"]};
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }}

        .acr-badge-count {{
            display: inline-block;
            background-color: {t["accent"]};
            color: white !important;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 11px;
            border-radius: 999px;
            margin-left: 6px;
        }}

        /* Severity finding badges */
        .acr-finding-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
            padding: 3px 10px;
            border-radius: 999px;
            text-transform: uppercase;
        }}

        /* Text area & inputs */
        .stTextArea textarea, .stTextInput input {{
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
            border: 1.5px solid {t["border"]} !important;
            border-radius: 12px !important;
            font-family: 'SF Mono', 'Fira Code', monospace !important;
        }}
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: {t["accent"]} !important;
            box-shadow: 0 0 0 3px {t["accent"]}33 !important;
        }}

        /* Buttons */
        .stButton button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.15s ease !important;
        }}
        .stButton button[kind="primary"] {{
            background: linear-gradient(135deg, {t["accent"]} 0%, {t["accent_hover"]} 100%) !important;
            box-shadow: {t["shadow"]};
        }}
        .stButton button[kind="primary"]:hover {{
            box-shadow: {t["shadow_hover"]};
            transform: translateY(-1px);
        }}

        /* Expander (finding cards) */
        [data-testid="stExpander"] {{
            background-color: {t["surface"]};
            border: 1px solid {t["border"]} !important;
            border-radius: 12px !important;
            box-shadow: {t["shadow"]};
            margin-bottom: 10px;
        }}
        [data-testid="stExpander"] summary {{
            font-weight: 600;
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
        }}
        [data-testid="stExpander"] summary * {{
            color: {t["text"]} !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: {t["surface"]} !important;
        }}

        /* Kode inline (`...`) di dalam teks markdown */
        .stMarkdown code {{
            background-color: {t["surface_alt"]} !important;
            color: {t["accent"]} !important;
            border-radius: 4px;
            padding: 1px 5px;
        }}

        /* Selectbox (React Aria ComboBox, Streamlit versi baru) */
        [data-testid="stSelectbox"] [role="group"] {{
            background-color: {t["surface"]} !important;
            border-color: {t["border"]} !important;
            border-radius: 10px !important;
        }}
        [data-testid="stSelectbox"] input[role="combobox"] {{
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
        }}
        [data-testid="stSelectbox"] button svg {{
            fill: {t["text_muted"]} !important;
            color: {t["text_muted"]} !important;
        }}
        /* Dropdown popover (dirender di luar sidebar/main, jadi selector global) */
        [role="listbox"], [role="option"] {{
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
        }}
        [role="option"]:hover, [role="option"][aria-selected="true"] {{
            background-color: {t["surface_alt"]} !important;
        }}

        /* Tombol ikon kecil (mis. show/hide password) */
        [data-testid="stTextInput"] button, .stTextInput button {{
            background-color: {t["surface"]} !important;
            border: 1px solid {t["border"]} !important;
        }}
        [data-testid="stTextInput"] button svg {{
            fill: {t["text_muted"]} !important;
        }}

        /* Toggle switch warna aksen (bukan merah bawaan Streamlit) */
        [data-testid="stSidebar"] label:has(input:checked) > div:first-of-type {{
            background-color: {t["accent"]} !important;
        }}

        /* Alert boxes */
        [data-testid="stAlert"] {{
            border-radius: 12px !important;
            border: 1px solid {t["border"]} !important;
        }}

        /* Divider spacing tighten */
        hr {{
            border-color: {t["border"]} !important;
            margin: 22px 0 !important;
        }}

        /* Status widget */
        [data-testid="stStatusWidget"] {{
            background-color: {t["surface"]} !important;
            border-radius: 12px !important;
            border: 1px solid {t["border"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    """Toggle dark/light mode di sidebar. Panggil di dalam `with st.sidebar:`."""
    mode = get_theme_mode()
    is_dark = mode == "dark"

    new_is_dark = st.toggle("🌙 Mode Gelap", value=is_dark, key="theme_toggle")

    new_mode = "dark" if new_is_dark else "light"
    if new_mode != mode:
        st.session_state.theme_mode = new_mode
        st.rerun()


def severity_badge_html(severity: str) -> str:
    """HTML span badge berwarna sesuai tingkat keparahan, mengikuti mode aktif."""
    mode = get_theme_mode()
    style = SEVERITY_STYLES.get(severity, SEVERITY_STYLES["low"])
    bg = style["bg_dark"] if mode == "dark" else style["bg"]
    color = style["text_dark"] if mode == "dark" else style["text"]
    return (
        f'<span class="acr-finding-badge" style="background-color:{bg}; color:{color};">'
        f'{style["icon"]} {severity}</span>'
    )
