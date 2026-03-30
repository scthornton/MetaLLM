#!/usr/bin/env python3
"""
MetaLLM - AI Security Testing & Exploitation Framework

Main entry point for the MetaLLM interactive console.

Usage:
    ./metallm                  # Start interactive console
    ./metallm --no-color       # Start console without colors
    ./metallm --help           # Show help message

Author: Scott Thornton (perfecXion.ai)
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from cli.console import main

if __name__ == "__main__":
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Start the console
    main()
