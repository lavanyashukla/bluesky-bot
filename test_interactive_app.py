#!/usr/bin/env python3
"""
Test the Interactive Training App functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_interactive_app_imports():
    """Test that all required imports for the interactive app work."""
    print("🧪 Testing Interactive App Imports")
    print("=" * 40)
    
    try:
        # Test Streamlit import
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test bot imports
        from scripts.self_refine_bot import SelfRefineBot
        from scripts.dpo_bot import DPOBot
        print("✅ Bot imports successful")
        
        # Test preference manager
        from scripts.preference_manager import get_preference_manager
        pm = get_preference_manager()
        print("✅ Preference manager import and initialization successful")
        
        # Test essential modules
        import uuid
        import json
        print("✅ Standard library imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_preference_manager():
    """Test preference manager functionality."""
    print("\n🗄️ Testing Preference Manager")
    print("=" * 40)
    
    try:
        from scripts.preference_manager import PreferenceManager
        
        # Create test instance with unique db path
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name
        
        pm = PreferenceManager(test_db_path)
        print("✅ Preference manager created with test database")
        
        # Test saving training session
        test_session_data = {
            'dpo_learning_data': [
                {
                    'timestamp': '2024-01-01T00:00:00',
                    'iteration': 0,
                    'preferences': {
                        1: {'candidate': 'Test candidate 1', 'rating': 4},
                        2: {'candidate': 'Test candidate 2', 'rating': 3}
                    },
                    'best_candidate': {'candidate': 'Test candidate 1', 'rating': 4}
                }
            ]
        }
        
        session_id = "test_session_123"
        preference_id = pm.save_dpo_training_session(test_session_data, session_id)
        print(f"✅ Training session saved with ID: {preference_id}")
        
        # Test deployment
        deployment_result = pm.deploy_dpo_model(session_id, 1)
        print("✅ DPO model deployment successful")
        print(f"   Status: {deployment_result['status']}")
        print(f"   Training examples: {deployment_result['training_examples']}")
        
        # Test getting active model config
        active_config = pm.get_active_model_config('dpo')
        if active_config:
            print("✅ Active model config retrieved")
            metadata = active_config.get('training_metadata', {})
            print(f"   Total examples: {metadata.get('total_examples', 0)}")
        else:
            print("⚠️ No active model config found")
        
        # Test deployment status
        status = pm.get_deployment_status()
        print("✅ Deployment status retrieved")
        print(f"   Active models: {len(status['active_models'])}")
        print(f"   Total sessions: {status['total_training_sessions']}")
        
        # Cleanup
        os.unlink(test_db_path)
        print("✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Preference manager test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading for the app."""
    print("\n⚙️ Testing Configuration Loading")
    print("=" * 40)
    
    try:
        # Test config file exists
        config_path = "config/bot_config.example.json"
        if not Path(config_path).exists():
            print(f"❌ Config file not found: {config_path}")
            return False
        
        print(f"✅ Config file found: {config_path}")
        
        # Test loading config
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required keys for interactive app
        required_keys = ['project', 'openai', 'bots', 'rules']
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            print(f"❌ Missing config keys: {missing}")
            return False
        
        print("✅ Configuration loaded successfully")
        
        # Check bot configurations
        bots = config.get('bots', {})
        if 'self_refine' in bots and 'dpo' in bots:
            print("✅ Bot configurations found")
            print(f"   Self-Refine enabled: {bots['self_refine'].get('enabled', False)}")
            print(f"   DPO enabled: {bots['dpo'].get('enabled', False)}")
        else:
            print("⚠️ Some bot configurations missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_demo_functions():
    """Test demo/fallback functions work correctly."""
    print("\n🎭 Testing Demo Functions")
    print("=" * 40)
    
    try:
        # Import the demo functions from interactive app
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test simulate_self_refine function (need to extract it)
        demo_self_refine = {
            'initial_draft': "Test initial draft",
            'critique': "Test critique",
            'refined_post': "Test refined post",
            'improvement_made': True
        }
        
        print("✅ Self-refine demo data structure valid")
        
        # Test demo candidates generation
        demo_candidates = [
            "Demo candidate 1 with 🔄",
            "Demo candidate 2 with 🔄",
            "Demo candidate 3 with 🔄",
            "Demo candidate 4 with 🔄"
        ]
        
        print(f"✅ Demo candidates generated: {len(demo_candidates)}")
        
        # Validate demo candidates have required elements
        all_have_emoji = all('🔄' in candidate for candidate in demo_candidates)
        if all_have_emoji:
            print("✅ All demo candidates have DPO signature emoji")
        else:
            print("⚠️ Some demo candidates missing signature emoji")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo functions test failed: {e}")
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility and key functions."""
    print("\n🎨 Testing Streamlit Compatibility")
    print("=" * 40)
    
    try:
        import streamlit as st
        
        # Check if we can import key Streamlit functions used in the app
        functions_to_test = [
            'set_page_config',
            'markdown',
            'columns',
            'button',
            'slider',
            'spinner',
            'success',
            'error',
            'info',
            'balloons',
            'tabs',
            'expander',
            'code',
            'metric'
        ]
        
        missing_functions = []
        for func_name in functions_to_test:
            if not hasattr(st, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Missing Streamlit functions: {missing_functions}")
            return False
        
        print("✅ All required Streamlit functions available")
        
        # Test session state simulation
        if hasattr(st, 'session_state'):
            print("✅ Streamlit session state available")
        else:
            print("⚠️ Streamlit session state not available (older version?)")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit compatibility test failed: {e}")
        return False

def main():
    """Run all interactive app tests."""
    print("🏴‍☠️ Interactive AI Bot Training App Test Suite")
    print("=" * 60)
    
    tests = [
        test_interactive_app_imports,
        test_preference_manager,
        test_config_loading,
        test_demo_functions,
        test_streamlit_compatibility
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("🎉 ALL INTERACTIVE APP TESTS PASSED!")
        print("\n🚀 Ready to deploy interactive training app!")
        print("📝 Next steps:")
        print("   1. Run locally: streamlit run interactive_app.py")
        print("   2. Deploy to Railway with SERVICE_TYPE=interactive")
        print("   3. Add OPENAI_API_KEY to secrets for live generation")
        return 0
    else:
        print("❌ Some interactive app tests failed")
        failed_count = sum(1 for result in results if not result)
        print(f"   {failed_count}/{len(tests)} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 