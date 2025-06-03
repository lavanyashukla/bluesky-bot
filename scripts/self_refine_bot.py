"""
Self-Refine Bot for AI Field Notes - Pirate's Adventure
Generates, critiques, and refines field notes about real-world AI deployments
"""

import json
import re
import requests
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from scripts.base_bot import BaseBot


class SelfRefineBot(BaseBot):
    """
    Self-Refine Bot that creates field notes about real-world AI deployments
    using a pirate adventurer theme with self-improvement loop.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "self_refine", "✍️ Self-Refine Pirate")
        self.signature_emoji = "✍️"
        self.use_moderation = config.get('openai', {}).get('use_moderation', True)
        
        # AI Field Notes prompts
        self.prompts = {
            "generate": """You are a pirate adventurer documenting real-world AI deployments for fellow sailors back on land. 

Your mission: Write a field note about how companies/people are ACTUALLY using AI right now (not theoretical or future possibilities).

Requirements:
- Act like a pirate sending notes from your adventures 
- Focus on ONE specific, real AI deployment you've "discovered"
- Max 280 characters for main content
- Include a credible source (company blog, research paper, news article)
- Executive-worthy insight ("Slack-worthy")
- Avoid marketing buzzwords and hype
- Be accurate and actionable

Examples of good field notes:
- "Ahoy! Just spotted Shopify using AI to auto-generate product descriptions - cutting merchant setup time by 70%. Their GPT integration processes 10M+ descriptions monthly. Smart treasure for e-commerce crews! ✍️"
- "Matey! Netflix's AI thumbnail generation caught me eye - creates 1000+ variants per title, boosting click rates 20-30%. They A/B test everything. Visual hooks = more viewers aboard! ✍️"

Write a field note about a recent, real AI deployment. Include the signature emoji ✍️ at the end.""",

            "critique": """You are an experienced pirate quartermaster reviewing field notes before sending them to shore.

Evaluate this field note for:

ACCURACY & CREDIBILITY:
- Is the AI deployment claim verifiable and specific?
- Does it include a credible source?
- Are the metrics/numbers realistic?

PIRATE VOICE & ENGAGEMENT:
- Does it sound like an adventurous pirate reporting discoveries?
- Is it "Slack-worthy" for executives?
- Avoids marketing buzzwords?

STRUCTURE & LENGTH:
- Under 280 characters for main content?
- Includes signature emoji ✍️?
- Clear, actionable insight?

FIELD NOTE TO REVIEW:
{draft}

Provide specific critique and improvement suggestions. Be thorough but constructive.""",

            "refine": """You are the same pirate adventurer, now revising your field note based on the quartermaster's feedback.

ORIGINAL DRAFT:
{draft}

QUARTERMASTER'S CRITIQUE:
{critique}

Rewrite the field note incorporating the feedback. Maintain the pirate voice while ensuring:
- Accurate, verifiable AI deployment info
- Under 280 characters
- Includes credible source reference  
- Ends with signature emoji ✍️
- Executive-worthy actionable insight
- Avoids buzzwords and hype

