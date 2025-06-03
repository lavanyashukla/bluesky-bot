"""Main orchestrator for the Bluesky Bot Showdown."""

import json
import sqlite3
import schedule
import time
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import W&B for logging
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("⚠️ W&B not installed. Run: pip install wandb")

from scripts.self_refine_bot import SelfRefineBot


class BotOrchestrator:
    """Manages the Bluesky bot showdown with round-robin posting."""
    
    def __init__(self, config_path: str = "config/bot_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config['monitoring']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("Orchestrator")
        
        # Initialize W&B if available
        self.wandb_table = None
        self._init_wandb()
        
        # Initialize database
        self.db_path = "bot_showdown.db"
        self._init_database()
        
        # Initialize bots
        self.bots = self._initialize_bots()
        self.current_bot_index = 0
        
        # State
        self.is_running = False
        self.start_time = None
        
        print(f"🤖 Orchestrator initialized with {len(self.bots)} bots")
        self.logger.info(f"Orchestrator initialized with {len(self.bots)} bots")
    
    def _init_wandb(self):
        """Initialize Weights & Biases logging."""
        if WANDB_AVAILABLE:
            try:
                wandb.init(
                    project="bluesky-bot-showdown",
                    name=f"showdown-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    config={
                        "goal_followers": self.config['project']['target_followers'],
                        "duration_days": self.config['project']['duration_days'],
                        "bots_enabled": [bot for bot, config in self.config['bots'].items() if config['enabled']]
                    }
                )
                
                # Create W&B table for tracking post generation process
                self.wandb_table = wandb.Table(columns=[
                    "timestamp",
                    "bot_type", 
                    "prompt",
                    "initial_draft",
                    "initial_draft_length",
                    "critique",
                    "critique_length",
                    "refined_post",
                    "refined_post_length",
                    "improvement_made",
                    "character_change",
                    "post_posted",
                    "post_success",
                    "error_message"
                ])
                
                print("✅ W&B logging initialized with post tracking table")
                self.logger.info("W&B logging initialized with post tracking table")
            except Exception as e:
                print(f"⚠️ W&B initialization failed: {e}")
                self.logger.warning(f"W&B initialization failed: {e}")
        else:
            print("⚠️ W&B not available - install with: pip install wandb")
    
    def log_post_process_to_wandb(self, process_data: Dict[str, Any]):
        """Log the complete post generation process to W&B table."""
        if WANDB_AVAILABLE and self.wandb_table is not None:
            try:
                # Calculate character change
                initial_length = len(process_data.get('initial_draft', ''))
                refined_length = len(process_data.get('refined_post', ''))
                character_change = refined_length - initial_length
                
                self.wandb_table.add_data(
                    process_data.get('timestamp', datetime.now().isoformat()),
                    process_data.get('bot_type', 'unknown'),
                    process_data.get('prompt', ''),
                    process_data.get('initial_draft', ''),
                    len(process_data.get('initial_draft', '')),
                    process_data.get('critique', ''),
                    len(process_data.get('critique', '')),
                    process_data.get('refined_post', ''),
                    len(process_data.get('refined_post', '')),
                    process_data.get('improvement_made', False),
                    character_change,
                    process_data.get('post_posted', False),
                    process_data.get('post_success', False),
                    process_data.get('error_message', '')
                )
                
                # Log the table to W&B
                wandb.log({"post_generation_process": self.wandb_table})
                
                # Also log individual metrics
                wandb.log({
                    "post_posted": 1 if process_data.get('post_posted', False) else 0,
                    "post_length": len(process_data.get('refined_post', '')),
                    "improvement_made": 1 if process_data.get('improvement_made', False) else 0,
                    "character_change": character_change,
                    "post_success": 1 if process_data.get('post_success', False) else 0,
                    "timestamp": datetime.now().timestamp()
                })
                
                print(f"📊 Logged post process to W&B table")
                
            except Exception as e:
                print(f"⚠️ Failed to log to W&B table: {e}")
                self.logger.warning(f"Failed to log to W&B table: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate required keys
            required_keys = ['bluesky', 'openai', 'bots', 'posting', 'rules']
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise ValueError(f"Missing required config keys: {missing_keys}")
            
            return config
            
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            self.logger.info("Please copy config/bot_config.example.json to config/bot_config.json and add your API keys")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def _init_database(self):
        """Initialize SQLite database for storing posts and metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                uri TEXT PRIMARY KEY,
                cid TEXT,
                bot_type TEXT,
                content TEXT,
                timestamp TEXT,
                likes INTEGER DEFAULT 0,
                reposts INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                posted_at TEXT
            )
        ''')
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp TEXT PRIMARY KEY,
                followers INTEGER,
                total_posts INTEGER,
                total_likes INTEGER,
                total_reposts INTEGER,
                bot_stats TEXT
            )
        ''')
        
        # Create post_process table for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_process (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                bot_type TEXT,
                prompt TEXT,
                initial_draft TEXT,
                critique TEXT,
                refined_post TEXT,
                improvement_made BOOLEAN,
                post_success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized with post process tracking")
        self.logger.info("Database initialized with post process tracking")
    
    def _initialize_bots(self) -> List:
        """Initialize all enabled bots."""
        bots = []
        
        # For now, only initialize Self-Refine bot
        # TODO: Add other bot types as they're implemented
        if self.config['bots']['self_refine']['enabled']:
            print("🪲 Initializing Self-Refine Bot...")
            bots.append(SelfRefineBot(self.config))
            print("✅ Self-Refine Bot ready!")
        
        return bots
    
    def start(self):
        """Start the bot showdown."""
        if self.is_running:
            self.logger.warning("Orchestrator is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Schedule round-robin posting
        shift_interval = self.config['posting']['shift_interval_minutes']
        schedule.every(shift_interval).minutes.do(self._post_next)
        
        # Schedule metrics collection
        schedule.every(5).minutes.do(self._collect_metrics)
        
        print(f"\n🚀 Bluesky Bot Showdown started! Posting every {shift_interval} minutes")
        print(f"🎯 Goal: {self.config['project']['target_followers']} followers in {self.config['project']['duration_days']} days")
        print("=" * 60)
        
        self.logger.info(f"🚀 Bot Showdown started! Posting every {shift_interval} minutes")
        self.logger.info(f"Goal: {self.config['project']['target_followers']} followers in {self.config['project']['duration_days']} days")
        
        # Post initial content immediately
        print("📝 Generating first post...")
        self._post_next()
        
        # Main loop
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Check if we should stop (duration reached or goal achieved)
                if self._should_stop():
                    self.stop()
                    
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal, stopping...")
            self.logger.info("Received interrupt signal, stopping...")
            self.stop()
    
    def _post_next(self):
        """Post content from the next bot in rotation."""
        if not self.bots:
            print("❌ No enabled bots available")
            self.logger.error("No enabled bots available")
            return
        
        # Get next bot
        current_bot = self.bots[self.current_bot_index]
        self.current_bot_index = (self.current_bot_index + 1) % len(self.bots)
        
        # Initialize process tracking
        process_data = {
            'timestamp': datetime.now().isoformat(),
            'bot_type': current_bot.bot_type,
            'post_posted': False,
            'post_success': False,
            'error_message': ''
        }
        
        try:
            print(f"\n🎯 {current_bot.name} starting post generation...")
            print("=" * 50)
            
            # Generate post and get process details
            self.logger.info(f"🎯 {current_bot.name} generating post...")
            post_content, refinement_details = current_bot.generate_post_with_details()
            
            # Update process data with refinement details
            process_data.update(refinement_details)
            process_data['post_posted'] = True
            
            print(f"\n📝 Generated Post:")
            print(f"'{post_content}'")
            print(f"Length: {len(post_content)} characters")
            
            # Validate post
            if not current_bot.validate_post(post_content):
                print("❌ Post validation failed!")
                print(f"Content: {post_content[:50]}...")
                process_data['error_message'] = 'Post validation failed'
                self.logger.warning(f"Post validation failed: {post_content[:50]}...")
                
                # Log failed attempt
                self._save_post_process(process_data)
                self.log_post_process_to_wandb(process_data)
                return
            
            print("✅ Post validation passed")
            
            # Post to Bluesky
            print("\n🦋 Attempting to post to Bluesky...")
            post_data = current_bot.post_to_bluesky(post_content)
            
            if post_data:
                # Save to database
                self._save_post(post_data)
                process_data['post_success'] = True
                print(f"✅ Successfully posted to Bluesky!")
                print(f"Post URI: {post_data['uri']}")
                
                self.logger.info(f"✅ Posted: {post_content[:50]}...")
            else:
                print("❌ Failed to post to Bluesky")
                process_data['error_message'] = 'Bluesky API posting failed'
                self.logger.error("Failed to post to Bluesky")
            
            print("=" * 50)
            
            # Save process details to database and W&B
            self._save_post_process(process_data)
            self.log_post_process_to_wandb(process_data)
                
        except Exception as e:
            print(f"❌ Error during post generation/posting: {e}")
            process_data['error_message'] = str(e)
            self.logger.error(f"Error during post generation/posting: {e}")
            
            # Log error
            self._save_post_process(process_data)
            self.log_post_process_to_wandb(process_data)
    
    def _save_post_process(self, process_data: Dict[str, Any]):
        """Save post generation process to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO post_process 
            (timestamp, bot_type, prompt, initial_draft, critique, refined_post, improvement_made, post_success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            process_data.get('timestamp'),
            process_data.get('bot_type'),
            process_data.get('prompt', ''),
            process_data.get('initial_draft', ''),
            process_data.get('critique', ''),
            process_data.get('refined_post', ''),
            process_data.get('improvement_made', False),
            process_data.get('post_success', False),
            process_data.get('error_message', '')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Post process saved to database")
    
    def _save_post(self, post_data: Dict[str, Any]):
        """Save post data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO posts 
            (uri, cid, bot_type, content, timestamp, likes, reposts, replies, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_data['uri'],
            post_data['cid'],
            post_data['bot_type'],
            post_data['text'],
            post_data['timestamp'],
            post_data['likes'],
            post_data['reposts'],
            post_data['replies'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Post saved to database")
    
    def _collect_metrics(self):
        """Collect current metrics for dashboard."""
        try:
            # Get current follower count (mock for now)
            # TODO: Implement actual Bluesky API call to get follower count
            followers = 42  # Mock data
            
            # Get post stats from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM posts')
            total_posts = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(likes), SUM(reposts) FROM posts')
            result = cursor.fetchone()
            total_likes = result[0] or 0
            total_reposts = result[1] or 0
            
            # Get process stats
            cursor.execute('SELECT COUNT(*) FROM post_process WHERE improvement_made = 1')
            successful_improvements = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM post_process')
            total_attempts = cursor.fetchone()[0]
            
            conn.close()
            
            # Collect bot stats
            bot_stats = {}
            for bot in self.bots:
                bot_stats[bot.bot_type] = bot.get_stats()
            
            # Save metrics
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO metrics 
                (timestamp, followers, total_posts, total_likes, total_reposts, bot_stats)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                followers,
                total_posts,
                total_likes,
                total_reposts,
                json.dumps(bot_stats)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"📊 Metrics: {followers} followers, {total_posts} posts, {total_likes} likes, {successful_improvements}/{total_attempts} improvements")
            
            # Log to W&B
            if WANDB_AVAILABLE:
                improvement_rate = (successful_improvements / max(1, total_attempts)) * 100
                wandb.log({
                    "followers": followers,
                    "total_posts": total_posts,
                    "total_likes": total_likes,
                    "total_reposts": total_reposts,
                    "successful_improvements": successful_improvements,
                    "total_attempts": total_attempts,
                    "improvement_rate": improvement_rate,
                    "timestamp": datetime.now().timestamp()
                })
            
            self.logger.info(f"📊 Metrics: {followers} followers, {total_posts} posts, {total_likes} likes")
            
        except Exception as e:
            print(f"❌ Error collecting metrics: {e}")
            self.logger.error(f"Error collecting metrics: {e}")
    
    def _should_stop(self) -> bool:
        """Check if orchestrator should stop."""
        if not self.start_time:
            return False
        
        # Check duration
        duration = datetime.now() - self.start_time
        max_duration = timedelta(days=self.config['project']['duration_days'])
        
        if duration > max_duration:
            print("🏁 Duration limit reached")
            self.logger.info("🏁 Duration limit reached")
            return True
        
        # TODO: Check if follower goal reached
        # This would require actual Bluesky API integration
        
        return False
    
    def stop(self):
        """Stop the bot showdown."""
        self.is_running = False
        schedule.clear()
        
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"🛑 Bot Showdown stopped after {duration}")
            self.logger.info(f"🛑 Bot Showdown stopped after {duration}")
        
        # Final metrics collection
        self._collect_metrics()
        
        print("\n📊 Final stats:")
        self.logger.info("Final stats:")
        for bot in self.bots:
            stats = bot.get_stats()
            print(f"  {stats['name']}: {stats['stats']['posts_created']} posts, {stats['stats']['improvements_made']} improvements")
            self.logger.info(f"  {stats['name']}: {stats['stats']['posts_created']} posts, {stats['stats']['improvements_made']} improvements")
        
        # Close W&B
        if WANDB_AVAILABLE:
            wandb.finish()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'active_bots': len(self.bots),
            'current_bot': self.bots[self.current_bot_index].name if self.bots else None,
            'next_post_in': self._get_next_post_time()
        }
    
    def _get_next_post_time(self) -> Optional[str]:
        """Get time until next scheduled post."""
        next_job = schedule.next_run()
        if next_job:
            return next_job.isoformat()
        return None


if __name__ == "__main__":
    # Check if config exists
    config_path = Path("config/bot_config.json")
    if not config_path.exists():
        print("❌ Configuration file not found!")
        print("Please copy config/bot_config.example.json to config/bot_config.json")
        print("and add your Bluesky and OpenAI API keys.")
        exit(1)
    
    # Start orchestrator
    orchestrator = BotOrchestrator()
    orchestrator.start() 