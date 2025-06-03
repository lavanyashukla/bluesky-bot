"""
DPO Bot for AI Field Notes - Pirate's Adventure
Uses Direct Preference Optimization to select the best field notes
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional
from scripts.base_bot import BaseBot


class DPOBot(BaseBot):
    """
    DPO Bot that generates multiple AI field note candidates and uses
    preference optimization to select the best one based on multiple criteria.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "dpo", "🔄 DPO Preference Optimizer")
        self.signature_emoji = "🔄"
        self.use_moderation = config.get('openai', {}).get('use_moderation', True)
        self.num_candidates = 4  # Generate 4 candidates to choose from
        
        # DPO prompts for AI Field Notes
        self.prompts = {
            "generate_candidates": """You are a pirate adventurer documenting real-world AI deployments. Generate {num_candidates} different field notes about actual AI implementations.

Each field note must:
- Act like a pirate sending notes from AI adventures
- Focus on ONE specific, real AI deployment happening now
- Max 250 characters (leaving room for links)
- Include company/organization name
- Mention specific metrics or outcomes
- Be "Slack-worthy" for executives
- Avoid marketing buzzwords
- End with signature emoji 🔄

Examples of real AI deployments to inspire you:
- Shopify's GPT product description generation (10M+ monthly)
- Netflix's AI thumbnail optimization (20-30% CTR boost) 
- Stripe's fraud detection ML (millions of transactions)
- Spotify's recommendation algorithms (user engagement)
- Tesla's Autopilot vision systems (safety improvements)

Generate {num_candidates} DIFFERENT field notes, each about a different real AI deployment. Format as:

CANDIDATE 1: [your field note with 🔄]
CANDIDATE 2: [your field note with 🔄]
CANDIDATE 3: [your field note with 🔄]
CANDIDATE 4: [your field note with 🔄]""",

            "preference_evaluation": """You are an expert evaluator choosing the best AI field note for a pirate adventurer's social media.

Evaluate these {num_candidates} candidates on:

ACCURACY & CREDIBILITY (40%):
- Specific, verifiable AI deployment details
- Realistic metrics and company references
- Current/recent implementations (not speculation)

ENGAGEMENT POTENTIAL (30%):
- "Slack-worthy" executive appeal
- Clear actionable insight
- Compelling pirate voice without being cheesy

STRUCTURE & QUALITY (30%):
- Under 250 characters (room for links)
- Clear, punchy writing
- Professional yet adventurous tone
- Proper signature emoji 🔄

CANDIDATES TO EVALUATE:
{candidates}

Rank them 1-{num_candidates} (1=best) and explain your reasoning. Then select the BEST candidate for posting.

Provide your analysis in this format:

RANKING:
1. Candidate X - [brief reason]
2. Candidate Y - [brief reason]
3. Candidate Z - [brief reason]
4. Candidate W - [brief reason]

SELECTED WINNER: [paste the full winning field note here]"""
        }

    def generate_post_with_details(self) -> Tuple[str, Dict[str, Any]]:
        """Generate field note using DPO candidate selection process."""
        
        process_details = {
            'timestamp': datetime.now().isoformat(),
            'bot_type': self.bot_type,
            'candidates_generated': [],
            'preference_ranking': '',
            'selected_candidate': '',
            'improvement_made': False,
            'error_message': ''
        }
        
        try:
            print("🔄 DPO Bot: Generating multiple field note candidates...")
            
            # Step 1: Generate multiple candidates
            candidates = self._generate_candidates()
            process_details['candidates_generated'] = candidates
            
            if not candidates:
                print("❌ No candidates generated")
                process_details['error_message'] = 'Failed to generate candidates'
                return self._generate_fallback_post(), process_details
            
            print(f"📝 Generated {len(candidates)} candidates:")
            for i, candidate in enumerate(candidates, 1):
                print(f"   {i}. {candidate[:80]}...")
            
            # Step 2: Use preference optimization to select best
            print("\n🎯 Running preference evaluation...")
            selected_post, ranking = self._select_best_candidate(candidates)
            process_details['preference_ranking'] = ranking
            process_details['selected_candidate'] = selected_post
            
            if not selected_post:
                print("❌ No candidate selected")
                process_details['error_message'] = 'Preference selection failed'
                return self._generate_fallback_post(), process_details
            
            print(f"🏆 Selected winner: {selected_post}")
            
            # Check moderation
            if self.use_moderation:
                if not self._passes_moderation(selected_post):
                    print("⚠️ Selected post flagged by moderation")
                    process_details['error_message'] = 'Content flagged by moderation'
                    return self._generate_fallback_post(), process_details
            
            # DPO improvement is inherent in the selection process
            process_details['improvement_made'] = True
            
            return selected_post, process_details
            
        except Exception as e:
            print(f"❌ Error in DPO generation: {e}")
            process_details['error_message'] = str(e)
            return self._generate_fallback_post(), process_details

    def _generate_candidates(self) -> List[str]:
        """Generate multiple field note candidates."""
        try:
            prompt = self.prompts['generate_candidates'].format(
                num_candidates=self.num_candidates
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.9  # Higher temperature for diversity
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse candidates from response
            candidates = []
            lines = content.split('\n')
            
            for line in lines:
                if line.strip().startswith('CANDIDATE'):
                    # Extract the content after "CANDIDATE X:"
                    if ':' in line:
                        candidate = line.split(':', 1)[1].strip()
                        if candidate and len(candidate) > 20:  # Basic validation
                            candidates.append(candidate)
            
            # Fallback parsing if structured format fails
            if len(candidates) < 2:
                print("⚠️ Structured parsing failed, trying fallback...")
                # Look for text with emoji signature
                emoji_lines = [line.strip() for line in lines if '🔄' in line and len(line.strip()) > 20]
                candidates = emoji_lines[:self.num_candidates]
            
            print(f"📊 Parsed {len(candidates)} candidates from response")
            return candidates[:self.num_candidates]  # Limit to requested number
            
        except Exception as e:
            print(f"❌ Error generating candidates: {e}")
            return []

    def _select_best_candidate(self, candidates: List[str]) -> Tuple[str, str]:
        """Use preference optimization to select best candidate."""
        try:
            # Format candidates for evaluation
            candidates_text = ""
            for i, candidate in enumerate(candidates, 1):
                candidates_text += f"CANDIDATE {i}: {candidate}\n\n"
            
            prompt = self.prompts['preference_evaluation'].format(
                num_candidates=len(candidates),
                candidates=candidates_text
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3  # Lower temperature for consistent evaluation
            )
            
            evaluation = response.choices[0].message.content.strip()
            
            # Extract the selected winner
            lines = evaluation.split('\n')
            selected = ""
            
            for line in lines:
                if line.strip().startswith('SELECTED WINNER:'):
                    if ':' in line:
                        selected = line.split(':', 1)[1].strip()
                        break
            
            # Fallback: extract any line with the signature emoji
            if not selected:
                for line in lines:
                    if '🔄' in line and len(line.strip()) > 20:
                        selected = line.strip()
                        break
            
            # Final fallback: use first candidate
            if not selected and candidates:
                selected = candidates[0]
                print("⚠️ Using first candidate as fallback")
            
            print(f"🎯 DPO selected: {selected[:100]}...")
            return selected, evaluation
            
        except Exception as e:
            print(f"❌ Error in preference selection: {e}")
            return (candidates[0] if candidates else "", str(e))

    def _passes_moderation(self, content: str) -> bool:
        """Check content against OpenAI moderation API."""
        try:
            response = self.openai_client.moderations.create(input=content)
            return not response.results[0].flagged
        except Exception as e:
            print(f"⚠️ Moderation check failed: {e}")
            return True

    def _generate_fallback_post(self) -> str:
        """Generate a safe fallback field note with DPO signature."""
        fallbacks = [
            "Ahoy! Spotted Amazon's Alexa using preference optimization to rank responses - millions of daily interactions teaching it what humans prefer. Smart learning from choices! 🔄",
            
            "Matey! Found Google Search using ML ranking models trained on billions of clicks. Their preference optimization decides which results ye see first. Treasure navigation! 🔄",
            
            "Avast! Discovered YouTube's recommendation engine using DPO-style training on viewer choices. 2B+ hours watched daily = massive preference dataset! 🔄"
        ]
        
        import random
        return random.choice(fallbacks)

    def validate_post(self, content: str) -> bool:
        """Validate field note meets DPO requirements."""
        
        # Check length
        if len(content) > 300:
            print(f"❌ Post too long: {len(content)} characters")
            return False
        
        # Check for DPO signature emoji
        if "🔄" not in content:
            print("❌ Missing DPO signature emoji 🔄")
            return False
        
        # Check for pirate elements
        pirate_indicators = [
            'ahoy', 'matey', 'avast', 'spotted', 'discovered', 'treasure',
            'crew', 'ship', 'sail', 'adventure', 'voyage', 'aboard', 'found'
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
        
        print("✅ DPO field note validation passed")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get DPO bot statistics."""
        return {
            "posts_generated": getattr(self, 'posts_generated', 0),
            "candidates_evaluated": getattr(self, 'candidates_evaluated', 0),
            "preference_selections": getattr(self, 'preference_selections', 0),
            "signature_emoji": self.signature_emoji,
            "optimization_method": "Direct Preference Optimization",
            "theme": "AI Field Notes - Pirate Adventure"
        } 