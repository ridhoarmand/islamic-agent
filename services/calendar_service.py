import aiohttp
from datetime import datetime
from config.config import MYQURAN_API_BASE_URL

class CalendarService:
    def __init__(self):
        # Gunakan base URL dari myQuran API
        self.myquran_api_url = MYQURAN_API_BASE_URL
    
    async def get_hijri_date(self):
        """
        Mendapatkan tanggal Hijriah saat ini menggunakan API MyQuran
        
        Returns:
            Dictionary berisi informasi tanggal Hijriah
        """
        try:
            # Dapatkan tanggal hari ini dalam format YYYY-MM-DD
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Gunakan endpoint API MyQuran untuk tanggal Hijriah saat ini: /cal/hijr/yyyy-mm-dd/adj=-1
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.myquran_api_url}/cal/hijr/{today}/adj=-1") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            # Format data hasil
                            hijri_date_parts = data['data']['date'][1].split(' ')  # "16 Dzulhijjah 1445 H"
                            hijri_day = hijri_date_parts[0]
                            hijri_month = hijri_date_parts[1]
                            hijri_year = hijri_date_parts[2]
                            weekday = data['data']['date'][0]  # "Ahad"
                            
                            formatted_data = {
                                'day': hijri_day,
                                'month': {
                                    'number': data['data']['num'][5],  # Nomor bulan Hijriah (1-12)
                                    'indonesian': hijri_month,  # Nama bulan dalam Bahasa Indonesia
                                    'english': hijri_month,     # Nama bulan dalam Bahasa Inggris (sama saja)
                                },
                                'year': hijri_year.replace(' H', ''),
                                'weekday': {
                                    'indonesian': weekday,
                                    'english': self._convert_day_to_english(weekday)
                                }
                            }
                            
                            return {
                                'status': 'success',
                                'data': formatted_data
                            }
                        else:
                            return {'status': 'error', 'message': 'Gagal mendapatkan tanggal Hijriah'}
                    else:
                        return {'status': 'error', 'message': f'HTTP error: {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def convert_to_hijri(self, day, month, year):
        """
        Mengkonversi tanggal masehi ke tanggal Hijriah menggunakan MyQuran API
        
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
            
            # Gunakan endpoint API MyQuran untuk konversi tanggal: /cal/hijr/yyyy-mm-dd/adj=-1
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.myquran_api_url}/cal/hijr/{date_str}/adj=-1") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            # Format data hasil
                            hijri_date_parts = data['data']['date'][1].split(' ')  # "16 Dzulhijjah 1445 H"
                            hijri_day = hijri_date_parts[0]
                            hijri_month = hijri_date_parts[1]
                            hijri_year = hijri_date_parts[2]
                            weekday = data['data']['date'][0]  # "Ahad"
                            
                            formatted_data = {
                                'day': hijri_day,
                                'month': {
                                    'number': data['data']['num'][5],  # Nomor bulan Hijriah (1-12)
                                    'indonesian': hijri_month,  # Nama bulan dalam Bahasa Indonesia
                                    'english': hijri_month,     # Nama bulan dalam Bahasa Inggris (sama saja)
                                },
                                'year': hijri_year.replace(' H', ''),
                                'weekday': {
                                    'indonesian': weekday,
                                    'english': self._convert_day_to_english(weekday)
                                }
                            }
                            
                            return {
                                'status': 'success',
                                'data': formatted_data
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
        Memeriksa apakah tanggal tertentu merupakan hari khusus Islam menggunakan data lokal
        
        Args:
            day: Hari (1-31)
            month: Bulan (1-12)
            year: Tahun
            
        Returns:
            Dictionary berisi informasi hari khusus
        """
        try:
            # Konversi tanggal ke format YYYY-MM-DD
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            # Menggunakan metode Hijriah API MyQuran untuk mendapatkan tanggal Hijriah
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.myquran_api_url}/cal/hijr/{date_str}/adj=-1") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == True:
                            # Dapatkan data Hijriah
                            hijri_day = data['data']['num'][4]  # tanggal Hijriah
                            hijri_month = data['data']['num'][5]  # bulan Hijriah
                            
                            # Periksa hari-hari khusus yang umum
                            is_special = self._check_common_special_days(hijri_day, hijri_month)
                            
                            if is_special:
                                return {
                                    'status': 'success',
                                    'data': is_special
                                }
                            else:
                                return {
                                    'status': 'success',
                                    'data': {
                                        'is_special_day': False
                                    }
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
            if isinstance(today_result['data']['year'], str):
                year = int(today_result['data']['year'].replace(' H', ''))
            else:
                year = today_result['data']['year']
            
        try:
            # Daftar bulan Hijriah
            hijri_months = ['', 'Muharram', 'Safar', 'Rabiul Awal', 'Rabiul Akhir', 
                           'Jumadil Awal', 'Jumadil Akhir', 'Rajab', 'Sya\'ban', 
                           'Ramadhan', 'Syawal', 'Dzulqaidah', 'Dzulhijjah']
            
            # Daftar hari-hari khusus Islam
            special_days = [
                {
                    'date': f'1 {hijri_months[1]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Tahun Baru Hijriah',
                    'description': 'Awal tahun dalam kalender Islam'
                },
                {
                    'date': f'10 {hijri_months[1]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Hari Asyura',
                    'description': 'Hari di mana banyak peristiwa penting terjadi dalam sejarah Islam'
                },
                {
                    'date': f'12 {hijri_months[3]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Maulid Nabi Muhammad SAW',
                    'description': 'Peringatan kelahiran Nabi Muhammad SAW'
                },
                {
                    'date': f'27 {hijri_months[7]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Isra Miraj',
                    'description': 'Peringatan perjalanan Nabi Muhammad SAW dari Masjidil Haram ke Masjidil Aqsa dan naik ke Sidratul Muntaha'
                },
                {
                    'date': f'1 {hijri_months[9]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Awal Ramadhan',
                    'description': 'Awal bulan puasa Ramadhan'
                },
                {
                    'date': f'17 {hijri_months[9]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Nuzulul Quran',
                    'description': 'Hari diturunkannya Al-Quran'
                },
                {
                    'date': f'21 {hijri_months[9]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Lailatul Qadar (kemungkinan)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                },
                {
                    'date': f'1 {hijri_months[10]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Idul Fitri',
                    'description': 'Hari Raya Idul Fitri'
                },
                {
                    'date': f'10 {hijri_months[12]} {year}',
                    'gregorian_date': 'Bervariasi',
                    'name': 'Idul Adha',
                    'description': 'Hari Raya Idul Adha'
                }
            ]
            
            return {
                'status': 'success',
                'data': special_days,
                'year': year
            }
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
        
        # Format baru berdasarkan API MyQuran yang telah diolah:
        message = f"📆 *Tanggal Hijriah Hari Ini*\n\n"
        message += f"🌙 Hijriah: {data['day']} {data['month']['indonesian']} {data['year']} H\n"
        message += f"📅 Hari: {data['weekday']['indonesian']}\n"
        
        # Tambahkan tanggal Masehi hari ini
        today = datetime.now().strftime("%d-%m-%Y")
        message += f"📌 Masehi: {today}\n\n"
        
        # Tambahkan detail bulan Hijriah
        hijri_month_names = [
            "", "Muharram", "Safar", "Rabiul Awal", "Rabiul Akhir", 
            "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", 
            "Ramadhan", "Syawal", "Zulkaidah", "Dzulhijjah"
        ]
        
        hijri_month_number = data['month']['number']
        hijri_month_name = hijri_month_names[hijri_month_number] if 1 <= hijri_month_number <= 12 else "Unknown"
        
        message += f"ℹ️ *Detail Bulan Hijriah:*\n"
        message += f"📆 Bulan: {hijri_month_number} - {hijri_month_name}\n"
        
        # Tambahkan informasi tentang keutamaan bulan jika tersedia
        if hijri_month_number == 9:
            message += f"\n✨ *Bulan Ramadhan* - Bulan suci di mana diwajibkan puasa dan diturunkannya Al-Qur'an."
        elif hijri_month_number == 12:
            message += f"\n✨ *Bulan Dzulhijjah* - Bulan ibadah haji dan berisi 10 hari pertama yang mulia."
        elif hijri_month_number == 1:
            message += f"\n✨ *Bulan Muharram* - Salah satu bulan yang dimuliakan, berisi hari Asyura (10 Muharram)."
        elif hijri_month_number == 7:
            message += f"\n✨ *Bulan Rajab* - Salah satu bulan yang dimuliakan dan bulan terjadinya Isra' Mi'raj."
                
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

    def _convert_day_to_english(self, indonesian_day):
        """
        Mengkonversi nama hari dari Bahasa Indonesia ke Bahasa Inggris
        
        Args:
            indonesian_day: Nama hari dalam Bahasa Indonesia
            
        Returns:
            Nama hari dalam Bahasa Inggris
        """
        day_mapping = {
            'Senin': 'Monday',
            'Selasa': 'Tuesday',
            'Rabu': 'Wednesday',
            'Kamis': 'Thursday',
            'Jumat': 'Friday',
            'Jum\'at': 'Friday',
            'Sabtu': 'Saturday',
            'Ahad': 'Sunday',
            'Minggu': 'Sunday',
            # Format khusus dari API MyQuran
            'Isnain': 'Monday',
            'Tsulasa': 'Tuesday',
            'Arba\'a': 'Wednesday',
            'Khamis': 'Thursday',
            'Jumu\'ah': 'Friday',
            'Sabt': 'Saturday',
            'Ahaad': 'Sunday',
        }
        
        return day_mapping.get(indonesian_day, indonesian_day)

    def _check_common_special_days(self, hijri_day, hijri_month):
        """
        Memeriksa apakah tanggal Hijriah merupakan hari khusus Islam yang umum
        
        Args:
            hijri_day: Tanggal Hijriah
            hijri_month: Bulan Hijriah
            
        Returns:
            Dictionary berisi informasi hari khusus atau None jika bukan hari khusus
        """
        special_days = {
            # Bulan Ramadhan
            (1, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Awal Ramadhan',
                    'description': 'Awal bulan puasa Ramadhan'
                }
            },
            # Nuzulul Quran
            (17, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Nuzulul Quran',
                    'description': 'Hari diturunkannya Al-Quran'
                }
            },
            # Lailatul Qadar
            (21, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Lailatul Qadar (kemungkinan malam ke-1)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                }
            },
            (23, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Lailatul Qadar (kemungkinan malam ke-2)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                }
            },
            (25, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Lailatul Qadar (kemungkinan malam ke-3)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                }
            },
            (27, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Lailatul Qadar (kemungkinan malam ke-4)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                }
            },
            (29, 9): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Lailatul Qadar (kemungkinan malam ke-5)',
                    'description': 'Malam yang lebih baik dari 1000 bulan'
                }
            },
            # Idul Fitri
            (1, 10): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Idul Fitri',
                    'description': 'Hari Raya Idul Fitri'
                }
            },
            # Idul Adha
            (10, 12): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Idul Adha',
                    'description': 'Hari Raya Idul Adha'
                }
            },
            # Tahun Baru Hijriah
            (1, 1): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Tahun Baru Hijriah',
                    'description': 'Awal tahun dalam kalender Islam'
                }
            },
            # Hari Asyura
            (10, 1): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Hari Asyura',
                    'description': 'Hari di mana banyak peristiwa penting terjadi dalam sejarah Islam'
                }
            },
            # Maulid Nabi Muhammad SAW
            (12, 3): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Maulid Nabi Muhammad SAW',
                    'description': 'Peringatan kelahiran Nabi Muhammad SAW'
                }
            },
            # Isra Miraj
            (27, 7): {
                'is_special_day': True,
                'special_day': {
                    'name': 'Isra Miraj',
                    'description': 'Peringatan perjalanan Nabi Muhammad SAW dari Masjidil Haram ke Masjidil Aqsa dan naik ke Sidratul Muntaha'
                }
            }
        }
        
        # Periksa apakah tanggal dan bulan cocok dengan hari khusus
        key = (hijri_day, hijri_month)
        return special_days.get(key)