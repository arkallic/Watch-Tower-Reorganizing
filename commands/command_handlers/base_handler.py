# commands/command_handlers/base_handler.py
import discord
from datetime import datetime
from colorama import Fore, Style

class BaseHandler:
    """Base class for command handlers"""
    
    def __init__(self, bot_commands):
        self.bot_commands = bot_commands
        self.bot = bot_commands.bot
        self.config = bot_commands.config
        self.logger = bot_commands.logger
        self.moderation_manager = bot_commands.moderation_manager
        self.report_generator = bot_commands.report_generator
        self.psychosis_manager = bot_commands.psychosis_manager
        self.deleted_message_logger = bot_commands.deleted_message_logger
        self.bot_settings = bot_commands.bot_settings
    
    def log_command(self, command_name: str, interaction: discord.Interaction, details: str = ""):
        """Log command usage"""
        self.logger.console_log_command(command_name, interaction.user, details)
    
    async def send_error(self, interaction: discord.Interaction, message: str, ephemeral: bool = True):
        """Send error message"""
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.red()
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    async def send_success(self, interaction: discord.Interaction, title: str, message: str, ephemeral: bool = False):
        """Send success message"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=message,
            color=discord.Color.green()
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)