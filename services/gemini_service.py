import google.generativeai as genai
from config.config import GEMINI_API_KEY, SHOW_THINKING_PROCESS
from services.mcp_service import MCPService

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.mcp_service = MCPService()
        self.show_thinking = SHOW_THINKING_PROCESS
    
    def generate_response(self, prompt, chat_history=None):
        """
        Generate a response using the Gemini LLM.
        
        Args:
            prompt: The user's input text.
            chat_history: Optional list of previous exchanges to provide context.
            
        Returns:
            The AI-generated response as a string.
        """
        try:
            # Create a chat session
            chat = self.model.start_chat(history=[])
            
            # Add chat history if available
            if chat_history:
                for message, response in chat_history:
                    chat.send_message(message)
                    # We don't need to wait for a response since we're just adding history
            
            # Send the current prompt and get a response
            response = chat.send_message(prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error generating response from Gemini: {str(e)}")
            return "Maaf, saya mengalami kesulitan menjawab pertanyaan Anda saat ini. Silakan coba lagi nanti."
    
    async def sequential_thinking(self, prompt, chat_history=None):
        """
        Perform sequential thinking for complex requests using MCP.
        
        Args:
            prompt: The user's input text.
            chat_history: Optional list of previous exchanges to provide context.
            
        Returns:
            The AI-generated response after sequential thinking as a string.
        """
        try:
            # Use MCP sequential thinking for complex questions if thinking process is enabled
            if self.show_thinking and len(prompt.split()) > 5:  # If the prompt is reasonably complex
                return await self.mcp_service.sequential_thinking(prompt)
            
            # For direct answer mode (or simpler questions in thinking mode)
            if self.show_thinking:
                # Thinking prompt that shows the process
                thinking_prompt = f"""
                Pikirkan secara bertahap untuk menjawab pertanyaan/permintaan ini:
                
                "{prompt}"
                
                1. Pahami terlebih dahulu maksud dari pertanyaan/permintaan
                2. Identifikasi apakah ini tentang jadwal sholat, doa, Al-Quran, kata motivasi, atau topik Islam lainnya
                3. Kumpulkan informasi yang relevan
                4. Susun jawaban yang jelas dan akurat sesuai ajaran Islam
                5. Tambahkan referensi jika ada
                
                Berikan jawaban yang lengkap dan sesuai kaidah Islam.
                """
            else:
                # Direct answer prompt without showing thinking process
                thinking_prompt = f"""
                Jawab pertanyaan/permintaan berikut dengan SINGKAT dan LANGSUNG ke poin utama:
                
                "{prompt}"
                
                Panduan untuk jawaban:
                - Mulai jawaban langsung ke poin utama tanpa menjelaskan proses berpikir
                - Jawab secara ringkas tapi lengkap (maksimal 3-5 paragraf pendek)
                - Gunakan bahasa yang sederhana dan mudah dipahami
                - Jika pertanyaan tentang hukum Islam, berikan jawaban sesuai pendapat yang paling umum diterima
                - Jangan gunakan kata-kata seperti "Saya berpikir" atau "Langkah pertama" atau "Mari kita analisis"
                - Berikan jawaban yang sesuai dengan kaidah Islam
                """
            
            # Create a chat session
            chat = self.model.start_chat(history=[])
            
            # Add chat history if available
            if chat_history:
                for message, response in chat_history:
                    chat.send_message(message)
            
            # Send the prompt
            response = chat.send_message(thinking_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error in sequential thinking: {str(e)}")
            return "Maaf, saya mengalami kesulitan memproses permintaan Anda. Silakan coba lagi nanti."
    
    async def search_and_answer(self, prompt, chat_history=None):
        """
        Search the internet using SERP API and answer the question.
        
        Args:
            prompt: The user's input text.
            chat_history: Optional list of previous exchanges to provide context.
            
        Returns:
            Response that incorporates search results.
        """
        try:
            # Search the internet for relevant information
            search_results = await self.mcp_service.search_internet(prompt)
            
            # Create a prompt that incorporates the search results
            if self.show_thinking:
                # Search prompt with thinking process
                search_prompt = f"""
                Berikut adalah informasi yang saya temukan di internet tentang pertanyaan Anda:
                
                {search_results}
                
                Berdasarkan informasi di atas dan pengetahuan islami saya, berikut adalah jawaban untuk pertanyaan:
                "{prompt}"
                
                Berikan jawaban yang komprehensif, akurat dan sesuai dengan ajaran Islam.
                """
            else:
                # Direct answer search prompt
                search_prompt = f"""
                Berikut adalah informasi yang saya temukan di internet tentang pertanyaan:
                
                {search_results}
                
                Berdasarkan informasi di atas, jawab pertanyaan berikut dengan SINGKAT dan LANGSUNG:
                "{prompt}"
                
                Jawab secara ringkas tapi lengkap (maksimal 3-5 paragraf pendek).
                Langsung ke poin utama tanpa menjelaskan proses berpikir.
                Jangan gunakan kata-kata seperti "Berdasarkan penelusuran" atau "Saya menemukan".
                Berikan jawaban yang sesuai dengan kaidah Islam.
                """
            
            # Create a chat session
            chat = self.model.start_chat(history=[])
            
            # Add chat history if available
            if chat_history:
                for message, response in chat_history:
                    chat.send_message(message)
            
            # Send the search-enhanced prompt
            response = chat.send_message(search_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error in search and answer: {str(e)}")
            return "Maaf, saya mengalami kesulitan memproses permintaan Anda. Silakan coba lagi nanti."
    
    async def get_simple_response(self, prompt):
        """
        Get a simple, direct response from Gemini without additional processing.
        Used for basic interpretations where only the text result is needed.
        
        Args:
            prompt: Text prompt to send to Gemini
            
        Returns:
            The text response from Gemini
        """
        try:
            # Use the base model for a straightforward response
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error getting simple response from Gemini: {str(e)}")
            return "Error processing request"
            
    def set_thinking_mode(self, show_thinking):
        """
        Enable or disable thinking process display in responses.
        
        Args:
            show_thinking: Boolean, True to show thinking process, False for direct answers
        """
        self.show_thinking = show_thinking