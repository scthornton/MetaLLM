"""
CLI Commands

Command handlers for the MetaLLM interactive console.
"""

from typing import Optional, List
from metaLLM.core.framework import MetaLLM
from metaLLM.cli import output
from metaLLM.base.target import LLMTarget, RAGTarget, AgentTarget, MLOpsTarget


class CommandHandler:
    """
    Handles CLI commands for the MetaLLM framework

    Example:
        handler = CommandHandler(framework)
        handler.cmd_search("prompt injection")
        handler.cmd_use("exploits/llm/prompt_injection")
        handler.cmd_run()
    """

    def __init__(self, framework: MetaLLM):
        """
        Initialize command handler

        Args:
            framework: MetaLLM framework instance
        """
        self.framework = framework
        self.current_module = None

    # ========================================================================
    # Module Commands
    # ========================================================================

    def cmd_search(self, query: str) -> None:
        """
        Search for modules

        Args:
            query: Search query
        """
        if not query:
            output.print_error("Usage: search <query>")
            return

        results = self.framework.search_modules(query)

        if not results:
            output.print_warning(f"No modules found matching: {query}")
            return

        output.print_success(f"Found {len(results)} module(s) matching '{query}':")
        output.print_modules_list(results)

    def cmd_show(self, what: Optional[str] = None) -> None:
        """
        Show information

        Args:
            what: What to show (modules, targets, sessions, options, stats)
        """
        if not what:
            output.print_error("Usage: show <modules|targets|sessions|options|stats>")
            return

        what = what.lower()

        if what == "modules":
            modules = self.framework.list_modules()
            if not modules:
                output.print_warning("No modules discovered. Run 'reload' to discover modules.")
                return
            output.print_modules_list(modules)

        elif what == "targets":
            targets = self.framework.list_targets()
            if not targets:
                output.print_warning("No targets configured. Use 'target add' to add a target.")
                return
            output.print_targets_table(targets)

        elif what == "sessions":
            sessions = self.framework.list_sessions()
            if not sessions:
                output.print_warning("No active sessions.")
                return
            output.print_sessions_table(sessions)

        elif what == "options":
            if not self.current_module:
                output.print_error("No module loaded. Use 'use <module_path>' first.")
                return
            module_info = self.current_module.get_info()
            output.print_options_table(module_info['options'])

        elif what == "stats":
            stats = self.framework.get_stats()
            output.print_stats(stats)

        else:
            output.print_error(f"Unknown show target: {what}")
            output.print_info("Valid options: modules, targets, sessions, options, stats")

    def cmd_use(self, module_path: str) -> None:
        """
        Load a module

        Args:
            module_path: Module path (e.g., exploits/llm/prompt_injection)
        """
        if not module_path:
            output.print_error("Usage: use <module_path>")
            return

        try:
            self.current_module = self.framework.load_module(module_path)
            output.print_success(f"Loaded module: {self.current_module.name}")

            # Show module info
            module_info = self.current_module.get_info()
            output.print_module_info(module_info)

        except ValueError as e:
            output.print_error(f"Failed to load module: {e}")
        except Exception as e:
            output.print_error(f"Error loading module: {e}")

    def cmd_info(self, module_path: Optional[str] = None) -> None:
        """
        Show module information

        Args:
            module_path: Optional module path (uses current module if not provided)
        """
        if module_path:
            # Show info for specified module
            try:
                module_info = self.framework.get_module_info(module_path)
                if not module_info:
                    output.print_error(f"Module not found: {module_path}")
                    return
                output.print_module_info(module_info)
            except Exception as e:
                output.print_error(f"Error getting module info: {e}")

        elif self.current_module:
            # Show info for current module
            module_info = self.current_module.get_info()
            output.print_module_info(module_info)

        else:
            output.print_error("No module loaded. Use 'use <module_path>' or 'info <module_path>'")

    def cmd_reload(self) -> None:
        """Reload module database"""
        output.print_info("Discovering modules...")
        count = self.framework.discover_modules()
        output.print_success(f"Discovered {count} module(s)")

    # ========================================================================
    # Option Commands
    # ========================================================================

    def cmd_set(self, option: str, value: Optional[str] = None) -> None:
        """
        Set a module option

        Args:
            option: Option name
            value: Option value
        """
        if not self.current_module:
            output.print_error("No module loaded. Use 'use <module_path>' first.")
            return

        if not option or value is None:
            output.print_error("Usage: set <option> <value>")
            return

        try:
            self.current_module.set_option(option, value)
            output.print_success(f"Set {option} => {value}")
        except KeyError as e:
            output.print_error(f"Unknown option: {option}")
        except ValueError as e:
            output.print_error(f"Invalid value: {e}")

    def cmd_unset(self, option: str) -> None:
        """
        Unset a module option

        Args:
            option: Option name
        """
        if not self.current_module:
            output.print_error("No module loaded. Use 'use <module_path>' first.")
            return

        if not option:
            output.print_error("Usage: unset <option>")
            return

        try:
            self.current_module.set_option(option, None)
            output.print_success(f"Unset {option}")
        except KeyError:
            output.print_error(f"Unknown option: {option}")

    # ========================================================================
    # Target Commands
    # ========================================================================

    def cmd_target(self, action: Optional[str] = None, *args) -> None:
        """
        Target management commands

        Args:
            action: Action to perform (add, remove, list, set)
            args: Additional arguments
        """
        if not action:
            output.print_error("Usage: target <add|remove|list|set> [args]")
            return

        action = action.lower()

        if action == "list":
            targets = self.framework.list_targets()
            if not targets:
                output.print_warning("No targets configured.")
                return
            output.print_targets_table(targets)

        elif action == "set":
            if not args:
                output.print_error("Usage: target set <target_name>")
                return
            target_name = args[0]

            if not self.current_module:
                output.print_error("No module loaded. Use 'use <module_path>' first.")
                return

            if self.framework.set_target(target_name):
                output.print_success(f"Target set to: {target_name}")
            else:
                output.print_error(f"Target not found: {target_name}")

        elif action == "add":
            output.print_info("Target creation wizard coming soon...")
            output.print_info("For now, targets can be added programmatically via the Python API")

        elif action == "remove":
            if not args:
                output.print_error("Usage: target remove <target_name>")
                return
            target_name = args[0]

            if self.framework.remove_target(target_name):
                output.print_success(f"Removed target: {target_name}")
            else:
                output.print_error(f"Target not found: {target_name}")

        else:
            output.print_error(f"Unknown target action: {action}")
            output.print_info("Valid actions: add, remove, list, set")

    # ========================================================================
    # Execution Commands
    # ========================================================================

    def cmd_check(self) -> None:
        """Run vulnerability check (non-destructive)"""
        if not self.current_module:
            output.print_error("No module loaded. Use 'use <module_path>' first.")
            return

        output.print_info(f"Checking vulnerability with {self.current_module.name}...")

        try:
            result = self.framework.check(self.current_module)
            output.print_check_result(result)

        except ValueError as e:
            output.print_error(f"Validation failed: {e}")
        except Exception as e:
            output.print_error(f"Check failed: {e}")

    def cmd_run(self) -> None:
        """Execute the module (potentially destructive)"""
        if not self.current_module:
            output.print_error("No module loaded. Use 'use <module_path>' first.")
            return

        output.print_warning(f"Executing module: {self.current_module.name}")
        output.print_info("This operation may be destructive!")

        try:
            result = self.framework.run(self.current_module)
            output.print_result(result)

        except ValueError as e:
            output.print_error(f"Validation failed: {e}")
        except Exception as e:
            output.print_error(f"Execution failed: {e}")

    # ========================================================================
    # Session Commands
    # ========================================================================

    def cmd_sessions(self, action: Optional[str] = None, *args) -> None:
        """
        Session management commands

        Args:
            action: Action to perform (list, kill, cleanup)
            args: Additional arguments
        """
        if not action:
            action = "list"

        action = action.lower()

        if action == "list" or action == "-l":
            sessions = self.framework.list_sessions()
            if not sessions:
                output.print_warning("No active sessions.")
                return
            output.print_sessions_table(sessions)

        elif action == "kill" or action == "-k":
            if not args:
                output.print_error("Usage: sessions kill <session_id>")
                return

            try:
                session_id = int(args[0])
                if self.framework.terminate_session(session_id):
                    output.print_success(f"Terminated session {session_id}")
                else:
                    output.print_error(f"Session not found: {session_id}")
            except ValueError:
                output.print_error("Invalid session ID (must be an integer)")

        elif action == "cleanup":
            count = self.framework.cleanup_sessions()
            output.print_success(f"Cleaned up {count} inactive session(s)")

        else:
            output.print_error(f"Unknown sessions action: {action}")
            output.print_info("Valid actions: list, kill <id>, cleanup")

    # ========================================================================
    # Utility Commands
    # ========================================================================

    def cmd_banner(self) -> None:
        """Display banner"""
        output.print_banner()

    def cmd_version(self) -> None:
        """Display version information"""
        info = self.framework.get_info()
        output.console.print(f"\n[bold cyan]{info['name']}[/bold cyan] [bold white]v{info['version']}[/bold white]")
        output.console.print(f"[dim]{info['description']}[/dim]")
        output.console.print(f"[dim]By {info['author']}[/dim]\n")

    def cmd_stats(self) -> None:
        """Display framework statistics"""
        stats = self.framework.get_stats()
        output.print_stats(stats)

    def cmd_help(self) -> None:
        """Display help message"""
        help_text = """
[bold cyan]MetaLLM Command Reference[/bold cyan]

[bold yellow]Module Commands:[/bold yellow]
  [cyan]search <query>[/cyan]          Search for modules
  [cyan]show modules[/cyan]            List all available modules
  [cyan]use <module_path>[/cyan]       Load a module
  [cyan]info [module_path][/cyan]      Show module information
  [cyan]reload[/cyan]                  Reload module database

[bold yellow]Options Commands:[/bold yellow]
  [cyan]show options[/cyan]            Display current module options
  [cyan]set <option> <value>[/cyan]    Set a module option
  [cyan]unset <option>[/cyan]          Unset a module option

[bold yellow]Target Commands:[/bold yellow]
  [cyan]target list[/cyan]             List all targets
  [cyan]target add[/cyan]              Add a new target
  [cyan]target set <name>[/cyan]       Set active target for module
  [cyan]target remove <name>[/cyan]    Remove a target
  [cyan]show targets[/cyan]            Display target information

[bold yellow]Execution Commands:[/bold yellow]
  [cyan]check[/cyan]                   Run vulnerability check (non-destructive)
  [cyan]run[/cyan]                     Execute the module (potentially destructive)

[bold yellow]Session Commands:[/bold yellow]
  [cyan]sessions[/cyan]                List active sessions
  [cyan]sessions kill <id>[/cyan]      Terminate a session
  [cyan]sessions cleanup[/cyan]        Remove inactive sessions

[bold yellow]Utility Commands:[/bold yellow]
  [cyan]banner[/cyan]                  Display banner
  [cyan]version[/cyan]                 Show version information
  [cyan]stats[/cyan]                   Display framework statistics
  [cyan]help[/cyan]                    Show this help message
  [cyan]exit/quit[/cyan]               Exit MetaLLM

[dim]For more information, visit: https://github.com/yourusername/MetaLLM[/dim]
        """
        output.console.print(help_text)

    def cmd_exit(self) -> bool:
        """
        Exit the framework

        Returns:
            True to signal exit
        """
        output.print_info("Exiting MetaLLM...")
        return True

    # Alias for exit
    cmd_quit = cmd_exit