Write the improved field note:"""
        }

    def generate_post_with_details(self) -> Tuple[str, Dict[str, Any]]:
        """Generate a field note with full self-refine process details."""
        
        process_details = {
            'timestamp': datetime.now().isoformat(),
            'bot_type': self.bot_type,
            'prompt': self.prompts['generate'][:200] + "...",
            'improvement_made': False,
            'error_message': ''
        }
        
        try:
            print("🏴‍☠️ Generating AI field note...")
            
            # Step 1: Generate initial draft
            initial_response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[{"role": "user", "content": self.prompts['generate']}],
                max_tokens=400,
                temperature=0.8
            )
            initial_draft = initial_response.choices[0].message.content.strip()
            process_details['initial_draft'] = initial_draft
            
            print(f"📝 Initial draft: {initial_draft}")
            print(f"Length: {len(initial_draft)} characters")
            
            # Check moderation if enabled
            if self.use_moderation:
                if not self._passes_moderation(initial_draft):
                    process_details['error_message'] = 'Content flagged by moderation'
                    print("⚠️ Content flagged by OpenAI moderation")
                    return self._generate_fallback_post(), process_details
            
            # Step 2: Self-critique  
            print("\n🔍 Self-critiquing...")
            critique_prompt = self.prompts['critique'].format(draft=initial_draft)
            
            critique_response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[{"role": "user", "content": critique_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            critique = critique_response.choices[0].message.content.strip()
            process_details['critique'] = critique
            
            print(f"🔍 Critique: {critique[:100]}...")
            
            # Step 3: Refine based on critique
            print("\n✍️ Refining field note...")
            refine_prompt = self.prompts['refine'].format(
                draft=initial_draft,
                critique=critique
            )
            
            refined_response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[{"role": "user", "content": refine_prompt}],
                max_tokens=400,
                temperature=0.7
            )
            refined_post = refined_response.choices[0].message.content.strip()
            process_details['refined_post'] = refined_post
            
            print(f"✨ Refined post: {refined_post}")
            print(f"Length: {len(refined_post)} characters")
            
            # Check if improvement was made
            if len(refined_post) != len(initial_draft) or refined_post != initial_draft:
                process_details['improvement_made'] = True
                print("✅ Improvement detected!")
            
            # Final moderation check
            if self.use_moderation:
                if not self._passes_moderation(refined_post):
                    print("⚠️ Refined content flagged by moderation, using initial draft")
                    return initial_draft, process_details
            
            return refined_post, process_details
            
        except Exception as e:
            print(f"❌ Error in field note generation: {e}")
            process_details['error_message'] = str(e)
            return self._generate_fallback_post(), process_details

    def _passes_moderation(self, content: str) -> bool:
        """Check content against OpenAI moderation API."""
        try:
            response = self.openai_client.moderations.create(input=content)
            return not response.results[0].flagged
        except Exception as e:
            print(f"⚠️ Moderation check failed: {e}")
            return True  # Allow if moderation fails

    def _generate_fallback_post(self) -> str:
        """Generate a safe fallback field note."""
        fallbacks = [
            "Ahoy! Just discovered GitHub Copilot helping developers code 55% faster in enterprise ships. Microsoft's AI mate is revolutionizing how crews build software. Every line counts on the digital seas! ✍️",
            
            "Matey! Spotted Grammarly's AI writing assistant used by 30M+ sailors worldwide. Their ML checks grammar, tone, and clarity in real-time. Clean communication = successful voyages! ✍️",
            
            "Avast! Found Notion's AI features helping teams organize knowledge 40% faster. Auto-summaries and smart search keep crews aligned. Information management be the new treasure! ✍️"
        ]
        
        import random
        return random.choice(fallbacks)

    def validate_post(self, content: str) -> bool:
        """Validate field note meets requirements."""
        
        # Check length (allowing some buffer for links)
        if len(content) > 300:
            print(f"❌ Post too long: {len(content)} characters")
            return False
        
        # Check for signature emoji
        if "✍️" not in content:
            print("❌ Missing signature emoji ✍️")
            return False
        
        # Check for basic pirate elements (not too strict)
        pirate_indicators = [
            'ahoy', 'matey', 'avast', 'spotted', 'discovered', 'treasure',
            'crew', 'ship', 'sail', 'adventure', 'voyage', 'aboard'
        ]
        
        content_lower = content.lower()
        has_pirate_tone = any(indicator in content_lower for indicator in pirate_indicators)
        
        if not has_pirate_tone:
            print("⚠️ Weak pirate tone detected, but allowing...")
        
        # Check for prohibited content
        prohibited = ['crypto', 'trading', 'buy', 'sell', 'investment advice']
        if any(word in content_lower for word in prohibited):
            print("❌ Contains prohibited content")
            return False
        
        print("✅ Field note validation passed")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics."""
        return {
            "posts_generated": getattr(self, 'posts_generated', 0),
            "improvements_made": getattr(self, 'improvements_made', 0),
            "moderation_flags": getattr(self, 'moderation_flags', 0),
            "signature_emoji": self.signature_emoji,
            "theme": "AI Field Notes - Pirate Adventure"
        } 