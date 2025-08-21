# managers/psychosis/notification_manager.py
import discord
from datetime import datetime, timedelta
from typing import Dict, Any

class NotificationManager:
    def __init__(self, config_manager, logger):
        self.config = config_manager
        self.logger = logger
    
    async def send_restriction_notifications(self, bot, guild: discord.Guild, 
                                           user: discord.Member, restriction_type: str, 
                                           restriction_data: Dict[str, Any]):
        """Send notifications when restriction is applied"""
        try:
            # Send DM to user if user comment provided
            user_comment = restriction_data.get("user_comment", "")
            if user_comment:
                await self._send_user_dm(user, restriction_type, restriction_data)
            
            # Send mod channel notification
            await self._send_mod_notification(bot, guild, user, restriction_type, restriction_data)
            
            # Log to psychosis channel if it exists
            await self._log_to_psychosis_channel(bot, guild, user, restriction_type, restriction_data)
            
        except Exception as e:
            self.logger.console_log_system(f"Error sending notifications: {e}", "WARNING")
    
    async def send_restriction_ended_notification(self, bot, guild: discord.Guild, 
                                                user: discord.Member, restriction_data: Dict[str, Any], 
                                                reason: str):
        """Send notifications when restriction ends"""
        try:
            # Send mod channel notification
            await self._send_restriction_ended_mod_notification(
                bot, guild, user, restriction_data, reason
            )
            
            # Send user DM if appropriate
            await self._send_restriction_ended_user_dm(user, restriction_data, reason)
            
        except Exception as e:
            self.logger.console_log_system(f"Error sending end notifications: {e}", "WARNING")
    
    async def _send_user_dm(self, user: discord.Member, restriction_type: str, 
                          restriction_data: Dict[str, Any]):
        """Send DM to user about restriction"""
        try:
            user_comment = restriction_data.get("user_comment", "")
            duration = restriction_data.get("duration_minutes", 0)
            
            embed = discord.Embed(
                title="🧠 Mental Health Support",
                description=f"You have been temporarily restricted to help ensure your wellbeing.",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Restriction Type",
                value=restriction_type.replace("_", " ").title(),
                inline=True
            )
            
            embed.add_field(
                name="Duration",
                value=f"{duration} minutes",
                inline=True
            )
            
            if user_comment:
                embed.add_field(
                    name="Message from Moderators",
                    value=user_comment,
                    inline=False
                )
            
            embed.add_field(
                name="Support Resources",
                value="If you're experiencing a mental health crisis, please reach out to local emergency services or a crisis helpline.",
                inline=False
            )
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            self.logger.console_log_system(f"Could not send DM to {user.display_name}", "WARNING")
        except Exception as e:
            self.logger.console_log_system(f"Error sending user DM: {e}", "WARNING")
    
    async def _send_mod_notification(self, bot, guild: discord.Guild, user: discord.Member,
                                   restriction_type: str, restriction_data: Dict[str, Any]):
        """Send notification to mod channel"""
        mod_channel_id = self.config.get("mod_chat_channel")
        if not mod_channel_id:
            return
        
        mod_channel = guild.get_channel(mod_channel_id)
        if not mod_channel:
            return
        
        try:
            duration = restriction_data.get("duration_minutes", 0)
            moderator_name = restriction_data.get("moderator_name", "Unknown")
            mod_comment = restriction_data.get("mod_comment", "No comment provided")
            
            embed = discord.Embed(
                title="🧠 Psychosis Restriction Applied",
                description=f"Mental health restriction has been applied to {user.display_name}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="User", value=f"{user.display_name} ({user.mention})", inline=True)
            embed.add_field(name="Restriction", value=restriction_type.replace("_", " ").title(), inline=True)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Applied By", value=moderator_name, inline=True)
            embed.add_field(name="Expires", value=f"<t:{int((datetime.now() + timedelta(minutes=duration)).timestamp())}:F>", inline=True)
            embed.add_field(name="Internal Notes", value=mod_comment[:1024], inline=False)
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await mod_channel.send(embed=embed)
            
        except Exception as e:
            self.logger.console_log_system(f"Error sending mod notification: {e}", "WARNING")
    
    async def _log_to_psychosis_channel(self, bot, guild: discord.Guild, user: discord.Member,
                                      restriction_type: str, restriction_data: Dict[str, Any]):
        """Log restriction to psychosis channel"""
        psychosis_channel_id = self.config.get("psychosis_channel_id")
        if not psychosis_channel_id:
            return
        
        psychosis_channel = guild.get_channel(psychosis_channel_id)
        if not psychosis_channel:
            return
        
        try:
            user_comment = restriction_data.get("user_comment", "")
            if user_comment:
                await psychosis_channel.send(f"📢 {user.mention}: {user_comment}")
                
        except Exception as e:
            self.logger.console_log_system(f"Error logging to psychosis channel: {e}", "WARNING")
    
    async def _send_restriction_ended_mod_notification(self, bot, guild: discord.Guild, 
                                                     user: discord.Member, restriction_data: Dict[str, Any], 
                                                     reason: str):
        """Send mod notification when restriction ends"""
        mod_channel_id = self.config.get("mod_chat_channel")
        if not mod_channel_id:
            return
        
        mod_channel = guild.get_channel(mod_channel_id)
        if not mod_channel:
            return
        
        try:
            restriction_type = restriction_data.get("type", "Unknown")
            duration = restriction_data.get("duration_minutes", 0)
            moderator_name = restriction_data.get("moderator_name", "Unknown")
            
            embed = discord.Embed(
                title="🧠 Psychosis Restriction Ended",
                description=f"Mental health restriction has been removed from {user.display_name}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="User", value=f"{user.display_name} ({user.mention})", inline=True)
            embed.add_field(name="Restriction Type", value=restriction_type.replace("_", " ").title(), inline=True)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Originally Applied By", value=moderator_name, inline=True)
            embed.add_field(name="End Reason", value=reason, inline=False)
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await mod_channel.send(embed=embed)
            
        except Exception as e:
            self.logger.console_log_system(f"Error sending end notification: {e}", "WARNING")
    
    async def _send_restriction_ended_user_dm(self, user: discord.Member, 
                                            restriction_data: Dict[str, Any], reason: str):
        """Send DM to user when restriction ends"""
        try:
            embed = discord.Embed(
                title="🧠 Restriction Removed",
                description="Your mental health restriction has been lifted.",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Support",
                value="If you continue to experience difficulties, please don't hesitate to reach out to our moderation team or seek professional help.",
                inline=False
            )
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            pass  # User has DMs disabled
        except Exception as e:
            self.logger.console_log_system(f"Error sending end DM: {e}", "WARNING")