# views/moderation/modals.py
import discord
from datetime import datetime, timedelta
from typing import Optional

class BaseModal(discord.ui.Modal):
    """Base class for moderation modals"""
    
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = "", title: str = "Moderation Action"):
        super().__init__(title=title)
        self.target_user = target_user
        self.moderation_manager = moderation_manager
        self.is_flagged_message = is_flagged_message
        self.flagged_message = flagged_message
        self.message_url = message_url
    
    async def send_success_response(self, interaction: discord.Interaction, 
                                  action_type: str, case_number: int, 
                                  reason: str, additional_info: str = ""):
        """Send success response after case creation"""
        embed = discord.Embed(
            title="✅ Case Created Successfully",
            description=f"Case #{case_number} has been created for {self.target_user.display_name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Action", value=action_type.title(), inline=True)
        embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
        
        if additional_info:
            embed.add_field(name="Details", value=additional_info, inline=True)
        
        embed.add_field(name="Reason", value=reason, inline=False)
        
        if self.is_flagged_message:
            embed.add_field(name="🚨 Flagged Message", value=self.flagged_message[:300], inline=False)
            if self.message_url:
                embed.add_field(name="🔗 Original Message", value=f"[Jump to Message]({self.message_url})", inline=False)
        
        embed.set_thumbnail(url=self.target_user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

class WarnModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Warn User")
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this warning...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Message that will be sent to the user...",
            required=False,
            max_length=1000
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Medium",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            severity = self.severity.value if self.severity.value else "Medium"
            user_comment = self.user_comment.value
            internal_comment = self.internal_comment.value
            
            # Send DM to user if comment provided
            dm_sent = False
            if user_comment:
                try:
                    dm_embed = discord.Embed(
                        title="⚠️ Warning",
                        description=f"You have received a warning in **{interaction.guild.name}**.",
                        color=discord.Color.yellow()
                    )
                    dm_embed.add_field(name="Message", value=user_comment, inline=False)
                    dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                    
                    await self.target_user.send(embed=dm_embed)
                    dm_sent = True
                except discord.Forbidden:
                    pass
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "warn",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": dm_sent,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Warning", case_number, internal_comment,
                f"DM Sent: {'✅' if dm_sent else '❌'}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating warning: {str(e)}", ephemeral=True)

class TimeoutModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Timeout User")
        
        self.duration = discord.ui.TextInput(
            label="Duration (minutes)",
            placeholder="60",
            required=True,
            max_length=10
        )
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this timeout...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Message that will be sent to the user...",
            required=False,
            max_length=1000
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Medium",
            required=False,
            max_length=20
        )
        
        self.add_item(self.duration)
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Validate duration
            try:
                duration_minutes = int(self.duration.value)
                if duration_minutes <= 0 or duration_minutes > 40320:  # 28 days max
                    await interaction.followup.send("❌ Duration must be between 1 and 40,320 minutes (28 days).", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("❌ Invalid duration. Please enter a number.", ephemeral=True)
                return
            
            severity = self.severity.value if self.severity.value else "Medium"
            user_comment = self.user_comment.value
            internal_comment = self.internal_comment.value
            
            # Apply timeout
            timeout_duration = timedelta(minutes=duration_minutes)
            await self.target_user.timeout(timeout_duration, reason=internal_comment)
            
            # Send DM to user if comment provided
            dm_sent = False
            if user_comment:
                try:
                    dm_embed = discord.Embed(
                        title="⏰ Timeout",
                        description=f"You have been timed out in **{interaction.guild.name}** for {duration_minutes} minutes.",
                        color=discord.Color.orange()
                    )
                    dm_embed.add_field(name="Message", value=user_comment, inline=False)
                    dm_embed.add_field(name="Duration", value=f"{duration_minutes} minutes", inline=True)
                    dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                    
                    await self.target_user.send(embed=dm_embed)
                    dm_sent = True
                except discord.Forbidden:
                    pass
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "timeout",
                "reason": internal_comment,
                "severity": severity,
                "duration": duration_minutes,
                "dm_sent": dm_sent,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Timeout", case_number, internal_comment,
                f"Duration: {duration_minutes}m | DM Sent: {'✅' if dm_sent else '❌'}"
            )
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to timeout this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating timeout: {str(e)}", ephemeral=True)

class KickModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Kick User")
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this kick...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Message that will be sent to the user before kick...",
            required=False,
            max_length=1000
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="High",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            severity = self.severity.value if self.severity.value else "High"
            user_comment = self.user_comment.value
            internal_comment = self.internal_comment.value
            
            # Send DM to user if comment provided (before kick)
            dm_sent = False
            if user_comment:
                try:
                    dm_embed = discord.Embed(
                        title="👢 Kicked",
                        description=f"You have been kicked from **{interaction.guild.name}**.",
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(name="Reason", value=user_comment, inline=False)
                    dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                    
                    await self.target_user.send(embed=dm_embed)
                    dm_sent = True
                except discord.Forbidden:
                    pass
            
            # Kick the user
            await self.target_user.kick(reason=internal_comment)
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "kick",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": dm_sent,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Kick", case_number, internal_comment,
                f"DM Sent: {'✅' if dm_sent else '❌'}"
            )
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to kick this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error kicking user: {str(e)}", ephemeral=True)

class BanModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Ban User")
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this ban...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Message that will be sent to the user before ban...",
            required=False,
            max_length=1000
        )
        
        self.delete_days = discord.ui.TextInput(
            label="Delete Messages (days, 0-7)",
            placeholder="1",
            required=False,
            max_length=1
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Critical",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.delete_days)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Validate delete days
            try:
                delete_days = int(self.delete_days.value) if self.delete_days.value else 1
                if delete_days < 0 or delete_days > 7:
                    delete_days = 1
            except ValueError:
                delete_days = 1
            
            severity = self.severity.value if self.severity.value else "Critical"
            user_comment = self.user_comment.value
            internal_comment = self.internal_comment.value
            
            # Send DM to user if comment provided (before ban)
            dm_sent = False
            if user_comment:
                try:
                    dm_embed = discord.Embed(
                        title="🔨 Banned",
                        description=f"You have been banned from **{interaction.guild.name}**.",
                        color=discord.Color.dark_red()
                    )
                    dm_embed.add_field(name="Reason", value=user_comment, inline=False)
                    dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                    
                    await self.target_user.send(embed=dm_embed)
                    dm_sent = True
                except discord.Forbidden:
                    pass
            
            # Ban the user
            await self.target_user.ban(reason=internal_comment, delete_message_days=delete_days)
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "ban",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": dm_sent,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Ban", case_number, internal_comment,
                f"Messages Deleted: {delete_days} days | DM Sent: {'✅' if dm_sent else '❌'}"
            )
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to ban this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error banning user: {str(e)}", ephemeral=True)

class ModNoteModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Add Mod Note")
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Note",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal note about this user...",
            required=True,
            max_length=1000
        )
        
        self.resolvable = discord.ui.TextInput(
            label="Resolvable? (Yes/No)",
            placeholder="No",
            required=False,
            max_length=3
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Low",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.resolvable)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            severity = self.severity.value if self.severity.value else "Low"
            resolvable = "Yes" if self.resolvable.value.lower() == "yes" else "No"
            internal_comment = self.internal_comment.value
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "mod_note",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": False,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Mod Note", case_number, internal_comment,
                f"Resolvable: {resolvable}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating mod note: {str(e)}", ephemeral=True)

class SilenceModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Silence User")
        
        self.duration = discord.ui.TextInput(
            label="Duration (minutes)",
            placeholder="60",
            required=True,
            max_length=10
        )
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this silence...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (Optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Message that will be sent to the user...",
            required=False,
            max_length=1000
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Medium",
            required=False,
            max_length=20
        )
        
        self.add_item(self.duration)
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Validate duration
            try:
                duration_minutes = int(self.duration.value)
                if duration_minutes <= 0:
                    await interaction.followup.send("❌ Duration must be greater than 0.", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("❌ Invalid duration. Please enter a number.", ephemeral=True)
                return
            
            severity = self.severity.value if self.severity.value else "Medium"
            user_comment = self.user_comment.value
            internal_comment = self.internal_comment.value
            
            # Apply silence (remove send_messages permission)
            success_count = 0
            total_channels = 0
            
            for channel in interaction.guild.text_channels:
                try:
                    total_channels += 1
                    overwrite = discord.PermissionOverwrite()
                    overwrite.send_messages = False
                    overwrite.add_reactions = False
                    
                    await channel.set_permissions(self.target_user, overwrite=overwrite)
                    success_count += 1
                except discord.Forbidden:
                    continue
                except Exception:
                    continue
            
            if success_count == 0:
                await interaction.followup.send("❌ Failed to apply silence restrictions. Check bot permissions.", ephemeral=True)
                return
            
            # Send DM to user if comment provided
            dm_sent = False
            if user_comment:
                try:
                    dm_embed = discord.Embed(
                        title="🔇 Silenced",
                        description=f"You have been silenced in **{interaction.guild.name}** for {duration_minutes} minutes.",
                        color=discord.Color.orange()
                    )
                    dm_embed.add_field(name="Message", value=user_comment, inline=False)
                    dm_embed.add_field(name="Duration", value=f"{duration_minutes} minutes", inline=True)
                    dm_embed.add_field(name="Moderator", value=interaction.user.display_name, inline=True)
                    
                    await self.target_user.send(embed=dm_embed)
                    dm_sent = True
                except discord.Forbidden:
                    pass
            
            # ✅ FIXED: Use new case creation method
            action_data = {
                "action_type": "silence",
                "reason": internal_comment,
                "severity": severity,
                "duration": duration_minutes,
                "dm_sent": dm_sent,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            await self.send_success_response(
                interaction, "Silence", case_number, internal_comment,
                f"Duration: {duration_minutes}m | Channels: {success_count}/{total_channels} | DM Sent: {'✅' if dm_sent else '❌'}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating silence: {str(e)}", ephemeral=True)