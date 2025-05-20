from telegram import Update
from telegram.ext import ContextTypes
from services.prayer_service import PrayerService
from services.quran_service import QuranService
from services.dua_service import DuaService
from services.quote_service import QuoteService
from services.gemini_service import GeminiService
from services.calendar_service import CalendarService
from utils.database import save_user, save_chat_history, get_recent_chat_history, subscribe_to_service, unsubscribe_from_service
import re
import sqlite3
import pytz
from config.config import DATABASE_PATH, TIMEZONE

def sanitize_markdown(text):
    """
    Sanitasi format Markdown agar tidak menyebabkan error parsing.
    Memperbaiki atau menghapus format Markdown yang tidak valid.
    """
    if not text:
        return text
        
    # Perbaiki pasangan tanda Markdown yang tidak lengkap
    # Hitung jumlah tanda markdown
    asterisk_count = text.count('*')
    backtick_count = text.count('`')
    underscore_count = text.count('_')
    
    # Jika jumlah tanda ganjil (tidak berpasangan), hapus tanda terakhir
    if asterisk_count % 2 != 0:
        # Cari posisi tanda asterisk terakhir
        last_asterisk_pos = text.rfind('*')
        if last_asterisk_pos != -1:
            text = text[:last_asterisk_pos] + text[last_asterisk_pos+1:]
    
    if backtick_count % 2 != 0:
        # Cari posisi tanda backtick terakhir
        last_backtick_pos = text.rfind('`')
        if last_backtick_pos != -1:
            text = text[:last_backtick_pos] + text[last_backtick_pos+1:]
    
    if underscore_count % 2 != 0:
        # Cari posisi tanda underscore terakhir
        last_underscore_pos = text.rfind('_')
        if last_underscore_pos != -1:
            text = text[:last_underscore_pos] + text[last_underscore_pos+1:]
    
    # Perbaiki tautan Markdown yang tidak lengkap
    # Format tautan Markdown: [teks](url)
    incomplete_link_pattern = r'\[([^\]]+)\]\([^\)]*$'
    text = re.sub(incomplete_link_pattern, r'\1', text)
    
    return text

