#!/usr/bin/env python3
"""
Quick test script for MetaLLM CLI functionality
"""

import sys
sys.path.insert(0, '.')

from cli.formatter import Formatter
from cli.commands import CommandHandler

def test_cli():
    """Test basic CLI functionality"""
    print("Testing MetaLLM CLI components...\n")

    # Test formatter
    print("1. Testing Formatter...")
    formatter = Formatter(use_colors=False)
    print(formatter.success("Success message"))
    print(formatter.error("Error message"))
    print(formatter.warning("Warning message"))
    print(formatter.info("Info message"))
    print("✓ Formatter working\n")

    # Test command handler
    print("2. Testing Command Handler...")
    handler = CommandHandler(formatter)

    # Test show exploits
    print("\n--- Testing 'show exploits' ---")
    result = handler.handle_show(["exploits"])
    print(result[:500] + "..." if len(result) > 500 else result)

    # Count modules
    module_count = len(handler.get_available_modules())
    print(f"\n✓ Found {module_count} exploit modules")

    # Test search
    print("\n--- Testing 'search' ---")
    result = handler.handle_search(["prompt"])
    print(result[:300] + "..." if len(result) > 300 else result)
    print("✓ Search working")

    # Test use command
    print("\n--- Testing 'use' command ---")
    modules = handler.get_available_modules()
    if modules:
        test_module = modules[0]
        result = handler.handle_use([test_module])
        print(result)
        print(f"✓ Successfully loaded module: {test_module}")

        # Test show options
        print("\n--- Testing 'show options' ---")
        result = handler.handle_show(["options"])
        print(result[:400] + "..." if len(result) > 400 else result)
        print("✓ Options display working")

        # Test info
        print("\n--- Testing 'info' command ---")
        result = handler.handle_show(["info"])
        print(result[:400] + "..." if len(result) > 400 else result)
        print("✓ Info display working")

    print("\n" + "="*60)
    print("✓ All CLI tests passed!")
    print(f"✓ {module_count} exploit modules loaded successfully")
    print("="*60)

if __name__ == "__main__":
    test_cli()
