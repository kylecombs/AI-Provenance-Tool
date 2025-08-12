#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Provenance Tool - Development Server Startup Script
Cross-platform script to start the development server

Usage:
    python run_dev.py [--port PORT] [--host HOST]
"""

import os
import sys
import subprocess
import argparse
import socket
from pathlib import Path

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8000, max_port=8010):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        if not is_port_in_use(port):
            return port
    return None

def main():
    parser = argparse.ArgumentParser(description="Start AI Provenance Tool development server")
    parser.add_argument("--port", "-p", default=8000, type=int, help="Port to run server on (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    args = parser.parse_args()

    # Check if we're in the backend directory
    if not Path("app/main.py").exists():
        print("ERROR: Please run this script from the backend directory")
        print("   Current directory:", Path.cwd())
        sys.exit(1)

    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    # Determine the correct python and pip paths
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like (macOS, Linux)
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"

    # Check if FastAPI is installed
    try:
        result = subprocess.run([str(python_path), "-c", "import fastapi"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Installing dependencies...")
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        sys.exit(1)

    # Check if port is available
    if is_port_in_use(args.port):
        print(f"Port {args.port} is already in use")
        available_port = find_available_port(args.port + 1)
        if available_port:
            print(f"Using alternative port {available_port}")
            args.port = available_port
        else:
            print("No available ports found between 8000-8010")
            sys.exit(1)

    # Print startup info
    print("Starting AI Provenance Tool Development Server...")
    print(f"API Documentation: http://localhost:{args.port}/docs")
    print(f"Health Check: http://localhost:{args.port}/health") 
    print("Press Ctrl+C to stop")
    print()

    # Start the server
    cmd = [
        str(python_path), "-m", "uvicorn", "app.main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if not args.no_reload:
        cmd.append("--reload")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()