# Initialize services
prayer_service = PrayerService()
quran_service = QuranService()
dua_service = DuaService()
quote_service = QuoteService()
gemini_service = GeminiService()
calendar_service = CalendarService()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Save user to database
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    welcome_message = (
        f"✨ Assalamu'alaikum {user.first_name}! 💫\n\n"
        f"🌙 Selamat datang di Islamic Agent, asisten virtual Islami personal Anda! 🕌\n\n"
        f"💖 Saya siap membantu Anda dengan:\n"
        f"🕰️ Jadwal sholat yang akurat\n"
        f"📖 Al-Quran digital dengan terjemahan\n"
        f"🤲 Doa-doa sehari-hari\n"
        f"📅 Informasi kalender Hijriah\n"
        f"💭 Menjawab pertanyaan seputar Islam\n\n"
        f"✨ Ketik */help* untuk melihat semua fitur dan petunjuk lengkap\n\n"
        f"🔸 Fitur Populer: 🔸\n"
        f"🕋 */sholat* [kota] - Jadwal sholat harian\n"
        f"📖 */quran* [surah] - Baca Al-Quran\n"
        f"🤲 */doa* - Doa-doa sehari-hari\n"
        f"📅 */kalender* - Tanggal Hijriah hari ini\n"
        f"💫 */motivasi* - Kata-kata motivasi islami\n\n"
        f"Atau langsung tanyakan apa saja tentang Islam kepada saya! 😊 Saya siap membantu Anda dalam perjalanan spiritual Anda. 💫"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    # Bagian 1: Perintah Dasar dan Jadwal Sholat
    help_text_part1 = (
        "📚 *Panduan Penggunaan Islamic Agent (1/3)*\n\n"
        "🔹 *Perintah Dasar:*\n"
        "/start - Memulai percakapan dengan bot\n"
        "/help - Menampilkan panduan ini\n\n"
        
        "🔹 *Jadwal Sholat:*\n"
        "/sholat [kota/daerah] - Mendapatkan jadwal sholat\n"
        "Contoh: /sholat Jakarta, /sholat 1301 (ID kota), /sholat Cisarua\n"
        "Bot akan cerdas mengenali kota terdekat dari daerah yang Anda sebutkan\n\n"
        
        "🔹 *Kalender Hijriah:*\n"
        "/kalender - Melihat tanggal Hijriah hari ini\n"
        "/bulan [nomor_bulan] [tahun] - Informasi bulan Hijriah\n"
        "Contoh: /bulan 9 untuk bulan Ramadhan\n"
        "/konversi\\_tanggal <tanggal> <bulan> <tahun> - Konversi tanggal Masehi ke Hijriah\n"
        "Contoh: /konversi\\_tanggal 17 8 1945\n"
    )
    
    # Bagian 2: Al-Quran dan Doa - DIPERBARUI
    help_text_part2 = (
        "📚 *Panduan Penggunaan Islamic Agent (2/3)*\n\n"
        "🔹 *Al-Quran:*\n"
        "/quran [nomor/nama surah] - Membaca surah Al-Quran\n"
        "Contoh:\n"
        "- /quran 1 untuk Surah Al-Fatihah\n"
        "- /quran al-fatihah untuk Surah Al-Fatihah\n"
        "- /quran yasin untuk Surah Yasin\n\n"
        "/cari\\_ayat [kata kunci] - Mencari ayat berdasarkan kata kunci\n"
        "Contoh: /cari\\_ayat rahmat\n\n"
        
        "🔹 *Doa-doa:*\n"
        "/doa - Mendapatkan doa acak\n"
        "/doa [judul] - Mencari doa berdasarkan judul\n"
        "Contoh: /doa Doa Sebelum Makan\n\n"
        
        "🔹 *Kata Motivasi:*\n"
        "/motivasi - Mendapatkan kata motivasi islami acak\n"
        "/motivasi\\_harian - Mendapatkan kata motivasi islami hari ini"
    )
      # Bagian 3: Berlangganan dan Tanya Jawab
    help_text_part3 = (
        "📚 *Panduan Penggunaan Islamic Agent (3/3)*\n\n"
        "🔹 *Berlangganan:*\n"
        "/subscribe sholat [kota] - Berlangganan notifikasi jadwal sholat\n"
        "/subscribe motivasi\\_harian - Berlangganan kata motivasi islami harian\n"
        "/unsubscribe [layanan] - Berhenti berlangganan\n"
        "/my\\_subscriptions - Melihat semua langganan aktif Anda\n"
        "/test\\_notifikasi - Menguji sistem notifikasi\n\n"
        
        "🔹 *Tanya Jawab:*\n"
        "Anda juga dapat mengirimkan pertanyaan langsung tentang Islam, dan saya akan mencoba menjawabnya dengan bantuan Gemini AI.\n"
        "Contoh: Apa hukum membaca Al-Quran tanpa wudhu? atau Jelaskan tentang sholat tahajud"
    )
    
    # Kirim semua bagian secara berurutan tanpa menggunakan parse_mode='Markdown' untuk bagian yang bermasalah
    try:
        await update.message.reply_text(help_text_part1, parse_mode='Markdown')
        await update.message.reply_text(help_text_part2, parse_mode='Markdown')
        await update.message.reply_text(help_text_part3, parse_mode='Markdown')
    except Exception as e:
        # Fallback ke format plain text jika terjadi error
        await update.message.reply_text("Maaf, terjadi error saat menampilkan bantuan dengan format Markdown.")
        await update.message.reply_text("Berikut panduan penggunaan Islamic Agent tanpa format khusus:\n\n" + 
                                       help_text_part1.replace('*', '') + "\n\n" +
                                       help_text_part2.replace('*', '') + "\n\n" +
                                       help_text_part3.replace('*', ''))
        print(f"Error saat mengirim pesan bantuan: {str(e)}")

async def sholat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /sholat command to get prayer times."""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Silakan berikan nama kota atau ID kota. Contoh:\n"
            "- `/sholat Jakarta` untuk mencari berdasarkan nama\n"
            "- `/sholat 1301` untuk mencari berdasarkan ID kota\n"
            "- `/sholat Tangerang Selatan` untuk area/daerah\n"
            "\nCatatan: Jadwal sholat hanya tersedia untuk wilayah di Indonesia.", 
            parse_mode='Markdown'
        )
        return
    
    city = ' '.join(args)  # Join all args to handle multi-word city names
    country = "Indonesia"  # API Kemenag hanya untuk Indonesia
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    await update.message.reply_text(f"Mencari jadwal sholat untuk '{city}'...")
    
    # Gunakan gemini_service untuk pencarian kota cerdas
    prayer_data = await prayer_service.get_prayer_times(city, country, gemini_service=gemini_service)
    formatted_prayer_times = prayer_service.format_prayer_times(prayer_data)
    
    await update.message.reply_text(formatted_prayer_times, parse_mode='Markdown')
    
async def quran_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /quran command to get Quranic verses with flexible query interpretation."""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Silakan berikan nama atau nomor surah. Contoh: \n"
            "- `/quran 1` untuk Surah Al-Fatihah\n"
            "- `/quran al-fatihah` untuk Surah Al-Fatihah\n"
            "- `/quran yasin` untuk Surah Yasin\n"
            "- `/quran 36` untuk Surah Yasin", 
            parse_mode='Markdown'
        )
        return
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    user_query = ' '.join(args)
    
    # Berikan feedback bahwa kita sedang memproses
    await update.message.reply_text(f"Menginterpretasikan permintaan dan mencari surah '{user_query}'...")
    
    # Gunakan LLM untuk menginterpretasikan query pengguna
    interpreted_query = await quran_service.interpret_query(user_query)
    
    if interpreted_query["type"] == "number":
        # Jika pengguna mengirim nomor surah
        surah_number = interpreted_query["query"]
        if not 1 <= surah_number <= 114:
            await update.message.reply_text("Nomor surah harus antara 1 dan 114.")
            return
            
        await update.message.reply_text(f"Mengambil Surah ke-{surah_number}...")
        surah_data = await quran_service.get_surah(surah_number)
    else:
        # Jika pengguna mengirim nama surah
        surah_name = interpreted_query["query"]
        await update.message.reply_text(f"Mencari Surah dengan nama '{surah_name}'...")
        surah_data = await quran_service.get_surah_by_name(surah_name)
    
    formatted_surah = quran_service.format_surah(surah_data)
    
    try:
        # Coba kirim dengan sanitasi format Markdown
        sanitized_response = sanitize_markdown(formatted_surah)
        await update.message.reply_text(sanitized_response, parse_mode='Markdown')
    except Exception as e:
        # Jika gagal karena markdown, kirim tanpa format
        await update.message.reply_text(formatted_surah.replace('*', '').replace('_', '').replace('`', ''))
        print(f"Error saat mengirim pesan format surah: {str(e)}")

