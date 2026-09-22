"""
Deteksi otomatis bahasa pemrograman dari isi kode yang dipaste user,
supaya user tidak perlu pilih manual (misal paste kode Laravel/PHP,
otomatis terdeteksi sebagai PHP).

Pendekatan: heuristik berbasis skor dari pola/keyword khas tiap bahasa.
Dipilih ketimbang pygments.guess_lexer karena untuk potongan kode pendek
(bukan file utuh), pygments sering salah tebak.
"""

import re

# Setiap bahasa punya daftar pola regex + bobot skornya.
# Pola yang sangat khas (jarang muncul di bahasa lain) dikasih bobot lebih besar.
LANGUAGE_PATTERNS = {
    "PHP": [
        (r"<\?php", 5),
        (r"\bnamespace\s+[\w\\]+;", 4),
        (r"\buse\s+[\w\\]+;", 3),
        (r"\$this->", 3),
        (r"\bfunction\s+\w+\s*\(", 2),
        (r"->[a-zA-Z_]+\(", 2),
        (r"::\s*\w+\(", 2),
        (r"\becho\s+", 2),
        (r"\$\w+\s*=", 1),
    ],
    "Python": [
        (r"^\s*def\s+\w+\s*\(.*\)\s*:", 4),
        (r"^\s*import\s+\w+", 3),
        (r"^\s*from\s+\w+\s+import\s+", 3),
        (r"\bself\.", 3),
        (r"^\s*class\s+\w+.*:", 3),
        (r"\bprint\(", 2),
        (r"^\s*elif\s+", 3),
        (r":\s*$", 1),
    ],
    "TypeScript": [
        (r"\binterface\s+\w+\s*{", 5),
        (r":\s*(string|number|boolean|any|void)\b", 4),
        (r"\bimplements\s+\w+", 3),
        (r"<\w+>\s*\(", 2),
        (r"\bexport\s+(default\s+)?(class|function|const|interface)", 3),
        (r"\bconst\s+\w+\s*:", 3),
    ],
    "JavaScript": [
        (r"\bfunction\s+\w+\s*\(", 3),
        (r"\bconst\s+\w+\s*=", 2),
        (r"\blet\s+\w+\s*=", 2),
        (r"=>\s*{", 3),
        (r"\brequire\(", 3),
        (r"\bimport\s+.*\s+from\s+['\"]", 2),
        (r"\bconsole\.log\(", 3),
        (r"\bdocument\.", 3),
    ],
    "Java": [
        (r"\bpublic\s+class\s+\w+", 5),
        (r"\bpublic\s+static\s+void\s+main\s*\(", 5),
        (r"\bimport\s+java\.", 4),
        (r"\bSystem\.out\.print", 4),
        (r"\bprivate\s+\w+\s+\w+;", 2),
        (r"\bnew\s+\w+\(", 1),
    ],
    "Go": [
        (r"^\s*package\s+main", 5),
        (r"\bfunc\s+\w*\s*\(", 4),
        (r":=", 4),
        (r"\bimport\s*\(", 3),
        (r"\bfmt\.Print", 4),
    ],
    "C++": [
        (r"#include\s*<\w+>", 2),
        (r"\bstd::", 5),
        (r"\bcout\s*<<", 4),
        (r"\bclass\s+\w+\s*{", 2),
        (r"\bnamespace\s+\w+\s*{", 3),
    ],
    "C": [
        (r"#include\s*<\w+\.h>", 4),
        (r"\bprintf\(", 4),
        (r"\bint\s+main\s*\(", 3),
        (r"\bmalloc\(", 3),
    ],
    "Ruby": [
        (r"^\s*def\s+\w+.*\n(.*\n)*?\s*end\b", 4),
        (r"\bputs\s+", 4),
        (r"\brequire\s+['\"]", 3),
        (r"\bend\s*$", 2),
        (r"\battr_accessor\b", 4),
        (r"@\w+", 1),
    ],
}


def detect_language(code: str) -> str | None:
    """
    Mendeteksi bahasa pemrograman dari isi kode.
    Mengembalikan nama bahasa (sesuai key di LANGUAGE_EXTENSIONS) atau None
    kalau tidak yakin (skor tertinggi terlalu rendah / ambigu).
    """
    if not code or not code.strip():
        return None

    scores = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        total = 0
        for pattern, weight in patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            total += len(matches) * weight
        scores[lang] = total

    best_lang = max(scores, key=scores.get)
    best_score = scores[best_lang]

    # Butuh skor minimal supaya tidak asal tebak dari kode yang terlalu pendek/ambigu.
    if best_score < 4:
        return None

    # Kasus khusus: TypeScript adalah superset JavaScript, jadi kalau skor
    # TypeScript dan JavaScript berdekatan, prioritaskan TypeScript karena
    # pola TypeScript lebih spesifik.
    if best_lang == "JavaScript" and scores.get("TypeScript", 0) >= scores["JavaScript"] * 0.5 and scores.get("TypeScript", 0) >= 4:
        return "TypeScript"

    return best_lang
