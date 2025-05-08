import aiohttp
import os
import json
from pathlib import Path
from google.generativeai import GenerativeModel
from config.config import GEMINI_API_KEY
import google.generativeai as genai

class QuranService:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.quran_data_dir = self.base_dir / "data" / "quran"
        # Update API URL ke equran.id
        self.api_url = "https://equran.id/api/v2"
        
        # Create quran data directory if it doesn't exist
        os.makedirs(self.quran_data_dir, exist_ok=True)
        
        # Initialize Gemini LLM untuk interpretasi input pengguna
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = GenerativeModel('gemini-1.5-pro')
    
    async def interpret_query(self, user_input):
        """
        Menggunakan LLM untuk menginterpretasikan input pengguna menjadi nomor atau nama surat.
        Contoh: "surat yasin" -> {"type": "name", "query": "yasin"}
                "al fatihah" -> {"type": "name", "query": "al-fatihah"}
                "surat 36" -> {"type": "number", "query": 36}
                "surat ke 1" -> {"type": "number", "query": 1}
        
        Args:
            user_input: Input dari pengguna (bisa berupa nama surat atau nomor)
            
        Returns:
            Dictionary dengan tipe query dan query yang sudah diinterpretasi
        """
        try:
            prompt = f"""
            Analisis input pengguna berikut dan tentukan apakah mereka mencari surah Al-Quran berdasarkan nama atau nomor:
            "{user_input}"

            Jika berdasarkan nama, berikan standardisasi nama surah (misalnya "yasin" -> "yasin", "alfatihah" -> "al-fatihah").
            Jika berdasarkan nomor, ekstrak angkanya saja.

            Berikan respons dalam format JSON:
            {{
                "type": "name" atau "number",
                "query": [nama surat terstandarisasi atau nomor surat]
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            result_text = response.text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Konversi query ke integer jika tipenya number
                if result["type"] == "number":
                    result["query"] = int(result["query"])
                return result
            else:
                # Fallback to simple parsing
                if user_input.isdigit():
                    return {"type": "number", "query": int(user_input)}
                else:
                    return {"type": "name", "query": user_input.lower()}
        
        except Exception as e:
            print(f"Error saat menginterpretasi query: {str(e)}")
            # Fallback parsing jika terjadi error
            if user_input.isdigit():
                return {"type": "number", "query": int(user_input)}
            else:
                return {"type": "name", "query": user_input.lower()}
    
    async def get_surah_by_name(self, surah_name):
        """
        Mendapatkan surah berdasarkan nama dengan equran.id API.
        
        Args:
            surah_name: Nama surah (contoh: "al-fatihah", "yasin")
            
        Returns:
            Dictionary dengan data surah atau error message
        """
        # Kita gunakan endpoint surat untuk mendapatkan daftar surat terlebih dahulu
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/surat") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["code"] == 200:
                            # Cari surat berdasarkan nama
                            surah_name_lower = surah_name.lower()
                            surah_number = None
                            
                            for surah in data["data"]:
                                # Cek nama surat dalam berbagai bentuk
                                if (surah_name_lower in surah["namaLatin"].lower() or
                                    surah_name_lower in surah["nama"].lower() or
                                    surah_name_lower in surah["arti"].lower()):
                                    surah_number = surah["nomor"]
                                    break
                            
                            if surah_number:
                                return await self.get_surah(surah_number)
                            else:
                                return {"status": "error", "message": f"Surah dengan nama '{surah_name}' tidak ditemukan"}
                        else:
                            return {"status": "error", "message": "API returned an error"}
                    else:
                        return {"status": "error", "message": f"HTTP error: {response.status}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
                
    async def get_surah(self, surah_number):
        """
        Mendapatkan surah berdasarkan nomor dari equran.id API.
        
        Args:
            surah_number: Nomor surah (1-114)
            
        Returns:
            Dictionary dengan data surah atau error message
        """
        cache_file = self.quran_data_dir / f"surah_{surah_number}_equran.json"
        
        # Check if we have cached data
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # If no cached data, fetch from API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/surat/{surah_number}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["code"] == 200:
                            # Cache the data
                            with open(cache_file, "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            return data
                        else:
                            return {"status": "error", "message": "API returned an error"}
                    else:
                        return {"status": "error", "message": f"HTTP error: {response.status}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_ayah(self, surah_number, ayah_number):
        """
        Mendapatkan ayat tertentu dari equran.id API.
        
        Args:
            surah_number: Nomor surah (1-114)
            ayah_number: Nomor ayat
            
        Returns:
            Dictionary dengan data ayat atau error message
        """
        try:
            # Dapatkan seluruh surah
            surah_data = await self.get_surah(surah_number)
            if "status" in surah_data and surah_data["status"] == "error":
                return surah_data
                
            # Filter untuk ayat tertentu
            ayahs = surah_data["data"]["ayat"]
            for ayah in ayahs:
                if ayah["nomorAyat"] == ayah_number:
                    return {"status": "success", "data": {"ayat": ayah, "surah": surah_data["data"]}}
            
            return {"status": "error", "message": f"Ayat {ayah_number} tidak ditemukan dalam Surah {surah_number}"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def cari_ayat(self, query):
        """
        Mencari ayat Al-Quran berdasarkan kata kunci di equran.id API.
        
        Args:
            query: Kata kunci pencarian
            
        Returns:
            Dictionary dengan hasil pencarian atau error message
        """
        try:
            # Untuk pencarian, kita perlu implementasi khusus karena equran.id tidak menyediakan
            # endpoint pencarian yang lengkap. Kita akan menggunakan pendekatan alternatif:
            # 1. Dapatkan daftar surah
            # 2. Untuk setiap surah, dapatkan ayat-ayatnya
            # 3. Lakukan pencarian pada teks terjemahan ayat
            
            results = {"status": "success", "data": {"matches": [], "count": 0}}
            max_results = 15  # Batasi hasil pencarian
            
            async with aiohttp.ClientSession() as session:
                # Get list of surahs
                async with session.get(f"{self.api_url}/surat") as response:
                    if response.status != 200:
                        return {"status": "error", "message": f"HTTP error: {response.status}"}
                        
                    surah_list = await response.json()
                    if surah_list["code"] != 200:
                        return {"status": "error", "message": "API returned an error"}
                    
                    # Untuk efisiensi, kita hanya periksa 30 surah pertama (sekitar 1/4 dari Al-Quran)
                    # Karena proses ini bisa memakan waktu lama jika memeriksa seluruh Al-Quran
                    query_lower = query.lower()
                    search_count = 0
                    
                    for surah in surah_list["data"][:30]:  # Batasi pencarian ke 30 surah pertama
                        surah_number = surah["nomor"]
                        
                        # Get surah details with verses
                        surah_data = await self.get_surah(surah_number)
                        if "status" in surah_data and surah_data["status"] == "error":
                            continue
                            
                        # Search in verses
                        for ayah in surah_data["data"]["ayat"]:
                            # Search in translation (arti)
                            if query_lower in ayah["teksIndonesia"].lower():
                                results["data"]["matches"].append({
                                    "surah": {
                                        "number": surah_number,
                                        "name": surah["nama"],
                                        "englishName": surah["namaLatin"],
                                        "indonesianName": surah["namaLatin"],
                                        "englishNameTranslation": surah["arti"]
                                    },
                                    "numberInSurah": ayah["nomorAyat"],
                                    "text": ayah["teksIndonesia"],
                                    "arabicText": ayah["teksArab"]
                                })
                                
                                search_count += 1
                                if search_count >= max_results:
                                    break
                        
                        if search_count >= max_results:
                            break
                    
                    results["data"]["count"] = search_count
                    return results
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def format_surah(self, surah_data):
        """Format surah untuk ditampilkan dalam pesan Telegram."""
        if "status" in surah_data and surah_data["status"] == "error":
            return f"Maaf, terjadi kesalahan: {surah_data['message']}"
        
        data = surah_data["data"]
        
        # Format the header
        message = f"📖 *{data['namaLatin']} ({data['nama']}) - {data['arti']}*\n"
        message += f"Surah ke-{data['nomor']}, terdiri dari {data['jumlahAyat']} ayat\n"
        message += f"_{data['tempatTurun']} • {data['jumlahAyat']} Ayat_\n\n"
        
        # Tambahkan tafsir singkat jika tersedia
        if "deskripsi" in data and data["deskripsi"]:
            message += f"*Deskripsi Singkat:*\n{data['deskripsi'][:300]}...\n\n"
        
        # Only include first 10 ayahs if there are more than 20 to avoid message too long
        ayahs = data["ayat"]
        if len(ayahs) > 20:
            message += "*Menampilkan 10 ayat pertama:*\n\n"
            ayahs = ayahs[:10]
            
        # Format each ayah
        for ayah in ayahs:
            message += f"{ayah['nomorAyat']}. {ayah['teksArab']}\n"
            message += f"_{ayah['teksIndonesia']}_\n\n"
            
        if len(data["ayat"]) > 20:
            message += "...\n\n"
            message += f"*Surah {data['namaLatin']} terdiri dari {data['jumlahAyat']} ayat.*\n\n"
            
        # Add audio link if available
        if "audioFull" in data and data["audioFull"]:
            message += f"🔊 [Dengarkan Audio Murottal]({data['audioFull']['05']})"
            
        return message
    
    def format_search_results(self, search_data):
        """Format hasil pencarian untuk ditampilkan dalam pesan Telegram."""
        if "status" in search_data and search_data["status"] == "error":
            return f"Maaf, terjadi kesalahan: {search_data['message']}"
            
        data = search_data["data"]
        count = data["count"]
        
        if count == 0:
            return "Maaf, pencarian Anda tidak menghasilkan ayat yang sesuai."
            
        message = f"🔍 Hasil pencarian: {count} ayat ditemukan\n\n"
        
        # Limit to first 5 matches to avoid message too long
        matches = data["matches"][:5] if len(data["matches"]) > 5 else data["matches"]
        
        for i, match in enumerate(matches, 1):
            surah_name = match["surah"]["indonesianName"]
            ayah_num = match["numberInSurah"]
            arabic_text = match.get("arabicText", "")
            indo_text = match["text"]
            
            message += f"{i}. *{surah_name} ({match['surah']['number']}:{ayah_num})*\n"
            if arabic_text:
                message += f"{arabic_text}\n"
            message += f"_{indo_text}_\n\n"
            
        if len(data["matches"]) > 5:
            message += f"... dan {count - 5} ayat lainnya."
            
        return message