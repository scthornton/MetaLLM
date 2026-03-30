"""
CLI Command Handlers

Implements all command handlers for the MetaLLM interactive console.

Author: Scott Thornton (perfecXion.ai)
"""

import os
import structlog
from typing import Dict, Any, List, Optional

from cli.formatter import Formatter
from metallm.core.module_loader import ModuleLoader
from metallm.base.module import _BaseModule, ExploitModule, AuxiliaryModule
from metallm.base.target import (
    Target, LLMTarget, RAGTarget, AgentTarget, MLOpsTarget,
    APITarget, MCPTarget, GenericHTTPTarget,
)

logger = structlog.get_logger()

# Map user-friendly names to target classes
TARGET_TYPES = {
    "llm": LLMTarget,
    "rag": RAGTarget,
    "agent": AgentTarget,
    "mlops": MLOpsTarget,
    "api": APITarget,
    "mcp": MCPTarget,
    "http": GenericHTTPTarget,
}


class CommandHandler:
    """Handles CLI command execution"""

    def __init__(self, formatter: Formatter):
        self.formatter = formatter
        self.current_module: Optional[str] = None
        self.current_module_instance: Optional[_BaseModule] = None
        self.loader = ModuleLoader()
        self.target: Optional[Target] = None

        # Discover all modules at startup
        self.loader.discover()
        logger.info(
            "cli.modules_discovered",
            total=len(self.loader.list_modules()),
            errors=len(self.loader.load_errors),
        )

    def handle_use(self, args: List[str]) -> str:
        """Handle 'use' command to select a module"""
        if not args:
            return self.formatter.error("Usage: use <module_path>")

        module_path = args[0]

        # Normalize: allow "exploits/llm/x" → "exploit/llm/x"
        for prefix_in, prefix_out in [("exploits/", "exploit/"), ("auxiliary/", "auxiliary/")]:
            if module_path.startswith(prefix_in):
                module_path = prefix_out + module_path[len(prefix_in):]

        # Check if module exists directly
        if module_path not in self.loader._registry:
            # Try fuzzy matching
            matches = self.loader.search(module_path)
            if matches:
                if len(matches) == 1:
                    module_path = matches[0]
                else:
                    return self.formatter.error(
                        f"Module not found. Did you mean:\n  " + "\n  ".join(matches[:10])
                    )
            else:
                return self.formatter.error(f"Module '{module_path}' not found")

        # Load the module
        instance = self.loader.load(module_path)
        if not instance:
            error_msg = self.loader.load_errors.get(module_path, "Unknown error")
            return self.formatter.error(f"Failed to load module: {error_msg}")

        self.current_module_instance = instance
        self.current_module = module_path

        # If we have a global target, bind it
        if self.target:
            instance.set_target(self.target)

        return self.formatter.success(f"Using module: {module_path}")

    def handle_show(self, args: List[str]) -> str:
        """Handle 'show' command"""
        if not args:
            return self.formatter.error(
                "Usage: show <exploits|auxiliary|modules|options|info|targets>"
            )

        show_type = args[0].lower()

        if show_type in ("exploits", "modules", "all"):
            return self._show_modules()
        elif show_type == "auxiliary":
            return self._show_modules(category="auxiliary")
        elif show_type == "options":
            return self._show_options()
        elif show_type == "info":
            return self._show_info()
        elif show_type == "targets":
            return self._show_target_types()
        else:
            return self.formatter.error(f"Unknown show type: {show_type}")

    def _show_modules(self, category: str = "") -> str:
        """Show all available modules"""
        all_modules = self.loader.list_modules(category)
        if not all_modules:
            return self.formatter.warning("No modules found")

        # Group by type/subcategory
        groups: Dict[str, List[str]] = {}
        for path in all_modules:
            parts = path.split("/")
            group = f"{parts[0]}/{parts[1]}" if len(parts) > 2 else parts[0]
            groups.setdefault(group, []).append(path)

        output = [self.formatter.heading("Available Modules")]

        for group in sorted(groups.keys()):
            output.append(f"\n{self.formatter.subheading(group.upper())}")
            for module_path in sorted(groups[group]):
                # Check if we know it loads successfully
                status = ""
                if module_path in self.loader.load_errors:
                    status = "  [LOAD ERROR]"
                output.append(f"  {module_path}{status}")

        # Summary
        total = len(all_modules)
        errors = sum(1 for p in all_modules if p in self.loader.load_errors)
        output.append(
            f"\n{self.formatter.info(f'Total: {total} modules ({errors} with load errors)')}"
        )

        return "\n".join(output)

    def _show_options(self) -> str:
        """Show options for current module"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        option_rows = []
        for opt_name, opt in self.current_module_instance.options.items():
            required = "yes" if opt.required else "no"
            current = opt.display_value()
            description = opt.description
            option_rows.append([opt_name, required, current, description])

        return self.formatter.table(
            ["Name", "Required", "Current Setting", "Description"],
            option_rows,
            title=f"Module Options: {self.current_module}",
        )

    def _show_info(self) -> str:
        """Show detailed info about current module"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        return self.formatter.module_info(
            self.current_module_instance.get_info()
        )

    def _show_target_types(self) -> str:
        """Show available target types"""
        rows = []
        for name, cls in TARGET_TYPES.items():
            rows.append([name, cls.__doc__.strip().split("\n")[0] if cls.__doc__ else ""])
        return self.formatter.table(
            ["Type", "Description"],
            rows,
            title="Available Target Types",
        )

    def handle_info(self, args: List[str]) -> str:
        """Handle 'info' command"""
        if not args:
            return self._show_info()

        module_path = args[0]
        instance = self.loader.load(module_path)
        if not instance:
            return self.formatter.error(f"Failed to load module: {module_path}")

        return self.formatter.module_info(instance.get_info())

    def handle_search(self, args: List[str]) -> str:
        """Handle 'search' command"""
        if not args:
            return self.formatter.error("Usage: search <term>")

        term = " ".join(args)
        matches = self.loader.search(term)

        if not matches:
            return self.formatter.warning(f"No modules found matching '{term}'")

        output = [self.formatter.heading(f"Search Results for '{term}'")]
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

        if option_name not in self.current_module_instance.options:
            return self.formatter.error(f"Unknown option: {option_name}")

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

        self.current_module_instance.options[option_name].value = ""
        return self.formatter.success(f"Unset {option_name}")

    def handle_setg(self, args: List[str]) -> str:
        """Handle 'setg' command — set global target"""
        if len(args) < 2:
            return self.formatter.error(
                "Usage: setg <target_type> <url>\n"
                "  Types: llm, rag, agent, mlops, api, mcp, http"
            )

        target_type = args[0].lower()
        url = args[1]

        if target_type not in TARGET_TYPES:
            return self.formatter.error(
                f"Unknown target type: {target_type}. "
                f"Valid: {', '.join(TARGET_TYPES.keys())}"
            )

        self.target = TARGET_TYPES[target_type](url=url)

        # Bind to current module if one is selected
        if self.current_module_instance:
            self.current_module_instance.set_target(self.target)

        return self.formatter.success(
            f"Global target set: {target_type} @ {url}"
        )

    def handle_run(self, args: List[str]) -> str:
        """Handle 'run' or 'exploit' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        # Validate required options
        errors = self.current_module_instance.validate_options()
        if errors:
            return self.formatter.error(
                f"Missing or invalid required options: {', '.join(errors)}"
            )

        # Execute
        try:
            print(self.formatter.info(f"Executing module: {self.current_module}"))
            self.current_module_instance._before_run()

            result = self.current_module_instance.run()

            self.current_module_instance._after_run(result)

            # Format result — handle both Result and ExploitResult/AuxiliaryResult
            result_dict = {
                "success": getattr(result, "success", False),
                "output": getattr(result, "output", str(result)),
                "details": getattr(result, "details", {}),
                "vulnerability_found": getattr(result, "vulnerability_found", False),
            }

            return self.formatter.exploit_result(result_dict)

        except Exception as e:
            logger.exception("cli.run_error", module=self.current_module)
            return self.formatter.error(f"Exploit execution failed: {str(e)}")

    def handle_check(self, args: List[str]) -> str:
        """Handle 'check' command"""
        if not self.current_module_instance:
            return self.formatter.error("No module selected. Use 'use <module>' first")

        if not isinstance(self.current_module_instance, ExploitModule):
            return self.formatter.error("check is only available for exploit modules")

        errors = self.current_module_instance.validate_options()
        if errors:
            return self.formatter.error(
                f"Missing or invalid required options: {', '.join(errors)}"
            )

        try:
            print(self.formatter.info("Checking target for vulnerabilities..."))

            result = self.current_module_instance.check()

            result_dict = {
                "success": getattr(result, "success", False),
                "output": getattr(result, "output", str(result)),
                "details": getattr(result, "details", {}),
                "vulnerability_found": getattr(result, "vulnerability_found", False),
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
        """Handle 'options' command"""
        return self._show_options()

    def handle_help(self, args: List[str]) -> str:
        """Handle 'help' command"""
        commands = {
            "use": "Select a module to use",
            "show": "Display modules, options, or info (exploits|auxiliary|modules|options|info|targets)",
            "search": "Search for modules by keyword",
            "info": "Display detailed information about a module",
            "options": "Show available options for current module",
            "set": "Set a module option value",
            "unset": "Clear a module option value",
            "setg": "Set global target (setg <type> <url>)",
            "run": "Execute the current module",
            "exploit": "Execute the current module (alias for 'run')",
            "check": "Check if target is vulnerable (non-destructive)",
            "back": "Unload the current module",
            "help": "Show this help message",
            "banner": "Display the MetaLLM banner",
            "version": "Show version information",
            "clear": "Clear the screen",
            "history": "Show command history",
            "exit": "Exit MetaLLM console",
        }
        return self.formatter.help_text(commands)

    def handle_banner(self, args: List[str]) -> str:
        return self.formatter.banner()

    def handle_version(self, args: List[str]) -> str:
        from metallm import __version__
        return self.formatter.info(
            f"MetaLLM v{__version__}\n"
            "AI Security Testing & Exploitation Framework\n"
            "Author: Scott Thornton (perfecXion.ai)"
        )

    def handle_clear(self, args: List[str]) -> str:
        os.system("clear" if os.name != "nt" else "cls")
        return ""

    def handle_history(self, args: List[str]) -> str:
        try:
            import readline
            length = readline.get_current_history_length()
            if length == 0:
                return self.formatter.info("No command history")

            output = [self.formatter.heading("Command History")]
            for i in range(1, length + 1):
                cmd = readline.get_history_item(i)
                if cmd:
                    output.append(f"  {i:3d}  {cmd}")
            return "\n".join(output)
        except Exception as e:
            return self.formatter.error(f"Failed to retrieve history: {str(e)}")

    def get_available_modules(self) -> List[str]:
        return self.loader.list_modules()

    def get_current_module_options(self) -> Dict[str, Any]:
        if not self.current_module_instance:
            return {}
        return {
            name: {
                "value": opt.value,
                "enum_values": opt.enum_values,
                "required": opt.required,
                "description": opt.description,
            }
            for name, opt in self.current_module_instance.options.items()
        }
