#!/usr/bin/env python3
"""
Entry point for the Bot Showdown Orchestrator
Fixes import paths and starts the orchestrator
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import
from scripts.orchestrator import BotOrchestrator

def main():
    """Main entry point."""
    print("🚀 Starting Bluesky Bot Showdown...")
    print("=" * 50)
    
    try:
        # Initialize and start orchestrator
        orchestrator = BotOrchestrator()
        orchestrator.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 