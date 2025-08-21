# commands/bot_commands.py
import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from colorama import Fore, Style
from core.settings import bot_settings

from .command_handlers import (
    ActionsHandler,
    CaseHandler, 
    StatsHandler,
    AdminHandler,
    PsychosisHandler
)

class BotCommands:
    def __init__(self, bot, config, logger, moderation_manager, report_generator, psychosis_manager, deleted_message_logger):
        self.bot = bot
        self.config = config
        self.logger = logger
        self.moderation_manager = moderation_manager
        self.report_generator = report_generator
        self.psychosis_manager = psychosis_manager
        self.deleted_message_logger = deleted_message_logger
        self.bot_settings = bot_settings
        
        # Initialize command handlers
        self.actions_handler = ActionsHandler(self)
        self.case_handler = CaseHandler(self)
        self.stats_handler = StatsHandler(self)
        self.admin_handler = AdminHandler(self)
        self.psychosis_handler = PsychosisHandler(self)
        
        # Register all commands
        self.setup_commands()
    
    def check_mod_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has mod permissions for commands"""
        user_roles = [role.id for role in interaction.user.roles]
        return self.bot_settings.user_has_mod_permissions(user_roles)
    
    def check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions"""
        user_roles = [role.id for role in interaction.user.roles]
        return self.bot_settings.user_has_admin_permissions(user_roles)
    
    def setup_commands(self):
        """Setup all slash commands with enhanced permission checks"""
        # Actions commands
        @self.bot.tree.command(name="actions", description="View and manage user moderation actions")
        async def actions_command(interaction: discord.Interaction, user: discord.Member):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.actions_handler.handle_actions_command(interaction, user)
        
        # Case management commands  
        @self.bot.tree.command(name="case", description="Create a new moderation case")
        @discord.app_commands.describe(
            user="User to create case for",
            action="Type of moderation action",
            reason="Reason for the action",
            duration="Duration in minutes (for timeouts)",
            send_dm="Send DM notification to user",
            severity="Case severity level"
        )
        @discord.app_commands.choices(
            action=[
                discord.app_commands.Choice(name="Warning", value="warn"),
                discord.app_commands.Choice(name="Timeout", value="timeout"),
                discord.app_commands.Choice(name="Kick", value="kick"),
                discord.app_commands.Choice(name="Ban", value="ban"),
                discord.app_commands.Choice(name="Mod Note", value="mod_note")
            ],
            severity=[
                discord.app_commands.Choice(name="Low", value="Low"),
                discord.app_commands.Choice(name="Medium", value="Medium"),
                discord.app_commands.Choice(name="High", value="High"),
                discord.app_commands.Choice(name="Critical", value="Critical")
            ]
        )
        async def case_command(interaction: discord.Interaction, user: discord.Member, 
                              action: discord.app_commands.Choice[str], reason: str,
                              duration: int = None, send_dm: bool = True, 
                              severity: discord.app_commands.Choice[str] = None):
            await self.case_handler.handle_case_command(interaction, user, action, reason, duration, send_dm, severity)
        
        @self.bot.tree.command(name="resolve", description="Resolve an open moderation case")
        @discord.app_commands.describe(
            user="User whose case to resolve",
            case_number="Case number to resolve",
            resolution="Resolution comment"
        )
        async def resolve_command(interaction: discord.Interaction, user: discord.Member, 
                                case_number: int, resolution: str):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.case_handler.handle_resolve_command(interaction, user, case_number, resolution)
        
        # Statistics commands
        @self.bot.tree.command(name="stats", description="View moderation statistics")
        async def stats_command(interaction: discord.Interaction, user: discord.User = None):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.stats_handler.handle_stats_command(interaction, user)
        
        @self.bot.tree.command(name="modstats", description="View server-wide moderation statistics")
        @discord.app_commands.describe(timeframe="Time period for statistics")
        @discord.app_commands.choices(timeframe=[
            discord.app_commands.Choice(name="Last 24 Hours", value="24h"),
            discord.app_commands.Choice(name="Last 30 Days", value="30d"),
            discord.app_commands.Choice(name="This Year", value="year")
        ])
        async def modstats_command(interaction: discord.Interaction, timeframe: discord.app_commands.Choice[str] = None):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.stats_handler.handle_modstats_command(interaction, timeframe)
        
        @self.bot.tree.command(name="modreview", description="View and review moderator performance")
        async def modreview_command(interaction: discord.Interaction, moderator: discord.Member):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.stats_handler.handle_modreview_command(interaction, moderator)
        
        # Psychosis management
        @self.bot.tree.command(name="psychosis", description="Apply psychosis management actions to a user")
        async def psychosis_command(interaction: discord.Interaction, user: discord.Member):
            if not self.check_mod_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await self.psychosis_handler.handle_psychosis_command(interaction, user)
        
        # Admin commands - REMOVED SETTINGS COMMAND
        @self.bot.tree.command(name="force_sync", description="Force sync commands (admin only)")
        async def force_sync_command(interaction: discord.Interaction):
            if not self.check_admin_permissions(interaction):
                await interaction.response.send_message("❌ You need admin permissions to use this command.", ephemeral=True)
                return
            await self.admin_handler.handle_force_sync_command(interaction)
        
        @self.bot.tree.command(name="dashboard", description="Get dashboard information and links")
        async def dashboard_command(interaction: discord.Interaction):
            await self.admin_handler.handle_dashboard_command(interaction)