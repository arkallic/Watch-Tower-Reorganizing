# integrations/ollama_client.py
import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from colorama import Fore, Style
from core.settings import bot_settings  # ✅ UPDATED: Changed from 'settings' to 'core.settings'

class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or bot_settings.get("ai_model_url", "http://localhost:11434")
        self.settings = bot_settings
        self.session = None
        self.queue = asyncio.Queue()
        self.processing = False
        self.model_name = "llama3.1"
        self.system_prompt = """You are a Discord moderation AI. Analyze messages for:
1. Harassment, bullying, or personal attacks
2. Hate speech or discrimination
3. Explicit sexual content
4. Violence or threats
5. Spam or excessive repetition
6. Self-harm or mental health crisis indicators

Respond with a confidence score (0-100) and reasoning."""
    
    async def initialize(self):
        """Initialize the Ollama client"""
        try:
            self.session = aiohttp.ClientSession()
            if await self.check_connection():
                print(f"{Fore.GREEN}✅ Ollama client initialized successfully{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to connect to Ollama server{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Ollama initialization error: {e}{Style.RESET_ALL}")
            return False
    
    async def check_connection(self) -> bool:
        """Check if Ollama server is available"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def analyze_message(self, message_content: str, user_id: int = None, 
                            channel_id: int = None) -> Dict[str, Any]:
        """Analyze a message for moderation flags"""
        if not await self.check_connection():
            return {"error": "Ollama server not available", "confidence": 0}
        
        try:
            prompt = f"{self.system_prompt}\n\nMessage to analyze: {message_content}"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 200
                }
            }
            
            async with self.session.post(f"{self.base_url}/api/generate", 
                                       json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    analysis = self._parse_response(result.get("response", ""))
                    analysis["user_id"] = user_id
                    analysis["channel_id"] = channel_id
                    analysis["timestamp"] = datetime.now().isoformat()
                    return analysis
                else:
                    return {"error": f"HTTP {response.status}", "confidence": 0}
                    
        except Exception as e:
            return {"error": str(e), "confidence": 0}
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        try:
            # Simple parsing - look for confidence score and reasoning
            confidence = 0
            reasoning = response_text.strip()
            flags = []
            
            # Extract confidence score if present
            import re
            confidence_match = re.search(r'confidence[:\s]*(\d+)', response_text.lower())
            if confidence_match:
                confidence = int(confidence_match.group(1))
            
            # Look for common flag indicators
            text_lower = response_text.lower()
            if "harassment" in text_lower or "bullying" in text_lower:
                flags.append("harassment")
            if "hate speech" in text_lower or "discrimination" in text_lower:
                flags.append("hate_speech")
            if "explicit" in text_lower or "sexual" in text_lower:
                flags.append("explicit_content")
            if "violence" in text_lower or "threat" in text_lower:
                flags.append("violence")
            if "spam" in text_lower:
                flags.append("spam")
            if "self-harm" in text_lower or "mental health" in text_lower:
                flags.append("mental_health")
            
            return {
                "confidence": confidence,
                "reasoning": reasoning,
                "flags": flags,
                "should_flag": confidence >= self.settings.get("flag_threshold", 70)
            }
            
        except Exception as e:
            return {
                "confidence": 0,
                "reasoning": f"Parse error: {str(e)}",
                "flags": [],
                "should_flag": False
            }
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "base_url": self.base_url,
            "model": self.model_name,
            "connected": self.session is not None,
            "queue_size": self.queue.qsize() if self.queue else 0
        }