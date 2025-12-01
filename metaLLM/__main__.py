"""
MetaLLM CLI Entry Point
"""

import sys
from metaLLM.cli import start_console


def main():
    """Main entry point for MetaLLM CLI"""
    try:
        start_console()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
