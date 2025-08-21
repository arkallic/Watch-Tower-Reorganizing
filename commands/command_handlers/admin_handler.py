# commands/command_handlers/admin_handler.py
import discord
from .base_handler import BaseHandler

class AdminHandler(BaseHandler):
    """Handler for administrative commands"""
    
    async def handle_force_sync_command(self, interaction: discord.Interaction):
        """Handle force sync command"""
        self.log_command("ForceSync", interaction.user, "Syncing commands")
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            synced = await self.bot.tree.sync()
            
            embed = discord.Embed(
                title="✅ Commands Synced",
                description=f"Successfully synced {len(synced)} slash commands.",
                color=discord.Color.green()
            )
            
            command_list = "\n".join([f"• /{cmd.name}" for cmd in synced])
            if len(command_list) > 1024:
                command_list = command_list[:1021] + "..."
            
            embed.add_field(
                name="Synced Commands",
                value=command_list or "No commands",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"Failed to sync commands: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    async def handle_dashboard_command(self, interaction: discord.Interaction):
        """Handle dashboard information command"""
        embed = discord.Embed(
            title="🖥️ Watch Tower Dashboard",
            description="Access the web dashboard for comprehensive bot management",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🌐 Dashboard URL",
            value="[http://localhost:3000](http://localhost:3000)",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Forge Studio (ModStrings)",
            value="[http://localhost:8000](http://localhost:8000)",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Bot API",
            value="[http://localhost:8001](http://localhost:8001)",
            inline=False
        )
        
        embed.add_field(
            name="📊 Dashboard Features",
            value="• View and manage all moderation cases\n• Configure bot settings\n• Monitor AI flagging statistics\n• Create and manage ModStrings\n• Review moderator performance\n• Export reports and analytics",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Settings Management",
            value="**All bot settings are now managed through the web dashboard.** Use the dashboard for a better configuration experience with real-time validation and organized categories.",
            inline=False
        )
        
        # Check user permissions for dashboard access
        user_roles = [role.id for role in interaction.user.roles]
        can_access = self.bot_settings.can_access_dashboard(user_roles)
        
        if can_access:
            embed.add_field(
                name="✅ Access Granted",
                value="You have permission to access the dashboard with your current roles.",
                inline=False
            )
        else:
            embed.add_field(
                name="❌ Access Denied",
                value="You don't have the required roles to access the dashboard. Contact an administrator.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)