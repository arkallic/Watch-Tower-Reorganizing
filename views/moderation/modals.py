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
        
        await interaction.followup.send(embed=embed)

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
            label="Message to User (if sending DM)",
            style=discord.TextStyle.paragraph,
            placeholder="Enter message to send to user...",
            required=False,
            max_length=800
        )
        
        self.send_dm = discord.ui.TextInput(
            label="Send DM to User? (Yes/No)",
            placeholder="Yes",
            required=False,
            max_length=3
        )
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="Medium",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.send_dm)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            severity = self.severity.value if self.severity.value else "Medium"
            send_dm = self.send_dm.value.lower() == "yes" if self.send_dm.value else True
            internal_comment = self.internal_comment.value
            user_comment = self.user_comment.value if self.user_comment.value else internal_comment
            
            # FIXED: Use new async case creation method with guild and bot
            action_data = {
                "action_type": "warn",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": send_dm,
                "moderator_id": interaction.user.id,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name,
                "user_comment": user_comment,
                "flagged_message": self.flagged_message if self.is_flagged_message else None,
                "modstring_triggered": False
            }
            
            case_number = await self.moderation_manager.create_moderation_case(
                self.target_user.id, action_data, interaction.guild, interaction.client
            )
            
            await self.send_success_response(
                interaction, "Warning", case_number, internal_comment,
                f"DM Sent: {'✅' if send_dm else '❌'}"
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
            max_length=6
        )
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes about this timeout...",
            required=True,
            max_length=1000
        )
        
        self.user_comment = discord.ui.TextInput(
            label="Message to User (if sending DM)",
            style=discord.TextStyle.paragraph,
            placeholder="Enter message to send to user...",
            required=False,
            max_length=800
        )
        
        self.send_dm = discord.ui.TextInput(
            label="Send DM to User? (Yes/No)",
            placeholder="Yes",
            required=False,
            max_length=3
        )
        
        self.add_item(self.duration)
        self.add_item(self.internal_comment)
        self.add_item(self.user_comment)
        self.add_item(self.send_dm)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            duration = int(self.duration.value)
            send_dm = self.send_dm.value.lower() == "yes" if self.send_dm.value else True
            internal_comment = self.internal_comment.value
            user_comment = self.user_comment.value if self.user_comment.value else internal_comment
            
            # Apply the timeout
            timeout_until = datetime.now() + timedelta(minutes=duration)
            await self.target_user.timeout(timeout_until, reason=internal_comment)
            
            # FIXED: Use new async case creation method with guild and bot
            action_data = {
                "action_type": "timeout",
                "reason": internal_comment,
                "severity": "Medium",
                "duration": duration,
                "dm_sent": send_dm,
                "moderator_id": interaction.user.id,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name,
                "user_comment": user_comment,
                "flagged_message": self.flagged_message if self.is_flagged_message else None,
                "modstring_triggered": False
            }
            
            case_number = await self.moderation_manager.create_moderation_case(
                self.target_user.id, action_data, interaction.guild, interaction.client
            )
            
            await self.send_success_response(
                interaction, "Timeout", case_number, internal_comment,
                f"Duration: {duration} minutes"
            )
            
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
        
        self.severity = discord.ui.TextInput(
            label="Severity (Low/Medium/High/Critical)",
            placeholder="High",
            required=False,
            max_length=20
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.severity)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            severity = self.severity.value if self.severity.value else "High"
            internal_comment = self.internal_comment.value
            
            # FIXED: Use new async case creation method with guild and bot
            action_data = {
                "action_type": "kick",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": False,
                "moderator_id": interaction.user.id,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name,
                "flagged_message": self.flagged_message if self.is_flagged_message else None,
                "modstring_triggered": False
            }
            
            case_number = await self.moderation_manager.create_moderation_case(
                self.target_user.id, action_data, interaction.guild, interaction.client
            )
            
            # Kick the user after creating the case
            await self.target_user.kick(reason=internal_comment)
            
            await self.send_success_response(
                interaction, "Kick", case_number, internal_comment
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating kick: {str(e)}", ephemeral=True)

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
        
        self.delete_days = discord.ui.TextInput(
            label="Delete Messages (days 0-7)",
            placeholder="1",
            required=False,
            max_length=1
        )
        
        self.add_item(self.internal_comment)
        self.add_item(self.delete_days)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            internal_comment = self.internal_comment.value
            delete_days = int(self.delete_days.value) if self.delete_days.value else 1
            delete_days = max(0, min(delete_days, 7))  # Clamp between 0-7
            
            # FIXED: Use new async case creation method with guild and bot
            action_data = {
                "action_type": "ban",
                "reason": internal_comment,
                "severity": "Critical",
                "duration": None,
                "dm_sent": False,
                "moderator_id": interaction.user.id,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name,
                "flagged_message": self.flagged_message if self.is_flagged_message else None,
                "modstring_triggered": False
            }
            
            case_number = await self.moderation_manager.create_moderation_case(
                self.target_user.id, action_data, interaction.guild, interaction.client
            )
            
            # Ban the user after creating the case
            await self.target_user.ban(reason=internal_comment, delete_message_days=delete_days)
            
            await self.send_success_response(
                interaction, "Ban", case_number, internal_comment,
                f"Messages deleted: {delete_days} days"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating ban: {str(e)}", ephemeral=True)

class ModNoteModal(BaseModal):
    def __init__(self, target_user: discord.Member, moderation_manager, 
                 is_flagged_message: bool = False, flagged_message: str = "", 
                 message_url: str = ""):
        super().__init__(target_user, moderation_manager, is_flagged_message, 
                        flagged_message, message_url, "Add Mod Note")
        
        self.internal_comment = discord.ui.TextInput(
            label="Internal Mod Comment",
            style=discord.TextStyle.paragraph,
            placeholder="Enter internal notes...",
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
            
            # FIXED: Use new async case creation method with guild and bot
            action_data = {
                "action_type": "mod_note",
                "reason": internal_comment,
                "severity": severity,
                "duration": None,
                "dm_sent": False,
                "moderator_id": interaction.user.id,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name,
                "resolvable": resolvable,
                "flagged_message": self.flagged_message if self.is_flagged_message else None,
                "modstring_triggered": False
            }
            
            case_number = await self.moderation_manager.create_moderation_case(
                self.target_user.id, action_data, interaction.guild, interaction.client
            )
            
            await self.send_success_response(
                interaction, "Mod Note", case_number, internal_comment,
                f"Resolvable: {resolvable}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating mod note: {str(e)}", ephemeral=True)