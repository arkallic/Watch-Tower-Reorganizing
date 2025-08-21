# views/moderation_views.py
import discord
from .moderation.action_view import ModActionView
from .moderation.modals import WarnModal, TimeoutModal, KickModal, BanModal, ModNoteModal

def create_mod_action_view(target_user: discord.Member, moderator: discord.Member, 
                          moderation_manager, is_flagged_message: bool = False,
                          flagged_message: str = "", message_url: str = ""):
    """Factory function to create moderation action view"""
    return ModActionView(
        target_user, moderation_manager, is_flagged_message,
        flagged_message, message_url
    )

# Re-export all view classes for backward compatibility
__all__ = [
    'ModActionView',
    'WarnModal',
    'TimeoutModal', 
    'KickModal',
    'BanModal',
    'ModNoteModal',
    'create_mod_action_view'
]