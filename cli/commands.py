"""
CLI Command Handlers

Implements all command handlers for the MetaLLM interactive console.

Author: Scott Thornton (perfecXion.ai)
"""

import os
import sys
import importlib
import inspect
from typing import Optional, Dict, Any, List
from pathlib import Path

from cli.formatter import Formatter
from modules.exploits.base import ExploitModule


class CommandHandler:
    """Handles CLI command execution"""

    def __init__(self, formatter: Formatter):
        self.formatter = formatter
        self.current_module = None
        self.current_module_instance = None
        self.modules_cache = {}
        self.modules_path = Path(__file__).parent.parent / "modules" / "exploits"

        # Load all available modules
        self._load_modules()

    def _load_modules(self):
        """Discover and cache all available exploit modules"""
        self.modules_cache = {}

        # Scan modules directory
        for category_dir in self.modules_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue

            category = category_dir.name

            for module_file in category_dir.glob("*.py"):
                if module_file.name.startswith('_'):
                    continue

                module_name = module_file.stem
                module_path = f"exploits/{category}/{module_name}"

                self.modules_cache[module_path] = {
                    "path": module_path,
                    "category": category,
                    "file": str(module_file),
                    "name": module_name
                }

    def handle_use(self, args: List[str]) -> str:
        """Handle 'use' command to select a module"""
        if not args:
            return self.formatter.error("Usage: use <module_path>")

        module_path = args[0]

        # Check if module exists
        if module_path not in self.modules_cache:
            # Try fuzzy matching
            matches = [m for m in self.modules_cache.keys() if module_path in m]
            if matches:
                return self.formatter.error(
                    f"Module not found. Did you mean:\n  " + "\n  ".join(matches[:5])
                )
            return self.formatter.error(f"Module '{module_path}' not found")

        # Load the module
        try:
            module_info = self.modules_cache[module_path]
            category = module_info["category"]
            name = module_info["name"]

            # Import the module
            import_path = f"modules.exploits.{category}.{name}"
            module = importlib.import_module(import_path)

            # Find the ExploitModule subclass
            module_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (inspect.isclass(item) and
                    issubclass(item, ExploitModule) and
                    item != ExploitModule):
                    module_class = item
                    break

            if not module_class:
                return self.formatter.error(f"No exploit module class found in {module_path}")

            # Instantiate the module
            self.current_module_instance = module_class()
            self.current_module = module_path

            return self.formatter.success(f"Using module: {module_path}")

        except Exception as e:
            return self.formatter.error(f"Failed to load module: {str(e)}")

    def handle_show(self, args: List[str]) -> str:
        """Handle 'show' command"""
        if not args:
            return self.formatter.error("Usage: show <exploits|modules|options|info>")

        show_type = args[0].lower()

        if show_type in ["exploits", "modules"]:
            return self._show_modules()
        elif show_type == "options":
            return self._show_options()
        elif show_type == "info":
            return self._show_info()
        else:
            return self.formatter.error(f"Unknown show type: {show_type}")

    def _show_modules(self) -> str:
        """Show all available modules"""
        if not self.modules_cache:
            return self.formatter.warning("No modules found")

        # Group by category
        categories = {}
        for module_path, module_info in self.modules_cache.items():
            category = module_info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(module_path)

        output = [self.formatter.heading("Available Exploit Modules")]

        for category in sorted(categories.keys()):
            output.append(f"\n{self.formatter.subheading(category.upper() + ' Exploits')}")
            for module_path in sorted(categories[category]):
                output.append(f"  {module_path}")

        output.append(f"\n{self.formatter.info(f'Total modules: {len(self.modules_cache)}')}")

        return "\n".join(output)

    def _show_options(self) -> str:
        """Show options for current module"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        module_data = {
            "name": self.current_module_instance.name,
            "options": {}
        }

        # Get options from module
        for opt_name, opt_obj in self.current_module_instance.options.items():
            module_data["options"][opt_name] = {
                "value": opt_obj.value,
                "required": opt_obj.required,
                "description": opt_obj.description,
                "enum_values": opt_obj.enum_values
            }

        # Format as table
        option_rows = []
        for opt_name, opt_data in module_data["options"].items():
            required = "yes" if opt_data["required"] else "no"
            current = str(opt_data["value"])
            description = opt_data["description"]

            option_rows.append([opt_name, required, current, description])

        return self.formatter.table(
            ["Name", "Required", "Current Setting", "Description"],
            option_rows,
            title=f"Module Options: {self.current_module}"
        )

    def _show_info(self) -> str:
        """Show detailed info about current module"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        module_data = {
            "name": self.current_module_instance.name,
            "description": self.current_module_instance.description,
            "author": self.current_module_instance.author,
            "owasp": self.current_module_instance.owasp,
            "cves": self.current_module_instance.cves,
            "references": self.current_module_instance.references,
            "options": {}
        }

        # Get options
        for opt_name, opt_obj in self.current_module_instance.options.items():
            module_data["options"][opt_name] = {
                "value": opt_obj.value,
                "required": opt_obj.required,
                "description": opt_obj.description,
                "enum_values": opt_obj.enum_values
            }

        return self.formatter.module_info(module_data)

    def handle_info(self, args: List[str]) -> str:
        """Handle 'info' command for a specific module"""
        if not args:
            # Show info for current module
            return self._show_info()

        module_path = args[0]

        # Temporarily load module to show info
        if module_path not in self.modules_cache:
            return self.formatter.error(f"Module '{module_path}' not found")

        try:
            module_info = self.modules_cache[module_path]
            category = module_info["category"]
            name = module_info["name"]

            # Import and instantiate
            import_path = f"modules.exploits.{category}.{name}"
            module = importlib.import_module(import_path)

            module_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (inspect.isclass(item) and
                    issubclass(item, ExploitModule) and
                    item != ExploitModule):
                    module_class = item
                    break

            if not module_class:
                return self.formatter.error(f"No exploit module class found")

            instance = module_class()

            module_data = {
                "name": instance.name,
                "description": instance.description,
                "author": instance.author,
                "owasp": instance.owasp,
                "cves": instance.cves,
                "references": instance.references,
                "options": {}
            }

            for opt_name, opt_obj in instance.options.items():
                module_data["options"][opt_name] = {
                    "value": opt_obj.value,
                    "required": opt_obj.required,
                    "description": opt_obj.description
                }

            return self.formatter.module_info(module_data)

        except Exception as e:
            return self.formatter.error(f"Failed to load module info: {str(e)}")

    def handle_search(self, args: List[str]) -> str:
        """Handle 'search' command"""
        if not args:
            return self.formatter.error("Usage: search <term> or search <type:value>")

        search_term = " ".join(args).lower()

        # Parse search type
        search_type = None
        search_value = search_term

        if ':' in search_term:
            search_type, search_value = search_term.split(':', 1)
            search_value = search_value.strip()

        matches = []

        for module_path, module_info in self.modules_cache.items():
            match = False

            if search_type == "type":
                # Search by category
                if search_value in module_info["category"].lower():
                    match = True
            elif search_type == "name":
                # Search by name
                if search_value in module_info["name"].lower():
                    match = True
            else:
                # General search in path
                if search_value in module_path.lower():
                    match = True

            if match:
                matches.append(module_path)

        if not matches:
            return self.formatter.warning(f"No modules found matching '{search_term}'")

        output = [self.formatter.heading(f"Search Results for '{search_term}'")]
        for match in matches:
            output.append(f"  {match}")

        output.append(f"\n{self.formatter.info(f'Found {len(matches)} module(s)')}")

        return "\n".join(output)

    def handle_set(self, args: List[str]) -> str:
        """Handle 'set' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        if len(args) < 2:
            return self.formatter.error("Usage: set <option> <value>")

        option_name = args[0].upper()
        option_value = " ".join(args[1:])

        # Check if option exists
        if option_name not in self.current_module_instance.options:
            return self.formatter.error(f"Unknown option: {option_name}")

        # Set the option
        self.current_module_instance.options[option_name].value = option_value

        return self.formatter.success(f"{option_name} => {option_value}")

    def handle_unset(self, args: List[str]) -> str:
        """Handle 'unset' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        if not args:
            return self.formatter.error("Usage: unset <option>")

        option_name = args[0].upper()

        if option_name not in self.current_module_instance.options:
            return self.formatter.error(f"Unknown option: {option_name}")

        # Clear the option
        self.current_module_instance.options[option_name].value = ""

        return self.formatter.success(f"Unset {option_name}")

    def handle_run(self, args: List[str]) -> str:
        """Handle 'run' or 'exploit' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        # Validate required options
        missing = []
        for opt_name, opt_obj in self.current_module_instance.options.items():
            if opt_obj.required and not opt_obj.value:
                missing.append(opt_name)

        if missing:
            return self.formatter.error(
                f"Missing required options: {', '.join(missing)}"
            )

        # Execute the exploit
        try:
            print(self.formatter.info(f"Executing module: {self.current_module}"))

            result = self.current_module_instance.run()

            # Format result
            result_dict = {
                "success": result.success,
                "output": result.output,
                "details": result.details if hasattr(result, 'details') else {},
                "vulnerability_found": result.vulnerability_found if hasattr(result, 'vulnerability_found') else False
            }

            return self.formatter.exploit_result(result_dict)

        except Exception as e:
            return self.formatter.error(f"Exploit execution failed: {str(e)}")

    def handle_check(self, args: List[str]) -> str:
        """Handle 'check' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        # Validate required options
        missing = []
        for opt_name, opt_obj in self.current_module_instance.options.items():
            if opt_obj.required and not opt_obj.value:
                missing.append(opt_name)

        if missing:
            return self.formatter.error(
                f"Missing required options: {', '.join(missing)}"
            )

        # Execute vulnerability check
        try:
            print(self.formatter.info(f"Checking target for vulnerabilities..."))

            result = self.current_module_instance.check()

            result_dict = {
                "success": result.success,
                "output": result.output,
                "details": result.details if hasattr(result, 'details') else {},
                "vulnerability_found": result.vulnerability_found if hasattr(result, 'vulnerability_found') else False
            }

            return self.formatter.exploit_result(result_dict)

        except Exception as e:
            return self.formatter.error(f"Vulnerability check failed: {str(e)}")

    def handle_back(self, args: List[str]) -> str:
        """Handle 'back' command"""
        if not self.current_module:
            return self.formatter.warning("No module selected")

        module_name = self.current_module
        self.current_module = None
        self.current_module_instance = None

        return self.formatter.success(f"Unloaded module: {module_name}")

    def handle_options(self, args: List[str]) -> str:
        """Handle 'options' command (alias for 'show options')"""
        return self._show_options()

    def handle_help(self, args: List[str]) -> str:
        """Handle 'help' command"""
        commands = {
            "use": "Select a module to use",
            "show": "Display modules, options, or info",
            "search": "Search for modules",
            "info": "Display detailed information about a module",
            "options": "Show available options for current module",
            "set": "Set an option value",
            "unset": "Clear an option value",
            "run": "Execute the current module",
            "exploit": "Execute the current module (alias for 'run')",
            "check": "Check if target is vulnerable",
            "back": "Unload the current module",
            "help": "Show this help message",
            "banner": "Display the MetaLLM banner",
            "version": "Show version information",
            "clear": "Clear the screen",
            "history": "Show command history",
            "exit": "Exit MetaLLM console",
            "quit": "Exit MetaLLM console (alias for 'exit')"
        }

        return self.formatter.help_text(commands)

    def handle_banner(self, args: List[str]) -> str:
        """Handle 'banner' command"""
        return self.formatter.banner()

    def handle_version(self, args: List[str]) -> str:
        """Handle 'version' command"""
        return self.formatter.info(
            "MetaLLM v1.0.0\n"
            "AI Security Testing & Exploitation Framework\n"
            "Author: Scott Thornton (perfecXion.ai)"
        )

    def handle_clear(self, args: List[str]) -> str:
        """Handle 'clear' command"""
        os.system('clear' if os.name != 'nt' else 'cls')
        return ""

    def handle_history(self, args: List[str]) -> str:
        """Handle 'history' command"""
        try:
            import readline
            history_length = readline.get_current_history_length()

            if history_length == 0:
                return self.formatter.info("No command history")

            output = [self.formatter.heading("Command History")]

            for i in range(1, history_length + 1):
                cmd = readline.get_history_item(i)
                if cmd:
                    output.append(f"  {i:3d}  {cmd}")

            return "\n".join(output)

        except Exception as e:
            return self.formatter.error(f"Failed to retrieve history: {str(e)}")

    def get_available_modules(self) -> List[str]:
        """Get list of all available module paths"""
        return list(self.modules_cache.keys())

    def get_current_module_options(self) -> Dict[str, Any]:
        """Get options for current module (for tab completion)"""
        if not self.current_module_instance:
            return {}

        return {
            name: {
                "value": opt.value,
                "enum_values": opt.enum_values,
                "required": opt.required,
                "description": opt.description
            }
            for name, opt in self.current_module_instance.options.items()
        }
