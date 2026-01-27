#!/usr/bin/env python3
"""
Local runner for RCWA service.
Runs in mock mode if S4 is not installed.

Usage:
    python run_local.py              # Run on port 8001
    python run_local.py --port 8002  # Run on custom port

To install S4 properly (if not on Mac ARM):
    conda create -n s4env python=3.9
    conda activate s4env
    conda install -c conda-forge s4py
    pip install fastapi uvicorn numpy pydantic
    python run_local.py
"""

import sys
import os
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="Run RCWA simulation service locally")
    parser.add_argument("--port", type=int, default=8001, help="Port to run on (default: 8001)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    # Check dependencies
    try:
        import fastapi
        import uvicorn
        import numpy
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nInstall with: pip install fastapi uvicorn numpy pydantic")
        sys.exit(1)

    # Check S4
    try:
        import S4
        print("✓ S4 RCWA library found - running in full simulation mode")
    except ImportError:
        print("⚠ S4 not installed - running in MOCK mode")
        print("  Mock mode returns physics-based approximations, not real RCWA results.")
        print("  To install S4: conda install -c conda-forge s4py")
        print()

    print(f"Starting RCWA service at http://{args.host}:{args.port}")
    print(f"API docs at http://{args.host}:{args.port}/docs")
    print(f"Help endpoint: http://{args.host}:{args.port}/help")
    print()

    import uvicorn
    uvicorn.run("api:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
