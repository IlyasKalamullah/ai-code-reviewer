# AI Code Reviewer 🔍

Aplikasi web sederhana yang mengoreksi dan memberi saran perbaikan kode —
mulai dari keamanan, bug, performa, hingga gaya penulisan — menggunakan
kombinasi **Semgrep** (static analysis, gratis & open-source) dan
**Groq LLM API** (gratis).

## Fitur

- Analisis multi-bahasa: Python, JavaScript, TypeScript, Java, Go, PHP, C, C++, Ruby
- Deteksi celah keamanan otomatis (SQL injection, XSS, hardcoded secret, dll) lewat Semgrep
- Penjelasan & saran perbaikan dalam bahasa natural dari LLM
- Kategori temuan: security, bug, performance, style — dengan tingkat keparahan
- Tampilan web interaktif (Streamlit)

## Kenapa gratis?

- **Semgrep**: open-source, ruleset publik (`p/security-audit`) tidak butuh login/API key.
- **Groq API**: punya free tier untuk model seperti Llama 3.3 70B, tidak butuh kartu kredit untuk mulai.

## Setup

### 1. Clone / masuk ke folder project

```bash
cd ai-code-reviewer
```

### 2. Buat virtual environment (opsional tapi disarankan)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Dapatkan Groq API Key gratis

1. Buka https://console.groq.com
2. Daftar/login (gratis, tanpa kartu kredit)
3. Masuk ke menu **API Keys** → buat key baru
4. Salin API key-nya

### 5. Set API key

Salin `.env.example` menjadi `.env`, lalu isi:

```bash
cp .env.example .env
```

Edit `.env`:
```
GROQ_API_KEY=isi_api_key_kamu_di_sini
```

Atau, kamu juga bisa langsung memasukkan API key lewat sidebar aplikasi tanpa perlu file `.env`.

### 6. Jalankan aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser (biasanya `http://localhost:8501`).

## Struktur Project

```
ai-code-reviewer/
├── app.py                  # UI utama Streamlit
├── utils/
│   ├── semgrep_runner.py   # Menjalankan static analysis Semgrep
│   └── groq_client.py      # Memanggil Groq API + prompt engineering
├── requirements.txt
├── .env.example
└── README.md
```

## Cara Kerja

1. User paste kode + pilih bahasa pemrograman
2. Semgrep menjalankan static analysis berbasis rule (cepat, gratis, akurat untuk pola yang sudah dikenal)
3. Temuan Semgrep dikirim sebagai konteks tambahan ke Groq LLM
4. LLM menjelaskan temuan dengan bahasa natural + menganalisis hal lain yang mungkin terlewat (logika, performa, best practice)
5. Hasil ditampilkan terstruktur berdasarkan tingkat keparahan

Pendekatan hybrid ini (static analysis + LLM) menghasilkan review yang lebih
akurat dibanding mengandalkan AI saja, karena Semgrep memberi "fakta" yang
sudah pasti benar, sementara LLM membantu menjelaskan dan menambahkan insight.

## Mengembangkan Lebih Lanjut (Ide)

- Simpan riwayat review ke database (SQLite)
- Upload file, bukan cuma paste teks
- Highlight baris bermasalah langsung di editor kode (Monaco Editor)
- Deploy gratis ke Streamlit Community Cloud atau Hugging Face Spaces
- Ganti model Groq ke model lain yang tersedia di akun kamu
- Tambah mode evaluasi: uji dengan contoh kode OWASP Top 10 untuk mengukur akurasi

## Troubleshooting

- **"Semgrep belum terinstall"** → jalankan `pip install semgrep`
- **Error API key** → pastikan key valid dan belum melewati limit gratis harian
- **Model tidak ditemukan** → cek daftar model aktif di https://console.groq.com/docs/models, sesuaikan `MODEL_NAME` di `utils/groq_client.py`
