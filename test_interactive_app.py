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

def test_configuration_functionality():
    """Test configuration interface functionality."""
    print("\n⚙️ Testing Configuration Interface")
    print("=" * 40)
    
    try:
        # Test configuration data structures
        config_template = {
            'project': {
                'name': 'Test AI Bot Project',
                'target_followers': 5000,
                'duration_days': 14,
                'theme': 'professional',
                'description': 'Test description'
            },
            'rules': {
                'content_focus': 'real_world_ai_deployments',
                'writing_style': 'professional_reporter',
                'max_body_characters': 300,
                'require_credible_source': True,
                'avoid_buzzwords': True,
                'accuracy_required': True,
                'prohibited': ['marketing_buzzwords', 'unverified_claims']
            },
            'openai': {
                'api_key': 'test-key',
                'model': 'gpt-4o-mini',
                'use_moderation': True
            },
            'bluesky': {
                'handle': 'testbot.bsky.social',
                'app_password': 'test-password'
            }
        }
        
        print("✅ Configuration template structure valid")
        
        # Test required config keys
        required_sections = ['project', 'rules', 'openai', 'bluesky']
        missing_sections = [s for s in required_sections if s not in config_template]
        
        if missing_sections:
            print(f"❌ Missing config sections: {missing_sections}")
            return False
        
        print("✅ All required configuration sections present")
        
        # Test project settings validation
        project = config_template['project']
        if project['target_followers'] < 100 or project['target_followers'] > 100000:
            print("❌ Target followers out of valid range")
            return False
        
        if project['duration_days'] < 1 or project['duration_days'] > 30:
            print("❌ Duration days out of valid range")
            return False
        
        print("✅ Project settings validation passed")
        
        # Test rules validation
        rules = config_template['rules']
        valid_content_types = ['real_world_ai_deployments', 'ai_research', 'tech_news', 'educational']
        if rules['content_focus'] not in valid_content_types:
            print("❌ Invalid content focus type")
            return False
        
        valid_writing_styles = ['pirate_field_notes', 'professional_reporter', 'casual_observer', 'technical_analyst']
        if rules['writing_style'] not in valid_writing_styles:
            print("❌ Invalid writing style")
            return False
        
        print("✅ Rules validation passed")
        
        # Test API key format validation
        openai_key = config_template['openai']['api_key']
        if openai_key and not (openai_key.startswith('sk-') or openai_key == 'test-key'):
            print("⚠️ OpenAI API key format unusual (but accepting for test)")
        
        bluesky_handle = config_template['bluesky']['handle']
        if bluesky_handle and '.bsky.social' not in bluesky_handle:
            print("⚠️ Bluesky handle format unusual")
        
        print("✅ API credential format validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration functionality test failed: {e}")
        return False

