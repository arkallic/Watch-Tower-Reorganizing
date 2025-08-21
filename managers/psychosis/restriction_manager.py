# managers/psychosis/restriction_manager.py
import discord
from typing import Dict, Any
from colorama import Fore, Style

class RestrictionManager:
    def __init__(self, config_manager, logger):
        self.config = config_manager
        self.logger = logger
    
    async def apply_restriction(self, guild: discord.Guild, user: discord.Member, 
                              restriction_type: str) -> bool:
        """Apply Discord permission restrictions based on type"""
        try:
            if restriction_type == "silence":
                return await self._apply_silence_restriction(guild, user)
            elif restriction_type == "voice_timeout":
                return await self._apply_voice_restriction(guild, user)
            elif restriction_type == "full_restriction":
                return await self._apply_full_restriction(guild, user)
            elif restriction_type == "isolation":
                return await self._apply_isolation_restriction(guild, user)
            else:
                return False
                
        except Exception as e:
            self.logger.console_log_system(f"Error applying {restriction_type}: {e}", "ERROR")
            return False
    
    async def remove_restriction(self, guild: discord.Guild, user: discord.Member, 
                               restriction_type: str) -> bool:
        """Remove Discord permission restrictions"""
        try:
            if restriction_type == "silence":
                return await self._remove_silence_restriction(guild, user)
            elif restriction_type == "voice_timeout":
                return await self._remove_voice_restriction(guild, user)
            elif restriction_type == "full_restriction":
                return await self._remove_full_restriction(guild, user)
            elif restriction_type == "isolation":
                return await self._remove_isolation_restriction(guild, user)
            else:
                return False
                
        except Exception as e:
            self.logger.console_log_system(f"Error removing {restriction_type}: {e}", "ERROR")
            return False
    
    async def _apply_silence_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove speaking permissions from all channels"""
        success_count = 0
        total_channels = 0
        
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)):
                try:
                    total_channels += 1
                    overwrite = discord.PermissionOverwrite()
                    overwrite.send_messages = False
                    overwrite.speak = False
                    overwrite.add_reactions = False
                    
                    await channel.set_permissions(user, overwrite=overwrite)
                    success_count += 1
                    
                except discord.Forbidden:
                    continue
                except Exception:
                    continue
        
        self.logger.console_log_system(
            f"Applied silence restriction: {success_count}/{total_channels} channels", 
            "PSYCHOSIS"
        )
        return success_count > 0
    
    async def _apply_voice_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove voice permissions from all voice channels"""
        success_count = 0
        total_channels = 0
        
        for channel in guild.voice_channels:
            try:
                total_channels += 1
                overwrite = discord.PermissionOverwrite()
                overwrite.speak = False
                overwrite.stream = False
                overwrite.use_voice_activation = False
                
                await channel.set_permissions(user, overwrite=overwrite)
                success_count += 1
                
            except discord.Forbidden:
                continue
            except Exception:
                continue
        
        return success_count > 0
    
    async def _apply_full_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Apply comprehensive restrictions"""
        success_count = 0
        total_channels = 0
        
        for channel in guild.channels:
            try:
                total_channels += 1
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = False
                overwrite.speak = False
                overwrite.add_reactions = False
                overwrite.connect = False
                overwrite.view_channel = False
                
                await channel.set_permissions(user, overwrite=overwrite)
                success_count += 1
                
            except discord.Forbidden:
                continue
            except Exception:
                continue
        
        return success_count > 0
    
    async def _apply_isolation_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Complete isolation - hide all channels except psychosis channel"""
        psychosis_channel_id = self.config.get("psychosis_channel_id")
        success_count = 0
        total_channels = 0
        
        for channel in guild.channels:
            try:
                total_channels += 1
                
                if channel.id == psychosis_channel_id:
                    # Allow access to psychosis channel only
                    overwrite = discord.PermissionOverwrite()
                    overwrite.view_channel = True
                    overwrite.send_messages = True
                    overwrite.read_message_history = True
                else:
                    # Hide all other channels
                    overwrite = discord.PermissionOverwrite()
                    overwrite.view_channel = False
                
                await channel.set_permissions(user, overwrite=overwrite)
                success_count += 1
                
            except discord.Forbidden:
                continue
            except Exception:
                continue
        
        return success_count > 0
    
    async def _remove_silence_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove silence restrictions"""
        return await self._remove_all_overwrites(guild, user)
    
    async def _remove_voice_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove voice restrictions"""
        return await self._remove_all_overwrites(guild, user)
    
    async def _remove_full_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove full restrictions"""
        return await self._remove_all_overwrites(guild, user)
    
    async def _remove_isolation_restriction(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove isolation restrictions"""
        return await self._remove_all_overwrites(guild, user)
    
    async def _remove_all_overwrites(self, guild: discord.Guild, user: discord.Member) -> bool:
        """Remove all permission overwrites for a user"""
        success_count = 0
        total_channels = 0
        
        for channel in guild.channels:
            try:
                total_channels += 1
                overwrites = channel.overwrites
                if user in overwrites:
                    await channel.set_permissions(user, overwrite=None)
                success_count += 1
                
            except discord.Forbidden:
                continue
            except Exception:
                continue
        
        self.logger.console_log_system(
            f"Removed restrictions: {success_count}/{total_channels} channels", 
            "PSYCHOSIS"
        )
        return success_count > 0