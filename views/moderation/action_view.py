# views/moderation/action_view.py
import discord
from datetime import datetime, timedelta
from .modals import WarnModal, TimeoutModal, KickModal, BanModal, ModNoteModal, SilenceModal

class ModActionView(discord.ui.View):
    def __init__(self, target_user: discord.Member, moderation_manager, is_flagged_message: bool = False, 
                 flagged_message: str = "", message_url: str = ""):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.moderation_manager = moderation_manager
        self.is_flagged_message = is_flagged_message
        self.flagged_message = flagged_message
        self.message_url = message_url

    @discord.ui.select(
        placeholder="Choose a moderation action...",
        options=[
            discord.SelectOption(label="Warn User", description="Issue a warning to the user", emoji="⚠️"),
            discord.SelectOption(label="Timeout User", description="Temporarily timeout the user", emoji="⏰"),
            discord.SelectOption(label="Add Mod Note", description="Add an internal note about the user", emoji="📝"),
            discord.SelectOption(label="Silence User", description="Remove messaging permissions", emoji="🔇"),
            discord.SelectOption(label="Kick User", description="Remove user from server", emoji="👢"),
            discord.SelectOption(label="Ban User", description="Permanently ban user from server", emoji="🔨"),
        ]
    )
    async def action_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        
        # ✅ CORRECT: Using logger through moderation manager
        self.moderation_manager.logger.console_log_command(f"Moderation Action - {action}", interaction.user, 
                                                         f"Target: {self.target_user.name}")
        
        if action == "Warn User":
            modal = WarnModal(self.target_user, self.moderation_manager, self.is_flagged_message, 
                            self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
        elif action == "Timeout User":
            modal = TimeoutModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                               self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
        elif action == "Add Mod Note":
            modal = ModNoteModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                               self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
        elif action == "Silence User":
            modal = SilenceModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                               self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
        elif action == "Kick User":
            modal = KickModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                            self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
        elif action == "Ban User":
            modal = BanModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                           self.flagged_message, self.message_url)
            await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="View Cases", style=discord.ButtonStyle.secondary, emoji="📋")
    async def view_cases(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View all cases for this user"""
        # ✅ CORRECT: Using our new case manager structure
        cases = self.moderation_manager.case_manager.get_user_cases(self.target_user.id)
        
        if not cases:
            embed = discord.Embed(
                title="📋 User Cases",
                description=f"{self.target_user.display_name} has no moderation cases.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Sort cases by case number (newest first)
        sorted_cases = sorted(cases, key=lambda x: x.get("case_number", 0), reverse=True)
        
        embed = discord.Embed(
            title=f"📋 Cases for {self.target_user.display_name}",
            description=f"Showing {len(cases)} total cases",
            color=discord.Color.blue()
        )
        
        # Show up to 10 most recent cases
        for case in sorted_cases[:10]:
            status_emoji = "🟢" if case.get("status") == "Resolved" else "🟡"
            case_text = f"{status_emoji} **{case.get('action_type', 'Unknown').title()}** - {case.get('severity', 'Medium')}\n"
            case_text += f"*{case.get('reason', 'No reason')[:60]}...*\n"
            case_text += f"By: {case.get('moderator_name', 'Unknown')}"
            
            embed.add_field(
                name=f"Case #{case.get('case_number', 'Unknown')}",
                value=case_text,
                inline=True
            )
        
        if len(cases) > 10:
            embed.set_footer(text=f"Showing 10 of {len(cases)} cases. Use /stats @{self.target_user.name} for full history.")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="User Profile", style=discord.ButtonStyle.secondary, emoji="👤")
    async def view_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View detailed user profile information"""
        try:
            # ✅ CORRECT: Using statistics manager through main manager
            user_stats = self.moderation_manager.statistics_manager.get_user_stats(self.target_user.id)
            
            # Get AI flags if logger is available
            ai_flags = {}
            if hasattr(self.moderation_manager, 'logger'):
                ai_flags = self.moderation_manager.logger.get_user_flags(self.target_user.id, 168)  # Last week
            
            embed = discord.Embed(
                title=f"👤 User Profile - {self.target_user.display_name}",
                description="Comprehensive user information and statistics",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url=self.target_user.display_avatar.url)
            
            # Basic information
            embed.add_field(
                name="📊 Basic Information",
                value=f"**Username:** {self.target_user.name}\n**Display Name:** {self.target_user.display_name}\n**User ID:** {self.target_user.id}\n**Account Created:** <t:{int(self.target_user.created_at.timestamp())}:R>",
                inline=True
            )
            
            # Server information
            joined_at = self.target_user.joined_at
            embed.add_field(
                name="🏠 Server Information",
                value=f"**Joined Server:** {f'<t:{int(joined_at.timestamp())}:R>' if joined_at else 'Unknown'}\n**Highest Role:** {self.target_user.top_role.name}\n**Role Count:** {len(self.target_user.roles) - 1}\n**Is Bot:** {'Yes' if self.target_user.bot else 'No'}",
                inline=True
            )
            
            # Moderation statistics
            embed.add_field(
                name="⚖️ Moderation History",
                value=f"**Total Cases:** {user_stats.get('total_cases', 0)}\n**Open Cases:** {user_stats.get('open_cases', 0)}\n**Warnings:** {user_stats.get('warns', 0)}\n**Timeouts:** {user_stats.get('timeouts', 0)}",
                inline=True
            )
            
            # AI monitoring (if available)
            if ai_flags:
                embed.add_field(
                    name="🤖 AI Monitoring",
                    value=f"**Total Flags:** {ai_flags.get('total_flags', 0)}\n**Recent Flags (7d):** {ai_flags.get('recent_flags', 0)}\n**Average Confidence:** {ai_flags.get('avg_confidence', 0)}%\n**Escalation Level:** {user_stats.get('escalation_level', 0)}",
                    inline=True
                )
            
            # Role list (if not too many)
            roles = [role.name for role in self.target_user.roles[1:]]  # Exclude @everyone
            if len(roles) <= 10:
                embed.add_field(
                    name="🎭 Roles",
                    value=", ".join(roles) if roles else "No special roles",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🎭 Roles",
                    value=f"{len(roles)} roles (too many to display)",
                    inline=True
                )
            
            # Key permissions summary
            key_permissions = []
            perms = self.target_user.guild_permissions
            if perms.administrator:
                key_permissions.append("Administrator")
            if perms.manage_guild:
                key_permissions.append("Manage Server")
            if perms.manage_channels:
                key_permissions.append("Manage Channels")
            if perms.manage_messages:
                key_permissions.append("Manage Messages")
            if perms.kick_members:
                key_permissions.append("Kick Members")
            if perms.ban_members:
                key_permissions.append("Ban Members")
            
            embed.add_field(
                name="🔑 Key Permissions",
                value=", ".join(key_permissions) if key_permissions else "No special permissions",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to load user profile: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @discord.ui.button(label="Quick Actions", style=discord.ButtonStyle.primary, emoji="⚡")
    async def quick_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show quick action menu for common moderation tasks"""
        embed = discord.Embed(
            title="⚡ Quick Actions",
            description=f"Quick moderation actions for {self.target_user.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔧 Available Quick Actions",
            value="• **5min Timeout** - Quick 5 minute timeout\n• **1hr Timeout** - Standard 1 hour timeout\n• **Remove Timeout** - Remove existing timeout\n• **Quick Warn** - Issue standard warning\n• **Collect Evidence** - Gather recent messages",
            inline=False
        )
        
        view = QuickActionsView(self.target_user, self.moderation_manager, self.is_flagged_message, 
                               self.flagged_message, self.message_url)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the moderation action"""
        embed = discord.Embed(
            title="❌ Action Cancelled",
            description="Moderation action has been cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Disable the view
        for item in self.children:
            item.disabled = True
        
        try:
            await interaction.edit_original_response(view=self)
        except:
            pass  # Message might have been deleted

class QuickActionsView(discord.ui.View):
    def __init__(self, target_user: discord.Member, moderation_manager, is_flagged_message: bool = False,
                 flagged_message: str = "", message_url: str = ""):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.moderation_manager = moderation_manager
        self.is_flagged_message = is_flagged_message
        self.flagged_message = flagged_message
        self.message_url = message_url

    @discord.ui.button(label="5min Timeout", style=discord.ButtonStyle.secondary, emoji="⏰")
    async def quick_timeout_5min(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Apply a quick 5-minute timeout"""
        try:
            await interaction.response.defer()
            
            # ✅ CORRECT: Using action executor through main manager
            success = await self.moderation_manager.action_executor.timeout_user(
                interaction.guild,
                self.target_user,
                5,  # 5 minutes
                "Quick timeout - 5 minutes",
                interaction.user,
                send_dm=False
            )
            
            if not success:
                await interaction.followup.send("❌ Failed to apply timeout. Check bot permissions.", ephemeral=True)
                return
            
            # ✅ CORRECT: Using new case creation method
            action_data = {
                "action_type": "timeout",
                "reason": "Quick timeout - 5 minutes",
                "severity": "Low",
                "duration": 5,
                "dm_sent": False,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            embed = discord.Embed(
                title="✅ Quick Timeout Applied",
                description=f"5-minute timeout applied to {self.target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Case Number", value=f"#{case_number}", inline=True)
            embed.add_field(name="Duration", value="5 minutes", inline=True)
            embed.add_field(name="Auto-Resolves", value=f"<t:{int((datetime.now() + timedelta(minutes=5)).timestamp())}:R>", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error applying timeout: {str(e)}", ephemeral=True)

    @discord.ui.button(label="1hr Timeout", style=discord.ButtonStyle.secondary, emoji="⏰")
    async def quick_timeout_1hr(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Apply a quick 1-hour timeout"""
        try:
            await interaction.response.defer()
            
            # ✅ CORRECT: Using action executor
            success = await self.moderation_manager.action_executor.timeout_user(
                interaction.guild,
                self.target_user,
                60,  # 60 minutes
                "Quick timeout - 1 hour",
                interaction.user,
                send_dm=False
            )
            
            if not success:
                await interaction.followup.send("❌ Failed to apply timeout. Check bot permissions.", ephemeral=True)
                return
            
            # ✅ CORRECT: Using new case creation method
            action_data = {
                "action_type": "timeout",
                "reason": "Quick timeout - 1 hour",
                "severity": "Medium",
                "duration": 60,
                "dm_sent": False,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            embed = discord.Embed(
                title="✅ Quick Timeout Applied",
                description=f"1-hour timeout applied to {self.target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Case Number", value=f"#{case_number}", inline=True)
            embed.add_field(name="Duration", value="1 hour", inline=True)
            embed.add_field(name="Auto-Resolves", value=f"<t:{int((datetime.now() + timedelta(hours=1)).timestamp())}:R>", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error applying timeout: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Remove Timeout", style=discord.ButtonStyle.success, emoji="🔓")
    async def remove_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove existing timeout"""
        try:
            await interaction.response.defer()
            
            if not self.target_user.is_timed_out():
                await interaction.followup.send("❌ User is not currently timed out.", ephemeral=True)
                return
            
            # Remove timeout directly (this is a Discord API call, not our moderation action)
            await self.target_user.timeout(None, reason=f"Timeout removed by {interaction.user.display_name}")
            
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"Timeout removed from {self.target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Removed By", value=interaction.user.display_name, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to modify this user's timeout.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error removing timeout: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Quick Warn", style=discord.ButtonStyle.secondary, emoji="⚠️")
    async def quick_warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Issue a quick warning"""
        modal = QuickWarnModal(self.target_user, self.moderation_manager, self.is_flagged_message,
                              self.flagged_message, self.message_url)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Collect Evidence", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def collect_evidence(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Collect recent messages from the user"""
        try:
            await interaction.response.defer()
            
            # ✅ CORRECT: Using delegated method that calls message_collector internally
            messages = await self.moderation_manager.collect_user_messages(
                interaction.guild, self.target_user.id, limit=10
            )
            
            if not messages:
                await interaction.followup.send("❌ No recent messages found for this user.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🔍 Evidence Collection",
                description=f"Recent messages from {self.target_user.display_name}",
                color=discord.Color.blue()
            )
            
            for i, msg in enumerate(messages[:5], 1):  # Show top 5 messages
                timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                
                embed.add_field(
                    name=f"Message {i} - #{msg['channel']}",
                    value=f"**Content:** {content}\n**Time:** <t:{int(timestamp.timestamp())}:R>",
                    inline=False
                )
            
            if len(messages) > 5:
                embed.set_footer(text=f"Showing 5 of {len(messages)} collected messages")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error collecting evidence: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go back to main moderation view"""
        main_view = ModActionView(self.target_user, self.moderation_manager, self.is_flagged_message,
                                 self.flagged_message, self.message_url)
        
        embed = discord.Embed(
            title=f"🛡️ Moderation Actions - {self.target_user.display_name}",
            description="Choose a moderation action to take",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=main_view)

class QuickWarnModal(discord.ui.Modal):
    def __init__(self, target_user: discord.Member, moderation_manager, is_flagged_message: bool = False,
                 flagged_message: str = "", message_url: str = ""):
        super().__init__(title="Quick Warning")
        self.target_user = target_user
        self.moderation_manager = moderation_manager
        self.is_flagged_message = is_flagged_message
        self.flagged_message = flagged_message
        self.message_url = message_url

        self.reason = discord.ui.TextInput(
            label="Warning Reason",
            style=discord.TextStyle.paragraph,
            placeholder="Enter the reason for this warning...",
            required=True,
            max_length=500
        )

        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            reason = self.reason.value
            
            # ✅ CORRECT: Using new case creation method
            action_data = {
                "action_type": "warn",
                "reason": reason,
                "severity": "Low",
                "duration": None,
                "dm_sent": False,
                "moderator_name": interaction.user.display_name,
                "display_name": self.target_user.display_name,
                "username": self.target_user.name
            }
            
            case_number = await self.moderation_manager.create_moderation_case(self.target_user.id, action_data)
            
            embed = discord.Embed(
                title="✅ Quick Warning Issued",
                description=f"Warning has been issued to {self.target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Case Number", value=f"#{case_number}", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            if self.is_flagged_message:
                embed.add_field(name="🚨 Related to Flagged Message", value=self.flagged_message[:200], inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error issuing warning: {str(e)}", ephemeral=True)