#!/usr/bin/env python3
"""
Runner script for the Streamlit dashboard
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting Bot Showdown Dashboard...")
    
    # Check if streamlit is available
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Check if dashboard file exists
    dashboard_path = Path("dashboard/app.py")
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        return 1
    
    print("🌐 Starting dashboard at http://localhost:8501")
    print("Press Ctrl+C to stop")
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
        return 0

if __name__ == "__main__":
    exit(main()) 