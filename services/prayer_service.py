import aiohttp
from datetime import datetime
from config.config import KEMENAG_API_BASE_URL

class PrayerService:
    def __init__(self):
        self.api_url = KEMENAG_API_BASE_URL
    
    async def get_prayer_times(self, city, country=None, date=None):
        """
        Mendapatkan jadwal sholat untuk kota tertentu menggunakan API Kemenag.
        
        Args:
            city: Nama kota atau ID kota di Indonesia
            country: Tidak digunakan untuk API Kemenag, tetap ada untuk kompatibilitas
            date: Format tanggal opsional (YYYY-MM-DD), default hari ini
            
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
            
            # Jika input bukan ID (angka), coba cari ID kota
            if not city.isdigit():
                city_id = await self._find_city_id(city)
                if not city_id:
                    return {
                        'status': 'error', 
                        'message': f'Kota {city} tidak ditemukan. Gunakan ID kota atau coba nama kota lain di Indonesia.'
                    }
            
            async with aiohttp.ClientSession() as session:
                # Get prayer schedule using Kemenag API
                jadwal_url = f"{self.api_url}/jadwalshalat/jadwal/{city_id}/{date}"
                async with session.get(jadwal_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "data" in data and data["data"]:
                            jadwal = data["data"]["jadwal"]
                            kota = data["data"]["lokasi"]
                            
                            # Ekstrak waktu sholat
                            return {
                                'status': 'success',
                                'data': {
                                    'Fajr': jadwal["subuh"],
                                    'Sunrise': jadwal["terbit"],
                                    'Dhuhr': jadwal["dzuhur"],
                                    'Asr': jadwal["ashar"],
                                    'Maghrib': jadwal["maghrib"],
                                    'Isha': jadwal["isya"],
                                    'Imsak': jadwal["imsak"],
                                },
                                'date': jadwal["tanggal"],
                                'meta': {
                                    'city': kota,
                                    'country': "Indonesia",
                                    'timezone': "Asia/Jakarta",
                                }
                            }
                        else:
                            return {'status': 'error', 'message': 'Tidak dapat memperoleh jadwal sholat'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error: {str(e)}'}
    
    async def _find_city_id(self, city_name):
        """
        Mencari ID kota berdasarkan nama kota menggunakan API Kemenag
        
        Args:
            city_name: Nama kota yang dicari
            
        Returns:
            ID kota jika ditemukan, None jika tidak ditemukan
        """
        try:
            async with aiohttp.ClientSession() as session:
                search_url = f"{self.api_url}/kota/cari/{city_name}"
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and data["data"]:
                            # Ambil kota pertama yang cocok
                            return data["data"][0]["id"]
        except Exception as e:
            print(f"Error mencari ID kota: {str(e)}")
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
        message += f"🌙 Imsak: {data['Imsak']}\n"
        message += f"🕋 Subuh: {data['Fajr']}\n"
        message += f"🌅 Terbit: {data['Sunrise']}\n"
        message += f"☀️ Dzuhur: {data['Dhuhr']}\n"
        message += f"🌇 Ashar: {data['Asr']}\n"
        message += f"🌆 Maghrib: {data['Maghrib']}\n"
        message += f"🌙 Isya: {data['Isha']}\n\n"
        message += "Semoga Allah SWT memberikan keberkahan waktu Anda. 🤲"
        
        return message