async def cari_ayat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cari_ayat command to search for verses in the Quran."""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Silakan berikan kata kunci pencarian. Contoh: `/cari_ayat rahmat`", 
            parse_mode='Markdown'
        )
        return
    
    query = ' '.join(args)
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    await update.message.reply_text(f"Mencari ayat dengan kata kunci: '{query}'...")
    
    search_data = await quran_service.cari_ayat(query)
    formatted_results = quran_service.format_search_results(search_data)
    
    try:
        # Coba kirim dengan sanitasi format Markdown
        sanitized_response = sanitize_markdown(formatted_results)
        await update.message.reply_text(sanitized_response, parse_mode='Markdown')
    except Exception as e:
        # Jika gagal karena markdown, kirim tanpa format
        await update.message.reply_text(formatted_results.replace('*', '').replace('_', '').replace('`', ''))
        print(f"Error saat mengirim hasil pencarian ayat: {str(e)}")

async def doa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /doa command to get duas (prayers) with intelligent query interpretation."""
    args = context.args
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    if not args:
        # No arguments, return random dua
        dua = dua_service.get_random_dua()
        formatted_dua = dua_service.format_dua(dua)
        await update.message.reply_text(formatted_dua, parse_mode='Markdown')
        return
        
    # User provided a query, interpret it with LLM
    doa_query = ' '.join(args)
    
    # Berikan feedback bahwa kita sedang memproses
    await update.message.reply_text(f"Menginterpretasikan permintaan dan mencari doa '{doa_query}'...")
    
    # Gunakan LLM untuk menginterpretasikan query doa
    dua = await dua_service.interpret_query(doa_query, gemini_service)
    
    if not dua:
        await update.message.reply_text(
            f"Maaf, doa dengan maksud '{doa_query}' tidak ditemukan. "
            f"Silakan coba dengan kata kunci lain atau ketik /doa untuk mendapatkan doa acak."
        )
        return
    
    formatted_dua = dua_service.format_dua(dua)
    await update.message.reply_text(formatted_dua, parse_mode='Markdown')

