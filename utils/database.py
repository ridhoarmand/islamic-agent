import sqlite3
import os
from config.config import DATABASE_PATH

# Ensure data directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table for storing user information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        chat_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create subscriptions table for prayer time and daily reminders
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subscription_type TEXT,  -- 'prayer', 'daily_quote'
        city TEXT,
        country TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Create conversation history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def save_user(user_id, first_name, last_name, username, chat_id):
    """Save or update user information."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO users (user_id, first_name, last_name, username, chat_id)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, first_name, last_name, username, chat_id))
    
    conn.commit()
    conn.close()

def save_chat_history(user_id, message, response):
    """Save chat history for a user."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO chat_history (user_id, message, response)
    VALUES (?, ?, ?)
    ''', (user_id, message, response))
    
    conn.commit()
    conn.close()

def get_recent_chat_history(user_id, limit=5):
    """Get recent chat history for a user."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT message, response FROM chat_history
    WHERE user_id = ?
    ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    
    history = cursor.fetchall()
    conn.close()
    
    return history

def subscribe_to_service(user_id, subscription_type, city=None, country=None):
    """Subscribe a user to a service (prayer times or daily quotes)."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO subscriptions (user_id, subscription_type, city, country)
    VALUES (?, ?, ?, ?)
    ''', (user_id, subscription_type, city, country))
    
    conn.commit()
    conn.close()

def unsubscribe_from_service(user_id, subscription_type):
    """Unsubscribe a user from a service."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE subscriptions 
    SET active = 0
    WHERE user_id = ? AND subscription_type = ?
    ''', (user_id, subscription_type))
    
    conn.commit()
    conn.close()

def get_subscribers(subscription_type):
    """Get all active subscribers for a specific service."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT u.user_id, u.chat_id, s.city, s.country
    FROM subscriptions s
    JOIN users u ON s.user_id = u.user_id
    WHERE s.subscription_type = ? AND s.active = 1
    ''', (subscription_type,))
    
    subscribers = cursor.fetchall()
    conn.close()
    
    return subscribers