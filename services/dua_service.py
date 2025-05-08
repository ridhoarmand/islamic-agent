import json
import os
import random
from pathlib import Path

class DuaService:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.duas_dir = self.base_dir / "data" / "duas"
        
        # Create duas directory if it doesn't exist
        os.makedirs(self.duas_dir, exist_ok=True)
        
        # Initialize with some common short duas
        self._initialize_duas()
        
    def _initialize_duas(self):
        """Initialize the duas data file if it doesn't exist."""
        duas_file = self.duas_dir / "short_duas.json"
        
        if not os.path.exists(duas_file):
            # Sample duas to start with
            initial_duas = [
                {
                    "title": "Doa Sebelum Makan",
                    "arabic": "بِسْمِ اللهِ",
                    "latin": "Bismillah",
                    "translation": "Dengan menyebut nama Allah",
                    "category": "daily"
                },
                {
                    "title": "Doa Setelah Makan",
                    "arabic": "اَلْحَمْدُ لِلّٰهِ الَّذِىْ اَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مِنَ الْمُسْلِمِيْنَ",
                    "latin": "Alhamdulillahil ladzii ath'amanaa wa saqoonaa wa ja'alnaa minal muslimiin",
                    "translation": "Segala puji bagi Allah yang telah memberi makan kami dan minuman kami, serta menjadikan kami sebagai orang-orang islam.",
                    "category": "daily"
                },
                {
                    "title": "Doa Sebelum Tidur",
                    "arabic": "بِسْمِكَ اللّٰهُمَّ اَحْيَا وَاَمُوْتُ",
                    "latin": "Bismikallaahumma ahyaa wa amuutu",
                    "translation": "Dengan nama-Mu ya Allah aku hidup dan aku mati",
                    "category": "daily"
                },
                {
                    "title": "Doa Bangun Tidur",
                    "arabic": "اَلْحَمْدُ لِلّٰهِ الَّذِىْ اَحْيَانَا بَعْدَ مَا اَمَاتَنَا وَاِلَيْهِ النُّشُوْرُ",
                    "latin": "Alhamdulillahil ladzii ahyaanaa ba'da maa amaa tanaa wa ilaihin nusyuur",
                    "translation": "Segala puji bagi Allah yang telah menghidupkan kami setelah mematikan kami, dan kepada-Nya kami dikembalikan.",
                    "category": "daily"
                },
                {
                    "title": "Doa Masuk Masjid",
                    "arabic": "اَللّٰهُمَّ افْتَحْ لِيْ اَبْوَابَ رَحْمَتِكَ",
                    "latin": "Allaahummaf tahlii abwaaba rohmatik",
                    "translation": "Ya Allah, bukalah untukku pintu-pintu rahmat-Mu",
                    "category": "worship"
                },
                {
                    "title": "Doa Keluar Masjid",
                    "arabic": "اَللّٰهُمَّ اِنِّى اَسْأَلُكَ مِنْ فَضْلِكَ",
                    "latin": "Allaahumma innii as-aluka min fadlik",
                    "translation": "Ya Allah, sesungguhnya aku memohon keutamaan dari-Mu",
                    "category": "worship"
                },
                {
                    "title": "Doa Mohon Ilmu Yang Bermanfaat",
                    "arabic": "اَللّٰهُمَّ اِنِّى اَسْأَلُكَ عِلْمًا نَافِعًا وَرِزْقًا طَيِّبًا وَعَمَلاً مُتَقَبَّلاً",
                    "latin": "Allaahumma innii as-aluka 'ilman naafi'an, wa rizqon thoyyiban, wa 'amalan mutaqobbalan",
                    "translation": "Ya Allah, sesungguhnya aku mohon kepada-Mu ilmu yang bermanfaat, rezeki yang baik, dan amalan yang diterima",
                    "category": "knowledge"
                }
            ]
            
            with open(duas_file, "w", encoding="utf-8") as f:
                json.dump(initial_duas, f, ensure_ascii=False, indent=2)
                
    def get_dua_by_title(self, title):
        """
        Get a dua by its title.
        
        Args:
            title: The title of the dua, case insensitive
            
        Returns:
            Dictionary with dua data or None if not found
        """
        duas_file = self.duas_dir / "short_duas.json"
        
        try:
            with open(duas_file, "r", encoding="utf-8") as f:
                duas = json.load(f)
                
            title_lower = title.lower()
            for dua in duas:
                if dua["title"].lower() == title_lower:
                    return dua
            
            return None
        except Exception as e:
            print(f"Error getting dua: {e}")
            return None
            
    def get_dua_by_category(self, category):
        """
        Get all duas in a specific category.
        
        Args:
            category: The category name, case insensitive
            
        Returns:
            List of duas in the category or empty list if none found
        """
        duas_file = self.duas_dir / "short_duas.json"
        
        try:
            with open(duas_file, "r", encoding="utf-8") as f:
                duas = json.load(f)
                
            category_lower = category.lower()
            return [dua for dua in duas if dua["category"].lower() == category_lower]
        except Exception as e:
            print(f"Error getting duas by category: {e}")
            return []
            
    def get_random_dua(self):
        """
        Get a random dua.
        
        Returns:
            Dictionary with a random dua or None if error
        """
        duas_file = self.duas_dir / "short_duas.json"
        
        try:
            with open(duas_file, "r", encoding="utf-8") as f:
                duas = json.load(f)
                
            if duas:
                return random.choice(duas)
            else:
                return None
        except Exception as e:
            print(f"Error getting random dua: {e}")
            return None
    
    def format_dua(self, dua):
        """Format a dua for display in Telegram message."""
        if not dua:
            return "Maaf, doa tidak ditemukan."
            
        message = f"📿 *{dua['title']}*\n\n"
        message += f"*Arab:*\n{dua['arabic']}\n\n"
        message += f"*Latin:*\n{dua['latin']}\n\n"
        message += f"*Arti:*\n{dua['translation']}"
        
        return message
        
    def search_duas(self, keyword):
        """
        Search duas by keyword.
        
        Args:
            keyword: Keyword to search for in title, arabic, latin or translation
            
        Returns:
            List of matching duas
        """
        duas_file = self.duas_dir / "short_duas.json"
        
        try:
            with open(duas_file, "r", encoding="utf-8") as f:
                duas = json.load(f)
                
            keyword_lower = keyword.lower()
            matches = []
            
            for dua in duas:
                if (keyword_lower in dua["title"].lower() or 
                    keyword_lower in dua["latin"].lower() or 
                    keyword_lower in dua["translation"].lower()):
                    matches.append(dua)
                    
            return matches
        except Exception as e:
            print(f"Error searching duas: {e}")
            return []

    async def interpret_query(self, query, gemini_service):
        """
        Use LLM to interpret user's doa query and find the most relevant doa.
        
        Args:
            query: User's query text
            gemini_service: Instance of GeminiService to use for LLM processing
            
        Returns:
            Dictionary with the most relevant doa or None if not found
        """
        try:
            # Get all available duas
            duas_file = self.duas_dir / "short_duas.json"
            with open(duas_file, "r", encoding="utf-8") as f:
                duas = json.load(f)
            
            dua_titles = [dua["title"] for dua in duas]
            
            # Create a prompt for Gemini to understand what doa the user is looking for
            prompt = (
                f"Saya mencari doa dengan query: '{query}'. "
                f"Berikut adalah daftar doa yang tersedia: {dua_titles}. "
                f"Berdasarkan maksud saya, doa mana yang paling relevan dengan permintaan saya? "
                f"Mohon jawab hanya dengan judul doa yang sesuai saja, tanpa penjelasan tambahan."
            )
            
            # Use Gemini to interpret the query
            interpreted_title = await gemini_service.get_simple_response(prompt)
            interpreted_title = interpreted_title.strip()
            
            # Check if the interpreted title matches any doa
            for dua in duas:
                # Exact match
                if dua["title"] == interpreted_title:
                    return dua
                
                # Partial match
                if interpreted_title.lower() in dua["title"].lower():
                    return dua
            
            # If no match found, try to find partial matches in our database
            matches = self.search_duas(query)
            if matches:
                return matches[0]  # Return the first match
                
            return None
        except Exception as e:
            print(f"Error interpreting doa query: {e}")
            return None