async def motivasi_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /motivasi command to get Islamic quotes."""
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    quote = quote_service.get_random_quote()
    formatted_quote = quote_service.format_quote(quote)
    
    await update.message.reply_text(formatted_quote, parse_mode='Markdown')

async def motivasi_harian_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /motivasi_harian command to get the Islamic quote of the day."""
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    quote = quote_service.get_daily_quote()
    formatted_quote = quote_service.format_quote(quote)
    
    await update.message.reply_text(formatted_quote, parse_mode='Markdown')

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /subscribe command to subscribe to services."""
    args = context.args
    user = update.effective_user
    
    if not args:
        await update.message.reply_text(
            "Silakan tentukan layanan yang ingin Anda langganan:\n"
            "/subscribe sholat [kota] - Untuk jadwal sholat\n"
            "/subscribe motivasi_harian - Untuk kata motivasi harian",
            parse_mode='Markdown'
        )
        return
    
    subscription_type = args[0]
    
    # Save user info
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    if subscription_type == "sholat":
        if len(args) < 2:
            await update.message.reply_text(
                "Silakan berikan nama kota atau ID kota. Contoh:\n"
                "- `/subscribe sholat Jakarta` untuk berlangganan jadwal sholat Jakarta\n"
                "- `/subscribe sholat 1301` untuk berlangganan dengan ID kota\n"
                "- `/subscribe sholat Depok Timur` untuk area/daerah\n"
                "\nCatatan: Jadwal sholat hanya tersedia untuk wilayah di Indonesia.", 
                parse_mode='Markdown'
            )
            return
            
        city = ' '.join(args[1:])  # Join all remaining args for multi-word city names
        country = "Indonesia"  # API Kemenag hanya untuk Indonesia
        
        # Verifikasi kota tersedia sebelum mendaftarkan
        try:
            await update.message.reply_text(f"Mencari lokasi '{city}'...")
            
            # Gunakan gemini_service untuk pencarian kota cerdas
            prayer_data = await prayer_service.get_prayer_times(city, country, gemini_service=gemini_service)
            
            if prayer_data['status'] == 'error':
                await update.message.reply_text(
                    f"Maaf, terjadi kesalahan: {prayer_data['message']}\n"
                    f"Silakan coba kota lain atau gunakan ID kota.",
                    parse_mode='Markdown'
                )
                return
                
            # Jika sukses, dapatkan nama kota yang benar dari hasil API
            actual_city = prayer_data['meta']['city']
            
            message = f"✅ Berhasil menemukan lokasi: *{actual_city}, {country}*\n\n"
            
            # Jika menggunakan pencarian cerdas, tampilkan info tambahan
            if 'smart_search' in prayer_data:
                message += f"ℹ️ Anda mencari: *{prayer_data['smart_search']['original_query']}*\n"
                message += f"✅ Ditemukan sebagai: *{actual_city}*\n\n"
            
            # Perbarui atau buat langganan dengan nama kota yang benar dari API
            from utils.database import update_prayer_subscription
            status = update_prayer_subscription(
                user_id=user.id, 
                city=actual_city, 
                country=country, 
                city_id=prayer_data['meta'].get('id', '')  # Simpan juga ID kota untuk API MyQuran
            )
            
            if status == "updated":
                message += f"🔄 Langganan jadwal sholat Anda telah diperbarui ke *{actual_city}*.\n"
            else:
                message += f"🔔 Anda telah berlangganan notifikasi jadwal sholat untuk *{actual_city}*.\n"
            
            message += f"Anda akan menerima pengingat untuk setiap waktu sholat berikutnya setiap jam."
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(
                f"Maaf, terjadi kesalahan saat memverifikasi kota: {str(e)}\n"
                f"Silakan coba lagi nanti atau gunakan kota lain.",
                parse_mode='Markdown'
            )
    
    elif subscription_type == "motivasi_harian":
        subscribe_to_service(user.id, "daily_quote")
        await update.message.reply_text(
            "✅ Anda telah berlangganan kata motivasi islami harian.\n"
            "Anda akan menerima sebuah kata motivasi islami setiap hari.",
            parse_mode='Markdown'
        )
    
    else:
        await update.message.reply_text(
            "Layanan yang Anda pilih tidak tersedia. Layanan yang tersedia:\n"
            "- sholat (jadwal sholat)\n"
            "- motivasi_harian (kata motivasi harian)",
            parse_mode='Markdown'
        )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /unsubscribe command to unsubscribe from services."""
    args = context.args
    user = update.effective_user
    
    if not args:
        await update.message.reply_text(
            "Silakan tentukan layanan yang ingin Anda berhenti langganan:\n"
            "/unsubscribe sholat - Untuk jadwal sholat\n"
            "/unsubscribe motivasi_harian - Untuk kata motivasi harian",
            parse_mode='Markdown'
        )
        return
    
    subscription_type = args[0]
    
    # Save user info
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    if subscription_type == "sholat":
        unsubscribe_from_service(user.id, "prayer")
        await update.message.reply_text(
            f"Anda telah berhenti berlangganan layanan jadwal sholat.",
            parse_mode='Markdown'
        )
    elif subscription_type == "motivasi_harian":
        unsubscribe_from_service(user.id, "daily_quote")
        await update.message.reply_text(
            f"Anda telah berhenti berlangganan layanan motivasi harian.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Layanan yang Anda pilih tidak tersedia. Layanan yang tersedia:\n"
            "- sholat (jadwal sholat)\n"
            "- motivasi_harian (kata motivasi harian)",
            parse_mode='Markdown'
        )
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and provide responses using Gemini."""
    user = update.effective_user
    message_text = update.message.text
    
    # Save user to database
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    # Get recent chat history for context
    chat_history = get_recent_chat_history(user.id)
    
    # Let the user know we're processing their message
    await update.message.reply_text("Sedang berpikir... 🤔")
    
    # Determine if we need to search the internet
    need_search = any(keyword in message_text.lower() for keyword in 
                     ["terbaru", "berita", "info", "informasi", "update"])
    
    # Generate response
    if need_search:
        # Use SERP API to search and answer
        response = await gemini_service.search_and_answer(message_text, chat_history)
    else:
        # Use sequential thinking for normal queries
        response = await gemini_service.sequential_thinking(message_text, chat_history)
    
    # Save the conversation to history
    save_chat_history(user.id, message_text, response)
    
    # Coba kirim respons dengan penanganan error Markdown
    try:
        # Coba kirim dengan sanitasi format Markdown
        sanitized_response = sanitize_markdown(response)
        await update.message.reply_text(sanitized_response, parse_mode='Markdown')
    except Exception as e:
        try:
            # Jika masih gagal, coba kirim teks polos
            plain_response = response.replace('*', '').replace('_', '').replace('`', '')
            await update.message.reply_text(plain_response)
            print(f"Error parsing Markdown: {str(e)}, mengirim dalam format teks polos")
        except Exception as e2:
            # Jika masih gagal juga, potong pesan menjadi bagian yang lebih kecil
            chunks = [response[i:i+3000] for i in range(0, len(response), 3000)]
            for chunk in chunks:
                try:
                    await update.message.reply_text(chunk.replace('*', '').replace('_', '').replace('`', ''))
                except Exception:
                    print(f"Gagal mengirim pesan bahkan setelah dibagi menjadi bagian kecil: {str(e2)}")
                    await update.message.reply_text("Maaf, terjadi kesalahan saat mengirimkan jawaban. Silakan tanyakan lagi dengan cara berbeda.")

async def kalender_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /kalender command to get Hijri date information."""
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    await update.message.reply_text("Mengambil informasi tanggal Hijriah hari ini...")
    
    hijri_data = await calendar_service.get_hijri_date()
    formatted_hijri_date = calendar_service.format_hijri_date(hijri_data)
    
    await update.message.reply_text(formatted_hijri_date, parse_mode='Markdown')

