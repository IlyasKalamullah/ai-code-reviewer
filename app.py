"""
AI Code Reviewer — Streamlit App
Mengoreksi dan memberi saran perbaikan kode (keamanan, bug, performa, style)
dengan menggabungkan Semgrep (static analysis, gratis) + Groq LLM (gratis).
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils.semgrep_runner import run_semgrep, LANGUAGE_EXTENSIONS
from utils.groq_client import review_code
from utils.language_detector import detect_language

AUTO_DETECT_LABEL = "🔍 Deteksi Otomatis"

load_dotenv()

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")

SEVERITY_COLOR = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "error": "🔴",
    "warning": "🟠",
    "info": "🔵",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def render_findings(findings: list):
    if not findings:
        st.success("Tidak ada temuan. Kode terlihat baik dari sisi yang dianalisis.")
        return

    sorted_findings = sorted(
        findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "low"), 4)
    )

    for f in sorted_findings:
        severity = f.get("severity", "low")
        icon = SEVERITY_COLOR.get(severity, "⚪")
        line_info = f" (baris {f['line']})" if f.get("line") else ""
        category = f.get("category", "").upper()

        with st.expander(f"{icon} [{severity.upper()}] {category}{line_info} — {f.get('issue', '')[:80]}"):
            st.markdown(f"**Masalah:** {f.get('issue', '-')}")
            st.markdown(f"**Saran perbaikan:**")
            st.markdown(f.get("suggestion", "-"))


def main():
    st.title("🔍 AI Code Reviewer")
    st.caption(
        "Analisis kode otomatis: keamanan, bug, performa, dan gaya penulisan. "
        "Ditenagai Semgrep (static analysis) + Groq LLM — 100% gratis."
    )

    with st.sidebar:
        st.header("⚙️ Pengaturan")
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
        )
        st.markdown("---")
        st.markdown("[Dapatkan Groq API Key gratis →](https://console.groq.com/keys)")

    code_input = st.text_area(
        "Paste kode di sini",
        height=350,
        placeholder="# Tempel kode yang ingin direview di sini (bahasa apa saja, akan terdeteksi otomatis)...",
    )

    detected = detect_language(code_input) if code_input.strip() else None

    col1, col2 = st.columns([1, 3])
    with col1:
        language_options = [AUTO_DETECT_LABEL] + list(LANGUAGE_EXTENSIONS.keys())
        language_choice = st.selectbox(
            "Bahasa Pemrograman",
            language_options,
            help="Biarkan di 'Deteksi Otomatis' supaya bahasa terdeteksi sendiri dari kode yang kamu paste, atau pilih manual kalau deteksinya kurang tepat.",
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

    run_button = st.button("🚀 Review Kode", type="primary", use_container_width=False)

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
                    "Silakan pilih bahasa secara manual di dropdown lalu klik 'Review Kode' lagi."
                )
                return
        else:
            language = language_choice

        with st.status(f"Menjalankan analisis ({language})...", expanded=True) as status:
            st.write("Menjalankan static analysis (Semgrep)...")
            semgrep_result = run_semgrep(code_input, language)

            if not semgrep_result["success"]:
                st.warning(
                    f"Semgrep tidak berjalan sempurna: {semgrep_result['raw_error']}. "
                    "Melanjutkan dengan analisis AI saja."
                )

            st.write("Mengirim ke Groq LLM untuk analisis mendalam...")
            llm_result = review_code(
                code=code_input,
                language=language,
                semgrep_findings=semgrep_result.get("findings", []),
                api_key=api_key_input,
            )

            status.update(label="Selesai!", state="complete", expanded=False)

        if not llm_result["success"]:
            st.error(f"Gagal mendapatkan review dari AI: {llm_result['raw_error']}")
            return

        result = llm_result["result"]

        st.subheader("📋 Ringkasan")
        st.info(result.get("summary", "-"))

        st.subheader("🔎 Temuan Detail")
        render_findings(result.get("findings", []))

        with st.expander("Lihat temuan mentah Semgrep (opsional)"):
            if semgrep_result.get("findings"):
                st.json(semgrep_result["findings"])
            else:
                st.write("Tidak ada temuan mentah dari Semgrep.")


if __name__ == "__main__":
    main()
