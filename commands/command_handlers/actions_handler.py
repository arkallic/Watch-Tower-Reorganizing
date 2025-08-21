# commands/command_handlers/actions_handler.py
import discord
from datetime import datetime
from .base_handler import BaseHandler

class ActionsHandler(BaseHandler):
    """Handler for action-related commands"""
    
    async def handle_actions_command(self, interaction: discord.Interaction, user: discord.Member):
        """Handle the /actions command with enhanced case data"""
        from views.moderation_views import create_mod_action_view
        
        self.log_command("Actions", interaction, f"Target: {user.name}")
        
        await interaction.response.defer()
        
        try:
            # Get user cases with enhanced data
            user_stats = self.moderation_manager.get_user_stats(user.id)
            user_data = self.moderation_manager.user_data.get(str(user.id), {})
            cases = user_data.get("cases", [])
            
            # Get AI flags
            ai_flags = self.logger.get_user_flags(user.id, 168)  # Last week
            
            embed = discord.Embed(
                title=f"🛡️ Moderation Actions - {user.display_name}",
                description=f"Complete moderation history and statistics",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # User info
            embed.add_field(
                name="👤 User Information",
                value=f"**Username:** {user.name}\n**Display Name:** {user.display_name}\n**ID:** {user.id}\n**Account Created:** <t:{int(user.created_at.timestamp())}:R>",
                inline=True
            )
            
            # Case statistics
            embed.add_field(
                name="📊 Case Statistics",
                value=f"**Total Cases:** {user_stats['total_cases']}\n**Open Cases:** {user_stats['open_cases']}\n**Warnings:** {user_stats['warns']}\n**Timeouts:** {user_stats['timeouts']}",
                inline=True
            )
            
            # AI & Flags
            embed.add_field(
                name="🤖 AI Monitoring",
                value=f"**Total Flags:** {ai_flags.get('total_flags', 0)}\n**Recent Flags (7d):** {ai_flags.get('recent_flags', 0)}\n**Escalation Level:** {user_stats.get('escalation_level', 0)}",
                inline=True
            )
            
            # Recent cases
            if cases:
                recent_cases = sorted(cases, key=lambda x: x.get("case_number", 0), reverse=True)[:5]
                case_text = ""
                for case in recent_cases:
                    status_emoji = "🟢" if case.get("status") == "Resolved" else "🟡" if case.get("status") == "Open" else "🔴"
                    case_text += f"{status_emoji} **Case #{case['case_number']}** - {case['action_type']}\n"
                    case_text += f"   *{case.get('reason', 'No reason')[:60]}...*\n"
                    case_text += f"   {case.get('moderator_name', 'Unknown')} • <t:{int(datetime.fromisoformat(case['created_at'].replace('Z', '+00:00')).timestamp())}:R>\n\n"
                
                embed.add_field(
                    name="📋 Recent Cases",
                    value=case_text[:1024],
                    inline=False
                )
            
            # Create action view
            view = create_mod_action_view(user, interaction.user, self.moderation_manager)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            await self.send_error(interaction, f"Error retrieving user actions: {str(e)}")