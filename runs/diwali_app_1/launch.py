#!/usr/bin/env python3
"""
Simple launcher for the Diwali App
Starts a local web server and opens the app in your default browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 8000
HOST = "localhost"

def main():
    # Change to the script's directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create HTTP server
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
            url = f"http://{HOST}:{PORT}"
            print("=" * 60)
            print("🪔  DIWALI APP - Festival of Lights  🪔")
            print("=" * 60)
            print(f"\n✨ Server started successfully!")
            print(f"🌐 URL: {url}")
            print(f"📂 Serving from: {script_dir}")
            print(f"\n🎆 Opening in your default browser...")
            print(f"\n⚠️  Press Ctrl+C to stop the server\n")
            print("=" * 60)
            
            # Open browser
            webbrowser.open(url)
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("👋 Server stopped. Happy Diwali! 🪔")
        print("=" * 60)
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use.")
            print(f"💡 Try closing other applications or use a different port.")
            print(f"   You can also open index.html directly in your browser.")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
