# commands/command_handlers/psychosis_handler.py
import discord
from datetime import datetime
from .base_handler import BaseHandler

class PsychosisHandler(BaseHandler):
    """Handler for psychosis management commands"""
    
    async def handle_psychosis_command(self, interaction: discord.Interaction, user: discord.Member):
        """Handle psychosis management command"""
        from managers.psychosis_manager import PsychosisActionView, ExistingRestrictionView
        
        self.log_command("Psychosis", interaction, f"Target: {user.name}")
        
        await interaction.response.defer()
        
        try:
            # Check if user already has restrictions
            existing_restriction = self.psychosis_manager.get_user_restriction(user.id)
            
            if existing_restriction:
                await self._send_existing_restriction_view(interaction, user, existing_restriction)
            else:
                await self._send_new_restriction_view(interaction, user)
                
        except Exception as e:
            await self.send_error(interaction, f"Error with psychosis command: {str(e)}")
    
    async def _send_existing_restriction_view(self, interaction: discord.Interaction, 
                                            user: discord.Member, existing_restriction: dict):
        """Send view for existing restriction"""
        from managers.psychosis_manager import ExistingRestrictionView
        
        embed = discord.Embed(
            title="⚠️ Existing Psychosis Restriction",
            description=f"{user.display_name} already has an active psychosis restriction.",
            color=discord.Color.orange()
        )
        
        restriction_type = existing_restriction.get("type", "Unknown")
        started_at = existing_restriction.get("started_at", "Unknown")
        duration = existing_restriction.get("duration_minutes", 0)
        
        embed.add_field(name="Restriction Type", value=restriction_type, inline=True)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Started", value=f"<t:{int(datetime.fromisoformat(started_at).timestamp())}:R>", inline=True)
        
        view = ExistingRestrictionView(user, existing_restriction, self.psychosis_manager)
        await interaction.followup.send(embed=embed, view=view)
    
    async def _send_new_restriction_view(self, interaction: discord.Interaction, user: discord.Member):
        """Send view for new restriction"""
        from managers.psychosis_manager import PsychosisActionView
        
        embed = discord.Embed(
            title="🧠 Psychosis Management",
            description=f"Select an appropriate restriction for {user.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Available Restrictions",
            value="• **Silence** - Remove speaking permissions\n• **Voice Timeout** - Remove voice permissions\n• **Full Restriction** - Complete isolation",
            inline=False
        )
        
        view = PsychosisActionView(user, self.psychosis_manager)
        await interaction.followup.send(embed=embed, view=view)