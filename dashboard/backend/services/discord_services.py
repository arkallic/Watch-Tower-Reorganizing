import discord
import asyncio
import os
from typing import Dict, List, Optional
from datetime import datetime

class DiscordService:
    def __init__(self, bot_token: str, guild_id: int):
        self.bot_token = bot_token
        self.guild_id = guild_id
        self.client = None
        self.guild = None
        
    async def initialize(self):
        """Initialize Discord client and connect"""
        intents = discord.Intents.default()
        intents.members = True  # Enable member intent
        intents.guilds = True
        
        self.client = discord.Client(intents=intents)
        
        @self.client.event
        async def on_ready():
            print(f'Discord service connected as {self.client.user}')
            self.guild = self.client.get_guild(self.guild_id)
            if not self.guild:
                print(f'Guild {self.guild_id} not found')
        
        await self.client.login(self.bot_token)
        # Don't call start() here, we'll handle connection differently
        
    async def get_all_members(self) -> List[Dict]:
        """Get all server members with detailed info"""
        if not self.guild:
            return []
            
        members = []
        async for member in self.guild.fetch_members(limit=None):
            member_data = {
                "user_id": str(member.id),
                "username": member.name,
                "display_name": member.display_name,
                "discriminator": member.discriminator,
                "avatar_url": str(member.avatar.url) if member.avatar else None,
                "banner_url": str(member.banner.url) if member.banner else None,
                "accent_color": member.accent_color,
                "created_at": member.created_at.isoformat(),
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "premium_since": member.premium_since.isoformat() if member.premium_since else None,
                "roles": [
                    {
                        "id": str(role.id),
                        "name": role.name,
                        "color": str(role.color),
                        "position": role.position,
                        "permissions": str(role.permissions.value)
                    }
                    for role in member.roles if role.name != "@everyone"
                ],
                "top_role": {
                    "id": str(member.top_role.id),
                    "name": member.top_role.name,
                    "color": str(member.top_role.color)
                } if member.top_role else None,
                "status": str(member.status),
                "activities": [
                    {
                        "name": activity.name,
                        "type": str(activity.type),
                        "details": getattr(activity, 'details', None),
                        "state": getattr(activity, 'state', None)
                    }
                    for activity in member.activities
                ],
                "bot": member.bot,
                "system": member.system,
                "mutual_guilds": len(member.mutual_guilds),
                "public_flags": str(member.public_flags) if member.public_flags else None
            }
            members.append(member_data)
            
        return members
    
    async def get_member(self, user_id: int) -> Optional[Dict]:
        """Get specific member details"""
        if not self.guild:
            return None
            
        try:
            member = await self.guild.fetch_member(user_id)
            return {
                "user_id": str(member.id),
                "username": member.name,
                "display_name": member.display_name,
                "discriminator": member.discriminator,
                "avatar_url": str(member.avatar.url) if member.avatar else None,
                "banner_url": str(member.banner.url) if member.banner else None,
                "accent_color": member.accent_color,
                "created_at": member.created_at.isoformat(),
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "premium_since": member.premium_since.isoformat() if member.premium_since else None,
                "roles": [
                    {
                        "id": str(role.id),
                        "name": role.name,
                        "color": str(role.color),
                        "position": role.position
                    }
                    for role in member.roles if role.name != "@everyone"
                ],
                "top_role": {
                    "name": member.top_role.name,
                    "color": str(member.top_role.color)
                } if member.top_role else None,
                "status": str(member.status),
                "bot": member.bot
            }
        except discord.NotFound:
            return None
            
    async def disconnect(self):
        """Clean disconnect"""
        if self.client:
            await self.client.close()

# Global service instance
discord_service = None

async def get_discord_service():
    """Get or create Discord service instance"""
    global discord_service
    if not discord_service:
        # You'll need to set these environment variables
        bot_token = os.getenv('DISCORD_BOT_TOKEN')
        guild_id = int(os.getenv('DISCORD_GUILD_ID'))
        
        discord_service = DiscordService(bot_token, guild_id)
        await discord_service.initialize()
    
    return discord_service