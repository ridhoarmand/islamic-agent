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
            
    async def get_json_response(self, prompt):
        """
        Generate a JSON response using the Gemini LLM.
        This method specifically requests output in JSON format.
        
        Args:
            prompt: The input prompt requesting JSON output
            
        Returns:
            The parsed JSON object from the AI response or None if parsing fails
        """
        try:
            import json
            import re
            
            # Enhanced prompt to ensure JSON output
            json_prompt = f"""
            {prompt}
            
            IMPORTANT INSTRUCTION:
            - You MUST respond ONLY with a valid JSON object
            - Do NOT include any explanations, markdown formatting, or text outside the JSON
            - Do NOT include ```json or ``` markers
            - Ensure all keys and values are properly quoted and formatted
            """
            
            # Create a chat session with JSON output requirement
            chat = self.model.start_chat(history=[])
            
            # Set system instruction for JSON output
            response = chat.send_message(json_prompt)
            response_text = response.text
            
            # Try to parse as JSON - sometimes model will include markdown code block markers
            try:
                # Clean the response - remove markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].strip()
                
                # Remove any non-JSON text before or after the JSON object
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                
                # Parse the JSON
                json_data = json.loads(response_text)
                return json_data
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text}")
                
                # Retry with a more explicit request for proper JSON
                try:
                    retry_prompt = f"""
                    I received an invalid JSON response. Please provide a VALID JSON object for the following request:
                    
                    {prompt}
                    
                    CRITICAL: Only output a properly formatted JSON object with no other text or explanation.
                    """
                    
                    # Retry with more explicit instructions
                    retry_response = chat.send_message(retry_prompt)
                    retry_text = retry_response.text
                    
                    # Clean and parse the retry response
                    if "```json" in retry_text:
                        retry_text = retry_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in retry_text:
                        retry_text = retry_text.split("```")[1].strip()
                    
                    # Extract JSON object pattern
                    json_match = re.search(r'(\{.*\})', retry_text, re.DOTALL)
                    if json_match:
                        retry_text = json_match.group(1)
                    
                    return json.loads(retry_text)
                    
                except Exception:
                    # If retry fails, return None
                    return None
                
        except Exception as e:
            print(f"Error generating JSON response from Gemini: {str(e)}")
            return None
            
    def set_thinking_mode(self, show_thinking):
        """
        Enable or disable thinking process display in responses.
        
        Args:
            show_thinking: Boolean, True to show thinking process, False for direct answers
        """
        self.show_thinking = show_thinking