import aiohttp
from datetime import datetime
from config.config import MUSLIM_API_BASE_URL

class CalendarService:
    def __init__(self):
        # Gunakan base URL dari myQuran API
        self.api_url = MUSLIM_API_BASE_URL
    
    async def get_hijri_date(self):
        """
        Mendapatkan tanggal Hijriah saat ini
        
        Returns:
            Dictionary berisi informasi tanggal Hijriah
        """
        try:
            # Gunakan endpoint API baru untuk tanggal Hijriah saat ini: /cal/hijr/?adj=-1
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/cal/hijr/?adj=-1") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            return {
                                'status': 'success',
                                'data': data['data']
                            }
                        else:
                            return {'status': 'error', 'message': 'Gagal mendapatkan tanggal Hijriah'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def convert_to_hijri(self, day, month, year):
        """
        Mengkonversi tanggal masehi ke tanggal Hijriah
        
        Args:
            day: Hari (1-31)
            month: Bulan (1-12)
            year: Tahun
            
        Returns:
            Dictionary berisi informasi tanggal Hijriah
        """
        try:
            # Format tanggal yyyy-mm-dd
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            # Gunakan endpoint API baru untuk konversi tanggal: /cal/hijr/:date?adj=-1
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/cal/hijr/{date_str}?adj=-1") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            return {
                                'status': 'success',
                                'data': data['data']
                            }
                        else:
                            return {'status': 'error', 'message': 'Gagal mengkonversi tanggal ke Hijriah'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_current_hijri_date_from_api_data(self, hijri_data):
        """
        Extract hijri date components from API response
        
        Args:
            hijri_data: Data from API
            
        Returns:
            Tuple containing (month, year)
        """
        if hijri_data['status'] == 'error':
            return None, None
            
        # Extract month and year from num array where:
        # num[5] = bulan hijriah (1-12)
        # num[6] = tahun hijriah
        data = hijri_data['data']
        month = data['num'][5]
        year = data['num'][6]
        
        return month, year
    
    async def get_monthly_info(self, year=None):
        """
        Mendapatkan informasi tentang bulan-bulan dalam tahun Hijriah tertentu
        
        Args:
            year: Tahun Hijriah, default tahun saat ini
            
        Returns:
            Dictionary berisi informasi bulan Hijriah
        """
        if year is None:
            today_result = await self.get_hijri_date()
            if today_result['status'] == 'error':
                return today_result
            
            _, year = self.get_current_hijri_date_from_api_data(today_result)
            if year is None:
                return {'status': 'error', 'message': 'Gagal mendapatkan tahun Hijriah saat ini'}
        
        # Karena API tidak menyediakan endpoint untuk daftar bulan,
        # kita gunakan data yang sudah diketahui
        hijri_months = [
            {"number": 1, "arabic": "محرم", "indonesian": "Muharram", "english": "Muharram"},
            {"number": 2, "arabic": "صفر", "indonesian": "Safar", "english": "Safar"},
            {"number": 3, "arabic": "ربيع الأول", "indonesian": "Rabiul Awal", "english": "Rabi al-Awwal"},
            {"number": 4, "arabic": "ربيع الثاني", "indonesian": "Rabiul Akhir", "english": "Rabi al-Thani"},
            {"number": 5, "arabic": "جمادى الأولى", "indonesian": "Jumadil Awal", "english": "Jumada al-Awwal"},
            {"number": 6, "arabic": "جمادى الآخرة", "indonesian": "Jumadil Akhir", "english": "Jumada al-Thani"},
            {"number": 7, "arabic": "رجب", "indonesian": "Rajab", "english": "Rajab"},
            {"number": 8, "arabic": "شعبان", "indonesian": "Syaban", "english": "Shaban"},
            {"number": 9, "arabic": "رمضان", "indonesian": "Ramadan", "english": "Ramadan"},
            {"number": 10, "arabic": "شوال", "indonesian": "Syawal", "english": "Shawwal"},
            {"number": 11, "arabic": "ذو القعدة", "indonesian": "Dzulkaidah", "english": "Dhu al-Qadah"},
            {"number": 12, "arabic": "ذو الحجة", "indonesian": "Dzulhijjah", "english": "Dhu al-Hijjah"}
        ]
        
        return {
            'status': 'success',
            'data': hijri_months,
            'year': year
        }
    
    async def get_hijri_calendar(self, month=None, year=None):
        """
        Mendapatkan informasi bulan Hijriah tertentu
        
        Args:
            month: Bulan Hijriah (1-12), default bulan saat ini
            year: Tahun Hijriah, default tahun saat ini
            
        Returns:
            Dictionary berisi informasi bulan Hijriah
        """
        # Jika bulan atau tahun tidak ditentukan, dapatkan tanggal Hijriah hari ini
        if month is None or year is None:
            today_result = await self.get_hijri_date()
            if today_result['status'] == 'error':
                return today_result
                
            curr_month, curr_year = self.get_current_hijri_date_from_api_data(today_result)
            
            if month is None and curr_month is not None:
                month = curr_month
            elif month is None:
                return {'status': 'error', 'message': 'Gagal mendapatkan bulan Hijriah saat ini'}
                
            if year is None and curr_year is not None:
                year = curr_year
            elif year is None:
                return {'status': 'error', 'message': 'Gagal mendapatkan tahun Hijriah saat ini'}
        
        # Dapatkan informasi bulan dari daftar bulan Hijriah
        try:
            monthly_info = await self.get_monthly_info(year)
            if monthly_info['status'] == 'error':
                return monthly_info
            
            # Filter untuk bulan yang diminta
            month_data = None
            for m in monthly_info['data']:
                if m['number'] == month:
                    month_data = m
                    break
            
            if month_data is None:
                return {'status': 'error', 'message': f'Bulan {month} tidak ditemukan'}
                
            return {
                'status': 'success',
                'data': month_data,
                'month': month,
                'year': year
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def is_special_day(self, day, month, year):
        """
        Memeriksa apakah tanggal tertentu merupakan hari khusus Islam
        
        Args:
            day: Hari (1-31)
            month: Bulan (1-12)
            year: Tahun
            
        Returns:
            Dictionary berisi informasi hari khusus
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/hijri/is-special-day?d={day}&m={month}&y={year}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            return {
                                'status': 'success',
                                'data': data['data']
                            }
                        else:
                            return {'status': 'error', 'message': 'Gagal memeriksa hari khusus'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def get_special_days(self, year=None):
        """
        Mendapatkan hari-hari khusus Islam untuk tahun tertentu
        
        Args:
            year: Tahun Hijriah, default tahun saat ini
            
        Returns:
            Dictionary berisi informasi hari-hari khusus Islam
        """
        if year is None:
            today_result = await self.get_hijri_date()
            if today_result['status'] == 'error':
                return today_result
            year = today_result['data']['year']
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/hijri/special-day/{year}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            return {
                                'status': 'success',
                                'data': data['data'],
                                'year': year
                            }
                        else:
                            return {'status': 'error', 'message': 'Gagal mendapatkan hari-hari khusus Islam'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def format_hijri_date(self, hijri_data):
        """
        Format tanggal Hijriah menjadi pesan yang mudah dibaca
        
        Args:
            hijri_data: Data tanggal Hijriah dari get_hijri_date
            
        Returns:
            String tanggal Hijriah yang diformat
        """
        if hijri_data['status'] == 'error':
            return f"Maaf, terjadi kesalahan: {hijri_data['message']}"
        
        data = hijri_data['data']
        
        # Format baru berdasarkan API myquran.com:
        # data.date[0] = nama hari (Senin, Selasa, dll)
        # data.date[1] = tanggal hijriah lengkap (misalnya: "27 Syaban 1445 H")
        # data.date[2] = tanggal masehi (format: dd-mm-yyyy)
        
        message = f"📆 *Tanggal Hijriah Hari Ini*\n\n"
        message += f"📅 Hari: {data['date'][0]}\n"
        message += f"🌙 Hijriah: {data['date'][1]}\n"
        message += f"📌 Masehi: {data['date'][2]}\n\n"
        
        # Tambahan informasi dari array num
        # num[0] = hari dalam seminggu (1=Ahad, 2=Senin, ..., 7=Sabtu)
        # num[1] = tanggal masehi
        # num[2] = bulan masehi
        # num[3] = tahun masehi
        # num[4] = tanggal hijriah
        # num[5] = bulan hijriah
        # num[6] = tahun hijriah
        
        hijri_month_names = [
            "", "Muharram", "Safar", "Rabiul Awal", "Rabiul Akhir", 
            "Jumadil Awal", "Jumadil Akhir", "Rajab", "Syaban", 
            "Ramadan", "Syawal", "Dzulkaidah", "Dzulhijjah"
        ]
        
        hijri_month_name = hijri_month_names[data['num'][5]] if data['num'][5] <= 12 else "Unknown"
        
        message += f"Detail:\n"
        message += f"📆 Tanggal Hijriah: {data['num'][4]}\n"
        message += f"📅 Bulan Hijriah: {data['num'][5]} ({hijri_month_name})\n"
        message += f"📆 Tahun Hijriah: {data['num'][6]}\n"
                
        return message
        
    def format_special_days(self, special_days_data):
        """
        Format hari-hari khusus Islam menjadi pesan yang mudah dibaca
        
        Args:
            special_days_data: Data hari-hari khusus
            
        Returns:
            String hari-hari khusus yang diformat
        """
        if special_days_data['status'] == 'error':
            return f"Maaf, terjadi kesalahan: {special_days_data['message']}"
        
        # Note: API doesn't directly provide special days so we use predefined ones
        year = special_days_data['year']
        
        # Predefined special Islamic days
        special_days = [
            {"name": "Tahun Baru Hijriah", "day": 1, "month": 1, "description": "Awal tahun dalam kalender Hijriah"},
            {"name": "Asyura", "day": 10, "month": 1, "description": "Hari ke-10 bulan Muharram, peristiwa penting dalam sejarah Islam"},
            {"name": "Maulid Nabi Muhammad SAW", "day": 12, "month": 3, "description": "Peringatan kelahiran Nabi Muhammad SAW"},
            {"name": "Isra Mi'raj", "day": 27, "month": 7, "description": "Peringatan perjalanan Nabi Muhammad SAW dari Masjidil Haram ke Masjidil Aqsa dan naik ke langit"},
            {"name": "Awal Ramadan", "day": 1, "month": 9, "description": "Awal bulan puasa Ramadan"},
            {"name": "Nuzulul Quran", "day": 17, "month": 9, "description": "Peringatan turunnya Al-Quran"},
            {"name": "Idul Fitri", "day": 1, "month": 10, "description": "Hari Raya Idul Fitri, merayakan selesainya bulan Ramadan"},
            {"name": "Idul Adha", "day": 10, "month": 12, "description": "Hari Raya Idul Adha, hari raya kurban"}
        ]
        
        message = f"🌟 *Hari-Hari Khusus Islam Tahun {year} H*\n\n"
        
        hijri_months = [
            "", "Muharram", "Safar", "Rabiul Awal", "Rabiul Akhir", 
            "Jumadil Awal", "Jumadil Akhir", "Rajab", "Syaban", 
            "Ramadan", "Syawal", "Dzulkaidah", "Dzulhijjah"
        ]
        
        for day in special_days:
            month_name = hijri_months[day["month"]]
            message += f"🌙 *{day['name']}*\n"
            message += f"📅 {day['day']} {month_name} {year} H\n"
            message += f"ℹ️ {day['description']}\n\n"
        
        return message
    
    def format_monthly_info(self, monthly_info):
        """
        Format informasi bulan Hijriah menjadi pesan yang mudah dibaca
        
        Args:
            monthly_info: Data informasi bulan dari get_hijri_calendar
            
        Returns:
            String informasi bulan Hijriah yang diformat
        """
        if monthly_info['status'] == 'error':
            return f"Maaf, terjadi kesalahan: {monthly_info['message']}"
        
        data = monthly_info['data']
        month_number = monthly_info['month']
        year = monthly_info['year']
        
        message = f"📅 *Informasi Bulan {data['indonesian']} {year} H*\n\n"
        message += f"🌙 Nama Bulan: {data['indonesian']} / {data['english']}\n"
        message += f"🔤 Dalam Bahasa Arab: {data['arabic']}\n"
        message += f"📊 Nomor Bulan: {data['number']}\n"
        message += f"📆 Tahun: {year} H\n\n"
        
        # Add information about the significance of this month
        month_significance = {
            1: "Bulan Muharram adalah bulan pertama dalam kalender Hijriah dan salah satu dari empat bulan suci.",
            2: "Bulan Safar adalah bulan kedua dalam kalender Hijriah.",
            3: "Bulan Rabiul Awal adalah bulan kelahiran Nabi Muhammad SAW.",
            9: "Bulan Ramadan adalah bulan puasa wajib bagi umat Islam.",
            12: "Bulan Dzulhijjah adalah bulan pelaksanaan ibadah haji."
        }
        
        if month_number in month_significance:
            message += f"ℹ️ *Tentang Bulan Ini:*\n{month_significance[month_number]}\n\n"
        
        return message