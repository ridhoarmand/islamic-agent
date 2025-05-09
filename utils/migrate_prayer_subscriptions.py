#!/usr/bin/env python3
# Database migration script for prayer subscriptions to use MyQuran API

import asyncio
import sqlite3
import aiohttp
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DATABASE_PATH, MYQURAN_API_BASE_URL

async def fetch_city_id(city_name):
    """
    Fetch city ID from MyQuran API
    
    Args:
        city_name: Name of the city to search for
        
    Returns:
        Dictionary with city ID and name if found, None otherwise
    """
    api_url = f"{MYQURAN_API_BASE_URL}/sholat/kota/cari/"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}{city_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] and data["data"]:
                        # Return the first matching city
                        return {
                            "id": data["data"][0]["id"],
                            "name": data["data"][0]["lokasi"]
                        }
    except Exception as e:
        print(f"Error fetching city ID for {city_name}: {str(e)}")
    
    return None

async def migrate_database():
    """
    Migrate prayer subscriptions to use MyQuran API city IDs
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if city_id column exists
    cursor.execute("PRAGMA table_info(subscriptions)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Add city_id column if it doesn't exist
    if 'city_id' not in column_names:
        cursor.execute('ALTER TABLE subscriptions ADD COLUMN city_id TEXT')
        conn.commit()
        print("Added city_id column to subscriptions table")
    
    # Get all prayer subscriptions that don't have a city_id
    cursor.execute('''
    SELECT id, city FROM subscriptions 
    WHERE subscription_type = 'prayer' AND active = 1 AND (city_id IS NULL OR city_id = '')
    ''')
    
    subscriptions = cursor.fetchall()
    print(f"Found {len(subscriptions)} prayer subscriptions to update")
    
    updated_count = 0
    for sub_id, city in subscriptions:
        print(f"Updating subscription {sub_id} for city {city}...")
        
        # Fetch city ID from MyQuran API
        city_data = await fetch_city_id(city)
        if city_data:
            # Update subscription with city ID
            cursor.execute('''
            UPDATE subscriptions SET city_id = ?, city = ? WHERE id = ?
            ''', (city_data["id"], city_data["name"], sub_id))
            
            print(f"  ✅ Updated to {city_data['name']} (ID: {city_data['id']})")
            updated_count += 1
        else:
            print(f"  ❌ Could not find city ID for {city}")
    
    conn.commit()
    conn.close()
    
    print(f"Migration complete: Updated {updated_count} out of {len(subscriptions)} subscriptions")

if __name__ == "__main__":
    asyncio.run(migrate_database())
