# managers/moderation/message_collector.py
import discord
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

class MessageCollector:
    def __init__(self, logger):
        self.logger = logger
    
    async def collect_user_messages(self, guild: discord.Guild, user_id: int, 
                                  limit: int = 10, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Collect recent messages from a user across all channels"""
        messages = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        try:
            # Get the user
            user = guild.get_member(user_id)
            if not user:
                self.logger.console_log_system(f"User {user_id} not found in guild", "WARNING")
                return []
            
            # Search through all text channels
            for channel in guild.text_channels:
                try:
                    # Check bot permissions
                    if not channel.permissions_for(guild.me).read_message_history:
                        continue
                    
                    # Collect messages from this channel
                    channel_messages = await self._collect_from_channel(
                        channel, user, cutoff_time, limit
                    )
                    messages.extend(channel_messages)
                    
                    # Stop if we have enough messages
                    if len(messages) >= limit:
                        break
                        
                except discord.Forbidden:
                    continue
                except Exception as e:
                    self.logger.console_log_system(f"Error collecting from {channel.name}: {e}", "WARNING")
                    continue
            
            # Sort by timestamp (newest first) and limit
            messages.sort(key=lambda x: x['timestamp'], reverse=True)
            return messages[:limit]
            
        except Exception as e:
            self.logger.console_log_system(f"Error collecting user messages: {e}", "ERROR")
            return []
    
    async def _collect_from_channel(self, channel: discord.TextChannel, user: discord.Member,
                                  cutoff_time: datetime, limit: int) -> List[Dict[str, Any]]:
        """Collect messages from a specific channel"""
        messages = []
        
        try:
            async for message in channel.history(limit=200, after=cutoff_time):
                if message.author.id == user.id:
                    message_data = {
                        'id': message.id,
                        'content': message.content,
                        'timestamp': message.created_at.isoformat(),
                        'channel': channel.name,
                        'channel_id': channel.id,
                        'attachments': [att.url for att in message.attachments],
                        'embeds': len(message.embeds),
                        'reactions': len(message.reactions),
                        'jump_url': message.jump_url
                    }
                    messages.append(message_data)
                    
                    if len(messages) >= limit:
                        break
            
            return messages
            
        except Exception as e:
            self.logger.console_log_system(f"Error collecting from channel {channel.name}: {e}", "WARNING")
            return []
    
    async def collect_evidence_for_case(self, guild: discord.Guild, user_id: int,
                                      case_number: int, context_messages: int = 5) -> Dict[str, Any]:
        """Collect comprehensive evidence for a moderation case"""
        try:
            user = guild.get_member(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Collect recent messages
            recent_messages = await self.collect_user_messages(guild, user_id, context_messages)
            
            # Collect user info
            user_info = {
                'id': user.id,
                'username': user.name,
                'display_name': user.display_name,
                'avatar_url': str(user.display_avatar.url),
                'joined_at': user.joined_at.isoformat() if user.joined_at else None,
                'created_at': user.created_at.isoformat(),
                'roles': [role.name for role in user.roles[1:]],  # Exclude @everyone
                'top_role': user.top_role.name,
                'is_bot': user.bot,
                'status': str(user.status) if hasattr(user, 'status') else 'unknown'
            }
            
            # Collect server context
            server_info = {
                'name': guild.name,
                'id': guild.id,
                'member_count': guild.member_count,
                'collection_time': datetime.now().isoformat()
            }
            
            evidence = {
                'case_number': case_number,
                'user_info': user_info,
                'server_info': server_info,
                'recent_messages': recent_messages,
                'message_count': len(recent_messages),
                'channels_searched': len([ch for ch in guild.text_channels if ch.permissions_for(guild.me).read_message_history])
            }
            
            self.logger.console_log_system(
                f"Collected evidence for case #{case_number}: {len(recent_messages)} messages",
                "EVIDENCE"
            )
            
            return evidence
            
        except Exception as e:
            self.logger.console_log_system(f"Error collecting evidence: {e}", "ERROR")
            return {"error": str(e)}
    
    async def search_messages_by_content(self, guild: discord.Guild, search_term: str,
                                       user_id: Optional[int] = None, 
                                       channel_id: Optional[int] = None,
                                       days_back: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for messages containing specific content"""
        messages = []
        cutoff_time = datetime.now() - timedelta(days=days_back)
        search_term_lower = search_term.lower()
        
        try:
            # Determine channels to search
            channels_to_search = []
            if channel_id:
                channel = guild.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    channels_to_search = [channel]
            else:
                channels_to_search = guild.text_channels
            
            # Search through channels
            for channel in channels_to_search:
                try:
                    if not channel.permissions_for(guild.me).read_message_history:
                        continue
                    
                    async for message in channel.history(limit=500, after=cutoff_time):
                        # Filter by user if specified
                        if user_id and message.author.id != user_id:
                            continue
                        
                        # Check if message contains search term
                        if search_term_lower in message.content.lower():
                            message_data = {
                                'id': message.id,
                                'content': message.content,
                                'author': {
                                    'id': message.author.id,
                                    'name': message.author.name,
                                    'display_name': message.author.display_name
                                },
                                'timestamp': message.created_at.isoformat(),
                                'channel': channel.name,
                                'channel_id': channel.id,
                                'jump_url': message.jump_url,
                                'attachments': len(message.attachments),
                                'embeds': len(message.embeds)
                            }
                            messages.append(message_data)
                            
                            if len(messages) >= limit:
                                break
                    
                    if len(messages) >= limit:
                        break
                        
                except discord.Forbidden:
                    continue
                except Exception as e:
                    self.logger.console_log_system(f"Error searching {channel.name}: {e}", "WARNING")
                    continue
            
            # Sort by timestamp (newest first)
            messages.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self.logger.console_log_system(
                f"Found {len(messages)} messages containing '{search_term}'",
                "SEARCH"
            )
            
            return messages[:limit]
            
        except Exception as e:
            self.logger.console_log_system(f"Error searching messages: {e}", "ERROR")
            return []