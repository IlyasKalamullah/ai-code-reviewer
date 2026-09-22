"""
Modul untuk menjalankan Semgrep (static analysis) terhadap kode yang dikirim user.
Semgrep dipilih karena gratis, open-source, dan mendukung banyak bahasa
(Python, JavaScript, TypeScript, Java, Go, dan lainnya) dalam satu tool.
"""

import json
import subprocess
import tempfile
import os

# Ekstensi file untuk tiap bahasa yang didukung di UI.
# Semgrep mengenali bahasa dari ekstensi file, jadi ini penting.
LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "JavaScript": ".js",
    "TypeScript": ".ts",
    "Java": ".java",
    "Go": ".go",
    "PHP": ".php",
    "C": ".c",
    "C++": ".cpp",
    "Ruby": ".rb",
}

# Ruleset publik Semgrep yang gratis dan tidak butuh login.
# "p/security-audit" fokus ke isu keamanan lintas bahasa.
DEFAULT_RULESET = "p/security-audit"


def run_semgrep(code: str, language: str, ruleset: str = DEFAULT_RULESET) -> dict:
    """
    Menjalankan semgrep terhadap potongan kode dan mengembalikan temuan
    dalam bentuk terstruktur.

    Returns dict dengan keys:
        - success: bool
        - findings: list of dict (rule_id, message, severity, line, line_end)
        - raw_error: str (jika ada error)
    """
    ext = LANGUAGE_EXTENSIONS.get(language, ".txt")

    # Semgrep butuh file fisik untuk dianalisis, bukan string langsung.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=ext, delete=False, encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(code)
        tmp_path = tmp_file.name

    # Nonaktifkan telemetry/version check Semgrep supaya tidak mencoba
    # menghubungi internet saat scan (dan supaya tidak hang di jaringan terbatas).
    env = os.environ.copy()
    env["SEMGREP_SEND_METRICS"] = "off"
    env["SEMGREP_ENABLE_VERSION_CHECK"] = "0"

    try:
        result = subprocess.run(
            [
                "semgrep",
                "scan",
                "--config",
                ruleset,
                "--json",
                "--quiet",
                "--no-git-ignore",
                "--metrics",
                "off",
                tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode not in (0, 1):
            # returncode 1 = semgrep jalan normal tapi menemukan match, itu bukan error.
            return {
                "success": False,
                "findings": [],
                "raw_error": result.stderr[:2000] if result.stderr else "Semgrep gagal dijalankan.",
            }

        output = json.loads(result.stdout)
        findings = []

        for item in output.get("results", []):
            findings.append(
                {
                    "rule_id": item.get("check_id", "unknown"),
                    "message": item.get("extra", {}).get("message", ""),
                    "severity": item.get("extra", {}).get("severity", "INFO"),
                    "line_start": item.get("start", {}).get("line"),
                    "line_end": item.get("end", {}).get("line"),
                }
            )

        return {"success": True, "findings": findings, "raw_error": None}

    except FileNotFoundError:
        return {
            "success": False,
            "findings": [],
            "raw_error": (
                "Semgrep belum terinstall. Jalankan: pip install semgrep"
            ),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "findings": [],
            "raw_error": "Semgrep timeout (kode terlalu besar atau kompleks).",
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "findings": [],
            "raw_error": "Gagal membaca output Semgrep.",
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
