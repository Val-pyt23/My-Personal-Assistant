import ollama

def generate_response_stream(konteks_pesan, pdf_text_context=None, user_input="", model_pilihan='qwen2.5:7b'):
    """
    Fungsi generator untuk memanggil Ollama dengan efek streaming.
    Menerima riwayat pesan dan teks PDF (jika ada).
    """
    
    # 1. Aturan Wajib untuk LaTeX, Coding Python, dan Identitas Model
    instruksi_sistem = {
        "role": "system",
        "content": """Kamu adalah asisten ahli Data Science, Statistika, dan Pemrograman Python.
Ikuti aturan berikut secara mutlak:

1. BAHASA (PRIORITAS TERTINGGI — TIDAK DAPAT DILANGGAR):
Seluruh jawaban WAJIB dalam Bahasa Indonesia atau Bahasa Inggris.
Berlaku dalam kondisi apapun — termasuk saat menjawab pertanyaan panjang,
kompleks, atau membingungkan sekalipun.
JANGAN PERNAH menggunakan Bahasa Mandarin, Jepang, atau bahasa asing lainnya,
bahkan hanya satu kata atau satu kalimat di tengah jawaban.

2. MATEMATIKA & STATISTIKA:
Setiap rumus atau persamaan WAJIB dibungkus dengan $$ di awal dan di akhir.
Contoh yang benar: $$MSE = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2$$
DILARANG menggunakan format \\[, \\], \\(, atau \\).

3. PEMROGRAMAN PYTHON:
JANGAN tulis kode Python kecuali pesan pengguna mengandung kata seperti:
"buatkan kode", "tulis script", "implementasikan", "buat fungsi", atau "coding".
Jika tidak ada kata tersebut → berikan penjelasan konseptual dan contoh
kasus nyata dalam bentuk teks saja. DILARANG menulis kode.

4. GAYA INTERAKSI:
Berikan jawaban yang to-the-point.
Di akhir setiap jawaban, WAJIB tambahkan satu pertanyaan penutup yang natural,
mengalir seperti percakapan manusia biasa.
Contoh yang benar:
- "Apakah kamu ingin mencoba menerapkannya pada dataset tertentu?"
- "Bagian mana yang ingin kamu eksplorasi lebih lanjut?"
DILARANG menggunakan label seperti "Pertanyaan lanjutan:" atau "Follow-up:".

5. FOKUS EKOSISTEM:
Fokus pada metode Core ML dan library standar (pandas, scikit-learn).
JANGAN menyebut LangChain atau time series kecuali pengguna memintanya.

6. EKSTRAKSI FAKTA DOKUMEN:
Jika pengguna menanyakan fakta dari dokumen yang dilampirkan, WAJIB kutip
teks aslinya secara exact. DILARANG mengarang atau menyimpulkan sendiri."""
    }

    # 2. Injeksi PDF jika dilampirkan (Modifikasi pesan terakhir)
    if pdf_text_context:
        prompt_injeksi = (
            f"Berdasarkan isi dokumen berikut:\n"
            f"------------------\n"
            f"{pdf_text_context}\n"
            f"------------------\n\n"
            f"Tolong jawab pertanyaan ini: {user_input}"
        )
        konteks_pesan[-1] = {"role": "user", "content": prompt_injeksi}

    # 3. Gabungkan sistem prompt dengan riwayat pesan
    pesan_final = [instruksi_sistem] + konteks_pesan

    # 4. Panggil model dan yield hasilnya secara streaming
    for chunk in ollama.chat(
        model=model_pilihan,
        messages=pesan_final,
        options={'temperature':0.4},
        stream=True
    ):
        yield chunk['message']['content']