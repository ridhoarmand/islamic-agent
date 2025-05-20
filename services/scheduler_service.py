import asyncio
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from services.prayer_service import PrayerService
from services.quote_service import QuoteService
from services.gemini_service import GeminiService
from utils.database import get_subscribers
from utils.notification_tracker import NotificationTracker
from config.config import TELEGRAM_BOT_TOKEN, TIMEZONE, DAILY_QUOTE_TIME, PRAYER_NOTIFICATION_MINUTES

# Setup logging for scheduler service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SchedulerService")

class SchedulerService:
    def __init__(self):
        self.prayer_service = PrayerService()
        self.quote_service = QuoteService()
        self.gemini_service = GeminiService()
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self._stop_event = threading.Event()
        self._thread = None
        
        # For tracking notifications persistently
        self.notification_tracker = NotificationTracker()
        
        # Initialize log directory if it doesn't exist
        import os
        os.makedirs("logs", exist_ok=True)
        
        # Backup in-memory tracking for redundancy (should use DB for persistence)
        self._notified_prayers = {}
        self._quote_sent_date = None
        
        logger.info("SchedulerService initialized with notification tracking")
    
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
                # Get current time with correct timezone
                timezone = pytz.timezone(TIMEZONE)
                now = datetime.now(timezone)
                current_time = now.strftime("%H:%M")
                current_date = now.strftime("%Y-%m-%d")
                
                logger.info(f"Checking prayer schedule for {city}, {country} (User ID: {user_id})")
                
                next_prayer = None
                next_prayer_time = None
                
                # Waktu target notifikasi
                notification_time = now + timedelta(minutes=PRAYER_NOTIFICATION_MINUTES)
                notification_time_str = notification_time.strftime("%H:%M")
                
                # Log waktu dan informasi notifikasi
                logger.debug(f"Current time: {current_time}")
                logger.debug(f"Target notification: {PRAYER_NOTIFICATION_MINUTES} minutes before prayer time")
                
                for prayer, time in prayer_data['data'].items():
                    if prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                        # Untuk setiap waktu sholat, hitung berapa menit lagi waktu tersebut akan tiba
                        prayer_hour, prayer_minute = map(int, time.split(':'))
                        current_hour, current_minute = map(int, current_time.split(':'))
                        
                        total_minutes_current = current_hour * 60 + current_minute
                        total_minutes_prayer = prayer_hour * 60 + prayer_minute
                        
                        minutes_until_prayer = total_minutes_prayer - total_minutes_current
                        
                        # Jika waktunya sudah lewat, lewati
                        if minutes_until_prayer <= 0:
                            continue
                        
                        # Jangkauan waktu notifikasi (1 menit = 60 detik, untuk menghindari notifikasi yang terlewatkan)
                        if (PRAYER_NOTIFICATION_MINUTES - 1) <= minutes_until_prayer <= (PRAYER_NOTIFICATION_MINUTES + 1):
                            # Periksa persistent tracker terlebih dahulu
                            if self.notification_tracker.has_sent_prayer_notification(user_id, prayer, current_date):
                                logger.info(f"DB check: Already sent notification for {prayer} ({time}) today to user {user_id}")
                                continue
                                
                            # Cek juga in-memory cache sebagai backup
                            prayer_key = f"{current_date}_{user_id}_{prayer}_prep"
                            if prayer_key in self._notified_prayers:
                                logger.info(f"Memory check: Already sent notification for {prayer} ({time}) today to user {user_id}")
                                continue
                            
                            # Tandai sholat ini sudah diberi notifikasi (double tracking for safety)
                            self._notified_prayers[prayer_key] = True
                            self.notification_tracker.mark_prayer_notification_sent(user_id, prayer, current_date, subtype='prep')
                            
                            next_prayer = prayer
                            next_prayer_time = time
                            logger.info(f"Sending notification for {prayer} ({time}) - {minutes_until_prayer:.1f} minutes remaining")
                            break  # Langsung pilih waktu sholat ini
                        
                        # Jika belum ada waktu sholat berikutnya yang dipilih, pilih yang paling dekat
                        if next_prayer is None or minutes_until_prayer < (total_minutes_prayer - total_minutes_current):
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
                    
                    message += f"Sekarang pukul {current_time} (WIB)\n"
                    message += f"Waktu sholat {prayer_names[next_prayer]} di {prayer_data['meta']['city']}, {country} adalah pukul {next_prayer_time}\n\n"
                    
                    # Calculate time remaining
                    current_hour, current_minute = map(int, current_time.split(':'))
                    next_hour, next_minute = map(int, next_prayer_time.split(':'))
                    
                    minutes_remaining = (next_hour - current_hour) * 60 + (next_minute - current_minute)
                    
                    # Notifikasi khusus 10 menit sebelum waktu sholat
                    if minutes_remaining <= PRAYER_NOTIFICATION_MINUTES:
                        message += f"🔔 *Waktunya bersiap untuk sholat! Waktu tersisa hanya {minutes_remaining} menit.*"
                    else:
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
                    logger.info(f"Successfully sent prayer notification for {prayer_names[next_prayer]} to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending prayer notification: {str(e)}", exc_info=True)
    async def _send_daily_quote_notification(self, user_id, chat_id):
        """Send daily Islamic quote notification to a user."""
        try:
            quote = self.quote_service.get_daily_quote()
            formatted_quote = self.quote_service.format_quote(quote)
            
            # Send message
            await self.bot.send_message(
                chat_id=chat_id,
                text=f"🌙 *Kata Motivasi Islami Hari Ini*\n\n{formatted_quote}",
                parse_mode='Markdown'
            )
            logger.info(f"Successfully sent daily quote to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending daily quote notification: {str(e)}", exc_info=True)
            return False
    
    def _run_daily_notifications(self):
        """Run daily quote notifications - dipanggil sekali pada jam yang ditentukan setiap hari."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        # Dapatkan waktu saat ini
        timezone = pytz.timezone(TIMEZONE)
        now = datetime.now(timezone)
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        
        logger.info(f"Daily quotes notification check at {current_time}")
        
        # Clean up old notification records
        self.notification_tracker.cleanup_old_records(days=7)
        
        # Get daily quote subscribers
        quote_subscribers = get_subscribers("daily_quote")
        quote_count = len(quote_subscribers)
        
        if quote_count == 0:
            logger.info("No subscribers for daily quotes")
            return
            
        logger.info(f"Sending daily quotes to {quote_count} subscribers")
        
        for subscriber in quote_subscribers:
            user_id = subscriber[0]
            chat_id = subscriber[1]
            
            # Check if we've already sent the quote to this user today
            if self.notification_tracker.has_sent_daily_quote(user_id, current_date):
                logger.info(f"DB check: Already sent daily quote to user {user_id} today")
                continue
                
            # Backup check using in-memory tracking
            if self._quote_sent_date == current_date and user_id in getattr(self, '_quote_sent_users', []):
                logger.info(f"Memory check: Already sent daily quote to user {user_id} today")
                continue
                
            # Send the quote
            success = loop.run_until_complete(self._send_daily_quote_notification(user_id, chat_id))
            
            if success:
                # Mark as sent in both persistent DB and memory
                self.notification_tracker.mark_daily_quote_sent(user_id, current_date)
                self._quote_sent_date = current_date
                
                # Initialize _quote_sent_users if it doesn't exist
                if not hasattr(self, '_quote_sent_users'):
                    self._quote_sent_users = []
                      # Add user to the list of users who got the quote today
                self._quote_sent_users.append(user_id)
    
    def _schedule_prayer_notifications(self):
        """Schedule prayer notifications for all subscribed users."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        # Dapatkan waktu saat ini
        timezone = pytz.timezone(TIMEZONE)
        now = datetime.now(timezone)
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        
        logger.info(f"Scheduling prayer notifications for today ({current_date})")
        
        # Reset notification memory at midnight
        self._notified_prayers = {}
        if hasattr(self, '_quote_sent_users'):
            self._quote_sent_users = []
        
        # Get all prayer subscribers
        prayer_subscribers = get_subscribers("prayer")
        prayer_count = len(prayer_subscribers)
        
        if prayer_count == 0:
            logger.info("No prayer subscribers found")
            return
            
        logger.info(f"Setting up precise prayer notifications for {prayer_count} subscribers")
        
        for subscriber in prayer_subscribers:
            # Handle both legacy format (4 columns) and new format (5 columns with city_id)
            user_id = subscriber[0]
            chat_id = subscriber[1]
            city = subscriber[2]
            country = subscriber[3]
            city_id = subscriber[4] if len(subscriber) >= 5 else None
            
            if not (city and country):
                continue
                
            # Get prayer times for this user's location
            location = city_id if city_id else city
            
            try:
                # Get prayer times
                prayer_data = loop.run_until_complete(self.prayer_service.get_prayer_times(
                    location, 
                    country, 
                    gemini_service=self.gemini_service
                ))
                
                if prayer_data['status'] != 'success':
                    logger.error(f"Failed to get prayer times for {city}, {country}: {prayer_data.get('message', 'Unknown error')}")
                    continue
                
                # Schedule notifications for each prayer time
                self._schedule_user_prayer_notifications(user_id, chat_id, city, country, prayer_data)
                
            except Exception as e:
                logger.error(f"Error scheduling prayer notifications for user {user_id}: {str(e)}", exc_info=True)
    
    def _schedule_user_prayer_notifications(self, user_id, chat_id, city, country, prayer_data):
        """Schedule notifications for a specific user's prayer times."""
        timezone = pytz.timezone(TIMEZONE)
        now = datetime.now(timezone)
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        today_str = now.strftime("%Y-%m-%d")
        
        prayer_names = {
            'Fajr': 'Subuh',
            'Dhuhr': 'Dzuhur',
            'Asr': 'Ashar',
            'Maghrib': 'Maghrib',
            'Isha': 'Isya'
        }
        
        for prayer, prayer_time in prayer_data['data'].items():
            if prayer not in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                continue
                
            # Convert prayer time to datetime
            prayer_hour, prayer_minute = map(int, prayer_time.split(':'))
            
            # Create prayer datetime for today
            prayer_datetime = datetime(
                now.year, now.month, now.day, 
                prayer_hour, prayer_minute, 0, 0, 
                timezone
            )
            
            # 1. Schedule preparation notification (10 minutes before prayer)
            prep_notification_datetime = prayer_datetime - timedelta(minutes=PRAYER_NOTIFICATION_MINUTES)
            
            # If preparation time already passed for today, skip
            if prep_notification_datetime < now:
                logger.info(f"Preparation time for {prayer} ({prayer_time}) has already passed today for user {user_id}")
            else:
                # Check if preparation notification already sent
                if self.notification_tracker.has_sent_prayer_notification(user_id, prayer, current_date, subtype='prep'):
                    logger.info(f"Already sent preparation notification for {prayer} ({prayer_time}) today to user {user_id}")
                else:
                    # Format the preparation notification time
                    prep_notification_time = prep_notification_datetime.strftime("%H:%M")
                    
                    # Schedule preparation notification
                    prep_notification_job = schedule.every().day.at(prep_notification_time).do(
                        self._send_scheduled_prayer_notification,
                        user_id=user_id,
                        chat_id=chat_id,
                        prayer=prayer,
                        prayer_time=prayer_time,
                        city=city,
                        country=country,
                        prayer_data=prayer_data,
                        notification_type='prep'
                    )
                    
                    logger.info(f"Scheduled preparation notification for {prayer_names[prayer]} at {prep_notification_time} for user {user_id}")
            
            # 2. Schedule actual prayer time notification
            # If prayer time already passed for today, skip
            if prayer_datetime < now:
                logger.info(f"Prayer time for {prayer} ({prayer_time}) has already passed today for user {user_id}")
                continue
                
            # Check if actual prayer time notification already sent
            if self.notification_tracker.has_sent_prayer_notification(user_id, prayer, current_date, subtype='actual'):
                logger.info(f"Already sent actual prayer time notification for {prayer} ({prayer_time}) today to user {user_id}")
                continue
            
            # Format the actual prayer time for scheduling
            actual_notification_time = prayer_time
            
            # Schedule actual prayer time notification
            actual_notification_job = schedule.every().day.at(actual_notification_time).do(
                self._send_scheduled_prayer_notification,
                user_id=user_id,
                chat_id=chat_id,
                prayer=prayer,
                prayer_time=prayer_time,
                city=city,
                country=country,
                prayer_data=prayer_data,
                notification_type='actual'
            )
            
            logger.info(f"Scheduled actual prayer time notification for {prayer_names[prayer]} at {actual_notification_time} for user {user_id}")
    
    def _send_scheduled_prayer_notification(self, user_id, chat_id, prayer, prayer_time, city, country, prayer_data, notification_type='prep'):
        """Send a scheduled prayer notification."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        # Dapatkan waktu saat ini
        timezone = pytz.timezone(TIMEZONE)
        now = datetime.now(timezone)
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        
        # Double-check if already sent (belt and suspenders approach)
        if self.notification_tracker.has_sent_prayer_notification(user_id, prayer, current_date, subtype=notification_type):
            logger.info(f"DB check: Already sent {notification_type} notification for {prayer} ({prayer_time}) today to user {user_id}")
            return
            
        # Create unique keys for both notification types
        prayer_key = f"{current_date}_{user_id}_{prayer}_{notification_type}"
        if prayer_key in self._notified_prayers:
            logger.info(f"Memory check: Already sent {notification_type} notification for {prayer} ({prayer_time}) today to user {user_id}")
            return
        
        try:
            # Get prayer names in Indonesian
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
            
            message += f"Sekarang pukul {current_time} (WIB)\n"
            message += f"Waktu sholat {prayer_names[prayer]} di {prayer_data['meta']['city']}, {country} adalah pukul {prayer_time}\n\n"
            
            # Calculate time remaining
            prayer_hour, prayer_minute = map(int, prayer_time.split(':'))
            current_hour, current_minute = map(int, current_time.split(':'))
            
            minutes_remaining = (prayer_hour - current_hour) * 60 + (prayer_minute - current_minute)
            
            # Different message based on notification type
            if notification_type == 'prep':
                # Preparation notification (10 minutes before)
                message += f"🔔 *Waktunya bersiap untuk sholat! Waktu tersisa hanya {minutes_remaining} menit.*"
            else:
                # Actual prayer time notification
                message += f"🕌 *Allahu Akbar! Sudah masuk waktu sholat {prayer_names[prayer]}!*"
            
            # Send notification
            loop.run_until_complete(self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            ))
            
            # Mark as sent in both database and memory
            self.notification_tracker.mark_prayer_notification_sent(user_id, prayer, current_date, subtype=notification_type)
            self._notified_prayers[prayer_key] = True
            
            logger.info(f"Successfully sent {notification_type} notification for {prayer_names[prayer]} to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending scheduled prayer notification: {str(e)}", exc_info=True)
    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        # Get current timezone for scheduling
        timezone = pytz.timezone(TIMEZONE)
        
        # Clear all existing jobs to prevent duplicates on restart
        schedule.clear()
        
        # Schedule daily quote notification to run ONCE at a specific time daily
        schedule.every().day.at(DAILY_QUOTE_TIME).do(self._run_daily_notifications)
        
        # Schedule to update prayer time schedules at midnight each day (00:05)
        schedule.every().day.at("00:05").do(self._schedule_prayer_notifications)
        
        # Schedule nightly cleanup at 1:00 AM - cleans up old notification records
        schedule.every().day.at("01:00").do(lambda: self.notification_tracker.cleanup_old_records(days=7))
        
        logger.info(f"Scheduler configured: Daily quotes at {DAILY_QUOTE_TIME}, Prayer notifications at exactly {PRAYER_NOTIFICATION_MINUTES} minutes before each prayer time and at actual prayer time")
        
        # Immediately run prayer time scheduling on startup
        self._schedule_prayer_notifications()
        
        # Main scheduler loop
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
                time.sleep(5)  # Wait a bit before retrying
    def start(self):
        """Start the scheduler service."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_scheduler)
            self._thread.daemon = True
            self._thread.start()
            logger.info(f"Scheduler service started")
            logger.info(f"- Daily quotes will be sent at: {DAILY_QUOTE_TIME} WIB")
            logger.info(f"- Prayer notifications will be sent: {PRAYER_NOTIFICATION_MINUTES} minutes before each prayer time AND at prayer time")
            return True
        else:
            logger.warning("Scheduler is already running")
            return False
    
    def stop(self):
        """Stop the scheduler service."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=5)  # Wait up to 5 seconds for thread to terminate
            logger.info("Scheduler service stopped")
            return True
        else:
            logger.warning("Scheduler was not running")
            return False
    
    def status(self):
        """Get the scheduler service status."""
        if self._thread and self._thread.is_alive():
            return "running"
        else:
            return "stopped"
    
    def test_notification(self, chat_id):
        """Send a test notification to verify bot can send messages."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        async def send_test():
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="🧪 *Test Notification*\n\nJika Anda menerima pesan ini, berarti notifikasi bot berfungsi dengan benar.",
                    parse_mode='Markdown'
                )
                return True
            except Exception as e:
                logger.error(f"Error sending test notification: {str(e)}", exc_info=True)
                return False
                
        return loop.run_until_complete(send_test())