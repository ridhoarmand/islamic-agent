import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.config import TELEGRAM_BOT_TOKEN
from handlers.command_handler import (
    start_command, help_command, sholat_command, quran_command, cari_ayat_command,
    doa_command, motivasi_command, motivasi_harian_command, subscribe_command, unsubscribe_command,
    kalender_command, bulan_command, konversi_tanggal_command, hijriyah_command,
    toggle_thinking_command, my_subscriptions_command, test_notification_command, handle_message
)
from services.scheduler_service import SchedulerService
from utils.database import init_db

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Reduce unnecessary logging from httpx (removes "getUpdates HTTP OK" messages)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    """Start the bot."""
    # Initialize the database
    init_db()
    
    # Create the Application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sholat", sholat_command))
    application.add_handler(CommandHandler("quran", quran_command))    
    application.add_handler(CommandHandler("cari_ayat", cari_ayat_command))
    # Tetap dukung command lama untuk backward compatibility
    application.add_handler(CommandHandler("search_quran", cari_ayat_command))
    application.add_handler(CommandHandler("doa", doa_command))
    application.add_handler(CommandHandler("motivasi", motivasi_command))
    application.add_handler(CommandHandler("motivasi_harian", motivasi_harian_command))
    application.add_handler(CommandHandler("kalender", kalender_command))
    # Removed hari_islam command handler as requested
    # Tambahkan command hijriyah yang cerdas menggantikan bulan dan konversi_tanggal
    application.add_handler(CommandHandler("hijriyah", hijriyah_command))
    # Tetap dukung command lama untuk backward compatibility
    application.add_handler(CommandHandler("bulan", hijriyah_command))
    application.add_handler(CommandHandler("konversi_tanggal", hijriyah_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("my_subscriptions", my_subscriptions_command))
    application.add_handler(CommandHandler("toggle_thinking", toggle_thinking_command))
    application.add_handler(CommandHandler("test_notifikasi", test_notification_command))
    
    # Register message handler for chat with Gemini LLM
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the scheduler for notifications
    scheduler = SchedulerService()
    scheduler.start()
    
    # Start the Bot
    logger.info("Starting Islamic Agent bot...")
    application.run_polling()
    
    # Stop the scheduler when the bot stops
    scheduler.stop()

if __name__ == '__main__':
    main()
