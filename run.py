#!/usr/bin/env python3
"""
Startup script for Instagram Auto Poster Web Interface
"""

from app import app

if __name__ == '__main__':
    print("🚀 Starting Instagram Auto Poster Web Interface...")
    print("📱 Access the dashboard at: http://localhost:5001")
    print("⚡ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001) 