# integrations/modstring_manager.py
import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from colorama import Fore, Style

class ModStringManager:
    def __init__(self, bot, data_persistence):
        self.bot = bot
        self.data_persistence = data_persistence
        self.enabled = False
        self.active_modstrings = {}
        self.word_lists = {}
        self.last_sync = None
        self.studio_url = "http://localhost:8000"
        
    async def initialize(self):
        """Initialize ModString integration"""
        try:
            # Load persistent data
            self.active_modstrings = await self.data_persistence.load_modstrings()
            self.word_lists = await self.data_persistence.load_word_lists()
            
            # Test connection to Forge Studio
            if await self.check_studio_connection():
                self.enabled = True
                await self.sync_with_studio()
                print(f"{Fore.GREEN}✅ ModString integration initialized{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ ModString integration disabled - Forge Studio not available{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ ModString initialization error: {e}{Style.RESET_ALL}")
    
    async def check_studio_connection(self) -> bool:
        """Check if Forge Studio is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.studio_url}/health", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def sync_with_studio(self):
        """Sync ModStrings and word lists with Forge Studio"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get active ModStrings
                async with session.get(f"{self.studio_url}/api/modstrings") as response:
                    if response.status == 200:
                        studio_modstrings = await response.json()
                        self.active_modstrings = studio_modstrings
                        await self.data_persistence.save_modstrings(studio_modstrings)
                
                # Get word lists
                async with session.get(f"{self.studio_url}/api/lists") as response:
                    if response.status == 200:
                        studio_lists = await response.json()
                        self.word_lists = studio_lists
                        await self.data_persistence.save_word_lists(studio_lists)
            
            self.last_sync = datetime.now().isoformat()
            print(f"{Fore.GREEN}🔄 ModString sync completed{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ ModString sync error: {e}{Style.RESET_ALL}")
    
    async def evaluate_message(self, message_content: str, user_id: int, 
                             channel_id: int) -> Dict[str, Any]:
        """Evaluate a message against active ModStrings"""
        if not self.enabled or not self.active_modstrings:
            return {"matched": False, "results": []}
        
        try:
            results = []
            for modstring_id, modstring_data in self.active_modstrings.items():
                result = await self._evaluate_single_modstring(
                    message_content, user_id, channel_id, modstring_data
                )
                if result["matched"]:
                    results.append(result)
            
            return {
                "matched": len(results) > 0,
                "results": results,
                "total_checks": len(self.active_modstrings)
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ ModString evaluation error: {e}{Style.RESET_ALL}")
            return {"matched": False, "results": [], "error": str(e)}
    
    async def _evaluate_single_modstring(self, message_content: str, user_id: int,
                                       channel_id: int, modstring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a message against a single ModString"""
        try:
            # Send evaluation request to Forge Studio
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": message_content,
                    "user_id": str(user_id),
                    "channel_id": str(channel_id),
                    "modstring": modstring_data
                }
                
                async with session.post(f"{self.studio_url}/api/evaluate", 
                                      json=payload, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"matched": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"matched": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ModString integration statistics"""
        return {
            "enabled": self.enabled,
            "active_modstrings": len(self.active_modstrings),
            "word_lists": len(self.word_lists),
            "last_sync": self.last_sync,
            "studio_url": self.studio_url
        }
    
    async def reload_modstrings(self):
        """Reload ModStrings from Forge Studio"""
        if self.enabled:
            await self.sync_with_studio()
            return True
        return False
    
    async def get_modstring_by_id(self, modstring_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific ModString by ID"""
        return self.active_modstrings.get(modstring_id)
    
    async def get_word_list_by_name(self, list_name: str) -> Optional[List[str]]:
        """Get a specific word list by name"""
        return self.word_lists.get(list_name)
    
    def is_enabled(self) -> bool:
        """Check if ModString integration is enabled"""
        return self.enabled
    
    def get_modstring_count(self) -> int:
        """Get the number of active ModStrings"""
        return len(self.active_modstrings)
    
    def get_word_list_count(self) -> int:
        """Get the number of word lists"""
        return len(self.word_lists)