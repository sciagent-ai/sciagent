#!/usr/bin/env python3
"""Entry point for running SCI Agent as a module.

This allows the agent to be invoked via:
python -m sciagent [args]
"""

from .main import main

if __name__ == "__main__":
    main()