"""
Preference Manager for Interactive AI Bot Training
Handles storing and applying user preferences to live bot deployment
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class PreferenceManager:
    """Manages user preferences and applies them to bot deployment."""
    
    def __init__(self, db_path: str = "preferences.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize preference database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                technique TEXT,
                session_id TEXT,
                preferences_data TEXT,
                deployed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create deployed_models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployed_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                technique TEXT,
                model_config TEXT,
                training_examples INTEGER,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_dpo_training_session(self, session_data: Dict[str, Any], session_id: str) -> int:
        """Save DPO training session data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_preferences 
            (timestamp, technique, session_id, preferences_data, deployed)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            'dpo',
            session_id,
            json.dumps(session_data),
            False
        ))
        
        preference_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return preference_id
    
    def deploy_dpo_model(self, session_id: str, training_examples: int) -> Dict[str, Any]:
        """Deploy a DPO model based on training session."""
        # Get training data
        training_data = self.get_training_data(session_id)
        
        if not training_data:
            raise ValueError(f"No training data found for session {session_id}")
        
        # Create model configuration
        model_config = self._create_dpo_model_config(training_data)
        
        # Save deployed model
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mark previous models as inactive
        cursor.execute('''
            UPDATE deployed_models 
            SET status = 'inactive' 
            WHERE technique = 'dpo'
        ''')
        
        # Insert new model
        cursor.execute('''
            INSERT INTO deployed_models 
            (timestamp, technique, model_config, training_examples, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            'dpo',
            json.dumps(model_config),
            training_examples,
            'active'
        ))
        
        # Mark training session as deployed
        cursor.execute('''
            UPDATE user_preferences 
            SET deployed = TRUE 
            WHERE session_id = ? AND technique = 'dpo'
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return {
            'status': 'deployed',
            'model_config': model_config,
            'training_examples': training_examples,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_active_model_config(self, technique: str) -> Optional[Dict[str, Any]]:
        """Get active model configuration for a technique."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model_config FROM deployed_models 
            WHERE technique = ? AND status = 'active'
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (technique,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_training_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Get training data for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preferences_data FROM user_preferences 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        training_data = []
        for result in results:
            data = json.loads(result[0])
            training_data.extend(data.get('dpo_learning_data', []))
        
        return training_data
    
    def _create_dpo_model_config(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create DPO model configuration from training data."""
        
        # Analyze training data to extract preferences
        preferred_features = {
            'avg_length': 0,
            'pirate_words': [],
            'tech_companies': [],
            'metrics_mentioned': [],
            'preferred_style': {}
        }
        
        total_examples = len(training_data)
        if total_examples == 0:
            return preferred_features
        
        # Extract patterns from high-rated examples
        high_rated_examples = []
        for example in training_data:
            best_candidate = example.get('best_candidate', {})
            if best_candidate.get('rating', 0) >= 4:  # 4+ stars
                high_rated_examples.append(best_candidate['candidate'])
        
        if high_rated_examples:
            # Calculate average length of preferred posts
            preferred_features['avg_length'] = sum(len(post) for post in high_rated_examples) // len(high_rated_examples)
            
            # Extract common pirate words
            pirate_words = ['ahoy', 'matey', 'avast', 'spotted', 'discovered', 'treasure', 'crew', 'ship']
            word_counts = {}
            for word in pirate_words:
                count = sum(1 for post in high_rated_examples if word.lower() in post.lower())
                if count > 0:
                    word_counts[word] = count
            
            preferred_features['pirate_words'] = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Extract mentioned companies/technologies
            tech_terms = ['AI', 'ML', 'GPT', 'neural', 'algorithm', 'machine learning', 'deep learning']
            for term in tech_terms:
                count = sum(1 for post in high_rated_examples if term.lower() in post.lower())
                if count > 0:
                    preferred_features['tech_companies'].append((term, count))
        
        # Add preference weights for prompt engineering
        preferred_features['preference_weights'] = {
            'accuracy': 0.4,
            'engagement': 0.3,
            'structure': 0.3
        }
        
        # Add training metadata
        preferred_features['training_metadata'] = {
            'total_examples': total_examples,
            'high_rated_examples': len(high_rated_examples),
            'training_date': datetime.now().isoformat()
        }
        
        return preferred_features
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get active models
        cursor.execute('''
            SELECT technique, model_config, training_examples, timestamp 
            FROM deployed_models 
            WHERE status = 'active'
            ORDER BY timestamp DESC
        ''')
        
        active_models = []
        for row in cursor.fetchall():
            active_models.append({
                'technique': row[0],
                'training_examples': row[2],
                'deployed_at': row[3],
                'config_preview': json.loads(row[1]).get('training_metadata', {})
            })
        
        # Get training sessions
        cursor.execute('''
            SELECT COUNT(*) as total_sessions,
                   SUM(CASE WHEN deployed = TRUE THEN 1 ELSE 0 END) as deployed_sessions
            FROM user_preferences
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'active_models': active_models,
            'total_training_sessions': stats[0] if stats else 0,
            'deployed_sessions': stats[1] if stats else 0
        }


# Global instance
preference_manager = PreferenceManager()


def get_preference_manager() -> PreferenceManager:
    """Get the global preference manager instance."""
    return preference_manager 