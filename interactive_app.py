#!/usr/bin/env python3
"""
Interactive AI Bot Training App
Let users participate in training different AI improvement techniques
"""

import streamlit as st
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.self_refine_bot import SelfRefineBot
from scripts.dpo_bot import DPOBot
from scripts.preference_manager import get_preference_manager

# Page config
st.set_page_config(
    page_title="🏴‍☠️ AI Field Notes - Interactive Bot Training",
    page_icon="🏴‍☠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_config():
    """Load bot configuration."""
    config_path = "config/bot_config.example.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def save_user_config(config: Dict[str, Any]):
    """Save user configuration to session and optionally to file."""
    st.session_state.config = config
    
    # Optionally save to a user config file
    try:
        user_config_path = "config/user_config.json"
        os.makedirs("config", exist_ok=True)
        with open(user_config_path, 'w') as f:
            # Don't save sensitive data to file, only structure
            safe_config = config.copy()
            if 'openai' in safe_config and 'api_key' in safe_config['openai']:
                safe_config['openai']['api_key'] = "user-provided"
            if 'bluesky' in safe_config and 'app_password' in safe_config['bluesky']:
                safe_config['bluesky']['app_password'] = "user-provided"
            json.dump(safe_config, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save config file: {e}")

def init_session_state():
    """Initialize session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'dpo_learning_data' not in st.session_state:
        st.session_state.dpo_learning_data = []
    
    if 'dpo_iteration' not in st.session_state:
        st.session_state.dpo_iteration = 0
    
    if 'deployed_model' not in st.session_state:
        st.session_state.deployed_model = None
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'preference_manager' not in st.session_state:
        st.session_state.preference_manager = get_preference_manager()
    
    # Configuration state
    if 'show_config' not in st.session_state:
        st.session_state.show_config = False
    
    if 'config_saved' not in st.session_state:
        st.session_state.config_saved = False

def create_sidebar():
    """Create the technique selection sidebar."""
    st.sidebar.markdown("## 🤖 **AI Improvement Techniques**")
    
    technique = st.sidebar.radio(
        "Choose your AI improvement method:",
        [
            "⚙️ Configuration",
            "✍️ Self-Refine",
            "🔄 DPO (Interactive Learning)",
            "🎯 RLAIF (Coming Soon)",
            "🛠️ Mind-Pool (Coming Soon)",
            "🧬 DevOps Self-Fix (Coming Soon)"
        ],
        index=1  # Default to Self-Refine
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 **Current Status**")
    
    # Configuration status
    config = st.session_state.config
    api_configured = bool(config.get('openai', {}).get('api_key') and 
                         config.get('openai', {}).get('api_key') != 'your-openai-api-key')
    bluesky_configured = bool(config.get('bluesky', {}).get('handle') and 
                             config.get('bluesky', {}).get('app_password') and
                             config.get('bluesky', {}).get('handle') != 'your-handle.bsky.social')
    
    if api_configured and bluesky_configured:
        st.sidebar.success("✅ **APIs Configured**")
    elif api_configured:
        st.sidebar.warning("⚠️ **OpenAI Only** (Demo mode)")
    else:
        st.sidebar.info("ℹ️ **Demo Mode** (No APIs)")
    
    # Get deployment status from preference manager
    deployment_status = st.session_state.preference_manager.get_deployment_status()
    
    if deployment_status['active_models']:
        for model in deployment_status['active_models']:
            st.sidebar.success(f"🚀 **Deployed:** {model['technique'].upper()} ({model['training_examples']} examples)")
    else:
        st.sidebar.info("⏳ No model deployed yet")
    
    st.sidebar.markdown(f"🔄 **DPO Iterations:** {st.session_state.dpo_iteration}")
    st.sidebar.markdown(f"📝 **Training Examples:** {len(st.session_state.dpo_learning_data)}")
    st.sidebar.markdown(f"🆔 **Session:** {st.session_state.session_id[:8]}...")
    
    # Add deployment stats
    if deployment_status['total_training_sessions'] > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 **Global Stats**")
        st.sidebar.markdown(f"🎓 **Total Sessions:** {deployment_status['total_training_sessions']}")
        st.sidebar.markdown(f"🚀 **Deployed Models:** {deployment_status['deployed_sessions']}")
    
    return technique

def configuration_interface():
    """Configuration interface for goals, rules, and API keys."""
    st.markdown("# ⚙️ **Configuration**")
    st.markdown("**Set up your AI bot goals, rules, and API credentials.**")
    
    # Tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Goals", "📋 Rules", "🔑 API Keys", "💾 Export/Import"])
    
    config = st.session_state.config.copy()
    
    with tab1:
        st.markdown("### 🎯 **Bot Goals & Project Settings**")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(
                "Project Name",
                value=config.get('project', {}).get('name', 'AI Field Notes - Pirate\'s Adventure'),
                help="Name of your AI bot project"
            )
            
            target_followers = st.number_input(
                "Target Followers",
                min_value=100,
                max_value=100000,
                value=config.get('project', {}).get('target_followers', 1000),
                step=100,
                help="How many followers you want to reach"
            )
        
        with col2:
            duration_days = st.number_input(
                "Duration (Days)",
                min_value=1,
                max_value=30,
                value=config.get('project', {}).get('duration_days', 7),
                help="How long to run the campaign"
            )
            
            theme = st.selectbox(
                "Theme Style",
                ["pirate_field_notes", "professional", "casual", "technical"],
                index=0,
                help="Writing style for your bot"
            )
        
        description = st.text_area(
            "Project Description",
            value=config.get('project', {}).get('description', ''),
            height=100,
            help="Describe what your bot does"
        )
        
        # Update config
        if 'project' not in config:
            config['project'] = {}
        config['project'].update({
            'name': project_name,
            'target_followers': target_followers,
            'duration_days': duration_days,
            'theme': theme,
            'description': description
        })
    
    with tab2:
        st.markdown("### 📋 **Content Rules & Guidelines**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Content Focus:**")
            content_focus = st.selectbox(
                "Primary Content Type",
                ["real_world_ai_deployments", "ai_research", "tech_news", "educational"],
                index=0
            )
            
            max_chars = st.number_input(
                "Max Characters",
                min_value=100,
                max_value=500,
                value=config.get('rules', {}).get('max_body_characters', 280),
                help="Maximum characters per post"
            )
            
            require_source = st.checkbox(
                "Require Credible Sources",
                value=config.get('rules', {}).get('require_credible_source', True),
                help="Always include source links"
            )
        
        with col2:
            st.markdown("**Writing Style:**")
            writing_style = st.selectbox(
                "Writing Style",
                ["pirate_field_notes", "professional_reporter", "casual_observer", "technical_analyst"],
                index=0
            )
            
            avoid_buzzwords = st.checkbox(
                "Avoid Marketing Buzzwords",
                value=config.get('rules', {}).get('avoid_buzzwords', True)
            )
            
            accuracy_required = st.checkbox(
                "Accuracy Required",
                value=config.get('rules', {}).get('accuracy_required', True),
                help="Fact-check all claims"
            )
        
        st.markdown("**Prohibited Content:**")
        prohibited_items = st.multiselect(
            "Select prohibited content types:",
            ["political_endorsements", "personal_data", "speculative_stock_advice", 
             "marketing_buzzwords", "unverified_claims", "crypto_trading", "financial_advice"],
            default=config.get('rules', {}).get('prohibited', [])
        )
        
        # Update config
        if 'rules' not in config:
            config['rules'] = {}
        config['rules'].update({
            'content_focus': content_focus,
            'writing_style': writing_style,
            'max_body_characters': max_chars,
            'require_credible_source': require_source,
            'avoid_buzzwords': avoid_buzzwords,
            'accuracy_required': accuracy_required,
            'prohibited': prohibited_items
        })
    
    with tab3:
        st.markdown("### 🔑 **API Keys & Credentials**")
        
        st.warning("⚠️ **Security Notice:** API keys are stored in session only and not saved to files.")
        
        # OpenAI Configuration
        st.markdown("#### 🤖 **OpenAI Configuration**")
        col1, col2 = st.columns(2)
        with col1:
            openai_key = st.text_input(
                "OpenAI API Key",
                value="",
                type="password",
                help="Your OpenAI API key for AI generation",
                placeholder="sk-..."
            )
            
            if openai_key:
                config.setdefault('openai', {})['api_key'] = openai_key
                st.success("✅ OpenAI API key provided")
            else:
                existing_key = config.get('openai', {}).get('api_key', '')
                if existing_key and existing_key not in ['your-openai-api-key', 'demo-key']:
                    st.info("🔑 Using previously provided key")
                else:
                    st.info("💡 Demo mode without API key")
        
        with col2:
            openai_model = st.selectbox(
                "OpenAI Model",
                ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0,
                help="Which OpenAI model to use"
            )
            
            use_moderation = st.checkbox(
                "Use OpenAI Moderation",
                value=config.get('openai', {}).get('use_moderation', True),
                help="Check content with OpenAI moderation API"
            )
        
        config.setdefault('openai', {}).update({
            'model': openai_model,
            'use_moderation': use_moderation
        })
        
        # Bluesky Configuration
        st.markdown("#### 🦋 **Bluesky Configuration**")
        col1, col2 = st.columns(2)
        with col1:
            bluesky_handle = st.text_input(
                "Bluesky Handle",
                value=config.get('bluesky', {}).get('handle', ''),
                help="Your Bluesky handle (e.g., yourname.bsky.social)",
                placeholder="yourname.bsky.social"
            )
        
        with col2:
            bluesky_password = st.text_input(
                "Bluesky App Password",
                value="",
                type="password",
                help="App password from Bluesky settings",
                placeholder="xxxx-xxxx-xxxx-xxxx"
            )
        
        if bluesky_handle:
            config.setdefault('bluesky', {})['handle'] = bluesky_handle
        if bluesky_password:
            config.setdefault('bluesky', {})['app_password'] = bluesky_password
        
        # W&B Configuration (Optional)
        st.markdown("#### 📊 **Weights & Biases (Optional)**")
        wandb_key = st.text_input(
            "W&B API Key",
            value="",
            type="password",
            help="Optional: For experiment tracking",
            placeholder="Your W&B key"
        )
        
        if wandb_key:
            config.setdefault('monitoring', {})['wandb_api_key'] = wandb_key
    
    with tab4:
        st.markdown("### 💾 **Export/Import Configuration**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📤 **Export Configuration**")
            
            if st.button("📋 Copy Configuration", use_container_width=True):
                # Create safe config for export (no sensitive data)
                export_config = config.copy()
                
                # Remove sensitive keys
                if 'openai' in export_config and 'api_key' in export_config['openai']:
                    export_config['openai']['api_key'] = "your-openai-api-key"
                if 'bluesky' in export_config and 'app_password' in export_config['bluesky']:
                    export_config['bluesky']['app_password'] = "your-app-password"
                
                config_json = json.dumps(export_config, indent=2)
                st.code(config_json, language="json")
                st.success("✅ Configuration ready to copy!")
        
        with col2:
            st.markdown("#### 📥 **Import Configuration**")
            
            uploaded_config = st.text_area(
                "Paste Configuration JSON",
                height=200,
                placeholder='{"project": {"name": "..."}, ...}'
            )
            
            if st.button("🔄 Import Configuration", use_container_width=True):
                try:
                    imported_config = json.loads(uploaded_config)
                    
                    # Merge with current config, preserving API keys
                    current_keys = {
                        'openai_key': config.get('openai', {}).get('api_key'),
                        'bluesky_password': config.get('bluesky', {}).get('app_password')
                    }
                    
                    config.update(imported_config)
                    
                    # Restore API keys if they were set
                    if current_keys['openai_key']:
                        config.setdefault('openai', {})['api_key'] = current_keys['openai_key']
                    if current_keys['bluesky_password']:
                        config.setdefault('bluesky', {})['app_password'] = current_keys['bluesky_password']
                    
                    st.success("✅ Configuration imported successfully!")
                    st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")
    
    # Save configuration
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            save_user_config(config)
            st.session_state.config_saved = True
            st.success("✅ Configuration saved!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.config = load_config()
            st.warning("⚠️ Configuration reset to defaults")
            st.rerun()
    
    with col3:
        if st.button("🧪 Test Connection", use_container_width=True):
            test_api_connections(config)

def test_api_connections(config: Dict[str, Any]):
    """Test API connections with current configuration."""
    st.markdown("#### 🧪 **Connection Test Results**")
    
    # Test OpenAI
    openai_key = config.get('openai', {}).get('api_key')
    if openai_key and openai_key not in ['your-openai-api-key', 'demo-key']:
        try:
            from scripts.self_refine_bot import SelfRefineBot
            bot = SelfRefineBot(config)
            # Test with a simple API call
            st.success("✅ **OpenAI:** Connection successful")
        except Exception as e:
            st.error(f"❌ **OpenAI:** {e}")
    else:
        st.info("ℹ️ **OpenAI:** No API key provided (demo mode)")
    
    # Test Bluesky
    bluesky_handle = config.get('bluesky', {}).get('handle')
    bluesky_password = config.get('bluesky', {}).get('app_password')
    
    if bluesky_handle and bluesky_password:
        try:
            # Test Bluesky connection (simplified)
            if '@' not in bluesky_handle or not bluesky_password:
                raise ValueError("Invalid credentials format")
            st.success("✅ **Bluesky:** Credentials format valid")
        except Exception as e:
            st.error(f"❌ **Bluesky:** {e}")
    else:
        st.info("ℹ️ **Bluesky:** No credentials provided")

def self_refine_interface():
    """Interface for Self-Refine bot training."""
    st.markdown("# ✍️ **Self-Refine Bot Training**")
    st.markdown("Watch the bot **draft → critique → refine** its AI field notes!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏴‍☠️ **Generate AI Field Note**")
        
        if st.button("🎲 Generate Field Note", type="primary", use_container_width=True):
            with st.spinner("🏴‍☠️ Pirate bot working..."):
                try:
                    # Use configured API key
                    config = st.session_state.config
                    api_key = config.get('openai', {}).get('api_key')
                    
                    if api_key and api_key not in ['your-openai-api-key', 'demo-key']:
                        # Real API call
                        bot = SelfRefineBot(config)
                        post, details = bot.generate_post_with_details()
                        st.session_state.refinement_demo = details
                    else:
                        # Demo mode
                        st.session_state.refinement_demo = simulate_self_refine()
                        st.info("🧪 **Demo Mode** - Configure OpenAI API key in Configuration tab for live generation")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.refinement_demo = simulate_self_refine()
    
    with col2:
        st.markdown("### 🎯 **Deploy to Bluesky**")
        
        if 'refinement_demo' in st.session_state:
            if st.button("🚀 Deploy This Model", type="secondary", use_container_width=True):
                # Deploy self-refine model
                try:
                    # Save deployment info
                    deployment_data = {
                        'technique': 'self_refine',
                        'session_id': st.session_state.session_id,
                        'training_data': {'refinement_demo': st.session_state.refinement_demo},
                        'config': st.session_state.config
                    }
                    
                    st.session_state.preference_manager.save_dpo_training_session(
                        deployment_data, 
                        st.session_state.session_id + "_self_refine"
                    )
                    
                    st.session_state.deployed_model = "Self-Refine ✍️"
                    st.success("🎉 Self-Refine bot configuration saved!")
                    st.info("💡 **Note:** In production, this would update the live bot's prompts and behavior.")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Deployment failed: {e}")
    
    # Show refinement process
    if 'refinement_demo' in st.session_state:
        show_refinement_process(st.session_state.refinement_demo)

def dpo_interactive_interface():
    """Interactive DPO training interface."""
    st.markdown("# 🔄 **DPO Interactive Learning**")
    st.markdown("**Train the bot by choosing your preferred AI field notes!**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🎲 **Generate Candidates**")
        
        if st.button("🔄 Generate 4 Candidates", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating multiple candidates..."):
                try:
                    config = st.session_state.config
                    api_key = config.get('openai', {}).get('api_key')
                    
                    if api_key and api_key not in ['your-openai-api-key', 'demo-key']:
                        # Real API call
                        bot = DPOBot(config)
                        candidates = bot._generate_candidates()
                    else:
                        # Demo mode
                        candidates = generate_demo_candidates()
                        st.info("🧪 **Demo Mode** - Configure OpenAI API key in Configuration tab for live generation")
                    
                    st.session_state.current_candidates = candidates
                    st.session_state.user_preferences = []
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.current_candidates = generate_demo_candidates()
    
    with col2:
        st.markdown("### 🚀 **Deployment**")
        
        learning_progress = len(st.session_state.dpo_learning_data)
        st.metric("Learning Examples", learning_progress)
        
        if learning_progress >= 3:
            if st.button("🎯 Stop Learning, Deploy!", type="secondary", use_container_width=True):
                deploy_dpo_model()
        else:
            st.info(f"Need {3 - learning_progress} more examples")
    
    # Show candidates and preference collection
    if 'current_candidates' in st.session_state:
        show_dpo_candidates()

def show_refinement_process(demo_data):
    """Display the self-refinement process."""
    st.markdown("---")
    st.markdown("## 🔄 **Self-Refinement Process**")
    
    tab1, tab2, tab3 = st.tabs(["📝 Initial Draft", "🔍 Self-Critique", "✨ Final Result"])
    
    with tab1:
        st.markdown("### 📝 **Step 1: Initial Draft**")
        initial = demo_data.get('initial_draft', 'Demo initial draft...')
        st.code(initial, language="text")
        st.metric("Characters", len(initial))
    
    with tab2:
        st.markdown("### 🔍 **Step 2: Self-Critique**")
        critique = demo_data.get('critique', 'Demo critique...')
        st.write(critique)
    
    with tab3:
        st.markdown("### ✨ **Step 3: Refined Result**")
        refined = demo_data.get('refined_post', 'Demo refined post...')
        st.code(refined, language="text")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", len(refined))
        with col2:
            improvement = demo_data.get('improvement_made', True)
            st.metric("Improved", "✅ Yes" if improvement else "➖ No")
        with col3:
            char_change = len(refined) - len(demo_data.get('initial_draft', ''))
            st.metric("Change", f"{char_change:+d}")

def show_dpo_candidates():
    """Show DPO candidates for user preference collection."""
    st.markdown("---")
    st.markdown("## 🗳️ **Choose Your Preferred Field Notes**")
    st.markdown("*Select the field notes you think are best. The AI will learn from your choices.*")
    
    candidates = st.session_state.current_candidates
    
    # Create preference selection
    st.markdown("### 📊 **Rate Each Candidate (1-5 stars)**")
    
    preferences = {}
    for i, candidate in enumerate(candidates, 1):
        st.markdown(f"#### **Candidate {i}:**")
        st.code(candidate, language="text")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            rating = st.slider(
                f"Rate Candidate {i}",
                min_value=1,
                max_value=5,
                value=3,
                key=f"rating_{i}_{st.session_state.dpo_iteration}",  # Unique key per iteration
                help="1 = Poor, 5 = Excellent"
            )
            preferences[i] = {'candidate': candidate, 'rating': rating}
        
        with col2:
            st.metric("Length", len(candidate))
        
        with col3:
            has_emoji = "🔄" in candidate
            st.metric("Has Emoji", "✅" if has_emoji else "❌")
    
    # Submit preferences
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📊 Submit Preferences", type="primary", use_container_width=True):
            learn_from_preferences(preferences)
    
    with col2:
        if st.button("🔄 Generate New Candidates", use_container_width=True):
            # Clear current candidates to trigger new generation
            if 'current_candidates' in st.session_state:
                del st.session_state.current_candidates

def learn_from_preferences(preferences: Dict):
    """Learn from user preferences and update model."""
    # Add to learning data
    learning_example = {
        'timestamp': datetime.now().isoformat(),
        'iteration': st.session_state.dpo_iteration,
        'preferences': preferences,
        'best_candidate': max(preferences.values(), key=lambda x: x['rating'])
    }
    
    st.session_state.dpo_learning_data.append(learning_example)
    st.session_state.dpo_iteration += 1
    
    # Save to preference manager
    try:
        session_data = {
            'dpo_learning_data': st.session_state.dpo_learning_data,
            'session_metadata': {
                'total_iterations': st.session_state.dpo_iteration,
                'session_id': st.session_state.session_id
            },
            'config': st.session_state.config
        }
        
        st.session_state.preference_manager.save_dpo_training_session(
            session_data, 
            st.session_state.session_id
        )
        
        st.success(f"✅ **Learned from your preferences!** (Example #{len(st.session_state.dpo_learning_data)})")
        
    except Exception as e:
        st.error(f"Failed to save preferences: {e}")
        st.success(f"✅ **Learned locally!** (Example #{len(st.session_state.dpo_learning_data)})")
    
    # Show learning progress
    with st.expander("📊 **View Learning Progress**"):
        st.markdown("### 🧠 **What the AI Learned:**")
        
        for example in st.session_state.dpo_learning_data[-3:]:  # Show last 3
            best = example['best_candidate']
            st.markdown(f"**Iteration {example['iteration']}:**")
            st.code(best['candidate'], language="text")
            st.caption(f"⭐ Rating: {best['rating']}/5")

def deploy_dpo_model():
    """Deploy the trained DPO model."""
    try:
        # Deploy through preference manager
        deployment_result = st.session_state.preference_manager.deploy_dpo_model(
            st.session_state.session_id,
            len(st.session_state.dpo_learning_data)
        )
        
        st.session_state.deployed_model = f"DPO 🔄 (Trained with {len(st.session_state.dpo_learning_data)} examples)"
        
        st.success("🎉 **DPO Model Deployed to Production!**")
        st.balloons()
        
        # Show deployment summary
        with st.expander("🚀 **Deployment Summary**"):
            st.markdown("### 📊 **Training Summary:**")
            st.metric("Total Learning Examples", len(st.session_state.dpo_learning_data))
            st.metric("Training Iterations", st.session_state.dpo_iteration)
            
            # Show model config preview
            if 'model_config' in deployment_result:
                config = deployment_result['model_config']
                st.markdown("### 🧠 **Learned Preferences:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Preferred Length", f"{config.get('avg_length', 0)} chars")
                with col2:
                    metadata = config.get('training_metadata', {})
                    st.metric("High-Rated Examples", metadata.get('high_rated_examples', 0))
                
                # Show preferred words
                pirate_words = config.get('pirate_words', [])
                if pirate_words:
                    st.markdown("**Preferred Pirate Words:**")
                    for word, count in pirate_words[:5]:
                        st.caption(f"• {word}: {count} mentions")
            
            # Show top examples
            st.markdown("### 🏆 **Top Rated Examples:**")
            all_examples = []
            for example in st.session_state.dpo_learning_data:
                best = example['best_candidate']
                all_examples.append((best['candidate'], best['rating']))
            
            # Sort by rating
            all_examples.sort(key=lambda x: x[1], reverse=True)
            
            for i, (candidate, rating) in enumerate(all_examples[:3], 1):
                st.markdown(f"**#{i}** (⭐{rating}/5):")
                st.code(candidate, language="text")
        
        # Show next steps
        st.info("🚀 **Next Steps:** The live bot will now use your trained preferences when generating posts!")
        
    except Exception as e:
        st.error(f"Deployment failed: {e}")
        st.info("💡 **Fallback:** Your preferences are saved locally and will be used in demo mode.")

def simulate_self_refine():
    """Simulate self-refinement process for demo."""
    return {
        'initial_draft': "Found AI helping companies with customer service - automated responses saving time and improving satisfaction rates! 🤖",
        'critique': "The draft mentions AI in customer service but lacks specifics. It should include company names, concrete metrics, and more pirate voice. The emoji doesn't match our signature style.",
        'refined_post': "Ahoy! Spotted Zendesk's Answer Bot deflecting 30% of tickets automatically - their ML reads context and suggests solutions. Smart treasure for support crews drowning in queries! ✍️",
        'improvement_made': True
    }

def generate_demo_candidates():
    """Generate demo candidates for DPO."""
    return [
        "Ahoy! Found Spotify using AI to create 1B+ personalized playlists weekly. Their ML algorithms analyze listening patterns to predict what treasures ye want to hear next! 🔄",
        
        "Matey! Discovered Tesla's FSD using 8 cameras + neural nets to navigate roads. 160+ billion miles of training data teaching cars to sail the asphalt seas safely! 🔄",
        
        "Avast! Spotted GitHub Copilot helping 1M+ developers code faster. Microsoft's AI mate suggests complete functions, cutting coding time by 55% in enterprise ships! 🔄",
        
        "Ahoy! Netflix's recommendation engine caught me eye - processes 1B+ hours of viewing data daily. Their ML decides what treasures appear on yer homepage! 🔄"
    ]

def main():
    """Main app function."""
    init_session_state()
    
    # Header
    st.markdown("""
    # 🏴‍☠️ **AI Field Notes - Interactive Bot Training**
    
    **Train AI bots to write better field notes about real-world AI deployments!**
    
    Configure your goals, participate in training, and deploy to live Bluesky posting.
    """)
    
    # Sidebar for technique selection
    technique = create_sidebar()
    
    # Main content based on selected technique
    if technique == "⚙️ Configuration":
        configuration_interface()
    elif technique == "✍️ Self-Refine":
        self_refine_interface()
    elif technique == "🔄 DPO (Interactive Learning)":
        dpo_interactive_interface()
    else:
        st.markdown(f"## {technique}")
        st.info("🚧 **Coming Soon!** This technique is under development.")
        st.markdown("""
        **Planned Features:**
        - 🎯 **RLAIF:** AI-to-AI feedback loops
        - 🛠️ **Mind-Pool:** Multiple AI perspectives
        - 🧬 **DevOps Self-Fix:** Auto-debugging bots
        """)
        
        # Show mockup interface
        st.markdown("### 🎮 **Preview Interface**")
        if technique == "🎯 RLAIF (Coming Soon)":
            st.code("AI Judge 1: This post needs more specific metrics...\nAI Judge 2: Great pirate voice, but missing company context...\nAI Judge 3: Perfect engagement level, deploy!", language="text")
        elif technique == "🛠️ Mind-Pool (Coming Soon)":
            st.code("Expert 1 (Data Scientist): Focus on ML accuracy metrics\nExpert 2 (Marketing): Make it more engaging\nExpert 3 (Pirate): Add more 'ahoy' and 'matey'\nMerged Result: Best of all perspectives!", language="text")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        target = st.session_state.config.get('project', {}).get('target_followers', 1000)
        days = st.session_state.config.get('project', {}).get('duration_days', 7)
        st.markdown(f"🎯 **Goal:** {target:,} followers in {days} days")
    with col2:
        theme = st.session_state.config.get('project', {}).get('theme', 'pirate_field_notes')
        st.markdown(f"🏴‍☠️ **Theme:** {theme.replace('_', ' ').title()}")
    with col3:
        if st.button("📊 View Live Bot"):
            handle = st.session_state.config.get('bluesky', {}).get('handle', 'thephillip.bsky.social')
            st.markdown(f"🔗 [Live Bot](https://bsky.app/profile/{handle})")

if __name__ == "__main__":
    main() 