async def hari_islam_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /hari_islam command to get Islamic special days."""
    args = context.args
    year = None
    
    if args:
        try:
            year = int(args[0])
        except ValueError:
            await update.message.reply_text(
                "Format tahun tidak valid. Contoh: `/hari_islam 1445` untuk melihat hari khusus tahun 1445 H", 
                parse_mode='Markdown'
            )
            return
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    year_text = f"tahun {year} H" if year else "tahun ini"
    await update.message.reply_text(f"Mengambil informasi hari-hari khusus Islam untuk {year_text}...")
    
    special_days_data = await calendar_service.get_special_days(year)
    formatted_special_days = calendar_service.format_special_days(special_days_data)
    
    await update.message.reply_text(formatted_special_days, parse_mode='Markdown')

async def bulan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /bulan command to get information about a specific Hijri month."""
    args = context.args
    month = None
    year = None
    
    if args:
        try:
            # Jika pengguna menentukan bulan
            if len(args) >= 1:
                month = int(args[0])
                if not 1 <= month <= 12:
                    await update.message.reply_text("Nomor bulan harus antara 1 dan 12.")
                    return
            
            # Jika pengguna juga menentukan tahun
            if len(args) >= 2:
                year = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "Format tidak valid. Contoh: `/bulan 9` untuk Ramadhan tahun ini, atau `/bulan 9 1445` untuk Ramadhan tahun 1445 H", 
                parse_mode='Markdown'
            )
            return
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    await update.message.reply_text("Mengambil informasi bulan Hijriah...")
    
    monthly_info = await calendar_service.get_hijri_calendar(month, year)
    formatted_monthly_info = calendar_service.format_monthly_info(monthly_info)
    
    await update.message.reply_text(formatted_monthly_info, parse_mode='Markdown')

