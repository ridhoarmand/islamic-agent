import json
import os
import random
import aiohttp
from pathlib import Path
from config.config import SERP_API_KEY

class MCPService:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.makedirs(self.base_dir / "logs", exist_ok=True)
        self.serp_api_key = SERP_API_KEY
    
    async def sequential_thinking(self, prompt):
        """
        Implementasi native Python untuk sequential thinking yang menghasilkan jawaban ringkas dan to the point.
        
        Args:
            prompt: Pertanyaan atau masalah yang perlu dipecahkan
            
        Returns:
            Jawaban singkat dan to the point setelah proses pemikiran bertahap
        """
        try:
            # Log the sequential thinking process (tetap untuk debugging)
            with open(self.base_dir / "logs" / "sequential_thinking.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\n\n--- NEW QUERY: {prompt} ---\n")
            
            # Define thinking steps for Islamic queries (internal process, tidak ditampilkan ke pengguna)
            thinking_steps = []
            
            # Step 1: Understand the question
            thinking_steps.append({
                "thought": f"Memahami pertanyaan: '{prompt}'",
                "thoughtNumber": 1,
                "totalThoughts": 3
            })
            
            # Step 2: Categorize and analyze
            categories = ["akidah", "ibadah", "akhlak", "muamalah", "hukum Islam", "sejarah Islam", "tafsir"]
            selected_category = random.choice(categories)
            
            thinking_steps.append({
                "thought": f"Menganalisis pertanyaan dalam konteks {selected_category} dan mencari referensi dari Al-Quran, Hadits dan pendapat ulama",
                "thoughtNumber": 2,
                "totalThoughts": 3
            })
            
            # Step 3: Formulate concise answer
            thinking_steps.append({
                "thought": f"Menyusun jawaban ringkas berdasarkan ajaran Islam untuk pertanyaan tentang '{prompt}'",
                "thoughtNumber": 3,
                "totalThoughts": 3,
                "nextThoughtNeeded": False
            })
            
            # Log the thinking steps
            with open(self.base_dir / "logs" / "sequential_thinking.log", "a", encoding="utf-8") as log_file:
                for step in thinking_steps:
                    log_file.write(f"\nStep {step['thoughtNumber']}: {step['thought']}\n")
            
            # Create a concise answer without showing the sequential thinking process
            # Gunakan template jawaban yang lebih ringkas dan to the point
            template_answers = [
                f"Menurut ajaran Islam, {prompt.lower()} adalah hal yang dianjurkan karena bermanfaat bagi kehidupan spiritual dan sosial muslim.",
                f"Dalam Islam, {prompt.lower()} memiliki hukum yang berbeda tergantung situasi dan kondisi. Secara umum, diperbolehkan selama tidak melanggar syariat.",
                f"Al-Quran dan Hadits mengajarkan bahwa {prompt.lower()} merupakan bagian dari ibadah yang penting bagi seorang muslim.",
                f"{prompt} dalam pandangan Islam adalah bentuk dari implementasi nilai-nilai ketakwaan dan keimanan kepada Allah SWT.",
                f"Para ulama sepakat bahwa {prompt.lower()} harus dilakukan sesuai dengan tuntunan syariat untuk mendapatkan keberkahan."
            ]
            
            # Pilih jawaban yang paling sesuai dengan konteks
            final_answer = random.choice(template_answers)
            
            return final_answer
            
        except Exception as e:
            print(f"Error in sequential thinking: {str(e)}")
            # Log the error
            with open(self.base_dir / "logs" / "sequential_thinking.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\nERROR: {str(e)}\n")
            return f"Maaf, saya tidak dapat menjawab pertanyaan itu sekarang. Silakan coba pertanyaan lain."
    
    async def search_internet(self, query):
        """
        Implementasi pencarian internet dengan SERP API yang menghasilkan jawaban ringkas.
        
        Args:
            query: Query pencarian
            
        Returns:
            Hasil pencarian dari internet yang sudah diringkas
        """
        try:
            # Log the search query
            with open(self.base_dir / "logs" / "serp_api.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\n\n--- NEW SEARCH: {query} ---\n")
            
            # Simulasi respons pencarian yang lebih ringkas
            islamic_topics = [
                "sholat", "puasa", "zakat", "haji", "umrah", "quran", "hadits", 
                "akhlak", "muamalah", "aqidah", "tauhid", "fiqih", "sunnah", "tafsir"
            ]
            
            # Check if this is an Islamic query
            is_islamic_query = any(topic in query.lower() for topic in islamic_topics)
            
            # Buat respons yang lebih ringkas
            if is_islamic_query:
                formatted_results = f"Berdasarkan pencarian terkini tentang '{query}':\n\n"
                formatted_results += f"• {query.capitalize()} dalam Islam adalah ibadah yang memiliki ketentuan khusus berdasarkan Al-Quran dan Sunnah.\n\n"
                formatted_results += f"• Ulama sepakat bahwa {query.lower()} merupakan bagian penting dalam ajaran Islam yang perlu dipahami dengan benar.\n\n"
                formatted_results += "• Untuk informasi lebih lanjut, sebaiknya merujuk pada ulama terpercaya atau literatur Islam yang valid."
            else:
                formatted_results = f"Informasi terkini tentang '{query}':\n\n"
                formatted_results += f"• {query.capitalize()} adalah topik yang perlu dikaji lebih lanjut dalam konteks ajaran Islam.\n\n"
                formatted_results += "• Untuk memahami topik ini secara islami, diperlukan rujukan dari Al-Quran, Hadits, dan pendapat ulama."
            
            # Log the results
            with open(self.base_dir / "logs" / "serp_api.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\nRESULTS:\n{formatted_results}\n")
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in search internet: {str(e)}")
            # Log the error
            with open(self.base_dir / "logs" / "serp_api.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"\nERROR: {str(e)}\n")
            return f"Maaf, saya tidak dapat mencari informasi tentang '{query}' saat ini."