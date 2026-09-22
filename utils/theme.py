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
        "surface_alt": "#eef0f6",
        "text": "#1a1d29",
        "text_muted": "#6b7280",
        "border": "#e5e7eb",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
        "shadow": "0 1px 3px rgba(16, 24, 40, 0.06), 0 1px 2px rgba(16, 24, 40, 0.04)",
        "shadow_hover": "0 6px 16px rgba(16, 24, 40, 0.12)",
    },
    "dark": {
        "bg": "#0b0e14",
        "surface": "#161a23",
        "surface_alt": "#20242f",
        "text": "#e8eaf0",
        "text_muted": "#9199a8",
        "border": "#2a2f3d",
        "accent": "#818cf8",
        "accent_hover": "#a5b4fc",
        "shadow": "0 1px 3px rgba(0, 0, 0, 0.4)",
        "shadow_hover": "0 8px 20px rgba(0, 0, 0, 0.55)",
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {t["bg"]};
            transition: background-color 0.2s ease;
        }}

        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1000px;
            padding-top: 2rem;
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

        a, a:visited {{
            color: {t["accent"]} !important;
        }}

        /* ---------- Hero header ---------- */
        .acr-hero {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 24px 28px;
            border-radius: 20px;
            background: linear-gradient(135deg, {t["accent"]}26 0%, {t["surface"]} 65%);
            border: 1px solid {t["border"]};
            box-shadow: {t["shadow"]};
            margin-bottom: 26px;
        }}
        .acr-hero-icon {{
            font-size: 36px;
            line-height: 1;
            filter: drop-shadow(0 2px 4px {t["accent"]}55);
        }}
        .acr-hero-title {{
            font-size: 27px;
            font-weight: 800;
            margin: 0;
            color: {t["text"]};
            letter-spacing: -0.02em;
        }}
        .acr-hero-subtitle {{
            font-size: 14px;
            color: {t["text_muted"]};
            margin: 5px 0 0 0;
        }}

        /* ---------- Section headers ---------- */
        .acr-section-title {{
            font-size: 17px;
            font-weight: 700;
            color: {t["text"]};
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin: 4px 0 12px 0;
        }}

        .acr-badge-count {{
            display: inline-block;
            background-color: {t["accent"]};
            color: white !important;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 12px;
            border-radius: 999px;
        }}
        .acr-badge-lang {{
            display: inline-block;
            background-color: {t["surface_alt"]};
            color: {t["text_muted"]} !important;
            border: 1px solid {t["border"]};
            font-size: 12px;
            font-weight: 600;
            padding: 2px 11px;
            border-radius: 999px;
        }}

        /* Severity finding badges */
        .acr-finding-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 4px 11px;
            border-radius: 999px;
            text-transform: uppercase;
        }}

        /* ---------- Text area & inputs ---------- */
        .stTextArea textarea, .stTextInput input {{
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
            border: 1.5px solid {t["border"]} !important;
            border-radius: 12px !important;
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
            font-size: 13.5px !important;
        }}
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: {t["accent"]} !important;
            box-shadow: 0 0 0 3px {t["accent"]}30 !important;
        }}
        .stTextArea textarea::placeholder {{
            color: {t["text_muted"]} !important;
            opacity: 0.7;
        }}

        /* ---------- Buttons ---------- */
        .stButton button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.15s ease !important;
        }}
        /* Tombol sekunder (mis. "Mulai Ulang dari Awal") */
        .stButton button:not([kind="primary"]) {{
            background-color: {t["surface_alt"]} !important;
            color: {t["text"]} !important;
            border: 1.5px solid {t["border"]} !important;
        }}
        .stButton button:not([kind="primary"]):hover {{
            border-color: {t["accent"]} !important;
            color: {t["accent"]} !important;
        }}
        .stButton button[kind="primary"] {{
            background: linear-gradient(135deg, {t["accent"]} 0%, {t["accent_hover"]} 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: {t["shadow"]};
        }}
        .stButton button[kind="primary"]:hover {{
            box-shadow: {t["shadow_hover"]};
            transform: translateY(-1px);
        }}
        .stButton button p {{
            color: inherit !important;
        }}

        /* ---------- Expander (finding cards) ---------- */
        [data-testid="stExpander"] {{
            background-color: {t["surface"]};
            border: 1px solid {t["border"]} !important;
            border-radius: 12px !important;
            box-shadow: {t["shadow"]};
            margin-bottom: 10px;
            overflow: hidden;
        }}
        [data-testid="stExpander"]:hover {{
            box-shadow: {t["shadow_hover"]};
        }}
        [data-testid="stExpander"] summary {{
            font-weight: 600;
            background-color: {t["surface"]} !important;
            color: {t["text"]} !important;
            padding: 4px 2px !important;
        }}
        [data-testid="stExpander"] summary:hover {{
            background-color: {t["surface_alt"]} !important;
        }}
        [data-testid="stExpander"] summary * {{
            color: {t["text"]} !important;
        }}
        /* Kode inline di JUDUL expander (kadang muncul dari teks temuan AI) */
        [data-testid="stExpander"] summary code {{
            background-color: {t["surface_alt"]} !important;
            color: {t["accent"]} !important;
            border-radius: 4px;
            padding: 1px 5px;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: {t["surface"]} !important;
            padding-top: 6px !important;
        }}

        /* Kode inline (`...`) di dalam isi markdown */
        .stMarkdown code {{
            background-color: {t["surface_alt"]} !important;
            color: {t["accent"]} !important;
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 0.9em;
        }}
        .stMarkdown pre code {{
            color: {t["text"]} !important;
            background-color: transparent !important;
        }}
        .stMarkdown pre {{
            background-color: {t["surface_alt"]} !important;
            border: 1px solid {t["border"]} !important;
            border-radius: 10px !important;
        }}

        /* ---------- Selectbox (React Aria ComboBox) ---------- */
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
        [data-testid="stTextInput"] button {{
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

        /* ---------- Alert boxes ---------- */
        [data-testid="stAlert"] {{
            background-color: {t["surface_alt"]} !important;
            border-radius: 12px !important;
            border: 1px solid {t["border"]} !important;
        }}
        [data-testid="stAlert"] p, [data-testid="stAlert"] span {{
            color: {t["text"]} !important;
        }}

        /* ---------- st.json (temuan mentah Semgrep) ---------- */
        [data-testid="stJson"] {{
            background-color: {t["surface_alt"]} !important;
            border: 1px solid {t["border"]} !important;
            border-radius: 10px !important;
        }}

        /* Divider spacing */
        hr {{
            border-color: {t["border"]} !important;
            margin: 24px 0 !important;
            opacity: 0.6;
        }}

        /* Status widget (progress saat analisis berjalan) */
        [data-testid="stStatusWidget"] {{
            background-color: {t["surface"]} !important;
            border-radius: 12px !important;
            border: 1px solid {t["border"]} !important;
        }}
        [data-testid="stStatusWidget"] p {{
            color: {t["text"]} !important;
        }}

        /* Tooltip help icon */
        [data-testid="stTooltipHoverTarget"] svg {{
            color: {t["text_muted"]} !important;
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
