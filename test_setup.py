#!/usr/bin/env python3
"""
Test script for the I Wonder Social-Bot Showdown
Run this to verify your setup is working correctly.
"""

import json
import sys
from pathlib import Path

def test_config():
    """Test if configuration is set up correctly."""
    print("🔧 Testing configuration...")
    
    config_path = Path("config/bot_config.json")
    example_path = Path("config/bot_config.example.json")
    
    if not example_path.exists():
        print("❌ Example config not found")
        return False
    
    if not config_path.exists():
        print("⚠️  bot_config.json not found")
        print("   Please copy config/bot_config.example.json to config/bot_config.json")
        print("   and add your API keys")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        # Check for placeholder values
        if "YOUR_" in config.get('openai', {}).get('api_key', ''):
            print("⚠️  Please add your OpenAI API key to config/bot_config.json")
            return False
        
        if "YOUR_" in config.get('twitter', {}).get('api_key', ''):
            print("⚠️  Please add your Twitter API keys to config/bot_config.json")
            return False
        
        print("✅ Configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_imports():
    """Test if required packages are installed."""
    print("📦 Testing imports...")
    
    required_packages = [
        'openai',
        'tweepy', 
        'streamlit',
        'pandas',
        'matplotlib',
        'plotly',
        'schedule',
        'sqlite3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages installed!")
    return True

def test_bot_creation():
    """Test if we can create a Self-Refine bot."""
    print("🤖 Testing bot creation...")
    
    try:
        from scripts.base_bot import BaseBot
        from scripts.self_refine_bot import SelfRefineBot
        print("  ✅ Bot classes imported successfully")
        
        # Test with mock config (won't actually make API calls)
        mock_config = {
            'openai': {'api_key': 'test', 'model': 'gpt-4', 'max_tokens': 280, 'temperature': 0.7},
            'twitter': {'api_key': 'test', 'api_secret': 'test', 'access_token': 'test', 
                       'access_token_secret': 'test', 'bearer_token': 'test'},
            'bots': {
                'self_refine': {
                    'emoji': '🪲',
                    'name': 'Self-Refine Bot',
                    'enabled': True,
                    'improvement_frequency': 'every_post'
                }
            },
            'rules': {
                'tone': 'educational',
                'topics': ['AI/ML'],
                'forbidden_words': ['crypto'],
                'max_hashtags': 3
            },
            'monitoring': {'log_level': 'INFO'}
        }
        
        # This will fail on API calls, but should create the bot object
        try:
            bot = SelfRefineBot(mock_config)
            print("  ✅ Self-Refine bot created successfully")
            return True
        except Exception as e:
            if "api_key" in str(e).lower():
                print("  ✅ Bot creation works (API key needed for full functionality)")
                return True
            else:
                print(f"  ❌ Bot creation failed: {e}")
                return False
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_database():
    """Test database creation."""
    print("🗄️  Testing database...")
    
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect(':memory:')  # In-memory database for testing
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE test_tweets (
                id TEXT PRIMARY KEY,
                content TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO test_tweets (id, content) VALUES (?, ?)", ("1", "Test tweet"))
        result = cursor.fetchone()
        conn.close()
        
        print("  ✅ Database operations working")
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 I Wonder Social-Bot Showdown - Setup Test\n")
    
    tests = [
        test_imports,
        test_config,
        test_bot_creation,
        test_database
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! You're ready to start the bot showdown!")
        print("\nNext steps:")
        print("1. python scripts/orchestrator.py  # Start the bot showdown")
        print("2. streamlit run dashboard/app.py  # View the dashboard")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 