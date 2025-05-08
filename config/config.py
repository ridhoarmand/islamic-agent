import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# SERP API Configuration
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Database Configuration
DATABASE_PATH = "data/islamic_agent.db"

# Prayer API Configuration - Muslim API v2 by myQuran
MUSLIM_API_BASE_URL = "https://api.myquran.com/v2"

# Kemenag API Configuration
KEMENAG_API_BASE_URL = "https://api.kemenag.go.id/v1"

# Bot Response Configuration
SHOW_THINKING_PROCESS = False  # Set to True untuk menampilkan proses berpikir, False untuk jawaban langsung

# App Configuration
DEBUG = False