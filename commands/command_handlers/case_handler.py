# commands/command_handlers/case_handler.py
import discord
from datetime import datetime, timedelta
from .base_handler import BaseHandler

class CaseHandler(BaseHandler):
    """Handler for case management commands"""
    
    async def handle_case_command(self, interaction: discord.Interaction, user: discord.Member, 
                                action: discord.app_commands.Choice[str], reason: str,
                                duration: int = None, send_dm: bool = True, 
                                severity: discord.app_commands.Choice[str] = None):
        """Handle creating a new moderation case"""
        await interaction.response.defer()
        
        try:
            # Validate duration for timeouts
            if action.value == "timeout" and not duration:
                await self.send_error(interaction, "Duration is required for timeout actions.")
                return
            
            if duration and duration > 40320:  # 28 days in minutes
                await self.send_error(interaction, "Duration cannot exceed 28 days (40,320 minutes).")
                return
            
            # Apply Discord actions
            dm_sent = await self._apply_discord_action(user, action.value, reason, duration, send_dm, interaction)
            
            # Create the case record
            case_number = await self._create_case_record(
                interaction, user, action.value, reason, duration, 
                dm_sent, severity, send_dm
            )
            
            # Send success response
            await self._send_case_success_response(
                interaction, user, action.value, case_number, 
                reason, duration, dm_sent
            )
            
        except discord.Forbidden:
            await self.send_error(interaction, f"I don't have permission to {action.value} this user.")
        except Exception as e:
            await self.send_error(interaction, f"Error creating case: {str(e)}")
    
    async def _apply_discord_action(self, user: discord.Member, action: str, reason: str, 
                                  duration: int, send_dm: bool, interaction: discord.Interaction) -> bool:
        """Apply the actual Discord moderation action"""
        dm_sent = False
        
        if action == "timeout" and duration:
            timeout_duration = timedelta(minutes=duration)
            await user.timeout(timeout_duration, reason=reason)
            
            if send_dm:
                dm_sent = await self._send_timeout_dm(user, reason, duration, interaction)
        
        elif action == "kick":
            await user.kick(reason=reason)
            if send_dm:
                dm_sent = await self._send_kick_dm(user, reason, interaction)
        
        elif action == "ban":
            await user.ban(reason=reason, delete_message_days=1)
            if send_dm:
                dm_sent = await self._send_ban_dm(user, reason, interaction)
        
        elif action == "warn" and send_dm:
            dm_sent = await self._send_warn_dm(user, reason, interaction)
        
        return dm_sent
    
    async def _send_timeout_dm(self, user: discord.Member, reason: str, duration: int, interaction: discord.Interaction) -> bool:
        """Send timeout DM to user"""
        try:
            embed = discord.Embed(
                title="⏰ You have been timed out",
                description=f"You have been timed out in **{interaction.guild.name}** for {duration} minutes.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
            
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
    
    async def _send_kick_dm(self, user: discord.Member, reason: str, interaction: discord.Interaction) -> bool:
        """Send kick DM to user"""
        try:
            embed = discord.Embed(
                title="👢 You have been kicked",
                description=f"You have been kicked from **{interaction.guild.name}**.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
            
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
    
    async def _send_ban_dm(self, user: discord.Member, reason: str, interaction: discord.Interaction) -> bool:
        """Send ban DM to user"""
        try:
            embed = discord.Embed(
                title="🔨 You have been banned",
                description=f"You have been banned from **{interaction.guild.name}**.",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
            
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
    
    async def _send_warn_dm(self, user: discord.Member, reason: str, interaction: discord.Interaction) -> bool:
        """Send warning DM to user"""
        try:
            embed = discord.Embed(
                title="⚠️ You have received a warning",
                description=f"You have been warned in **{interaction.guild.name}**.",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
            
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
    
    async def _create_case_record(self, interaction: discord.Interaction, user: discord.Member,
                                action: str, reason: str, duration: int, dm_sent: bool,
                                severity: discord.app_commands.Choice[str], send_dm: bool) -> int:
        """Create the case record in the moderation system"""
        # Prepare action data
        action_data = {
            "action_type": action,
            "reason": reason,
            "severity": severity.value if severity else "Medium",
            "duration": duration,
            "dm_sent": dm_sent,
            "moderator_name": interaction.user.display_name,
            "moderator_id": interaction.user.id,
            "display_name": user.display_name,
            "username": user.name,
            "created_at": datetime.now().isoformat()
        }
        
        # Use new case creation method
        case_number = await self.moderation_manager.create_moderation_case(user.id, action_data)
        
        return case_number
    
    async def _send_case_success_response(self, interaction: discord.Interaction, user: discord.Member,
                                        action: str, case_number: int, reason: str, 
                                        duration: int, dm_sent: bool):
        """Send success response for case creation"""
        embed = discord.Embed(
            title="✅ Case Created Successfully",
            description=f"Case #{case_number} has been created for {user.display_name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Action", value=action.title(), inline=True)
        embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
        embed.add_field(name="DM Sent", value="✅" if dm_sent else "❌", inline=True)
        
        if duration:
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.followup.send(embed=embed)
    
    async def handle_resolve_command(self, interaction: discord.Interaction, user: discord.Member, 
                                   case_number: int, resolution: str):
        """Handle resolving a moderation case"""
        await interaction.response.defer()
        
        try:
            success = self.moderation_manager.resolve_case(
                user.id,
                case_number,
                interaction.user.id,
                "Manual",
                resolution,
                "Resolved"
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Case Resolved",
                    description=f"Case #{case_number} for {user.display_name} has been resolved.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Resolved By", value=interaction.user.display_name, inline=True)
                embed.add_field(name="Resolution", value=resolution, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await self.send_error(interaction, f"Case #{case_number} not found for {user.display_name}.")
                
        except Exception as e:
            await self.send_error(interaction, f"Error resolving case: {str(e)}")