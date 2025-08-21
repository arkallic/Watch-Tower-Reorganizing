# commands/command_handlers/stats_handler.py
import discord
from datetime import datetime, timedelta
from .base_handler import BaseHandler

class StatsHandler(BaseHandler):
    """Handler for statistics-related commands"""
    
    async def handle_stats_command(self, interaction: discord.Interaction, user: discord.User = None):
        """Handle user or server statistics"""
        if user:
            await self._handle_user_stats(interaction, user)
        else:
            await self._handle_server_stats(interaction)
    
    async def _handle_user_stats(self, interaction: discord.Interaction, user: discord.User):
        """Handle individual user statistics"""
        self.log_command("UserStats", interaction.user, f"Target: {user.name}")
        
        await interaction.response.defer()
        
        try:
            # Get user statistics
            user_stats = self.moderation_manager.statistics_manager.get_user_stats(user.id)
            
            # Get AI flags if available
            ai_flags = {}
            if hasattr(self.logger, 'get_user_flags'):
                ai_flags = self.logger.get_user_flags(user.id, 168)  # Last week
            
            embed = discord.Embed(
                title=f"📊 Statistics for {user.display_name}",
                description="Comprehensive user statistics and history",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Basic stats
            embed.add_field(
                name="📋 Moderation History",
                value=f"**Total Cases:** {user_stats.get('total_cases', 0)}\n**Open Cases:** {user_stats.get('open_cases', 0)}\n**Warnings:** {user_stats.get('warns', 0)}\n**Timeouts:** {user_stats.get('timeouts', 0)}",
                inline=True
            )
            
            # Recent activity
            embed.add_field(
                name="📅 Recent Activity",
                value=f"**Cases (30d):** {user_stats.get('recent_cases_30d', 0)}\n**Escalation Level:** {user_stats.get('escalation_level', 0)}\n**Trend:** {user_stats.get('trend', 'stable').title()}",
                inline=True
            )
            
            # AI monitoring if available
            if ai_flags:
                embed.add_field(
                    name="🤖 AI Monitoring",
                    value=f"**Total Flags:** {ai_flags.get('total_flags', 0)}\n**Recent Flags:** {ai_flags.get('recent_flags', 0)}\n**Avg Confidence:** {ai_flags.get('avg_confidence', 0)}%",
                    inline=True
                )
            
            # Severity breakdown
            severity_breakdown = user_stats.get('severity_breakdown', {})
            if severity_breakdown:
                severity_text = "\n".join([f"**{sev}:** {count}" for sev, count in severity_breakdown.items() if count > 0])
                embed.add_field(
                    name="🎯 Case Severity",
                    value=severity_text or "No cases",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating user statistics: {str(e)}", ephemeral=True)
    
    async def _handle_server_stats(self, interaction: discord.Interaction):
        """Handle server-wide statistics"""
        self.log_command("ServerStats", interaction.user, "Server overview")
        
        await interaction.response.defer()
        
        try:
            # Get server statistics
            server_stats = self.moderation_manager.statistics_manager.get_moderation_summary(30)
            
            embed = discord.Embed(
                title="📊 Server Statistics",
                description="Server-wide moderation statistics (Last 30 days)",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Overview stats
            embed.add_field(
                name="📋 Overview",
                value=f"**Total Cases:** {server_stats.get('total_cases', 0)}\n**Open Cases:** {server_stats.get('open_cases', 0)}\n**Resolution Rate:** {server_stats.get('resolution_rate', 0):.1f}%\n**Unique Users:** {server_stats.get('unique_users_moderated', 0)}",
                inline=True
            )
            
            # Action breakdown
            action_breakdown = server_stats.get('action_breakdown', {})
            if action_breakdown:
                action_text = "\n".join([f"**{action.title()}:** {count}" for action, count in sorted(action_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]])
                embed.add_field(
                    name="⚖️ Top Actions",
                    value=action_text,
                    inline=True
                )
            
            # Top moderators
            mod_activity = server_stats.get('moderator_activity', {})
            if mod_activity:
                mod_text = "\n".join([f"**{mod}:** {cases}" for mod, cases in list(mod_activity.items())[:5]])
                embed.add_field(
                    name="🏆 Top Moderators",
                    value=mod_text,
                    inline=True
                )
            
            # Daily activity trend
            daily_activity = server_stats.get('daily_activity', {})
            if daily_activity:
                avg_daily = server_stats.get('avg_cases_per_day', 0)
                embed.add_field(
                    name="📈 Activity Trend",
                    value=f"**Avg Cases/Day:** {avg_daily:.1f}\n**Most Active Day:** {max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else 'N/A'}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating server statistics: {str(e)}", ephemeral=True)
    
    async def handle_modstats_command(self, interaction: discord.Interaction, timeframe):
        """Handle server-wide moderation statistics with timeframe"""
        self.log_command("ModStats", interaction.user, f"Timeframe: {timeframe.value if timeframe else 'all'}")
        
        await interaction.response.defer()
        
        try:
            # Calculate time window
            now = datetime.now()
            if timeframe:
                if timeframe.value == "24h":
                    days = 1
                    timeframe_name = "Last 24 Hours"
                elif timeframe.value == "30d":
                    days = 30
                    timeframe_name = "Last 30 Days"
                elif timeframe.value == "year":
                    days = 365
                    timeframe_name = "This Year"
                else:
                    days = 30
                    timeframe_name = "Last 30 Days"
            else:
                days = 30
                timeframe_name = "Last 30 Days"
            
            # Get statistics
            stats = self.moderation_manager.statistics_manager.get_moderation_summary(days)
            
            embed = discord.Embed(
                title="📊 Server Moderation Statistics",
                description=f"Comprehensive statistics for **{timeframe_name}**",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Case statistics
            embed.add_field(
                name="📋 Case Statistics",
                value=f"**Total Cases:** {stats.get('total_cases', 0)}\n**Open Cases:** {stats.get('open_cases', 0)}\n**Resolved Cases:** {stats.get('resolved_cases', 0)}\n**Resolution Rate:** {stats.get('resolution_rate', 0):.1f}%",
                inline=True
            )
            
            # Activity metrics
            embed.add_field(
                name="📈 Activity Metrics",
                value=f"**Unique Users:** {stats.get('unique_users_moderated', 0)}\n**Avg Cases/Day:** {stats.get('avg_cases_per_day', 0):.1f}\n**Period:** {days} days",
                inline=True
            )
            
            # Action breakdown
            action_breakdown = stats.get('action_breakdown', {})
            if action_breakdown:
                action_text = "\n".join([f"**{action.title()}:** {count}" for action, count in sorted(action_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]])
                embed.add_field(
                    name="⚖️ Top Actions",
                    value=action_text,
                    inline=True
                )
            
            # Severity breakdown
            severity_breakdown = stats.get('severity_breakdown', {})
            if severity_breakdown:
                severity_text = "\n".join([f"**{sev}:** {count}" for sev, count in severity_breakdown.items() if count > 0])
                embed.add_field(
                    name="🎯 Case Severity",
                    value=severity_text,
                    inline=True
                )
            
            # Top moderators
            mod_activity = stats.get('moderator_activity', {})
            if mod_activity:
                mod_text = "\n".join([f"**{mod}:** {cases}" for mod, cases in list(mod_activity.items())[:5]])
                embed.add_field(
                    name="🏆 Active Moderators",
                    value=mod_text,
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating moderation statistics: {str(e)}", ephemeral=True)
    
    async def handle_modreview_command(self, interaction: discord.Interaction, moderator: discord.Member):
        """Handle moderator performance review"""
        self.log_command("ModReview", interaction.user, f"Target: {moderator.name}")
        
        await interaction.response.defer()
        
        try:
            # Get moderator statistics
            mod_stats = self.moderation_manager.statistics_manager.get_moderator_stats(moderator.display_name, 30)
            
            if "message" in mod_stats:
                await interaction.followup.send(f"ℹ️ {mod_stats['message']}", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🏆 Moderator Review - {moderator.display_name}",
                description="Performance review for the last 30 days",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url=moderator.display_avatar.url)
            
            # Activity overview
            embed.add_field(
                name="📊 Activity Overview",
                value=f"**Total Actions:** {mod_stats.get('total_actions', 0)}\n**Actions/Day:** {mod_stats.get('actions_per_day', 0):.1f}\n**Unique Users:** {mod_stats.get('unique_users_moderated', 0)}",
                inline=True
            )
            
            # Action breakdown
            action_breakdown = mod_stats.get('action_breakdown', {})
            if action_breakdown:
                action_text = "\n".join([f"**{action.title()}:** {count}" for action, count in sorted(action_breakdown.items(), key=lambda x: x[1], reverse=True)])
                embed.add_field(
                    name="⚖️ Action Types",
                    value=action_text,
                    inline=True
                )
            
            # Severity focus
            severity_breakdown = mod_stats.get('severity_breakdown', {})
            if severity_breakdown:
                severity_text = "\n".join([f"**{sev}:** {count}" for sev, count in severity_breakdown.items() if count > 0])
                embed.add_field(
                    name="🎯 Case Severity Focus",
                    value=severity_text,
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating moderator review: {str(e)}", ephemeral=True)