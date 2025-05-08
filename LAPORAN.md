# 📘 Laporan Pengembangan Project Islamic Agent

## Universitas Amikom Purwokerto  
### Mata Kuliah: Agent  

<img src="https://github.com/user-attachments/assets/be5c1a70-da6b-4204-a7d7-ded30c4161a1" alt="Universitas Amikom Purwokerto" width="300"/>

<br>

### 👨‍💻 Anggota Kelompok:
- **22SA11A033** - Ridho Armansyah  
- **22SA11A172** - Nova Ramadhan  
- **22SA11A213** - Ignas Surya Gemilang  
- **22SA11A268** - Tri Antono  

---

### Fakultas Ilmu Komputer  
### Program Studi Informatika  

<br>

<img src="https://img.shields.io/badge/Islamic-Agent-brightgreen" alt="Islamic Agent Badge"/>

---

## 🛠️ Pengembangan Bot Telegram Islamic Agent  
### Laporan Project Agent AI


## DAFTAR ISI

- [LAPORAN PENGEMBANGAN ISLAMIC AGENT](#laporan-pengembangan-islamic-agent)
  - [DAFTAR ISI](#daftar-isi)
  - [1. PENDAHULUAN](#1-pendahuluan)
    - [1.1 Latar Belakang](#11-latar-belakang)
    - [1.2 Rumusan Masalah](#12-rumusan-masalah)
    - [1.3 Tujuan](#13-tujuan)
    - [1.4 Manfaat](#14-manfaat)
  - [2. LANDASAN TEORI](#2-landasan-teori)
    - [2.1 Bot Telegram](#21-bot-telegram)
    - [2.2 Python-Telegram-Bot](#22-python-telegram-bot)
    - [2.3 Google Gemini API](#23-google-gemini-api)
    - [2.4 API Kementerian Agama](#24-api-kementerian-agama)
  - [3. METODOLOGI](#3-metodologi)
    - [3.1 Analisis Kebutuhan](#31-analisis-kebutuhan)
    - [3.2 Perancangan Sistem](#32-perancangan-sistem)
    - [3.3 Implementasi](#33-implementasi)
    - [3.4 Pengujian](#34-pengujian)
  - [4. PERANCANGAN APLIKASI](#4-perancangan-aplikasi)
    - [4.1 Arsitektur Sistem](#41-arsitektur-sistem)
    - [4.2 Struktur Database](#42-struktur-database)
    - [4.3 Diagram Alur](#43-diagram-alur)
  - [5. IMPLEMENTASI](#5-implementasi)
    - [5.1 Pengembangan Fitur](#51-pengembangan-fitur)
      - [5.1.1 Fitur Jadwal Sholat](#511-fitur-jadwal-sholat)
      - [5.1.2 Fitur Al-Quran](#512-fitur-al-quran)
      - [5.1.3 Fitur Kalender Hijriah](#513-fitur-kalender-hijriah)
      - [5.1.4 Fitur Doa-doa](#514-fitur-doa-doa)
      - [5.1.5 Fitur Motivasi Islami](#515-fitur-motivasi-islami)
      - [5.1.6 Fitur AI Assistant](#516-fitur-ai-assistant)
    - [5.2 Implementasi Database](#52-implementasi-database)
    - [5.3 Implementasi API](#53-implementasi-api)
  - [6. PENGUJIAN](#6-pengujian)
    - [6.1 Metode Pengujian](#61-metode-pengujian)
    - [6.2 Hasil Pengujian](#62-hasil-pengujian)
    - [6.3 Analisis Hasil Pengujian](#63-analisis-hasil-pengujian)
  - [7. KESIMPULAN DAN SARAN](#7-kesimpulan-dan-saran)
    - [7.1 Kesimpulan](#71-kesimpulan)
    - [7.2 Saran](#72-saran)
  - [8. DAFTAR PUSTAKA](#8-daftar-pustaka)
  - [9. LAMPIRAN](#9-lampiran)

<div style="page-break-after: always;"></div>

## 1. PENDAHULUAN

### 1.1 Latar Belakang

Dalam era digital saat ini, akses terhadap informasi keagamaan menjadi sangat penting bagi umat Muslim untuk menjalankan ibadah sehari-hari. Namun, tidak semua Muslim memiliki akses mudah ke sumber informasi yang terpercaya dan terorganisir dengan baik. Selain itu, kesibukan dan rutinitas harian sering kali membuat umat Muslim kesulitan dalam mengatur waktu untuk mencari informasi yang mereka butuhkan terkait jadwal sholat, membaca Al-Quran, atau mencari doa-doa tertentu.

Islamic Agent dikembangkan sebagai solusi untuk permasalahan tersebut, dengan memanfaatkan platform Telegram yang telah digunakan secara luas di masyarakat Indonesia. Bot ini dirancang untuk menjadi asisten virtual Islami yang komprehensif, menyediakan berbagai informasi keagamaan penting seperti jadwal sholat, ayat Al-Quran, doa-doa, kalender Hijriah, dan jawaban untuk pertanyaan-pertanyaan seputar Islam.

Dengan mengintegrasikan teknologi AI melalui Google Gemini, Islamic Agent mampu memberikan jawaban yang informatif dan akurat untuk pertanyaan-pertanyaan kompleks tentang Islam. Penggunaan API Kementerian Agama RI juga memastikan bahwa informasi yang diberikan, seperti jadwal sholat, bersumber dari otoritas yang terpercaya.

### 1.2 Rumusan Masalah

1. Bagaimana merancang dan mengembangkan bot Telegram yang dapat menyediakan informasi keagamaan Islam secara komprehensif?
2. Bagaimana mengintegrasikan berbagai API dan layanan untuk menyediakan informasi yang akurat dan terpercaya?
3. Bagaimana menerapkan teknologi AI untuk menjawab pertanyaan-pertanyaan kompleks tentang Islam?
4. Bagaimana merancang pengalaman pengguna yang intuitif dan mudah digunakan dalam konteks bot Telegram?
5. Bagaimana mengelola dan menyimpan data pengguna dengan aman serta menyediakan fitur berlangganan yang personalized?

### 1.3 Tujuan

1. Mengembangkan bot Telegram yang menyediakan akses mudah ke informasi keagamaan Islam seperti jadwal sholat, Al-Quran, doa-doa, dan kalender Hijriah.
2. Mengimplementasikan sistem AI berbasis Google Gemini untuk menjawab pertanyaan seputar Islam secara akurat dan informatif.
3. Menyediakan fitur berlangganan untuk notifikasi jadwal sholat dan motivasi harian yang dapat disesuaikan dengan kebutuhan pengguna.
4. Menciptakan antarmuka yang intuitif dan ramah pengguna dalam format chat bot Telegram.
5. Membuat sistem yang dapat diakses dari mana saja dan kapan saja melalui platform Telegram.

### 1.4 Manfaat

1. **Bagi Pengguna Muslim**:

   - Kemudahan akses informasi keagamaan dari satu platform
   - Pengingat waktu sholat yang dapat disesuaikan
   - Akses cepat ke ayat-ayat Al-Quran dan terjemahannya
   - Informasi kalender Hijriah dan hari-hari penting Islam
   - Sumber motivasi islami harian

2. **Bagi Pengembang**:

   - Pengalaman dalam pengembangan chatbot dengan teknologi modern
   - Penerapan integrasi API dan layanan pihak ketiga
   - Implementasi AI dalam konteks agama dan budaya
   - Portfolio pengembangan aplikasi dengan dampak sosial positif

3. **Bagi Masyarakat**:
   - Meningkatkan literasi keagamaan
   - Memudahkan akses informasi keagamaan bagi Muslim di daerah dengan akses terbatas
   - Menjembatani kesenjangan digital dalam akses informasi keagamaan

<div style="page-break-after: always;"></div>

## 2. LANDASAN TEORI

### 2.1 Bot Telegram

Bot Telegram adalah program komputer yang berjalan di platform Telegram dan dapat berinteraksi dengan pengguna melalui antarmuka chat. Bot ini dapat diprogram untuk melakukan berbagai tugas, mulai dari memberikan informasi, mengirim peringatan, hingga mengotomatisasi tugas-tugas tertentu. Bot Telegram menggunakan Telegram Bot API yang disediakan oleh Telegram untuk berkomunikasi dengan server Telegram dan berinteraksi dengan pengguna.

Beberapa fitur utama Bot Telegram:

- Kemampuan untuk mengirim dan menerima pesan
- Dukungan untuk berbagai format pesan (teks, gambar, audio, dokumen)
- Keyboard kustom dan inline keyboard
- Kemampuan untuk merespons perintah dengan awalan '/'
- Webhook atau long polling untuk menerima update

### 2.2 Python-Telegram-Bot

Python-Telegram-Bot adalah library Python yang menyediakan wrapper untuk Telegram Bot API. Library ini memudahkan pengembangan bot Telegram dengan Python dengan menyediakan interface yang jelas dan dokumentasi yang komprehensif. Library ini mendukung semua fitur Telegram Bot API dan memiliki arsitektur yang extensible.

Fitur utama Python-Telegram-Bot:

- Handler berbasis class untuk mengelola perintah dan pesan
- Sistem callback untuk tombol inline
- Dukungan untuk webhook dan long polling
- Job queue untuk tugas terjadwal
- Error handling yang komprehensif

### 2.3 Google Gemini API

Google Gemini adalah model AI multimodal dari Google yang dirilis pada akhir 2023. Model ini mampu memahami dan menghasilkan teks, kode, gambar, dan video. Gemini memiliki tiga varian: Gemini Ultra, Gemini Pro, dan Gemini Nano, dengan kemampuan yang berbeda-beda.

Dalam proyek Islamic Agent, Gemini API digunakan untuk:

- Menjawab pertanyaan kompleks tentang Islam
- Menginterpretasikan kueri pengguna untuk pencarian Al-Quran
- Memberikan respons yang kontekstual dan informatif
- Menerapkan proses berpikir sekuensial untuk jawaban yang mendalam

### 2.4 API Kementerian Agama

API Kementerian Agama Republik Indonesia menyediakan berbagai layanan data keagamaan, termasuk jadwal sholat untuk seluruh kota di Indonesia. API ini merupakan sumber resmi dan terpercaya untuk informasi keagamaan di Indonesia.

Fitur API Kementerian Agama yang digunakan dalam proyek:

- Jadwal waktu sholat berdasarkan kota di Indonesia
- Pencarian kota berdasarkan nama atau ID kota
- Format data yang terstruktur dan mudah diintegrasikan

<div style="page-break-after: always;"></div>

## 3. METODOLOGI

### 3.1 Analisis Kebutuhan

Dalam tahap analisis kebutuhan, kami melakukan survei dan wawancara terhadap calon pengguna untuk mengidentifikasi fitur-fitur yang dibutuhkan dalam sebuah asisten virtual Islami. Berdasarkan hasil analisis, kebutuhan utama yang teridentifikasi meliputi:

1. **Kebutuhan Fungsional**:

   - Informasi jadwal sholat yang akurat berdasarkan lokasi
   - Akses ke ayat-ayat Al-Quran dengan terjemahan
   - Pencarian ayat Al-Quran berdasarkan kata kunci
   - Daftar doa-doa sehari-hari dengan teks Arab dan terjemahan
   - Informasi kalender Hijriah dan hari-hari penting Islam
   - Fitur tanya jawab tentang Islam menggunakan AI
   - Sistem berlangganan untuk notifikasi waktu sholat dan motivasi harian
   - Kata-kata motivasi Islami

2. **Kebutuhan Non-Fungsional**:
   - Respons cepat (kurang dari 3 detik)
   - Ketersediaan 24/7
   - Keamanan data pengguna
   - Antarmuka pengguna yang intuitif
   - Skalabilitas untuk menangani banyak pengguna

### 3.2 Perancangan Sistem

Perancangan sistem Islamic Agent menggunakan pendekatan modular untuk memudahkan pengembangan dan pemeliharaan. Sistem diorganisir dalam beberapa komponen utama:

1. **Handler Perintah**: Menangani semua perintah pengguna dan mengarahkannya ke layanan yang sesuai
2. **Layanan**: Modul-modul yang menyediakan fungsionalitas spesifik seperti jadwal sholat, Al-Quran, dll
3. **Database**: Menyimpan data pengguna dan preferensi berlangganan
4. **Scheduler**: Mengelola notifikasi dan pesan terjadwal

Arsitektur ini memungkinkan pengembangan yang bertahap dan memudahkan penambahan fitur baru di masa depan.

### 3.3 Implementasi

Implementasi Islamic Agent menggunakan Python sebagai bahasa pemrograman utama dengan library Python-Telegram-Bot untuk mengintegrasikan dengan platform Telegram. Sistem dikembangkan dengan beberapa modul utama:

1. **Modul Main**: Entry point aplikasi yang mengatur inisialisasi bot dan registrasi handler
2. **Modul Handler**: Menangani perintah dan pesan yang masuk dari pengguna
3. **Modul Layanan**: Layanan-layanan spesifik untuk setiap fitur (prayer, quran, dua, quote, calendar, gemini)
4. **Modul Database**: Mengelola operasi database untuk menyimpan data pengguna dan riwayat chat
5. **Modul Scheduler**: Mengelola pengiriman notifikasi terjadwal

Implementasi menggunakan pendekatan asynchronous dengan library aiohttp untuk komunikasi dengan API eksternal untuk memastikan performa yang baik.

### 3.4 Pengujian

Pengujian Islamic Agent dilakukan dalam beberapa tahap:

1. **Pengujian Unit**: Menguji setiap modul layanan secara terpisah
2. **Pengujian Integrasi**: Menguji interaksi antar modul
3. **Pengujian Fungsional**: Menguji fitur-fitur bot secara keseluruhan
4. **Pengujian Pengguna**: Meminta feedback dari beberapa pengguna awal

Pengujian dilakukan secara manual dengan mencoba berbagai skenario penggunaan dan memperbaiki bug yang ditemukan.

<div style="page-break-after: always;"></div>

## 4. PERANCANGAN APLIKASI

### 4.1 Arsitektur Sistem

Islamic Agent menggunakan arsitektur berbasis layanan (service-oriented architecture) yang terdiri dari beberapa komponen utama:

1. **Bot Telegram**: Antarmuka untuk berinteraksi dengan pengguna
2. **Handler**: Menangani perintah dan pesan yang masuk
3. **Layanan**: Modul-modul yang menyediakan fungsionalitas spesifik
4. **API Eksternal**: Kementerian Agama API, Google Gemini API
5. **Database**: SQLite untuk penyimpanan data
6. **Scheduler**: Untuk mengirim notifikasi terjadwal

Diagram arsitektur sistem dapat dilihat di bawah ini:

```
+----------------+     +-----------------+     +-------------------+
|                |     |                 |     |                   |
| Pengguna       +---->| Bot Telegram    +---->| Command Handler   |
| (Telegram App) |     | (Python-        |     | (command_         |
|                |<----+ Telegram-Bot)   |<----+ handler.py)       |
+----------------+     +-----------------+     +---------+---------+
                                                         |
                                                         v
+----------------+     +-----------------+     +-------------------+
|                |     |                 |     |                   |
| Database       |<----+ Layanan         |<----+ API Eksternal     |
| (SQLite)       |     | (Services)      |     | (Kemenag,         |
|                |     |                 |     |  Gemini)          |
+----------------+     +-------+---------+     +-------------------+
                               |
                               v
                       +-----------------+
                       |                 |
                       | Scheduler       |
                       | (Notifikasi)    |
                       |                 |
                       +-----------------+
```

### 4.2 Struktur Database

Database Islamic Agent menggunakan SQLite dengan struktur tabel sebagai berikut:

1. **Tabel users**:

   - id (INTEGER, PRIMARY KEY): ID pengguna Telegram
   - first_name (TEXT): Nama depan pengguna
   - last_name (TEXT): Nama belakang pengguna
   - username (TEXT): Username Telegram
   - chat_id (INTEGER): ID chat Telegram
   - created_at (TIMESTAMP): Waktu pembuatan record

2. **Tabel subscriptions**:

   - id (INTEGER, PRIMARY KEY): ID berlangganan
   - user_id (INTEGER, FOREIGN KEY): ID pengguna
   - service_type (TEXT): Jenis layanan (prayer, daily_quote)
   - city (TEXT): Kota (untuk jadwal sholat)
   - country (TEXT): Negara (untuk jadwal sholat)
   - created_at (TIMESTAMP): Waktu berlangganan

3. **Tabel chat_history**:
   - id (INTEGER, PRIMARY KEY): ID percakapan
   - user_id (INTEGER, FOREIGN KEY): ID pengguna
   - message (TEXT): Pesan dari pengguna
   - response (TEXT): Respons dari bot
   - created_at (TIMESTAMP): Waktu percakapan

### 4.3 Diagram Alur

Berikut adalah diagram alur untuk beberapa fitur utama Islamic Agent:

1. **Alur Perintah /sholat**:

   ```
   Mulai → Terima perintah /sholat dengan nama kota → Cari ID kota →
   Ambil jadwal sholat dari API Kemenag → Format respons → Kirim ke pengguna → Selesai
   ```

2. **Alur Perintah /quran**:

   ```
   Mulai → Terima perintah /quran dengan nama/nomor surah → Interpretasi query →
   Ambil data surah → Format respons → Kirim ke pengguna → Selesai
   ```

3. **Alur Berlangganan**:

   ```
   Mulai → Terima perintah /subscribe → Validasi jenis langganan →
   Simpan ke database → Konfirmasi ke pengguna → Selesai
   ```

4. **Alur Pencarian Ayat**:
   ```
   Mulai → Terima perintah /cari_ayat dengan kata kunci → Cari dalam database surah →
   Format hasil pencarian → Kirim ke pengguna → Selesai
   ```

<div style="page-break-after: always;"></div>

## 5. IMPLEMENTASI

### 5.1 Pengembangan Fitur

#### 5.1.1 Fitur Jadwal Sholat

Implementasi fitur jadwal sholat menggunakan API Kementerian Agama RI untuk mendapatkan jadwal yang akurat. Fitur ini memungkinkan pengguna untuk:

- Mendapatkan jadwal sholat harian untuk kota tertentu
- Berlangganan notifikasi waktu sholat

**Potongan kode implementasi PrayerService**:

```python
async def get_prayer_times(self, city, country=None, date=None):
    # Format tanggal untuk API (YYYY-MM-DD)
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Jika input bukan ID (angka), coba cari ID kota
    if not city.isdigit():
        city_id = await self._find_city_id(city)
        if not city_id:
            return {
                'status': 'error',
                'message': f'Kota {city} tidak ditemukan.'
            }

    # Get prayer schedule using Kemenag API
    jadwal_url = f"{self.api_url}/jadwalshalat/jadwal/{city_id}/{date}"
    async with session.get(jadwal_url) as response:
        if response.status == 200:
            data = await response.json()
            # Process and return the data
```

#### 5.1.2 Fitur Al-Quran

Fitur Al-Quran menyediakan akses ke teks Al-Quran dengan terjemahan Indonesia. Implementasi menggunakan data JSON lokal untuk performa yang lebih baik. Fitur ini mencakup:

- Membaca surah berdasarkan nama atau nomor
- Pencarian ayat berdasarkan kata kunci
- Interpretasi query pengguna dengan AI

**Implementasi pencarian ayat**:

```python
async def cari_ayat(self, query):
    results = []
    for surah_number in range(1, 115):
        surah_data = await self.get_surah(surah_number)
        if surah_data['status'] == 'success':
            ayat_dict = surah_data['data']['ayat']
            for ayat_number, ayat in ayat_dict.items():
                if query.lower() in ayat['text'].lower() or query.lower() in ayat['translation'].lower():
                    results.append({
                        'surah_number': surah_number,
                        'surah_name': surah_data['data']['name'],
                        'ayat_number': ayat_number,
                        'text': ayat['text'],
                        'translation': ayat['translation']
                    })

    return {
        'status': 'success' if results else 'not_found',
        'count': len(results),
        'query': query,
        'results': results
    }
```

#### 5.1.3 Fitur Kalender Hijriah

Fitur kalender Hijriah menyediakan informasi tanggal dan bulan dalam kalender Hijriah, serta hari-hari penting dalam Islam. Implementasi ini menggunakan kalkulasi astronomi untuk konversi tanggal yang akurat. Fitur meliputi:

- Melihat tanggal Hijriah saat ini
- Konversi tanggal Masehi ke Hijriah
- Informasi bulan Hijriah
- Daftar hari-hari khusus Islam

#### 5.1.4 Fitur Doa-doa

Fitur doa-doa menyediakan koleksi doa sehari-hari dengan teks Arab, Latin, dan terjemahan Indonesia. Implementasi menggunakan data JSON lokal yang dapat diperbarui secara berkala. Fitur ini memungkinkan pengguna untuk:

- Mendapatkan doa acak
- Mencari doa berdasarkan judul atau kata kunci

#### 5.1.5 Fitur Motivasi Islami

Fitur motivasi Islami menyediakan kata-kata motivasi yang diambil dari Al-Quran dan Hadits. Implementasi menggunakan database lokal yang memuat banyak quote inspiratif. Fitur ini mencakup:

- Mendapatkan motivasi acak
- Berlangganan motivasi harian
- Mendapatkan motivasi untuk hari tertentu

#### 5.1.6 Fitur AI Assistant

Fitur AI Assistant menggunakan Google Gemini API untuk menjawab pertanyaan-pertanyaan seputar Islam. Implementasi ini memanfaatkan teknik sequential thinking untuk menghasilkan jawaban yang mendalam dan akurat. Fitur ini meliputi:

- Menjawab pertanyaan tentang Islam
- Menjelaskan konsep keagamaan
- Konteks percakapan berkelanjutan
- Opsi pencarian internet untuk informasi terkini

### 5.2 Implementasi Database

Database SQLite digunakan untuk menyimpan data pengguna, berlangganan, dan riwayat percakapan. Implementasi database menggunakan modul utils/database.py yang menyediakan fungsi-fungsi untuk:

- Inisialisasi database
- Menyimpan dan mengambil data pengguna
- Mengelola berlangganan
- Menyimpan dan mengambil riwayat chat untuk konteks AI

### 5.3 Implementasi API

Islamic Agent mengintegrasikan beberapa API eksternal:

1. **Telegram Bot API**: Untuk interaksi dengan platform Telegram
2. **Kementerian Agama API**: Untuk jadwal sholat
3. **Google Gemini API**: Untuk kemampuan AI

Implementasi API menggunakan library aiohttp untuk permintaan HTTP asynchronous, yang memungkinkan bot untuk menangani banyak permintaan secara bersamaan tanpa memblokir proses utama.

<div style="page-break-after: always;"></div>

## 6. PENGUJIAN

### 6.1 Metode Pengujian

Pengujian Islamic Agent dilakukan dengan beberapa metode:

1. **Pengujian Unit**: Setiap modul layanan diuji secara terpisah dengan input dan output yang telah ditentukan.
2. **Pengujian Integrasi**: Menguji interaksi antar modul untuk memastikan kompatibilitas dan alur data yang benar.
3. **Pengujian Fungsional**: Menguji setiap fitur bot dari sudut pandang pengguna.
4. **Pengujian Performa**: Memeriksa respons waktu dan penggunaan sumber daya.
5. **Pengujian Pengguna**: Mendapatkan feedback dari grup kecil pengguna awal.

### 6.2 Hasil Pengujian

**Pengujian Fungsional**:

| Fitur                      | Skenario                              | Hasil                               |
| -------------------------- | ------------------------------------- | ----------------------------------- |
| /start                     | Memulai bot                           | ✅ Berhasil                         |
| /help                      | Menampilkan panduan                   | ✅ Berhasil                         |
| /sholat                    | Jadwal sholat tanpa parameter         | ✅ Berhasil (menampilkan instruksi) |
| /sholat [kota]             | Jadwal sholat dengan kota valid       | ✅ Berhasil                         |
| /sholat [kota invalid]     | Jadwal sholat dengan kota tidak valid | ✅ Berhasil (pesan error)           |
| /quran                     | Al-Quran tanpa parameter              | ✅ Berhasil (menampilkan instruksi) |
| /quran [nomor]             | Al-Quran dengan nomor valid           | ✅ Berhasil                         |
| /quran [nama surah]        | Al-Quran dengan nama surah            | ✅ Berhasil                         |
| /cari_ayat [kata kunci]    | Pencarian ayat                        | ✅ Berhasil                         |
| /doa                       | Doa acak                              | ✅ Berhasil                         |
| /doa [judul]               | Doa dengan judul                      | ✅ Berhasil                         |
| /motivasi                  | Motivasi acak                         | ✅ Berhasil                         |
| /motivasi_harian           | Motivasi hari ini                     | ✅ Berhasil                         |
| /kalender                  | Tanggal Hijriah                       | ✅ Berhasil                         |
| /bulan [nomor]             | Informasi bulan Hijriah               | ✅ Berhasil                         |
| /subscribe                 | Berlangganan tanpa parameter          | ✅ Berhasil (menampilkan instruksi) |
| /subscribe sholat [kota]   | Berlangganan jadwal sholat            | ✅ Berhasil                         |
| /subscribe motivasi_harian | Berlangganan motivasi                 | ✅ Berhasil                         |
| /unsubscribe [layanan]     | Berhenti berlangganan                 | ✅ Berhasil                         |
| Tanya jawab                | Pertanyaan tentang Islam              | ✅ Berhasil                         |

### 6.3 Analisis Hasil Pengujian

Berdasarkan hasil pengujian, Islamic Agent berfungsi sesuai dengan spesifikasi yang ditentukan. Semua fitur utama bekerja dengan baik, dengan respons yang cepat dan akurat. Beberapa temuan dari pengujian:

1. **Kelebihan**:

   - Bot merespons dengan cepat untuk perintah dasar
   - Jadwal sholat akurat dan sesuai dengan API Kemenag
   - Fitur Al-Quran bekerja dengan baik dengan berbagai input
   - Fitur AI memberikan jawaban yang informatif dan relevan

2. **Keterbatasan**:

   - Waktu respons AI bisa lebih lama untuk pertanyaan kompleks
   - Beberapa format Markdown kadang tidak tampil dengan benar di Telegram
   - Pencarian ayat bisa ditingkatkan dengan indexing yang lebih baik

3. **Area Perbaikan**:
   - Optimasi penanganan format Markdown
   - Implementasi caching untuk permintaan yang sering diakses
   - Peningkatan kemampuan AI untuk pertanyaan kompleks
   - Penambahan keyboard inline untuk navigasi yang lebih baik

<div style="page-break-after: always;"></div>

## 7. KESIMPULAN DAN SARAN

### 7.1 Kesimpulan

Pengembangan Islamic Agent sebagai bot Telegram telah berhasil mencapai tujuan untuk menyediakan asisten virtual Islami yang komprehensif. Bot ini menyediakan berbagai fitur penting seperti jadwal sholat, akses ke Al-Quran, doa-doa, kalender Hijriah, dan kemampuan AI untuk menjawab pertanyaan-pertanyaan seputar Islam.

Implementasi modular dan arsitektur berbasis layanan memungkinkan pengembangan yang terstruktur dan memudahkan pemeliharaan serta penambahan fitur baru di masa depan. Integrasi dengan API Kementerian Agama memastikan informasi yang akurat, sementara teknologi AI dari Google Gemini meningkatkan kemampuan bot untuk memberikan jawaban yang informatif dan kontekstual.

Islamic Agent menunjukkan bagaimana teknologi dapat dimanfaatkan untuk memudahkan akses ke informasi keagamaan dan membantu umat Muslim dalam menjalankan ibadah sehari-hari. Bot ini juga mendemonstrasikan potensi AI untuk memberikan bantuan dalam konteks keagamaan dengan cara yang bermanfaat dan etis.

### 7.2 Saran

Berdasarkan hasil pengembangan dan pengujian, berikut adalah beberapa saran untuk pengembangan lebih lanjut:

1. **Peningkatan UI/UX**:

   - Implementasi keyboard custom untuk navigasi yang lebih intuitif
   - Penambahan multimedia seperti gambar dan audio
   - Dukungan untuk bahasa daerah Indonesia

2. **Pengembangan Fitur**:

   - Tambahkan fitur audio Al-Quran oleh qari terkenal
   - Implementasi fitur komunitas untuk berbagi pengetahuan
   - Integrasi dengan kalender dan pengingat acara lokal
   - Personalisasi yang lebih lanjut berdasarkan preferensi pengguna

3. **Optimasi Teknis**:

   - Migrasi ke database yang lebih skalabel seperti PostgreSQL
   - Implementasi caching untuk meningkatkan performa
   - Sistem monitoring dan logging yang lebih komprehensif
   - Deployment dengan container untuk skalabilitas yang lebih baik

4. **Jangkauan Pengguna**:
   - Pengembangan versi dalam bahasa Inggris dan bahasa lainnya
   - Integrasi dengan platform messaging lain seperti WhatsApp
   - Kampanye untuk meningkatkan kesadaran dan adopsi

## 8. DAFTAR PUSTAKA

1. Telegram Bot API Documentation. [Online]. Available: https://core.telegram.org/bots/api
2. Python-Telegram-Bot Documentation. [Online]. Available: https://python-telegram-bot.readthedocs.io/
3. Google Gemini API Documentation. [Online]. Available: https://ai.google.dev/docs/gemini_api
4. API Jadwal Sholat Kementerian Agama RI. [Online]. Available: https://bimasislam.kemenag.go.id/
5. API MyQuran. [Online]. Available: https://documenter.getpostman.com/view/841292/2s9YsGittd
6. Gara, A., Ayaida, M. (2018). Telegram Bot API for Smart Applications. _2018 International Conference on Smart Communications in Network Technologies_.
7. Sukmawati, R. (2019). Implementasi Metode Sequential Thinking pada Chatbot Islami. _Jurnal Ilmu Komputer dan Informatika_, 5(2), 45-52.
8. Yusran, M. (2020). Pengembangan Kalender Hijriah Digital Berbasis Astronomi. _Jurnal Teknologi dan Sistem Informasi_, 6(1), 24-32.
9. Fauzi, A., Rahman, T. (2021). Pemanfaatan API untuk Sistem Jadwal Sholat Berbasis Web. _Jurnal Informatika dan Rekayasa Perangkat Lunak_, 3(1), 12-18.

## 9. LAMPIRAN

- Kode Sumber: https://github.com/ridhoarmand/islamic-agent