async def konversi_tanggal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /konversi_tanggal command to convert Gregorian date to Hijri date."""
    args = context.args
    
    # Format: /konversi_tanggal <day> <month> <year>
    if len(args) != 3:
        await update.message.reply_text(
            "Format: `/konversi_tanggal <tanggal> <bulan> <tahun>`\n"
            "Contoh: `/konversi_tanggal 17 8 1945` untuk mengkonversi tanggal 17 Agustus 1945",
            parse_mode='Markdown'
        )
        return
    
    try:
        day = int(args[0])
        month = int(args[1])
        year = int(args[2])
        
        # Validasi tanggal
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            await update.message.reply_text(
                "Tanggal tidak valid. Pastikan tanggal antara 1-31, bulan antara 1-12, dan tahun antara 1900-2100."
            )
            return
            
    except ValueError:
        await update.message.reply_text("Format tidak valid. Gunakan angka untuk tanggal, bulan, dan tahun.")
        return
    
    # Save user info
    user = update.effective_user
    save_user(user.id, user.first_name, user.last_name, user.username, update.effective_chat.id)
    
    await update.message.reply_text(f"Mengkonversi tanggal {day}/{month}/{year} ke kalender Hijriah...")
    
    hijri_data = await calendar_service.convert_to_hijri(day, month, year)
    
    if hijri_data['status'] == 'error':
        await update.message.reply_text(f"Maaf, terjadi kesalahan: {hijri_data['message']}")
        return
    
    data = hijri_data['data']
    
    # Format response
    message = f"📅 *Hasil Konversi Tanggal*\n\n"
    message += f"📌 Masehi: {day}/{month}/{year}\n"
    message += f"🌙 Hijriah: {data['day']} {data['month']['indonesian']} {data['year']} H\n"
    message += f"📆 Hari: {data['weekday']['indonesian']}\n"
    
    # Tambahkan informasi hari spesial jika ada
    if 'is_special_day' in data and data['is_special_day']:
        message += f"\n🌟 *Hari Spesial:* {data['special_day']['name']}\n"
        if 'description' in data['special_day'] and data['special_day']['description']:
            message += f"ℹ️ {data['special_day']['description']}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def toggle_thinking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /toggle_thinking command to enable/disable thinking process display."""
    # Periksa apakah pengguna adalah admin atau memiliki akses khusus
    user = update.effective_user
    # Pemeriksaan sederhana untuk admin berdasarkan user_id
    # Ubah user_id di bawah sesuai dengan user_id admin Anda
    admin_ids = [123456789]  # Ganti dengan ID admin Anda
    
    is_admin = user.id in admin_ids
    
    if not is_admin:
        await update.message.reply_text(
            "Maaf, hanya admin yang dapat menggunakan perintah ini.",
            parse_mode='Markdown'
        )
        return
    
    # Toggle status mode berpikir
    gemini_service.show_thinking = not gemini_service.show_thinking
    
    status = "AKTIF" if gemini_service.show_thinking else "NONAKTIF"
    
    await update.message.reply_text(
        f"Mode proses berpikir sekarang *{status}*.\n\n"
        f"• Status saat ini: *{status}*\n"
        f"• Ketika AKTIF: Bot akan menampilkan proses berpikir dalam jawabannya\n"
        f"• Ketika NONAKTIF: Bot akan memberikan jawaban langsung dan singkat\n\n"
        f"Anda dapat mengaktifkan/menonaktifkan mode ini kapan saja dengan perintah `/toggle_thinking`",
        parse_mode='Markdown'
    )

