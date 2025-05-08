# 🌙 Islamic Agent - Asisten Virtual Islami Anda

![Islamic Agent](https://img.shields.io/badge/Islamic-Agent-brightgreen)
![Python](https://img.shields.io/badge/Made%20with-Python-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)

> "Barangsiapa yang menunjukkan kepada kebaikan, maka ia akan mendapatkan pahala seperti pahala orang yang melakukannya." (HR. Muslim)

Islamic Agent adalah bot Telegram yang dirancang untuk menjadi asisten virtual Islami lengkap. Bot ini menyediakan berbagai informasi dan layanan keagamaan dalam bahasa Indonesia untuk membantu Muslim dalam aktivitas ibadah sehari-hari.

## ✨ Fitur Utama

### 🕋 Jadwal Sholat

- Dapatkan jadwal sholat untuk kota manapun di Indonesia
- Berlangganan pengingat waktu sholat harian
- Data akurat dari API Kemenag RI

### 📖 Al-Quran

- Baca surah Al-Quran dengan teks Arab dan terjemahan Indonesia
- Cari ayat berdasarkan kata kunci
- Memahami input fleksibel (nama surah atau nomor)

### 📅 Kalender Hijriah

- Konversi tanggal Masehi ke Hijriah
- Informasi bulan Hijriah lengkap
- Daftar hari-hari khusus Islam

### 🤲 Doa-doa

- Koleksi doa sehari-hari lengkap dengan Arab, Latin, dan terjemahan
- Pencarian doa berdasarkan judul atau kata kunci

### 💬 Tanya Jawab Islam

- Jawaban AI untuk pertanyaan seputar Islam
- Didukung oleh Google Gemini untuk jawaban yang akurat dan informatif
- Proses berpikir sekuensial untuk jawaban mendalam

### 🌟 Motivasi Islami

- Kata-kata motivasi Islami harian
- Dikutip dari Al-Quran dan Hadits

## 🚀 Cara Menggunakan

1. Mulai percakapan dengan bot yang sudah kamu buat
2. Ketik `/start` untuk memulai dan melihat pesan sambutan
3. Ketik `/help` untuk melihat panduan penggunaan lengkap
4. Gunakan perintah yang tersedia atau tanyakan pertanyaan langsung

### Perintah Dasar:

- `/start` - Memulai bot
- `/help` - Menampilkan panduan penggunaan
- `/sholat [kota]` - Jadwal sholat untuk kota tertentu
- `/quran [surah]` - Membaca surah Al-Quran
- `/cari_ayat [kata kunci]` - Pencarian ayat Al-Quran
- `/doa [judul]` - Menemukan doa berdasarkan judul
- `/kalender` - Melihat tanggal Hijriah hari ini
- `/bulan [nomor_bulan] [tahun]` - Informasi bulan Hijriah
- `/motivasi` - Mendapatkan kata motivasi Islami acak
- `/motivasi_harian` - Kata motivasi Islami hari ini

## 🔧 Instalasi dan Pengembangan

### Prasyarat

- Python 3.8+
- API key Telegram Bot dari BotFather
- API key Google Gemini

### Langkah Instalasi

1. Clone repositori ini:

```bash
git clone https://github.com/ridhoarmand/islamic-agent.git
cd islamic-agent
```

2. Instal dependensi:

```bash
pip install -r requirements.txt
```
3. Copy contoh .env

```bash
cp .env.example .env
```
4. Sesuaikan konfigurasi di `.env`

5. Jalankan bot:

```bash
python main.py
```

## 📦 Struktur Proyek

```
islamic-agent/
├── main.py                  # Entry point aplikasi
├── config/                  # Konfigurasi
│   └── config.py            # Konfigurasi aplikasi
├── data/                    # Data dan database
│   ├── islamic_agent.db     # Database SQLite
│   ├── duas/                # Data doa-doa
│   ├── quotes/              # Data motivasi Islami
│   └── quran/               # Data Al-Quran
├── handlers/                # Handler perintah Telegram
│   └── command_handler.py   # Handler untuk semua perintah
├── logs/                    # File log aplikasi
├── services/                # Layanan aplikasi
│   ├── calendar_service.py  # Layanan kalender Hijriah
│   ├── dua_service.py       # Layanan untuk doa-doa
│   ├── gemini_service.py    # Layanan AI (Google Gemini)
│   ├── prayer_service.py    # Layanan jadwal sholat
│   ├── quote_service.py     # Layanan motivasi Islami
│   ├── quran_service.py     # Layanan Al-Quran
│   ├── scheduler_service.py # Layanan penjadwalan notifikasi
│   └── mcp_service.py       # Layanan MCP
└── utils/                   # Utilitas
    └── database.py          # Operasi database
```

## 🤝 Kontribusi

Kontribusi untuk pengembangan Islamic Agent sangat diterima! Jika Anda ingin berkontribusi:

1. Fork repositori ini
2. Buat branch fitur baru (`git checkout -b feature/amazing-feature`)
3. Commit perubahan Anda (`git commit -m 'Add some amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request

## 📝 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

## 📬 Kontak

Link Proyek: [https://github.com/ridhoarmand/islamic-agent](https://github.com/ridhoarmand/islamic-agent)

---

Dibuat dengan ❤️ dan 🤲 untuk Umat Muslim
