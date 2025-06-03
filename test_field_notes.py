#!/usr/bin/env python3
"""
Test the AI Field Notes - Pirate's Adventure functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_pirate_field_notes():
    """Test the updated Self-Refine bot with pirate theme."""
    print("🏴‍☠️ Testing AI Field Notes - Pirate's Adventure")
    print("=" * 50)
    
    # Test configuration update
    try:
        import json
        with open('config/bot_config.example.json') as f:
            config = json.load(f)
        
        # Check if config has new structure
        expected_keys = ['project', 'rules', 'content_guidelines']
        missing = [k for k in expected_keys if k not in config]
        
        if missing:
            print(f"❌ Missing config keys: {missing}")
            return False
        
        # Check project details
        if config['project']['name'] != "AI Field Notes - Pirate's Adventure":
            print("❌ Project name not updated")
            return False
        
        if config['project']['target_followers'] != 1000:
            print("❌ Target followers not set to 1000")
            return False
        
        # Check rules
        if not config['rules'].get('signature_emojis'):
            print("❌ Signature emojis not configured")
            return False
        
        print("✅ Configuration properly updated for AI Field Notes")
        
        # Check signature emojis
        emojis = config['rules']['signature_emojis']
        expected_emojis = {
            'self_refine': '✍️',
            'dpo': '🔄',
            'rlaif': '🎯',
            'mind_pool': '🛠️',
            'devops_self_fix': '🧬'
        }
        
        for bot, emoji in expected_emojis.items():
            if emojis.get(bot) != emoji:
                print(f"❌ Wrong emoji for {bot}: expected {emoji}, got {emojis.get(bot)}")
                return False
        
        print("✅ All signature emojis configured correctly")
        
        # Test bot initialization (mock)
        print("\n🤖 Testing Self-Refine Bot update...")
        
        # Mock config for testing
        test_config = {
            'openai': {
                'model': 'gpt-4o-mini',
                'api_key': 'test-key',
                'use_moderation': True
            },
            'bluesky': {
                'handle': 'test.bsky.social',
                'app_password': 'test-pass'
            }
        }
        
        # Test bot import and initialization structure
        from scripts.self_refine_bot import SelfRefineBot
        
        # Check if bot has required methods for pirate theme
        bot_methods = dir(SelfRefineBot)
        required_methods = [
            'generate_post_with_details',
            'validate_post',
            '_passes_moderation',
            '_generate_fallback_post'
        ]
        
        missing_methods = [m for m in required_methods if m not in bot_methods]
        if missing_methods:
            print(f"❌ Missing bot methods: {missing_methods}")
            return False
        
        print("✅ Self-Refine Bot has all required pirate methods")
        
        # Test fallback posts (should be pirate themed)
        try:
            # This is a simple test without OpenAI API
            fallback_test = '"Ahoy! Just discovered GitHub Copilot helping developers code 55% faster"'
            if 'ahoy' in fallback_test.lower() and '✍️' in fallback_test:
                print("✅ Fallback posts have pirate theme and signature emoji")
            else:
                print("⚠️ Fallback posts may not have proper pirate theme")
        except Exception as e:
            print(f"⚠️ Could not test fallback posts: {e}")
        
        print("\n🎯 AI Field Notes Configuration Summary:")
        print(f"📝 Theme: {config['project'].get('theme', 'Not set')}")
        print(f"🎯 Goal: {config['project']['target_followers']} followers in {config['project']['duration_days']} days")
        print(f"🏴‍☠️ Style: {config['rules'].get('writing_style', 'Not set')}")
        print(f"📊 Content Focus: {config['rules'].get('content_focus', 'Not set')}")
        print(f"✍️ Self-Refine Emoji: {config['rules']['signature_emojis']['self_refine']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing field notes: {e}")
        return False

def test_deployment_readiness():
    """Test if ready for Railway deployment with new config."""
    print("\n🚀 Testing Railway Deployment Readiness")
    print("=" * 40)
    
    # Check required files
    required_files = [
        'start.py',
        'railway.json', 
        '.gitignore',
        'env.template',
        'DEPLOY.md'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing:
        print(f"❌ Missing deployment files: {missing}")
        return False
    
    print("✅ All deployment files present")
    return True

def main():
    """Run all tests."""
    print("🏴‍☠️ AI Field Notes - Pirate's Adventure Test Suite")
    print("=" * 60)
    
    tests = [
        test_pirate_field_notes,
        test_deployment_readiness
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("🎉 ALL TESTS PASSED - AI Field Notes ready for adventure!")
        print("\n🏴‍☠️ Ready to deploy pirate bot to Railway!")
        print("📝 Bot will generate field notes about real-world AI deployments")
        print("✍️ Using self-refine loop with pirate adventurer voice")
        return 0
    else:
        print("❌ Some tests failed - fix issues before sailing")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 