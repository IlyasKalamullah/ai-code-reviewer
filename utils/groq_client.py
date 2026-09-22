"""
Modul untuk memanggil Groq API (gratis) dan meminta LLM mereview kode.
Hasil static analysis Semgrep (jika ada) disertakan sebagai konteks tambahan
supaya jawaban LLM lebih akurat dan tidak halusinasi.
"""

import json
import os
import time
from groq import Groq, APIStatusError

# Kadang Groq mengembalikan error "json_validate_failed" walau isi JSON-nya
# sebenarnya valid (bisa dilihat di field 'failed_generation' pada error body).
# MAX_RETRIES membuat sistem otomatis mencoba lagi sebelum menyerah, supaya
# user tidak perlu klik manual berkali-kali untuk error yang sifatnya sementara.
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.5

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

    client = Groq(api_key=key)
    user_prompt = build_user_prompt(code, language, semgrep_findings)

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
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

        except APIStatusError as e:
            # Kadang Groq menandai response sebagai gagal validasi JSON
            # ("json_validate_failed") padahal isinya (di 'failed_generation')
            # sebenarnya JSON yang valid. Coba parse itu dulu sebagai fallback
            # sebelum retry, supaya tidak buang hasil yang sebenarnya bagus.
            failed_generation = None
            try:
                if isinstance(e.body, dict):
                    failed_generation = e.body.get("error", {}).get("failed_generation")
            except Exception:
                pass

            if failed_generation:
                try:
                    parsed = json.loads(failed_generation)
                    return {"success": True, "result": parsed, "raw_error": None}
                except json.JSONDecodeError:
                    pass

            last_error = str(e)

        except json.JSONDecodeError:
            last_error = "Model mengembalikan format yang tidak valid."
        except Exception as e:
            last_error = str(e)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    return {
        "success": False,
        "result": None,
        "raw_error": f"{last_error} (sudah dicoba {MAX_RETRIES}x)",
    }
