# views/psychosis_views.py
import discord
from datetime import datetime, timedelta
from typing import Dict, Any

class PsychosisActionView(discord.ui.View):
    def __init__(self, target_user: discord.Member, psychosis_manager):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.psychosis_manager = psychosis_manager

    @discord.ui.button(label="Silence (Text)", style=discord.ButtonStyle.secondary, emoji="🔇")
    async def silence_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PsychosisModal(self.target_user, self.psychosis_manager, "silence")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Voice Timeout", style=discord.ButtonStyle.secondary, emoji="🎤")
    async def voice_timeout_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PsychosisModal(self.target_user, self.psychosis_manager, "voice_timeout")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Full Restriction", style=discord.ButtonStyle.danger, emoji="🔒")
    async def full_restriction_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PsychosisModal(self.target_user, self.psychosis_manager, "full_restriction")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Isolation", style=discord.ButtonStyle.danger, emoji="🧠")
    async def isolation_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PsychosisModal(self.target_user, self.psychosis_manager, "isolation")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Action Cancelled",
            description="Psychosis management action has been cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ExistingRestrictionView(discord.ui.View):
    def __init__(self, target_user: discord.Member, restriction_data: Dict[str, Any], psychosis_manager):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.restriction_data = restriction_data
        self.psychosis_manager = psychosis_manager

    @discord.ui.button(label="Remove Restriction", style=discord.ButtonStyle.danger, emoji="🔓")
    async def remove_restriction(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveRestrictionModal(self.target_user, self.restriction_data, self.psychosis_manager)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Extend Duration", style=discord.ButtonStyle.secondary, emoji="⏰")
    async def extend_restriction(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ExtendRestrictionModal(self.target_user, self.restriction_data, self.psychosis_manager)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Action Cancelled",
            description="No changes made to existing restriction.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PsychosisModal(discord.ui.Modal):
    def __init__(self, target_user: discord.Member, psychosis_manager, restriction_type: str):
        super().__init__(title=f"Apply {restriction_type.replace('_', ' ').title()}")
        self.target_user = target_user
        self.psychosis_manager = psychosis_manager
        self.restriction_type = restriction_type

        self.duration = discord.ui.TextInput(
            label="Duration (minutes)",
            placeholder="60",
            required=True,
            max_length=10
        )

        self.user_comment = discord.ui.TextInput(
            label="Message to User (Public in psychosis channel)",
            style=discord.TextStyle.paragraph,
            placeholder="Supportive message that will be posted in the psychosis channel...",
            required=False,
            max_length=1000
        )

        self.mod_comment = discord.ui.TextInput(
            label="Internal Mod Notes",
            style=discord.TextStyle.paragraph,
            placeholder="Internal notes about this restriction...",
            required=True,
            max_length=1000
        )

        self.add_item(self.duration)
        self.add_item(self.user_comment)
        self.add_item(self.mod_comment)

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

            # Apply the restriction
            success = await self.psychosis_manager.apply_restriction(
                interaction.client,
                interaction.guild,
                self.target_user,
                self.restriction_type,
                duration_minutes,
                interaction.user,
                self.user_comment.value,
                self.mod_comment.value
            )

            if success:
                embed = discord.Embed(
                    title="✅ Psychosis Restriction Applied",
                    description=f"{self.restriction_type.replace('_', ' ').title()} restriction has been applied to {self.target_user.display_name}",
                    color=discord.Color.green()
                )

                embed.add_field(name="Duration", value=f"{duration_minutes} minutes", inline=True)
                embed.add_field(name="Type", value=self.restriction_type.replace('_', ' ').title(), inline=True)
                embed.add_field(name="Applied By", value=interaction.user.display_name, inline=True)

                if self.user_comment.value:
                    embed.add_field(name="Public Message", value=self.user_comment.value[:500], inline=False)

                embed.add_field(name="Internal Notes", value=self.mod_comment.value[:500], inline=False)

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Failed to apply psychosis restriction. Check bot permissions.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error applying restriction: {str(e)}", ephemeral=True)

class RemoveRestrictionModal(discord.ui.Modal):
    def __init__(self, target_user: discord.Member, restriction_data: Dict[str, Any], psychosis_manager):
        super().__init__(title="Remove Psychosis Restriction")
        self.target_user = target_user
        self.restriction_data = restriction_data
        self.psychosis_manager = psychosis_manager

        self.reason = discord.ui.TextInput(
            label="Reason for Removal",
            style=discord.TextStyle.paragraph,
            placeholder="Why is this restriction being removed early?",
            required=True,
            max_length=500
        )

        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            success = await self.psychosis_manager.remove_restriction(
                interaction.client,
                self.target_user.id,
                f"Manual removal by {interaction.user.display_name}: {self.reason.value}"
            )

            if success:
                embed = discord.Embed(
                    title="✅ Psychosis Restriction Removed",
                    description=f"Restriction has been removed from {self.target_user.display_name}",
                    color=discord.Color.green()
                )

                embed.add_field(name="Removed By", value=interaction.user.display_name, inline=True)
                embed.add_field(name="Reason", value=self.reason.value, inline=False)

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Failed to remove psychosis restriction.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error removing restriction: {str(e)}", ephemeral=True)

class ExtendRestrictionModal(discord.ui.Modal):
    def __init__(self, target_user: discord.Member, restriction_data: Dict[str, Any], psychosis_manager):
        super().__init__(title="Extend Psychosis Restriction")
        self.target_user = target_user
        self.restriction_data = restriction_data
        self.psychosis_manager = psychosis_manager

        self.additional_minutes = discord.ui.TextInput(
            label="Additional Minutes",
            placeholder="30",
            required=True,
            max_length=10
        )

        self.reason = discord.ui.TextInput(
            label="Reason for Extension",
            style=discord.TextStyle.paragraph,
            placeholder="Why is this restriction being extended?",
            required=True,
            max_length=500
        )

        self.add_item(self.additional_minutes)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            # Validate additional minutes
            try:
                additional_minutes = int(self.additional_minutes.value)
                if additional_minutes <= 0:
                    await interaction.followup.send("❌ Additional minutes must be greater than 0.", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("❌ Invalid duration. Please enter a number.", ephemeral=True)
                return

            # Update restriction data
            current_duration = self.restriction_data.get("duration_minutes", 0)
            new_duration = current_duration + additional_minutes
            
            self.restriction_data["duration_minutes"] = new_duration
            self.psychosis_manager.add_user_restriction(self.target_user.id, self.restriction_data)

            # Restart timer with new duration
            await self.psychosis_manager.timer_manager.start_restriction_timer(
                interaction.client,
                self.target_user.id,
                self.restriction_data.get("type", "unknown"),
                additional_minutes  # Only extend by the additional time
            )

            embed = discord.Embed(
                title="✅ Psychosis Restriction Extended",
                description=f"Restriction for {self.target_user.display_name} has been extended",
                color=discord.Color.yellow()
            )

            embed.add_field(name="Extended By", value=interaction.user.display_name, inline=True)
            embed.add_field(name="Additional Time", value=f"{additional_minutes} minutes", inline=True)
            embed.add_field(name="New Total Duration", value=f"{new_duration} minutes", inline=True)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error extending restriction: {str(e)}", ephemeral=True)