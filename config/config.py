import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)  # Force reload environment variables

# Telegram Bot Configuration
# Directly set token here to bypass any caching issues
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"  # Model Gemini yang digunakan

# SERP API Configuration
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Database Configuration
DATABASE_PATH = "data/islamic_agent.db"

# Prayer API Configuration
MYQURAN_API_BASE_URL = "https://api.myquran.com/v2"

# Bot Response Configuration
SHOW_THINKING_PROCESS = False  # Set to True untuk menampilkan proses berpikir, False untuk jawaban langsung

# App Configuration
DEBUG = False

# Timezone Configuration
TIMEZONE = 'Asia/Jakarta'  # Zona waktu Indonesia WIB (UTC+7)

# Scheduler Configuration
DAILY_QUOTE_TIME = "08:00"   # Waktu pengiriman motivasi harian (format: "HH:MM")
PRAYER_NOTIFICATION_MINUTES = 10  # Notifikasi dikirim X menit sebelum waktu sholat