"""
AI Code Reviewer — Streamlit App
Mengoreksi dan memberi saran perbaikan kode (keamanan, bug, performa, style)
dengan menggabungkan Semgrep (static analysis, gratis) + Groq LLM (gratis).

Mendukung "Review Ulang": setelah hasil review pertama muncul, user bisa
paste kode yang sudah diperbaiki untuk dicek lagi, berkali-kali, sampai
semua temuan hilang.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils.semgrep_runner import run_semgrep, LANGUAGE_EXTENSIONS
from utils.groq_client import review_code
from utils.language_detector import detect_language
from utils.theme import inject_css, render_theme_toggle, severity_badge_html

AUTO_DETECT_LABEL = "🔍 Deteksi Otomatis"

load_dotenv()

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def escape_markdown(text: str) -> str:
    """
    Streamlit merender teks di antara tanda '$' sebagai rumus LaTeX.
    Karena saran perbaikan sering berisi kode (mis. variabel PHP seperti
    $user, $keyword), tanda '$' perlu di-escape supaya tidak dikira LaTeX
    dan menyebabkan teks tampil kacau/terduplikasi.
    """
    if not text:
        return text
    return text.replace("$", "\\$")


def render_findings(findings: list):
    if not findings:
        st.success("✅ Tidak ada temuan. Kode terlihat baik dari sisi yang dianalisis.")
        return

    sorted_findings = sorted(
        findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "low"), 4)
    )

    for f in sorted_findings:
        severity = f.get("severity", "low")
        line_info = f" · baris {f['line']}" if f.get("line") else ""
        category = f.get("category", "").upper()
        issue_text = f.get("issue", "-")
        suggestion_text = f.get("suggestion", "-")
        badge = severity_badge_html(severity)

        expander_label = f"{category}{line_info} — {issue_text[:70]}"
        with st.expander(expander_label):
            st.markdown(badge, unsafe_allow_html=True)
            st.markdown(f"**Masalah:** {escape_markdown(issue_text)}")
            st.markdown("**Saran perbaikan:**")
            st.markdown(escape_markdown(suggestion_text))


def run_analysis(code: str, language: str, api_key: str):
    """Menjalankan Semgrep + Groq LLM untuk satu potongan kode. Return (semgrep_result, llm_result)."""
    semgrep_result = run_semgrep(code, language)

    if not semgrep_result["success"]:
        st.warning(
            f"Semgrep tidak berjalan sempurna: {semgrep_result['raw_error']}. "
            "Melanjutkan dengan analisis AI saja."
        )

    llm_result = review_code(
        code=code,
        language=language,
        semgrep_findings=semgrep_result.get("findings", []),
        api_key=api_key,
    )

    return semgrep_result, llm_result


def display_round_result(round_index: int, round_data: dict):
    """Menampilkan hasil satu ronde review (baik ronde pertama maupun revisi)."""
    is_first = round_index == 0
    llm_result = round_data["llm"]
    semgrep_result = round_data["semgrep"]

    if not llm_result["success"]:
        st.error(f"Gagal mendapatkan review dari AI: {llm_result['raw_error']}")
        return

    result = llm_result["result"]
    findings = result.get("findings", [])

    title = "📋 Hasil Review Awal" if is_first else f"📋 Hasil Review Ulang #{round_index}"

    st.markdown(
        f'<div class="acr-section-title">{title} '
        f'<span class="acr-badge-count">{round_data["language"]}</span> '
        f'<span class="acr-badge-count">{len(findings)} temuan</span></div>',
        unsafe_allow_html=True,
    )

    st.info(escape_markdown(result.get("summary", "-")))

    render_findings(findings)

    with st.expander("Lihat temuan mentah Semgrep (opsional)"):
        if semgrep_result.get("findings"):
            st.json(semgrep_result["findings"])
        else:
            st.write("Tidak ada temuan mentah dari Semgrep.")


def main():
    inject_css()

    st.markdown(
        """
        <div class="acr-hero">
            <div class="acr-hero-icon">🔍</div>
            <div>
                <p class="acr-hero-title">AI Code Reviewer</p>
                <p class="acr-hero-subtitle">Analisis keamanan, bug, performa &amp; gaya penulisan —
                ditenagai Semgrep + Groq LLM, 100% gratis.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "rounds" not in st.session_state:
        st.session_state.rounds = []

    with st.sidebar:
        st.header("⚙️ Pengaturan")
        render_theme_toggle()
        st.markdown("---")
        api_key_input = st.text_input(
            "Groq API Key",
            value=os.getenv("GROQ_API_KEY", ""),
            type="password",
            help="Dapatkan gratis di https://console.groq.com",
        )
        st.markdown("---")
        st.markdown(
            "**Cara pakai:**\n"
            "1. Paste kode kamu (bahasa otomatis terdeteksi)\n"
            "2. Klik 'Review Kode'\n"
            "3. Perbaiki kode sesuai saran, lalu paste lagi di kotak 'Review Ulang' untuk cek ulang\n"
        )
        st.markdown("---")
        st.markdown("[Dapatkan Groq API Key gratis →](https://console.groq.com/keys)")

        if st.session_state.rounds:
            st.markdown("---")
            if st.button("🗑️ Mulai Ulang dari Awal"):
                st.session_state.rounds = []
                st.rerun()

    # Tampilkan hasil semua ronde yang sudah dijalankan (riwayat)
    for i, round_data in enumerate(st.session_state.rounds):
        display_round_result(i, round_data)
        st.markdown("---")

    round_num = len(st.session_state.rounds)
    is_first = round_num == 0
    prev_code = st.session_state.rounds[-1]["code"] if not is_first else ""

    section_label = (
        "Paste kode di sini"
        if is_first
        else f"✏️ Revisi #{round_num} — Paste kode yang sudah diperbaiki untuk dicek ulang"
    )

    code_input = st.text_area(
        section_label,
        value=prev_code,
        height=350,
        placeholder="# Tempel kode yang ingin direview di sini (bahasa apa saja, akan terdeteksi otomatis)...",
        key=f"code_area_{round_num}",
    )

    detected = detect_language(code_input) if code_input.strip() else None

    col1, col2 = st.columns([1, 3])
    with col1:
        language_options = [AUTO_DETECT_LABEL] + list(LANGUAGE_EXTENSIONS.keys())
        language_choice = st.selectbox(
            "Bahasa Pemrograman",
            language_options,
            help="Biarkan di 'Deteksi Otomatis' supaya bahasa terdeteksi sendiri dari kode yang kamu paste, atau pilih manual kalau deteksinya kurang tepat.",
            key=f"lang_select_{round_num}",
        )
    with col2:
        if language_choice == AUTO_DETECT_LABEL:
            if code_input.strip():
                if detected:
                    st.success(f"Bahasa terdeteksi: **{detected}**")
                else:
                    st.warning(
                        "Bahasa belum bisa dideteksi otomatis dari kode ini. "
                        "Silakan pilih bahasa secara manual di dropdown."
                    )
            else:
                st.caption("Bahasa akan terdeteksi otomatis begitu kamu paste kode.")

    button_label = "🚀 Review Kode" if is_first else "🔄 Review Ulang dengan Kode yang Diperbaiki"
    run_button = st.button(button_label, type="primary", key=f"run_button_{round_num}")

    if run_button:
        if not code_input.strip():
            st.warning("Masukkan kode terlebih dahulu.")
            return

        if not api_key_input.strip():
            st.warning("Masukkan Groq API Key di sidebar terlebih dahulu (gratis di console.groq.com).")
            return

        if language_choice == AUTO_DETECT_LABEL:
            language = detected
            if not language:
                st.error(
                    "Bahasa tidak bisa dideteksi otomatis dari kode ini. "
                    "Silakan pilih bahasa secara manual di dropdown lalu klik tombol lagi."
                )
                return
        else:
            language = language_choice

        with st.status(f"Menjalankan analisis ({language})...", expanded=True) as status:
            st.write("Menjalankan static analysis (Semgrep)...")
            st.write("Mengirim ke Groq LLM untuk analisis mendalam...")
            semgrep_result, llm_result = run_analysis(code_input, language, api_key_input)
            status.update(label="Selesai!", state="complete", expanded=False)

        st.session_state.rounds.append(
            {
                "code": code_input,
                "language": language,
                "semgrep": semgrep_result,
                "llm": llm_result,
            }
        )
        st.rerun()


if __name__ == "__main__":
    main()
