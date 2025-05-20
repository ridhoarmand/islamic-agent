# filepath: d:\Coding\Agent\islamic-agent\utils\notification_tracker.py
import sqlite3
import os
import datetime
import logging
import pytz
from config.config import DATABASE_PATH, TIMEZONE

# Set up logging
logger = logging.getLogger("NotificationTracker")

class NotificationTracker:
    """
    Class to track sent notifications persistently in the database
    to prevent duplicate notifications even if the bot restarts.
    """
    
    def __init__(self):
        """Initialize the notification tracker and ensure table exists."""
        self._init_table()
        self._migrate_schema_if_needed()
        logger.info("NotificationTracker initialized")
    
    def _init_table(self):
        """Create the notification tracking table if it doesn't exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create table for tracking sent notifications
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            notification_type TEXT,  -- 'prayer' or 'daily_quote'
            prayer_name TEXT,        -- Name of prayer (only for prayer notifications)
            notification_date TEXT,  -- YYYY-MM-DD format
            notification_subtype TEXT, -- 'prep' or 'actual' for prayer notifications
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("Notification tracking table initialized.")
    
    def _migrate_schema_if_needed(self):
        """Check if we need to update the schema and perform migrations."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if notification_subtype column exists
        cursor.execute("PRAGMA table_info(notification_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'notification_subtype' not in columns:
            print("Migrating database: Adding notification_subtype column")
            try:
                # Add the missing column with a default value of 'prep' for existing records
                cursor.execute('''
                ALTER TABLE notification_history
                ADD COLUMN notification_subtype TEXT DEFAULT 'prep'
                ''')
                
                conn.commit()
                print("Migration completed successfully")
                
            except Exception as e:
                print(f"Error during migration: {str(e)}")
        
        conn.close()
    
    def has_sent_prayer_notification(self, user_id, prayer_name, date=None, subtype='prep'):
        """
        Check if a prayer notification has already been sent to a user.
        
        Args:
            user_id: User ID
            prayer_name: Name of the prayer (Fajr, Dhuhr, etc.)
            date: Date in YYYY-MM-DD format. If None, uses today.
            subtype: Type of notification ('prep' for preparation 10 min before, 'actual' for actual prayer time)
            
        Returns:
            True if notification was already sent, False otherwise
        """
        if date is None:
            timezone = pytz.timezone(TIMEZONE)
            date = datetime.datetime.now(timezone).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id FROM notification_history 
        WHERE user_id = ? AND notification_type = 'prayer'
        AND prayer_name = ? AND notification_date = ? AND notification_subtype = ?
        ''', (user_id, prayer_name, date, subtype))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def has_sent_daily_quote(self, user_id, date=None):
        """
        Check if daily quote has already been sent to a user.
        
        Args:
            user_id: User ID
            date: Date in YYYY-MM-DD format. If None, uses today.
            
        Returns:
            True if daily quote was already sent today, False otherwise
        """
        if date is None:
            timezone = pytz.timezone(TIMEZONE)
            date = datetime.datetime.now(timezone).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # First, check if the notification_subtype column exists
        cursor.execute("PRAGMA table_info(notification_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'notification_subtype' in columns:
            cursor.execute('''
            SELECT id FROM notification_history 
            WHERE user_id = ? AND notification_type = 'daily_quote'
            AND notification_date = ?
            ''', (user_id, date))
        else:
            # Fallback for old schema
            cursor.execute('''
            SELECT id FROM notification_history 
            WHERE user_id = ? AND notification_type = 'daily_quote'
            AND notification_date = ?
            ''', (user_id, date))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def mark_prayer_notification_sent(self, user_id, prayer_name, date=None, subtype='prep'):
        """
        Mark a prayer notification as sent.
        
        Args:
            user_id: User ID
            prayer_name: Name of the prayer (Fajr, Dhuhr, etc.)
            date: Date in YYYY-MM-DD format. If None, uses today.
            subtype: Type of notification ('prep' for preparation 10 min before, 'actual' for actual prayer time)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if date is None:
                timezone = pytz.timezone(TIMEZONE)
                date = datetime.datetime.now(timezone).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO notification_history 
            (user_id, notification_type, prayer_name, notification_date, notification_subtype)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, 'prayer', prayer_name, date, subtype))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking prayer notification as sent: {e}")
            return False
    
    def mark_daily_quote_sent(self, user_id, date=None):
        """
        Mark daily quote as sent.
        
        Args:
            user_id: User ID
            date: Date in YYYY-MM-DD format. If None, uses today.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if date is None:
                timezone = pytz.timezone(TIMEZONE)
                date = datetime.datetime.now(timezone).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO notification_history 
            (user_id, notification_type, prayer_name, notification_date, notification_subtype)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, 'daily_quote', None, date, 'daily'))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking daily quote as sent: {e}")
            return False
    
    def cleanup_old_records(self, days=7):
        """
        Clean up notification history older than specified days.
        
        Args:
            days: Number of days to keep in history
            
        Returns:
            Number of records deleted
        """
        try:
            timezone = pytz.timezone(TIMEZONE)
            cutoff_date = (datetime.datetime.now(timezone) - 
                          datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM notification_history 
            WHERE notification_date < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old notification records")
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up old records: {e}")
            return 0
