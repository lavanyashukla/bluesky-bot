#!/usr/bin/env python3
"""
Test script for Bluesky Bot Showdown
Verifies setup without actually posting to Bluesky.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test if Bluesky config is set up."""
    print("🔧 Testing Bluesky configuration...")
    
    config_path = Path("config/bot_config.json")
    if not config_path.exists():
        print("❌ Config file not found!")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        bluesky_config = config.get('bluesky', {})
        
        if not bluesky_config.get('handle'):
            print("❌ No Bluesky handle found")
            return False
        
        if bluesky_config.get('password') == 'PASTE_YOUR_BLUESKY_APP_PASSWORD_HERE':
            print("⚠️  Please add your Bluesky app password to config/bot_config.json")
            print("   Go to Bluesky → Settings → App Passwords → Create new")
            return False
        
        print(f"✅ Bluesky handle: {bluesky_config['handle']}")
        print("✅ App password configured")
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_bot_creation():
    """Test if Self-Refine bot can be created."""
    print("🪲 Testing Self-Refine bot...")
    
    try:
        from scripts.self_refine_bot import SelfRefineBot
        
        # Load real config
        with open("config/bot_config.json") as f:
            config = json.load(f)
        
        # Create bot (but don't authenticate)
        bot = SelfRefineBot(config)
        print(f"✅ {bot.name} created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        return False

def test_post_generation():
    """Test post generation without posting."""
    print("📝 Testing post generation...")
    
    try:
        from scripts.self_refine_bot import SelfRefineBot
        
        # Load config
        with open("config/bot_config.json") as f:
            config = json.load(f)
        
        # Create bot
        bot = SelfRefineBot(config)
        
        # Generate post with details
        print("🔄 Generating test post...")
        post_content, details = bot.generate_post_with_details(
            "Share a quick tip about AI self-improvement"
        )
        
        print(f"\n📝 Generated Post:")
        print(f"'{post_content}'")
        print(f"Length: {len(post_content)} characters")
        print(f"Improvement made: {'✅' if details['improvement_made'] else '➖'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Post generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🦋 Bluesky Bot Showdown - Test Setup\n")
    
    tests = [
        test_config,
        test_bot_creation, 
        test_post_generation
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! Ready to start Bluesky bot showdown!")
        print("\nNext steps:")
        print("1. python3 run_bot.py           # Start the bot showdown")  
        print("2. python3 run_dashboard.py     # View the dashboard")
        print("\n🦋 Your Self-Refine bot will post to Bluesky every 30 minutes!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 