async def my_subscriptions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan daftar langganan aktif untuk pengguna."""
    user = update.effective_user
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Ambil semua langganan aktif untuk pengguna
    cursor.execute('''
    SELECT subscription_type, city, country, created_at
    FROM subscriptions
    WHERE user_id = ? AND active = 1
    ORDER BY subscription_type
    ''', (user.id,))
    
    subscriptions = cursor.fetchall()
    conn.close()
    
    if not subscriptions:
        await update.message.reply_text(
            "Anda belum berlangganan layanan apapun. Gunakan `/subscribe` untuk mulai berlangganan.",
            parse_mode='Markdown'
        )
        return
    
    message = "🔔 *Langganan Aktif Anda* 🔔\n\n"
    
    for sub in subscriptions:
        sub_type, city, country, created_at = sub
        if sub_type == "prayer":
            message += f"📌 *Jadwal Sholat*\n"
            message += f"📍 Lokasi: *{city}, {country}*\n"
            message += f"⏰ Berlangganan sejak: {created_at} (WIB)\n\n"
        elif sub_type == "daily_quote":
            message += f"📌 *Motivasi Harian*\n"
            message += f"⏰ Berlangganan sejak: {created_at} (WIB)\n\n"
    
    message += "ℹ️ *Cara Mengelola Langganan*\n"
    message += "• `/unsubscribe sholat` - Berhenti langganan jadwal sholat\n"
    message += "• `/unsubscribe motivasi_harian` - Berhenti langganan motivasi harian\n"
    message += "• `/subscribe sholat [kota]` - Ganti lokasi jadwal sholat"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def test_notification_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test notification system by sending a test message."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user info
    save_user(
        user.id, 
        user.first_name,
        user.last_name,
        user.username,
        chat_id
    )
    
    await update.message.reply_text(
        "🧪 *Pengujian Notifikasi*\n\n"
        "Mengirim pesan notifikasi uji untuk memverifikasi bahwa sistem notifikasi berfungsi dengan benar.\n"
        "Tunggu sebentar...",
        parse_mode='Markdown'
    )
    
    # Get the scheduler service
    from services.scheduler_service import SchedulerService
    scheduler = SchedulerService()
    
    # Send test notification
    success = scheduler.test_notification(chat_id)
    
    if success:
        await update.message.reply_text(
            "✅ *Sistem Notifikasi Berfungsi!*\n\n"
            "Pesan notifikasi uji berhasil dikirim. Sistem notifikasi Anda berfungsi dengan benar.\n\n"
            "ℹ️ Ini mengonfirmasi bahwa:\n"
            "• Bot dapat mengirim pesan notifikasi\n"
            "• Koneksi Telegram berfungsi normal\n"
            "• Scheduler aktif dan berjalan",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *Kesalahan Sistem Notifikasi*\n\n"
            "Terjadi masalah saat mengirim notifikasi uji. Silakan periksa log untuk detail lebih lanjut.",
            parse_mode='Markdown'
        )
