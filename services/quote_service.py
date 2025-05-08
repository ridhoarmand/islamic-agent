import json
import os
import random
from pathlib import Path
from datetime import datetime

class QuoteService:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.quotes_dir = self.base_dir / "data" / "quotes"
        
        # Create quotes directory if it doesn't exist
        os.makedirs(self.quotes_dir, exist_ok=True)
        
        # Initialize with some Islamic quotes
        self._initialize_quotes()
        
    def _initialize_quotes(self):
        """Initialize the quotes data file if it doesn't exist."""
        quotes_file = self.quotes_dir / "islamic_quotes.json"
        
        if not os.path.exists(quotes_file):
            # Sample quotes to start with
            initial_quotes = [
                {
                    "quote": "Sesungguhnya sholatku, ibadahku, hidupku dan matiku hanyalah untuk Allah, Tuhan semesta alam.",
                    "source": "Al-Quran, Al-An'am: 162"
                },
                {
                    "quote": "Barangsiapa bertakwa kepada Allah niscaya Dia akan mengadakan baginya jalan keluar. Dan memberinya rezeki dari arah yang tiada disangka-sangka.",
                    "source": "Al-Quran, At-Talaq: 2-3"
                },
                {
                    "quote": "Allah tidak membebani seseorang melainkan sesuai dengan kesanggupannya.",
                    "source": "Al-Quran, Al-Baqarah: 286"
                },
                {
                    "quote": "Sesungguhnya bersama kesulitan ada kemudahan.",
                    "source": "Al-Quran, Al-Insyirah: 6"
                },
                {
                    "quote": "Karena sesungguhnya sesudah kesulitan itu ada kemudahan.",
                    "source": "Al-Quran, Al-Insyirah: 5"
                },
                {
                    "quote": "Dan janganlah kamu berputus asa dari rahmat Allah. Sesungguhnya tiada berputus asa dari rahmat Allah, melainkan kaum yang kafir.",
                    "source": "Al-Quran, Yusuf: 87"
                },
                {
                    "quote": "Barangsiapa merintis jalan mencari ilmu maka Allah akan memudahkan baginya jalan ke surga.",
                    "source": "HR. Muslim"
                },
                {
                    "quote": "Sebaik-baik manusia adalah yang paling bermanfaat bagi manusia lain.",
                    "source": "HR. Ahmad"
                },
                {
                    "quote": "Kebersihan itu sebagian dari iman.",
                    "source": "HR. Muslim"
                },
                {
                    "quote": "Senyum di hadapan saudaramu adalah sedekah.",
                    "source": "HR. Tirmidzi"
                }
            ]
            
            with open(quotes_file, "w", encoding="utf-8") as f:
                json.dump(initial_quotes, f, ensure_ascii=False, indent=2)
                
    def get_random_quote(self):
        """
        Get a random Islamic quote.
        
        Returns:
            Dictionary with a random quote or None if error
        """
        quotes_file = self.quotes_dir / "islamic_quotes.json"
        
        try:
            with open(quotes_file, "r", encoding="utf-8") as f:
                quotes = json.load(f)
                
            if quotes:
                return random.choice(quotes)
            else:
                return None
        except Exception as e:
            print(f"Error getting random quote: {e}")
            return None
            
    def get_daily_quote(self):
        """
        Get the daily Islamic quote (same quote for the whole day).
        
        Returns:
            Dictionary with the daily quote
        """
        quotes_file = self.quotes_dir / "islamic_quotes.json"
        
        try:
            with open(quotes_file, "r", encoding="utf-8") as f:
                quotes = json.load(f)
                
            if not quotes:
                return None
                
            # Use the day of the year to pick a quote, so it changes daily but remains
            # consistent throughout the day
            day_of_year = datetime.now().timetuple().tm_yday
            index = day_of_year % len(quotes)
            
            return quotes[index]
        except Exception as e:
            print(f"Error getting daily quote: {e}")
            return None
    
    def format_quote(self, quote):
        """Format a quote for display in Telegram message."""
        if not quote:
            return "Maaf, kata motivasi tidak tersedia saat ini."
            
        message = f"✨ *Kata Motivasi Islami*\n\n"
        message += f"\"{quote['quote']}\"\n\n"
        message += f"— _{quote['source']}_"
        
        return message
        
    def add_quote(self, quote_text, source):
        """
        Add a new quote to the collection.
        
        Args:
            quote_text: The quote text
            source: The source of the quote
            
        Returns:
            Boolean indicating success or failure
        """
        quotes_file = self.quotes_dir / "islamic_quotes.json"
        
        try:
            with open(quotes_file, "r", encoding="utf-8") as f:
                quotes = json.load(f)
                
            # Add new quote
            quotes.append({
                "quote": quote_text,
                "source": source
            })
            
            with open(quotes_file, "w", encoding="utf-8") as f:
                json.dump(quotes, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Error adding quote: {e}")
            return False