"""
Modul untuk memanggil Groq API (gratis) dan meminta LLM mereview kode.
Hasil static analysis Semgrep (jika ada) disertakan sebagai konteks tambahan
supaya jawaban LLM lebih akurat dan tidak halusinasi.
"""

import json
import os
from groq import Groq

# Model gratis di Groq yang cukup kuat untuk reasoning soal kode.
# Cek daftar model yang tersedia di akun kamu di https://console.groq.com/docs/models
# Ganti string di bawah ini kalau model ini suatu saat di-deprecate atau tidak
# tersedia di akun kamu.
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """Kamu adalah code reviewer ahli yang berpengalaman di bidang keamanan aplikasi (application security), \
best practice engineering, dan performa kode. Tugasmu adalah menganalisis potongan kode yang diberikan user.

Selalu jawab HANYA dalam format JSON valid (tanpa markdown, tanpa teks tambahan di luar JSON), dengan struktur berikut:

{
  "summary": "ringkasan singkat kondisi kode secara umum",
  "findings": [
    {
      "severity": "critical | high | medium | low",
      "category": "security | bug | performance | style",
      "line": <nomor baris atau null jika tidak spesifik>,
      "issue": "penjelasan masalah dengan jelas",
      "suggestion": "saran perbaikan, sertakan contoh kode singkat jika relevan"
    }
  ]
}

Jika kode sudah baik dan tidak ada temuan, kembalikan "findings": [] dan summary yang menjelaskan itu.
Jangan mengarang temuan yang tidak benar-benar ada di kode. Fokus pada masalah nyata."""


def build_user_prompt(code: str, language: str, semgrep_findings: list) -> str:
    """Menyusun prompt user, menyertakan temuan Semgrep sebagai konteks tambahan."""
    prompt_parts = [
        f"Bahasa pemrograman: {language}",
        "",
        "Kode yang harus direview:",
        "```" + language.lower(),
        code,
        "```",
    ]

    if semgrep_findings:
        prompt_parts.append("")
        prompt_parts.append(
            "Berikut temuan awal dari static analysis tool (Semgrep). "
            "Gunakan ini sebagai referensi tambahan, jelaskan dengan bahasa yang mudah dipahami, "
            "dan lengkapi dengan analisis lain yang mungkin terlewat:"
        )
        for f in semgrep_findings:
            prompt_parts.append(
                f"- [{f['severity']}] baris {f['line_start']}: {f['message']} (rule: {f['rule_id']})"
            )
    else:
        prompt_parts.append("")
        prompt_parts.append(
            "Static analysis tool tidak menemukan masalah otomatis. "
            "Lakukan analisis manual yang lebih mendalam, termasuk celah keamanan, logika, dan performa."
        )

    return "\n".join(prompt_parts)


def review_code(code: str, language: str, semgrep_findings: list, api_key: str = None) -> dict:
    """
    Memanggil Groq API untuk mereview kode.

    Returns dict dengan keys:
        - success: bool
        - result: dict (summary, findings) jika sukses
        - raw_error: str jika gagal
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return {
            "success": False,
            "result": None,
            "raw_error": "GROQ_API_KEY belum diset. Isi di file .env atau masukkan lewat sidebar.",
        }

    try:
        client = Groq(api_key=key)

        user_prompt = build_user_prompt(code, language, semgrep_findings)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content
        parsed = json.loads(raw_content)

        return {"success": True, "result": parsed, "raw_error": None}

    except json.JSONDecodeError:
        return {
            "success": False,
            "result": None,
            "raw_error": "Model mengembalikan format yang tidak valid. Coba jalankan ulang.",
        }
    except Exception as e:
        return {"success": False, "result": None, "raw_error": str(e)}
