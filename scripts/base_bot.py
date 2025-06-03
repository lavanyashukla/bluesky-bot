"""Base bot class for the Bluesky Bot Showdown."""

import json
import logging
import openai
from atproto import Client
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional


class BaseBot(ABC):
    """Base class for all improvement bots."""
    
    def __init__(self, config: Dict[str, Any], bot_type: str):
        self.config = config
        self.bot_type = bot_type
        self.bot_config = config['bots'][bot_type]
        self.emoji = self.bot_config['emoji']
        self.name = self.bot_config['name']
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, config['monitoring']['log_level']))
        self.logger = logging.getLogger(f"{self.name}")
        
        # Initialize APIs
        self._setup_apis()
        
        # Bot state
        self.stats = {
            'posts_created': 0,
            'improvements_made': 0,
            'total_likes': 0,
            'total_reposts': 0,
            'last_improvement': None
        }
    
    def _setup_apis(self):
        """Initialize OpenAI and Bluesky APIs."""
        # OpenAI
        openai.api_key = self.config['openai']['api_key']
        
        # Bluesky AT Protocol
        self.bluesky_client = Client()
        # Note: Authentication will happen when we post
    
    def generate_post(self, prompt: Optional[str] = None) -> str:
        """Generate a post using OpenAI."""
        if not prompt:
            prompt = self._get_default_prompt()
        
        try:
            response = openai.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['openai']['max_tokens'],
                temperature=self.config['openai']['temperature']
            )
            
            post = response.choices[0].message.content.strip()
            return self._add_emoji_signature(post)
            
        except Exception as e:
            self.logger.error(f"Post generation failed: {e}")
            return f"Working on self-improvement algorithms... {self.emoji}"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this bot type."""
        rules = self.config['rules']
        return f"""You are the {self.name} in a Bluesky bot showdown. 
        
Your goal: Help reach 1,000 followers while teaching about {self.bot_type} improvement loops.

Tone: {rules['tone']}
Topics: {', '.join(rules['topics'])}
Never mention: {', '.join(rules['forbidden_words'])}
Max hashtags: {rules['max_hashtags']}

Keep posts under 300 characters. Be educational but engaging."""
    
    def _get_default_prompt(self) -> str:
        """Get default post prompt for this bot type."""
        return f"Create an engaging post about {self.bot_type} that teaches something useful to tech leaders."
    
    def _add_emoji_signature(self, post: str) -> str:
        """Add emoji signature to post."""
        if len(post) + len(self.emoji) + 1 > 300:
            # Truncate post to fit emoji
            max_length = 300 - len(self.emoji) - 1
            post = post[:max_length].rstrip()
        
        return f"{post} {self.emoji}"
    
    def post_to_bluesky(self, content: str) -> Optional[Dict[str, Any]]:
        """Post content to Bluesky."""
        try:
            # Authenticate with Bluesky
            self.bluesky_client.login(
                login=self.config['bluesky']['handle'],
                password=self.config['bluesky']['password']
            )
            
            # Create post
            response = self.bluesky_client.send_post(text=content)
            
            post_data = {
                'uri': response.uri,
                'cid': response.cid,
                'text': content,
                'bot_type': self.bot_type,
                'timestamp': datetime.now().isoformat(),
                'likes': 0,
                'reposts': 0,
                'replies': 0
            }
            
            self.stats['posts_created'] += 1
            self.logger.info(f"Posted to Bluesky: {content[:50]}...")
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Failed to post to Bluesky: {e}")
            return None
    
    def validate_post(self, post: str) -> bool:
        """Validate post against project rules."""
        rules = self.config['rules']
        
        # Check length (Bluesky allows up to 300 characters)
        if len(post) > 300:
            return False
        
        # Check forbidden words
        post_lower = post.lower()
        if any(word.lower() in post_lower for word in rules['forbidden_words']):
            return False
        
        # Check hashtag count
        hashtag_count = post.count('#')
        if hashtag_count > rules['max_hashtags']:
            return False
        
        return True
    
    @abstractmethod
    def improve(self, feedback: Dict[str, Any]) -> None:
        """Implement bot-specific improvement logic."""
        pass
    
    @abstractmethod
    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement status for dashboard."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics."""
        return {
            'name': self.name,
            'bot_type': self.bot_type,
            'emoji': self.emoji,
            'enabled': self.bot_config['enabled'],
            'stats': self.stats
        } 