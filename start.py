#!/usr/bin/env python3
"""
Startup script for Railway deployment
Runs bot orchestrator, dashboard, or interactive training app based on SERVICE_TYPE env var
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    service_type = os.getenv('SERVICE_TYPE', 'bot')
    
    if service_type == 'bot':
        print("🤖 Starting Bot Orchestrator...")
        subprocess.run([sys.executable, 'run_bot.py'])
    
    elif service_type == 'dashboard':
        print("📊 Starting Dashboard...")
        # For Railway, we need to bind to the correct port
        port = os.getenv('PORT', '8501')
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'dashboard/app.py',
            '--server.port', port,
            '--server.address', '0.0.0.0',
            '--server.headless', 'true'
        ])
    
    elif service_type == 'interactive':
        print("🏴‍☠️ Starting Interactive Training App...")
        # For Railway, we need to bind to the correct port
        port = os.getenv('PORT', '8501')
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'interactive_app.py',
            '--server.port', port,
            '--server.address', '0.0.0.0',
            '--server.headless', 'true'
        ])
    
    else:
        print(f"❌ Unknown SERVICE_TYPE: {service_type}")
        print("Set SERVICE_TYPE to 'bot', 'dashboard', or 'interactive'")
        sys.exit(1)

if __name__ == "__main__":
    main() 