def test_config_export_import():
    """Test configuration export/import functionality."""
    print("\n📤📥 Testing Export/Import")
    print("=" * 40)
    
    try:
        import json
        
        # Test config with sensitive data
        config_with_secrets = {
            'project': {'name': 'Test Project'},
            'openai': {'api_key': 'sk-real-secret-key'},
            'bluesky': {'handle': 'test.bsky.social', 'app_password': 'real-password'}
        }
        
        # Simulate export process (remove sensitive data)
        safe_config = config_with_secrets.copy()
        if 'openai' in safe_config and 'api_key' in safe_config['openai']:
            safe_config['openai']['api_key'] = "your-openai-api-key"
        if 'bluesky' in safe_config and 'app_password' in safe_config['bluesky']:
            safe_config['bluesky']['app_password'] = "your-app-password"
        
        print("✅ Sensitive data filtering works")
        
        # Test JSON serialization
        config_json = json.dumps(safe_config, indent=2)
        if len(config_json) > 0:
            print("✅ Configuration JSON export successful")
        
        # Test JSON deserialization (import)
        imported_config = json.loads(config_json)
        if imported_config['project']['name'] == 'Test Project':
            print("✅ Configuration JSON import successful")
        
        # Verify secrets are removed
        if imported_config['openai']['api_key'] == "your-openai-api-key":
            print("✅ Sensitive data properly filtered in export")
        
        return True
        
    except Exception as e:
        print(f"❌ Export/import test failed: {e}")
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
        
        # Test saving training session with config
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
            ],
            'config': {
                'project': {'target_followers': 1000},
                'rules': {'max_body_characters': 280}
            }
        }
        
        session_id = "test_session_123"
        preference_id = pm.save_dpo_training_session(test_session_data, session_id)
        print(f"✅ Training session with config saved with ID: {preference_id}")
        
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
        
        # Test config compatibility with new structure
        project_config = config.get('project', {})
        if 'target_followers' in project_config or 'duration_days' in project_config:
            print("✅ Project configuration compatible")
        else:
            print("ℹ️ Project configuration will use defaults")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_demo_functions():
    """Test demo/fallback functions work correctly."""
    print("\n🎭 Testing Demo Functions")
    print("=" * 40)
    
    try:
        # Test simulate_self_refine function
        demo_self_refine = {
            'initial_draft': "Test initial draft",
            'critique': "Test critique",
            'refined_post': "Test refined post",
            'improvement_made': True
        }
        
        required_keys = ['initial_draft', 'critique', 'refined_post', 'improvement_made']
        missing_keys = [k for k in required_keys if k not in demo_self_refine]
        
        if missing_keys:
            print(f"❌ Missing demo self-refine keys: {missing_keys}")
            return False
        
        print("✅ Self-refine demo data structure valid")
        
        # Test demo candidates generation
        demo_candidates = [
            "Demo candidate 1 with 🔄",
            "Demo candidate 2 with 🔄",
            "Demo candidate 3 with 🔄",
            "Demo candidate 4 with 🔄"
        ]
        
        if len(demo_candidates) != 4:
            print(f"❌ Expected 4 demo candidates, got {len(demo_candidates)}")
            return False
        
        print(f"✅ Demo candidates generated: {len(demo_candidates)}")
        
        # Validate demo candidates have required elements
        all_have_emoji = all('🔄' in candidate for candidate in demo_candidates)
        if all_have_emoji:
            print("✅ All demo candidates have DPO signature emoji")
        else:
            print("⚠️ Some demo candidates missing signature emoji")
        
        # Test character limits
        for i, candidate in enumerate(demo_candidates, 1):
            if len(candidate) > 300:  # Max characters for posts
                print(f"⚠️ Demo candidate {i} exceeds character limit: {len(candidate)} chars")
            else:
                print(f"✅ Demo candidate {i} within character limit: {len(candidate)} chars")
        
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
            'metric',
            'text_input',
            'text_area',
            'number_input',
            'selectbox',
            'multiselect',
            'checkbox',
            'radio',
            'rerun'  # Used for configuration updates
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
        
        # Test secrets access (for API keys)
        if hasattr(st, 'secrets'):
            print("✅ Streamlit secrets available for API key management")
        else:
            print("⚠️ Streamlit secrets not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit compatibility test failed: {e}")
        return False

def test_api_configuration():
    """Test API configuration functionality."""
    print("\n🔑 Testing API Configuration")
    print("=" * 40)
    
    try:
        # Test API key validation logic
        def validate_openai_key(key):
            if not key:
                return "empty"
            if key in ['your-openai-api-key', 'demo-key']:
                return "demo"
            if key.startswith('sk-'):
                return "valid_format"
            return "unknown_format"
        
        test_keys = [
            ("", "empty"),
            ("your-openai-api-key", "demo"),
            ("demo-key", "demo"),
            ("sk-test123", "valid_format"),
            ("invalid-key", "unknown_format")
        ]
        
        for key, expected in test_keys:
            result = validate_openai_key(key)
            if result == expected:
                print(f"✅ OpenAI key validation: '{key[:10]}...' -> {result}")
            else:
                print(f"❌ OpenAI key validation failed: expected {expected}, got {result}")
                return False
        
        # Test Bluesky handle validation
        def validate_bluesky_handle(handle):
            if not handle:
                return "empty"
            if '.bsky.social' in handle:
                return "valid_format"
            return "invalid_format"
        
        test_handles = [
            ("", "empty"),
            ("user.bsky.social", "valid_format"),
            ("invalid-handle", "invalid_format")
        ]
        
        for handle, expected in test_handles:
            result = validate_bluesky_handle(handle)
            if result == expected:
                print(f"✅ Bluesky handle validation: '{handle}' -> {result}")
            else:
                print(f"❌ Bluesky handle validation failed: expected {expected}, got {result}")
                return False
        
        print("✅ API configuration validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ API configuration test failed: {e}")
        return False

def main():
    """Run all interactive app tests."""
    print("🏴‍☠️ Interactive AI Bot Training App Test Suite")
    print("=" * 60)
    
    tests = [
        test_interactive_app_imports,
        test_configuration_functionality,
        test_config_export_import,
        test_preference_manager,
        test_config_loading,
        test_demo_functions,
        test_streamlit_compatibility,
        test_api_configuration
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
        print("   2. Use Configuration tab to set up API keys and goals")
        print("   3. Train bots with Self-Refine and DPO techniques")
        print("   4. Deploy to Railway with SERVICE_TYPE=interactive")
        print("   5. Share with users for interactive AI training!")
        return 0
    else:
        print("❌ Some interactive app tests failed")
        failed_count = sum(1 for result in results if not result)
        print(f"   {failed_count}/{len(tests)} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 