import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)  # Force reload environment variables

# Telegram Bot Configuration
# Directly set token here to bypass any caching issues
TELEGRAM_BOT_TOKEN = "2040568599:AAHy_pDH_CQU8kA1iWTFz9FMUkMboeIPyxk"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# SERP API Configuration
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Database Configuration
DATABASE_PATH = "data/islamic_agent.db"

# Prayer API Configuration
MYQURAN_API_BASE_URL = "https://api.myquran.com/v2"

# Muslim API Configuration for Calendar
MUSLIM_API_BASE_URL = "https://api.muslimgo.id/v1"

# Legacy API Configuration (no longer used)
# KEMENAG_API_BASE_URL = "https://api.kemenag.go.id/v1"

# Bot Response Configuration
SHOW_THINKING_PROCESS = False  # Set to True untuk menampilkan proses berpikir, False untuk jawaban langsung

# App Configuration
DEBUG = False