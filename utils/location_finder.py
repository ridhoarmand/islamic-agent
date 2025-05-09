import json
import os
import requests
from typing import Optional, Tuple, Dict, Any


class LocationFinder:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.mappings_path = os.path.join(self.script_dir, "..", "data", "area_mappings.json")
        
        try:
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                self.area_data = json.load(f)
            
            self.mappings = self.area_data.get('mappings', {})
            self.regions = self.area_data.get('regions', {})
        except Exception as e:
            print(f"Error loading area_mappings.json: {str(e)}")
            self.mappings = {}
            self.regions = {}
        
        # Cache for online searches
        self.search_cache_path = os.path.join(self.script_dir, "..", "data", "cities_temp.json")
        self.search_cache = self._load_search_cache()
    
    def _load_search_cache(self) -> Dict[str, Any]:
        """Load search cache from file"""
        if os.path.exists(self.search_cache_path):
            try:
                with open(self.search_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_search_cache(self) -> None:
        """Save search cache to file"""
        try:
            with open(self.search_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.search_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving search cache: {e}")
    
    def find_city_with_internet_search(self, city_name: str) -> Optional[Tuple[str, str]]:
        """Find city using local mappings first, then internet search as fallback"""
        # First try local mappings
        city_id = self.find_city_id_local(city_name)
        if city_id:
            return city_id
        
        # Check if we have cached search results
        city_lower = city_name.lower()
        if city_lower in self.search_cache:
            city_data = self.search_cache[city_lower]
            if city_data and "id" in city_data:
                print(f"Found in cache: {city_data['name']} (ID: {city_data['id']})")
                return city_data["id"], city_data["name"]
        
        # If not found in mappings or cache, try internet search
        try:
            city_data = self.search_city_online(city_name)
            if city_data:
                print(f"Found via online search: {city_data['name']} (ID: {city_data['id']})")
                self.search_cache[city_lower] = city_data
                self._save_search_cache()
                return city_data["id"], city_data["name"]
        except Exception as e:
            print(f"Error searching online: {e}")
        
        return None
    
    def find_city_id_local(self, city_name: str) -> Optional[Tuple[str, str]]:
        """Find city ID from local mappings"""
        city_name_lower = city_name.lower()
        
        # Direct city match
        if city_name_lower in self.mappings:
            city_data = self.mappings[city_name_lower]
            print(f"Exact match found: {city_data['name']} (ID: {city_data['id']})")
            return city_data['id'], city_data['name']
        
        # Check if it's in regions
        for city, districts in self.regions.items():
            if city_name_lower in districts:
                city_data = self.mappings[city]
                print(f"District match found: {city_name} is in {city_data['name']} (ID: {city_data['id']})")
                return city_data['id'], city_data['name']
        
        # Fuzzy match - check if the city name is part of any mapping key
        for key, data in self.mappings.items():
            if city_name_lower in key or key in city_name_lower:
                print(f"Fuzzy match found: {data['name']} (ID: {data['id']})")
                return data['id'], data['name']
        
        # Extended fuzzy match - try to match words individually
        words = city_name_lower.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 3:  # Only use words longer than 3 chars to avoid common words
                    for key, data in self.mappings.items():
                        if word in key and word not in ['kota', 'kabupaten', 'kab']:
                            print(f"Word match found: {word} matched with {data['name']} (ID: {data['id']})")
                            return data['id'], data['name']
        
        print(f"City not found locally: {city_name}")
        return None
    
    def search_city_online(self, city_name: str) -> Optional[Dict[str, str]]:
        """Search for city information online using MyQuran API"""
        try:
            # First try to get all cities list from MyQuran API
            response = requests.get("https://api.myquran.com/v2/sholat/kota/semua")
            if response.status_code != 200:
                print(f"Error fetching cities list: {response.status_code}")
                return None
            
            cities = response.json()["data"]
            
            # Find closest match
            city_name_lower = city_name.lower()
            best_match = None
            best_score = 0
            
            for city in cities:
                city_lokasi = city["lokasi"].lower()
                
                # Calculate simple matching score
                score = 0
                
                # Direct match (case insensitive)
                if city_name_lower in city_lokasi or city_lokasi in city_name_lower:
                    score += 10
                
                # Words matching
                words = city_name_lower.split()
                for word in words:
                    if len(word) > 3 and word in city_lokasi:
                        score += 5
                
                # If the score is better than previous best match
                if score > best_score:
                    best_score = score
                    best_match = city
            
            if best_match and best_score > 0:
                return {
                    "id": best_match["id"],
                    "name": best_match["lokasi"]
                }
            
            return None
        
        except Exception as e:
            print(f"Error searching online: {e}")
            return None


def test_location_finder():
    """Test the LocationFinder class with different cities"""
    finder = LocationFinder()
    
    test_cities = [
        "Purwokerto",
        "Banyumas", 
        "Sokaraja",
        "Jakarta",
        "Jakarta Selatan",
        "Cipete",
        "Fatmawati",
        "Yogyakarta",
        "Sleman",
        "Malang",
        "Klojen",
        "Pantai Indah Kapuk",
        "Bandung",
        "Ciumbuleuit",
        "Gresik",
        "Sidoarjo",
        "Madiun",
        "Kebumen",
        "Aceh",
        "Puncak",
        "Pekalongan",
        "Tanjung Pinang",  # Should trigger online search
        "Candi Prambanan",  # Should trigger online search
        "Kota Mungkid",     # Should trigger online search
        "Boyolali",         # Should trigger online search
        "Ngawi"             # Should trigger online search
    ]
    
    print("Testing location finder with online search fallback:")
    for city in test_cities:
        print(f"\nSearching for: {city}")
        result = finder.find_city_with_internet_search(city)
        if result:
            city_id, city_name = result
            print(f"SUCCESS: Found ID {city_id} for {city} ({city_name})")
        else:
            print(f"FAILED: Could not find ID for {city}")


if __name__ == "__main__":
    test_location_finder()
