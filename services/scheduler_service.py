import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from telegram import Bot
from services.prayer_service import PrayerService
from services.quote_service import QuoteService
from services.gemini_service import GeminiService
from utils.database import get_subscribers
from config.config import TELEGRAM_BOT_TOKEN

class SchedulerService:
    def __init__(self):
        self.prayer_service = PrayerService()
        self.quote_service = QuoteService()
        self.gemini_service = GeminiService()
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self._stop_event = threading.Event()
        self._thread = None
    
    async def _send_prayer_notification(self, user_id, chat_id, city, country, city_id=None):
        """Send prayer time notification to a user."""
        try:
            # Use city_id if available (from MyQuran API), otherwise use city name
            location = city_id if city_id else city
            
            # Gunakan gemini_service untuk pencarian kota cerdas
            prayer_data = await self.prayer_service.get_prayer_times(
                location, 
                country, 
                gemini_service=self.gemini_service
            )
            
            if prayer_data['status'] == 'success':
                # Format message with only the next prayer time
                current_time = datetime.now().strftime("%H:%M")
                next_prayer = None
                next_prayer_time = None
                
                for prayer, time in prayer_data['data'].items():
                    if prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                        if time > current_time and (next_prayer_time is None or time < next_prayer_time):
                            next_prayer = prayer
                            next_prayer_time = time
                
                if next_prayer:
                    prayer_names = {
                        'Fajr': 'Subuh',
                        'Dhuhr': 'Dzuhur',
                        'Asr': 'Ashar',
                        'Maghrib': 'Maghrib',
                        'Isha': 'Isya'
                    }
                    
                    message = f"⏰ *Pengingat Waktu Sholat*\n\n"
                    
                    # Jika penggunaan pencarian cerdas mengganti kota, berikan informasi
                    if 'smart_search' in prayer_data:
                        actual_city = prayer_data['meta']['city']
                        original_query = prayer_data['smart_search']['original_query']
                        message += f"ℹ️ Lokasi langganan Anda: *{original_query}*\n"
                        message += f"✅ Terjadwal untuk: *{actual_city}*\n\n"
                    
                    message += f"Sekarang pukul {current_time}\n"
                    message += f"Waktu sholat {prayer_names[next_prayer]} di {prayer_data['meta']['city']}, {country} adalah pukul {next_prayer_time}\n\n"
                    
                    # Calculate time remaining
                    current_hour, current_minute = map(int, current_time.split(':'))
                    next_hour, next_minute = map(int, next_prayer_time.split(':'))
                    
                    minutes_remaining = (next_hour - current_hour) * 60 + (next_minute - current_minute)
                    hours = minutes_remaining // 60
                    minutes = minutes_remaining % 60
                    
                    if hours > 0:
                        message += f"Waktu tersisa: {hours} jam {minutes} menit"
                    else:
                        message += f"Waktu tersisa: {minutes} menit"
                    
                    # Send notification
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
        except Exception as e:
            print(f"Error sending prayer notification: {str(e)}")
    
    async def _send_daily_quote_notification(self, user_id, chat_id):
        """Send daily Islamic quote notification to a user."""
        try:
            quote = self.quote_service.get_daily_quote()
            formatted_quote = self.quote_service.format_quote(quote)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=f"🌙 *Kata Motivasi Islami Hari Ini*\n\n{formatted_quote}",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error sending daily quote notification: {str(e)}")
    
    def _run_daily_notifications(self):
        """Run daily notifications for quotes and prayer times."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        # Send daily quote notifications at 5:00 AM
        quote_subscribers = get_subscribers("daily_quote")
        for user_id, chat_id, _, _ in quote_subscribers:
            loop.run_until_complete(self._send_daily_quote_notification(user_id, chat_id))
        
        # Check and send prayer time notifications every hour
        prayer_subscribers = get_subscribers("prayer")
        for subscriber in prayer_subscribers:
            # Handle both legacy format (4 columns) and new format (5 columns with city_id)
            user_id = subscriber[0]
            chat_id = subscriber[1]
            city = subscriber[2]
            country = subscriber[3]
            city_id = subscriber[4] if len(subscriber) >= 5 else None
            
            if city and country:
                loop.run_until_complete(self._send_prayer_notification(user_id, chat_id, city, country, city_id))
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        # Schedule daily quote notification at 5:00 AM
        schedule.every().day.at("05:00").do(self._run_daily_notifications)
        
        # Schedule prayer time checks every hour
        schedule.every().hour.do(self._run_daily_notifications)
        
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Start the scheduler service."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_scheduler)
            self._thread.daemon = True
            self._thread.start()
            print("Scheduler service started.")
    
    def stop(self):
        """Stop the scheduler service."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            print("Scheduler service stopped.")
