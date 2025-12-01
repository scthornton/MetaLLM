#!/usr/bin/env python3
"""
Test script for new exploit modules
"""

import sys
sys.path.insert(0, '.')

from cli.formatter import Formatter
from cli.commands import CommandHandler

def test_new_modules():
    """Test newly created exploit modules"""
    print("Testing newly created exploit modules...\n")

    formatter = Formatter(use_colors=False)
    handler = CommandHandler(formatter)

    # Test new modules
    new_modules = [
        "exploits/rag/document_poisoning",
        "exploits/rag/vector_injection",
        "exploits/rag/retrieval_manipulation",
        "exploits/rag/knowledge_corruption",
        "exploits/agent/tool_misuse",
        "exploits/agent/memory_manipulation",
        "exploits/api/excessive_agency",
        "exploits/api/unauthorized_access"
    ]

    print(f"Testing {len(new_modules)} newly created modules:\n")

    for module_path in new_modules:
        print(f"Testing: {module_path}")

        # Try to load module
        result = handler.handle_use([module_path])

        if "[+]" in result:  # Success marker
            print(f"  ✓ Module loaded successfully")

            # Show options
            options_result = handler.handle_show(["options"])
            if "Module Options" in options_result:
                print(f"  ✓ Options available")

            # Show info
            info_result = handler.handle_show(["info"])
            if "Description" in info_result:
                print(f"  ✓ Module info complete")

            print()
        else:
            print(f"  ✗ Failed to load: {result}")
            print()

if __name__ == "__main__":
    test_new_modules()
