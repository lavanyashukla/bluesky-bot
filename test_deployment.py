#!/usr/bin/env python3
"""
Deployment readiness test
Verifies all components work before Railway deployment
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports."""
    print("🧪 Testing imports...")
    
    try:
        from scripts.orchestrator import BotOrchestrator
        print("✅ BotOrchestrator import successful")
        
        from scripts.self_refine_bot import SelfRefineBot  
        print("✅ SelfRefineBot import successful")
        
        import streamlit
        print("✅ Streamlit import successful")
        
        import atproto
        print("✅ AT Protocol import successful")
        
        import openai
        print("✅ OpenAI import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test config file exists."""
    print("\n📋 Testing configuration...")
    
    config_path = Path("config/bot_config.json")
    if config_path.exists():
        print("✅ Config file found")
        
        # Try loading it
        import json
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            required_keys = ['bluesky', 'openai', 'bots', 'posting', 'rules']
            missing = [k for k in required_keys if k not in config]
            
            if missing:
                print(f"⚠️ Missing config keys: {missing}")
                return False
            else:
                print("✅ Config file valid")
                return True
                
        except json.JSONDecodeError as e:
            print(f"❌ Config JSON error: {e}")
            return False
    else:
        print("❌ Config file not found")
        return False

def test_credentials():
    """Test if we have required environment variables or config."""
    print("\n🔑 Testing credentials...")
    
    # Check for environment variables (Railway style)
    env_vars = ['BLUESKY_HANDLE', 'BLUESKY_APP_PASSWORD', 'OPENAI_API_KEY']
    env_found = all(os.getenv(var) for var in env_vars)
    
    if env_found:
        print("✅ All environment variables found")
        return True
    
    # Check config file has credentials
    config_path = Path("config/bot_config.json")  
    if config_path.exists():
        import json
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            bluesky_ok = (config.get('bluesky', {}).get('handle') and 
                         config.get('bluesky', {}).get('app_password'))
            openai_ok = config.get('openai', {}).get('api_key')
            
            if bluesky_ok and openai_ok:
                print("✅ Credentials found in config")
                return True
            else:
                print("⚠️ Some credentials missing in config")
                return False
                
        except Exception as e:
            print(f"❌ Error reading config: {e}")
            return False
    
    print("❌ No credentials found (env vars or config)")
    return False

def test_file_structure():
    """Test required files exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'requirements.txt',
        'run_bot.py', 
        'run_dashboard.py',
        'start.py',
        'scripts/orchestrator.py',
        'scripts/self_refine_bot.py',
        'dashboard/app.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Run all deployment tests."""
    print("🚀 Bot Showdown Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_config,
        test_credentials
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("✅ ALL TESTS PASSED - Ready for Railway deployment!")
        print("\n🎯 Next steps:")
        print("1. Commit and push to GitHub")
        print("2. Connect repository to Railway")
        print("3. Set environment variables in Railway")
        print("4. Deploy with SERVICE_TYPE=bot")
        print("\nSee DEPLOY.md for detailed instructions!")
        return 0
    else:
        print("❌ Some tests failed - fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 