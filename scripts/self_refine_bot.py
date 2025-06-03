"""Self-Refine Bot - Draft → self-critique → rewrite improvement loop."""

import openai
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from scripts.base_bot import BaseBot


class SelfRefineBot(BaseBot):
    """Bot that improves posts through self-critique and refinement."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, 'self_refine')
        self.refinement_history = []
    
    def generate_post(self, prompt: Optional[str] = None) -> str:
        """Generate a post with self-refinement (legacy method)."""
        post, _ = self.generate_post_with_details(prompt)
        return post
    
    def generate_post_with_details(self, prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Generate a post with self-refinement and return process details."""
        if not prompt:
            prompt = self._get_default_prompt()
        
        print(f"🪲 Self-Refine Bot: Starting generation process...")
        print(f"📋 Prompt: '{prompt}'")
        print()
        
        # Initialize process tracking
        process_details = {
            'prompt': prompt,
            'initial_draft': '',
            'critique': '',
            'refined_post': '',
            'improvement_made': False
        }
        
        # Step 1: Generate initial draft
        print("Step 1: 📝 Generating initial draft...")
        initial_draft = self._generate_initial_draft(prompt)
        process_details['initial_draft'] = initial_draft
        print(f"✅ Initial draft: '{initial_draft}'")
        print(f"   Length: {len(initial_draft)} characters")
        print()
        
        # Step 2: Self-critique
        print("Step 2: 🔍 Self-critiquing...")
        critique = self._self_critique(initial_draft)
        process_details['critique'] = critique
        print(f"✅ Critique: {critique[:100]}...")
        print()
        
        # Step 3: Refine based on critique
        print("Step 3: ✨ Refining based on critique...")
        refined_post = self._refine_post(initial_draft, critique)
        process_details['refined_post'] = refined_post
        print(f"✅ Refined post: '{refined_post}'")
        print(f"   Length: {len(refined_post)} characters")
        print()
        
        # Check if improvement was made
        improvement_made = initial_draft != refined_post.replace(f" {self.emoji}", "")
        process_details['improvement_made'] = improvement_made
        
        # Log the refinement process
        self._log_refinement(initial_draft, critique, refined_post)
        
        # Show comparison
        print("📊 COMPARISON:")
        print(f"   BEFORE: '{initial_draft}'")
        print(f"   AFTER:  '{refined_post}'")
        print(f"   IMPROVED: {'✅ Yes' if improvement_made else '➖ Minimal'}")
        print()
        
        return refined_post, process_details
    
    def _generate_initial_draft(self, prompt: str) -> str:
        """Generate the initial post draft."""
        try:
            print("   🤖 Calling OpenAI for initial draft...")
            response = openai.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['openai']['max_tokens'],
                temperature=self.config['openai']['temperature']
            )
            
            draft = response.choices[0].message.content.strip()
            print(f"   ✅ OpenAI responded with {len(draft)} characters")
            return draft
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.logger.error(f"Initial draft generation failed: {e}")
            return "Drafting thoughts on self-improvement..."
    
    def _self_critique(self, draft: str) -> str:
        """Generate self-critique of the draft."""
        critique_prompt = f"""
        Critique this Bluesky post draft for a bot showdown about self-refine improvement loops:

        DRAFT: "{draft}"

        Evaluate:
        1. Is it engaging and educational?
        2. Does it teach something about self-improvement or AI?
        3. Is the tone appropriate for tech leaders?
        4. Can it be made more compelling?
        5. Any unnecessary words that could be trimmed?

        Provide specific, actionable feedback for improvement.
        """
        
        try:
            print("   🤖 Calling OpenAI for self-critique...")
            response = openai.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are a expert social media content critic focused on educational tech content."},
                    {"role": "user", "content": critique_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            critique = response.choices[0].message.content.strip()
            print(f"   ✅ Generated critique ({len(critique)} characters)")
            return critique
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.logger.error(f"Self-critique failed: {e}")
            return "Could be more engaging and educational."
    
    def _refine_post(self, draft: str, critique: str) -> str:
        """Refine the post based on self-critique."""
        refinement_prompt = f"""
        Improve this Bluesky post based on the critique:

        ORIGINAL: "{draft}"
        CRITIQUE: "{critique}"

        Create an improved version that:
        - Addresses the critique points
        - Stays under 300 characters (including emoji)
        - Remains educational and engaging
        - Teaches about self-improvement or AI concepts

        Return only the improved post, no explanation.
        """
        
        try:
            print("   🤖 Calling OpenAI for refinement...")
            response = openai.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": refinement_prompt}
                ],
                max_tokens=self.config['openai']['max_tokens'],
                temperature=0.5
            )
            
            refined = response.choices[0].message.content.strip()
            result = self._add_emoji_signature(refined)
            print(f"   ✅ Refined and added emoji signature ({len(result)} characters)")
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.logger.error(f"Post refinement failed: {e}")
            return self._add_emoji_signature(draft)
    
    def _log_refinement(self, draft: str, critique: str, refined: str):
        """Log the refinement process for analysis."""
        refinement_record = {
            'timestamp': datetime.now().isoformat(),
            'initial_draft': draft,
            'critique': critique,
            'refined_post': refined,
            'improvement_made': draft != refined.replace(f" {self.emoji}", "")
        }
        
        self.refinement_history.append(refinement_record)
        
        if refinement_record['improvement_made']:
            self.stats['improvements_made'] += 1
            self.stats['last_improvement'] = refinement_record['timestamp']
            print(f"📈 Improvement #{self.stats['improvements_made']} logged!")
        else:
            print("📊 Minimal change detected")
        
        self.logger.info(f"Refinement {'successful' if refinement_record['improvement_made'] else 'minimal'}")
    
    def improve(self, feedback: Dict[str, Any]) -> None:
        """Improve based on engagement feedback."""
        # For Self-Refine bot, improvement happens during generation
        # But we can learn from engagement patterns
        if feedback.get('likes', 0) < 2:  # Low engagement threshold
            print(f"📉 Low engagement detected ({feedback.get('likes', 0)} likes)")
            self.logger.info("Low engagement detected, will increase temperature for next generation")
            # Could adjust parameters for future posts
    
    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement status for dashboard."""
        recent_refinements = [r for r in self.refinement_history[-10:]]
        
        return {
            'bot_type': self.bot_type,
            'total_refinements': len(self.refinement_history),
            'successful_improvements': self.stats['improvements_made'],
            'improvement_rate': (self.stats['improvements_made'] / max(1, len(self.refinement_history))) * 100,
            'recent_activity': recent_refinements,
            'next_improvement': 'Every post (built-in refinement loop)'
        }
    
    def _get_default_prompt(self) -> str:
        """Get default post prompt emphasizing self-refinement."""
        prompts = [
            "Share a practical insight about iterative improvement in AI systems",
            "Explain why self-critique leads to better outcomes than first drafts",
            "Describe how the best solutions emerge through refinement loops",
            "Share how self-reflection improves both humans and AI systems",
            "Explain the power of iterate-and-improve mindset for tech leaders"
        ]
        
        import random
        selected = random.choice(prompts)
        print(f"🎲 Selected prompt: '{selected}'")
        return selected 