import aiohttp
import json
import os
from datetime import datetime
from config.config import MYQURAN_API_BASE_URL
from utils.location_finder import LocationFinder
    


class PrayerService:
    def __init__(self):
        self.api_url = MYQURAN_API_BASE_URL
        self.location_finder = LocationFinder()
    
    async def get_prayer_times(self, city, country=None, date=None, gemini_service=None):
        """
        Mendapatkan jadwal sholat untuk kota tertentu menggunakan API MyQuran.
        
        Args:
            city: Nama kota atau ID kota di Indonesia
            country: Tidak digunakan untuk API MyQuran, tetap ada untuk kompatibilitas
            date: Format tanggal opsional (YYYY-MM-DD), default hari ini
            gemini_service: Instance dari GeminiService untuk pencarian kota cerdas
            
        Returns:
            Dictionary berisi jadwal sholat atau pesan kesalahan
        """
        # Format tanggal untuk API (YYYY-MM-DD)
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                # Ubah dari DD-MM-YYYY menjadi YYYY-MM-DD jika perlu
                date_obj = datetime.strptime(date, "%d-%m-%Y")
                date = date_obj.strftime("%Y-%m-%d")
            except:
                # Jika format tanggal tidak sesuai, gunakan hari ini
                date = datetime.now().strftime("%Y-%m-%d")
                
        try:
            # ID kota untuk Jakarta jika tidak ada yang cocok
            default_city_id = "1301" 
            city_id = city
            smart_search_used = False
            original_city_name = city
            reasoning = ""
            internet_search_used = False
            
            # Jika input bukan ID (angka), coba cari ID kota
            if not city.isdigit():
                # Regular direct city search first with internet fallback
                result = self.location_finder.find_city_with_internet_search(city)
                
                if result:
                    city_id, city_name = result
                    # Check if this came from internet search
                    if "cities_temp.json" in str(self.location_finder.search_cache):
                        city_lower = city.lower()
                        if city_lower in self.location_finder.search_cache:
                            internet_search_used = True
                            original_city_name = city
                    
                # If not found and gemini_service is provided, try intelligent search
                elif gemini_service:
                    smart_result = await self.intelligent_city_search(city, gemini_service)
                    if smart_result:
                        city_id = smart_result['id']
                        original_city_name = smart_result['original']
                        smart_search_used = True
                        reasoning = smart_result.get('reasoning', '')
                
                # If still not found, return error
                if not city_id:
                    return {
                        'status': 'error', 
                        'message': f'Kota {city} tidak ditemukan. Gunakan ID kota atau coba nama kota lain di Indonesia.'
                    }
            
            async with aiohttp.ClientSession() as session:
                # Get prayer schedule using MyQuran API
                jadwal_url = f"{self.api_url}/sholat/jadwal/{city_id}/{date}"
                async with session.get(jadwal_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data["status"] and "data" in data:
                            jadwal = data["data"]["jadwal"]
                            kota = data["data"]["lokasi"]
                            daerah = data["data"].get("daerah", "")
                            
                            # Format kota dengan daerah jika tersedia
                            lokasi_lengkap = kota
                            if daerah:
                                lokasi_lengkap = f"{kota}, {daerah}"
                            
                            # Ekstrak waktu sholat
                            result = {
                                'status': 'success',
                                'data': {
                                    'Fajr': jadwal["subuh"],
                                    'Sunrise': jadwal["terbit"],
                                    'Dhuhr': jadwal["dzuhur"],
                                    'Asr': jadwal["ashar"],
                                    'Maghrib': jadwal["maghrib"],
                                    'Isha': jadwal["isya"],
                                    'Imsak': jadwal["imsak"],
                                    'Dhuha': jadwal.get("dhuha", "")  # MyQuran menyediakan waktu Dhuha
                                },
                                'date': jadwal["tanggal"],
                                'meta': {
                                    'city': lokasi_lengkap,
                                    'id': city_id,
                                    'country': "Indonesia",
                                    'timezone': "Asia/Jakarta",
                                }
                            }
                            
                            # Add smart search metadata if used
                            if smart_search_used:
                                result['smart_search'] = {
                                    'original_query': original_city_name,
                                    'interpreted_as': lokasi_lengkap,
                                    'reasoning': reasoning
                                }
                            
                            # Add internet search metadata if used
                            if internet_search_used:
                                result['internet_search'] = {
                                    'original_query': original_city_name,
                                    'found_city': lokasi_lengkap
                                }
                                
                            return result
                        else:
                            return {'status': 'error', 'message': 'Tidak dapat memperoleh jadwal sholat'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error: {str(e)}'}
    
    async def _find_city_id(self, city_name):
        """
        Mencari ID kota berdasarkan nama kota menggunakan API MyQuran
        
        Args:
            city_name: Nama kota yang dicari
            
        Returns:
            ID kota jika ditemukan, None jika tidak ditemukan
        """
        try:
            # Pertama cek di pemetaan area lokal
            area_mapping = await self._check_area_mappings(city_name.lower())
            if area_mapping:
                return area_mapping["id"]
            
            # Variasi nama kota untuk dicoba
            name_variations = [
                city_name,                                # Original
                city_name.upper(),                        # All uppercase
                city_name.title(),                        # Title Case
                city_name.replace(" ", ""),               # No spaces
                f"kota {city_name}",                      # With "kota" prefix
                f"kabupaten {city_name}"                  # With "kabupaten" prefix
            ]
                
            # Coba semua variasi nama kota dengan API
            async with aiohttp.ClientSession() as session:
                for name_variant in name_variations:
                    search_url = f"{self.api_url}/sholat/kota/cari/{name_variant}"
                    try:
                        async with session.get(search_url) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data["status"] and "data" in data and data["data"]:
                                    # Ambil kota pertama yang cocok
                                    return data["data"][0]["id"]
                    except Exception as sub_e:
                        print(f"Error saat mencoba variasi nama '{name_variant}': {str(sub_e)}")
                        # Continue to try other variants
        except Exception as e:
            print(f"Error mencari ID kota: {str(e)}")
        return None
    
    async def intelligent_city_search(self, user_input, gemini_service):
        """
        Menggunakan LLM (Gemini) untuk menginterpretasikan input pengguna dan menemukan kota yang dimaksud.
        Berguna untuk kasus seperti nama daerah yang kurang spesifik, nama daerah lokal, dll.
        
        Args:
            user_input: Input pengguna yang mungkin berisi nama daerah/kota
            gemini_service: Instance dari GeminiService untuk mengakses model bahasa
            
        Returns:
            Dictionary berisi {'id': city_id, 'name': city_name} atau None jika tidak ditemukan
        """
        try:
            # Siapkan prompt untuk LLM
            prompt = f"""
            Saya perlu bantuan untuk menentukan kota di Indonesia berdasarkan nama daerah yang disebutkan oleh pengguna.
            
            Input pengguna: "{user_input}"
            
            Berikan nama kota besar/kabupaten terkait yang terdaftar secara resmi di Indonesia. 
            Misalnya jika pengguna menyebut "Depok" maka itu sudah jelas, tapi jika mereka menyebut "Cijantung" atau "Rawamangun", 
            maka berilah "Jakarta Timur" atau "Jakarta" sebagai kota besarnya.
            
            Beberapa contoh kasus khusus:
            - Jika pengguna menyebut "Purwokerto" atau daerah di Banyumas seperti "Sokaraja", "Patikraja", berikan "Purwokerto"
            - Jika pengguna menyebut nama kelurahan/kecamatan, prioritaskan untuk mencari kota/kabupaten induknya
            - Jika input langsung berupa nama kota utama (seperti Jakarta, Surabaya, Yogyakarta), kembalikan nama tersebut
            - Format nama kota sesuai dengan MyQuran API: gunakan format "KOTA NAMA" untuk kota dan "KAB. NAMA" untuk kabupaten
            - Contoh format MyQuran API: "KOTA KEDIRI", "KAB. KEDIRI", "KOTA JAKARTA TIMUR"
            
            Format jawaban (JSON):
            {{
                "original_input": "input asli pengguna",
                "interpreted_city": "nama kota/kabupaten yang diinterpretasikan",
                "alternatives": ["alternatif 1", "alternatif 2"],
                "reasoning": "penjelasan singkat kenapa memilih kota ini"
            }}
            
            Jawaban harus dalam format JSON YANG VALID dan hanya berikan JSON (tanpa penjelasan lain).
            """
            
            # Gunakan Gemini untuk menginterpretasi kota yang dimaksud
            response = await gemini_service.get_json_response(prompt)
            
            if response and 'interpreted_city' in response:
                interpreted_city = response['interpreted_city']
                
                # Cari ID kota berdasarkan interpretasi LLM
                city_id = await self._find_city_id(interpreted_city)
                
                # Jika interpretasi pertama tidak ditemukan, coba alternatif
                if not city_id and 'alternatives' in response and response['alternatives']:
                    for alt_city in response['alternatives']:
                        city_id = await self._find_city_id(alt_city)
                        if city_id:
                            interpreted_city = alt_city
                            break
                
                if city_id:
                    return {
                        'id': city_id,
                        'name': interpreted_city,
                        'original': user_input,
                        'reasoning': response.get('reasoning', '')
                    }
                
            return None
        
        except Exception as e:
            print(f"Error dalam intelligent_city_search: {str(e)}")
            return None
    
    async def _check_area_mappings(self, area):
        """
        Check if the area exists in local area mappings cache.
        
        Args:
            area: Area/district name to check
            
        Returns:
            Dictionary with city id and name if found, None otherwise
        """
        try:
            import json
            import os
            from config.config import DATABASE_PATH
            
            # Path to mappings file
            mappings_path = os.path.join(os.path.dirname(DATABASE_PATH), "area_mappings.json")
            
            # Check if mappings file exists
            if not os.path.exists(mappings_path):
                return None
                
            # Load mappings file
            with open(mappings_path, "r", encoding="utf-8") as f:
                mappings = json.load(f)
            
            # Check direct mappings
            area_lower = area.lower()
            if area_lower in mappings["mappings"]:
                return mappings["mappings"][area_lower]
            
            # Check if area is part of a region
            for region, districts in mappings["regions"].items():
                if area_lower in districts:
                    return mappings["mappings"][region]
                    
            return None
                
        except Exception as e:
            print(f"Error checking area mappings: {str(e)}")
            return None
    
    def format_prayer_times(self, prayer_data):
        """
        Format jadwal sholat menjadi pesan yang mudah dibaca.
        
        Args:
            prayer_data: Data jadwal sholat dari get_prayer_times
            
        Returns:
            String jadwal sholat yang diformat
        """
        if prayer_data['status'] == 'error':
            return f"Maaf, terjadi kesalahan: {prayer_data['message']}"
        
        data = prayer_data['data']
        meta = prayer_data['meta']
        date = prayer_data['date']
        
        message = f"📅 Jadwal Sholat untuk {meta['city']}, {meta['country']} pada {date}\n\n"
        
        # Jika menggunakan pencarian cerdas, tampilkan info tambahan
        if 'smart_search' in prayer_data:
            smart_data = prayer_data['smart_search']
            message += f"ℹ️ Anda mencari: *{smart_data['original_query']}*\n"
            message += f"✅ Ditemukan sebagai: *{smart_data['interpreted_as']}*\n"
            
            # Tampilkan alasan interpretasi jika ada
            if smart_data.get('reasoning'):
                message += f"💡 Info: {smart_data['reasoning']}\n"
            
            message += "\n"
        
        message += f"🌙 Imsak: {data['Imsak']}\n"
        message += f"🕋 Subuh: {data['Fajr']}\n"
        message += f"🌅 Terbit: {data['Sunrise']}\n"
        
        # Tambahkan waktu Dhuha jika tersedia dari API MyQuran
        if data.get('Dhuha'):
            message += f"☀️ Dhuha: {data['Dhuha']}\n"
            
        message += f"🕌 Dzuhur: {data['Dhuhr']}\n"
        message += f"🌇 Ashar: {data['Asr']}\n"
        message += f"🌆 Maghrib: {data['Maghrib']}\n"
        message += f"🌙 Isya: {data['Isha']}\n\n"
        message += "Semoga Allah SWT memberikan keberkahan waktu Anda. 🤲"
        
        return message