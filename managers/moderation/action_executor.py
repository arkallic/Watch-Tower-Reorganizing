# managers/moderation/action_executor.py
import discord
from datetime import timedelta
from typing import Optional

class ActionExecutor:
    def __init__(self, logger):
        self.logger = logger
    
    async def timeout_user(self, guild: discord.Guild, user: discord.Member, 
                          duration_minutes: int, reason: str, moderator: discord.Member,
                          send_dm: bool = True) -> bool:
        """Execute timeout action on Discord"""
        try:
            timeout_duration = timedelta(minutes=duration_minutes)
            await user.timeout(timeout_duration, reason=f"{reason} (by {moderator.display_name})")
            
            if send_dm:
                await self._send_action_dm(user, "timeout", reason, duration_minutes)
            
            self.logger.console_log_system(
                f"Applied {duration_minutes}m timeout to {user.display_name}: {reason}",
                "ACTION"
            )
            return True
            
        except discord.Forbidden:
            self.logger.console_log_system(f"No permission to timeout {user.display_name}", "ERROR")
            return False
        except Exception as e:
            self.logger.console_log_system(f"Error timing out user: {e}", "ERROR")
            return False
    
    async def kick_user(self, guild: discord.Guild, user: discord.Member, 
                       reason: str, moderator: discord.Member, send_dm: bool = True) -> bool:
        """Execute kick action on Discord"""
        try:
            if send_dm:
                await self._send_action_dm(user, "kick", reason)
            
            await guild.kick(user, reason=f"{reason} (by {moderator.display_name})")
            
            self.logger.console_log_system(
                f"Kicked {user.display_name}: {reason}",
                "ACTION"
            )
            return True
            
        except discord.Forbidden:
            self.logger.console_log_system(f"No permission to kick {user.display_name}", "ERROR")
            return False
        except Exception as e:
            self.logger.console_log_system(f"Error kicking user: {e}", "ERROR")
            return False
    
    async def ban_user(self, guild: discord.Guild, user: discord.Member, 
                      reason: str, moderator: discord.Member, delete_days: int = 1,
                      send_dm: bool = True) -> bool:
        """Execute ban action on Discord"""
        try:
            if send_dm:
                await self._send_action_dm(user, "ban", reason)
            
            await guild.ban(user, reason=f"{reason} (by {moderator.display_name})", 
                          delete_message_days=delete_days)
            
            self.logger.console_log_system(
                f"Banned {user.display_name}: {reason}",
                "ACTION"
            )
            return True
            
        except discord.Forbidden:
            self.logger.console_log_system(f"No permission to ban {user.display_name}", "ERROR")
            return False
        except Exception as e:
            self.logger.console_log_system(f"Error banning user: {e}", "ERROR")
            return False
    
    async def apply_role_restriction(self, guild: discord.Guild, user: discord.Member,
                                   role_id: int, reason: str) -> bool:
        """Apply or remove a restriction role"""
        try:
            role = guild.get_role(role_id)
            if not role:
                return False
            
            if role in user.roles:
                await user.remove_roles(role, reason=reason)
                action = "removed"
            else:
                await user.add_roles(role, reason=reason)
                action = "added"
            
            self.logger.console_log_system(
                f"Role {action}: {role.name} for {user.display_name}",
                "ACTION"
            )
            return True
            
        except discord.Forbidden:
            self.logger.console_log_system(f"No permission to modify roles for {user.display_name}", "ERROR")
            return False
        except Exception as e:
            self.logger.console_log_system(f"Error modifying role: {e}", "ERROR")
            return False
    
    async def _send_action_dm(self, user: discord.Member, action_type: str, 
                            reason: str, duration: Optional[int] = None):
        """Send DM notification about moderation action"""
        try:
            embed = discord.Embed(
                title=f"Moderation Action: {action_type.title()}",
                description=f"You have received a {action_type} in {user.guild.name}",
                color=discord.Color.orange()
            )
            
            embed.add_field(name="Reason", value=reason, inline=False)
            
            if duration:
                embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            
            embed.add_field(
                name="Questions?",
                value="If you have questions about this action, please contact the moderation team.",
                inline=False
            )
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            # User has DMs disabled
            pass
        except Exception as e:
            self.logger.console_log_system(f"Error sending DM: {e}", "WARNING")