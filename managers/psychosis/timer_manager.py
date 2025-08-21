# managers/psychosis/timer_manager.py
import asyncio
from datetime import datetime, timedelta
from colorama import Fore, Style

class TimerManager:
    def __init__(self, psychosis_manager):
        self.psychosis_manager = psychosis_manager
        self.active_timers = {}
    
    async def start_restriction_timer(self, bot, user_id: int, restriction_type: str, 
                                    duration_minutes: int):
        """Start a timer for automatic restriction removal"""
        if duration_minutes <= 0:
            return
        
        # Cancel existing timer if any
        if user_id in self.active_timers:
            self.active_timers[user_id].cancel()
        
        # Create new timer
        timer_task = asyncio.create_task(
            self._restriction_timer(bot, user_id, restriction_type, duration_minutes)
        )
        self.active_timers[user_id] = timer_task
        
        self.psychosis_manager.logger.console_log_system(
            f"Started {duration_minutes}m timer for user {user_id}",
            "PSYCHOSIS"
        )
    
    async def _restriction_timer(self, bot, user_id: int, restriction_type: str, 
                               duration_minutes: int):
        """Timer coroutine that removes restriction after duration"""
        try:
            # Wait for the duration
            await asyncio.sleep(duration_minutes * 60)
            
            # Remove the restriction
            success = await self.psychosis_manager.remove_restriction(
                bot, user_id, "Auto-removal (timer expired)"
            )
            
            if success:
                self.psychosis_manager.logger.console_log_system(
                    f"Auto-removed {restriction_type} restriction for user {user_id}",
                    "PSYCHOSIS"
                )
            else:
                self.psychosis_manager.logger.console_log_system(
                    f"Failed to auto-remove restriction for user {user_id}",
                    "WARNING"
                )
            
            # Clean up timer reference
            if user_id in self.active_timers:
                del self.active_timers[user_id]
                
        except asyncio.CancelledError:
            # Timer was cancelled (manual removal)
            if user_id in self.active_timers:
                del self.active_timers[user_id]
        except Exception as e:
            print(f"{Fore.RED}❌ Error in restriction timer: {e}{Style.RESET_ALL}")
    
    def cancel_timer(self, user_id: int):
        """Cancel an active timer"""
        if user_id in self.active_timers:
            self.active_timers[user_id].cancel()
            del self.active_timers[user_id]
            return True
        return False
    
    def get_active_timers(self) -> dict:
        """Get info about active timers"""
        return {
            user_id: {
                "active": not task.done(),
                "cancelled": task.cancelled() if task.done() else False
            }
            for user_id, task in self.active_timers.items()
        }