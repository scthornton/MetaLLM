"""
Interactive Console

Main interactive console for MetaLLM CLI.
"""

import sys
import shlex
from typing import Optional, List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from pathlib import Path
from metaLLM.core.framework import MetaLLM
from metaLLM.cli.commands import CommandHandler
from metaLLM.cli import output


class MetaLLMCompleter(Completer):
    """
    Auto-completion for MetaLLM commands
    """

    def __init__(self, framework: MetaLLM):
        self.framework = framework
        self.commands = [
            'search', 'show', 'use', 'info', 'reload',
            'set', 'unset',
            'target', 'check', 'run',
            'sessions', 'banner', 'version', 'stats',
            'help', 'exit', 'quit'
        ]

        self.show_options = ['modules', 'targets', 'sessions', 'options', 'stats']
        self.target_options = ['list', 'add', 'set', 'remove']
        self.session_options = ['list', 'kill', 'cleanup']

    def get_completions(self, document, complete_event):
        """Generate completions for current input"""
        text = document.text_before_cursor
        words = text.split()

        # Complete command names
        if len(words) == 0 or (len(words) == 1 and not text.endswith(' ')):
            word = words[0] if words else ''
            for cmd in self.commands:
                if cmd.startswith(word.lower()):
                    yield Completion(cmd, start_position=-len(word))

        # Complete 'show' subcommands
        elif len(words) >= 1 and words[0] == 'show':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                word = words[1] if len(words) == 2 else ''
                for option in self.show_options:
                    if option.startswith(word.lower()):
                        yield Completion(option, start_position=-len(word))

        # Complete 'target' subcommands
        elif len(words) >= 1 and words[0] == 'target':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                word = words[1] if len(words) == 2 else ''
                for option in self.target_options:
                    if option.startswith(word.lower()):
                        yield Completion(option, start_position=-len(word))

        # Complete 'sessions' subcommands
        elif len(words) >= 1 and words[0] == 'sessions':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                word = words[1] if len(words) == 2 else ''
                for option in self.session_options:
                    if option.startswith(word.lower()):
                        yield Completion(option, start_position=-len(word))

        # Complete module paths for 'use' and 'info' commands
        elif len(words) >= 1 and words[0] in ['use', 'info']:
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                word = words[1] if len(words) == 2 else ''
                modules = self.framework.list_modules()
                for module in modules:
                    if module.startswith(word.lower()):
                        yield Completion(module, start_position=-len(word))


class InteractiveConsole:
    """
    Interactive console for MetaLLM

    Example:
        framework = MetaLLM()
        console = InteractiveConsole(framework)
        console.run()
    """

    def __init__(self, framework: MetaLLM):
        """
        Initialize interactive console

        Args:
            framework: MetaLLM framework instance
        """
        self.framework = framework
        self.handler = CommandHandler(framework)
        self.running = False

        # Setup prompt session with history
        history_file = Path.home() / ".metaLLM" / "history"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=MetaLLMCompleter(framework),
        )

    def get_prompt(self) -> str:
        """
        Generate prompt string

        Returns:
            Prompt string with current module context
        """
        if self.handler.current_module:
            module_name = self.handler.current_module.name
            return f"metaLLM ({module_name}) > "
        else:
            return "metaLLM > "

    def parse_command(self, line: str) -> tuple[Optional[str], List[str]]:
        """
        Parse command line input

        Args:
            line: Input line

        Returns:
            Tuple of (command, args)
        """
        line = line.strip()

        if not line:
            return None, []

        try:
            # Use shlex to handle quoted arguments properly
            parts = shlex.split(line)
        except ValueError:
            # Fall back to simple split if shlex fails
            parts = line.split()

        command = parts[0].lower() if parts else None
        args = parts[1:] if len(parts) > 1 else []

        return command, args

    def dispatch_command(self, command: str, args: List[str]) -> bool:
        """
        Dispatch command to appropriate handler

        Args:
            command: Command name
            args: Command arguments

        Returns:
            True if should exit, False otherwise
        """
        # Map commands to handler methods
        command_map = {
            'search': lambda: self.handler.cmd_search(args[0] if args else ''),
            'show': lambda: self.handler.cmd_show(args[0] if args else None),
            'use': lambda: self.handler.cmd_use(args[0] if args else ''),
            'info': lambda: self.handler.cmd_info(args[0] if args else None),
            'reload': lambda: self.handler.cmd_reload(),
            'set': lambda: self.handler.cmd_set(args[0] if args else '', args[1] if len(args) > 1 else None),
            'unset': lambda: self.handler.cmd_unset(args[0] if args else ''),
            'target': lambda: self.handler.cmd_target(*args),
            'check': lambda: self.handler.cmd_check(),
            'run': lambda: self.handler.cmd_run(),
            'sessions': lambda: self.handler.cmd_sessions(*args),
            'banner': lambda: self.handler.cmd_banner(),
            'version': lambda: self.handler.cmd_version(),
            'stats': lambda: self.handler.cmd_stats(),
            'help': lambda: self.handler.cmd_help(),
            'exit': lambda: self.handler.cmd_exit(),
            'quit': lambda: self.handler.cmd_quit(),
        }

        # Execute command
        if command in command_map:
            try:
                result = command_map[command]()
                # Return True if exit/quit command
                return result if result is not None else False
            except Exception as e:
                output.print_error(f"Command execution failed: {e}")
                return False
        else:
            output.print_error(f"Unknown command: {command}")
            output.print_info("Type 'help' for available commands")
            return False

    def run(self):
        """Run the interactive console"""
        self.running = True

        # Display banner
        output.print_banner()

        # Discover modules
        output.print_info("Discovering modules...")
        count = self.framework.discover_modules()
        output.print_success(f"Discovered {count} module(s)")
        output.console.print()

        # Display quick start info
        output.print_info("Type 'help' for available commands")
        output.print_info("Type 'show modules' to see available modules")
        output.console.print()

        # Main command loop
        while self.running:
            try:
                # Get user input
                line = self.session.prompt(self.get_prompt())

                # Parse and dispatch command
                command, args = self.parse_command(line)

                if command:
                    should_exit = self.dispatch_command(command, args)
                    if should_exit:
                        self.running = False

            except KeyboardInterrupt:
                # Ctrl+C - cancel current input
                output.console.print()
                continue

            except EOFError:
                # Ctrl+D - exit
                output.console.print()
                output.print_info("Exiting MetaLLM...")
                self.running = False

            except Exception as e:
                output.print_error(f"Unexpected error: {e}")
                output.print_info("Type 'help' for available commands")

        # Cleanup
        output.print_success("Goodbye!")


def start_console(framework: Optional[MetaLLM] = None):
    """
    Start the interactive console

    Args:
        framework: Optional MetaLLM instance (creates new one if not provided)
    """
    if framework is None:
        framework = MetaLLM()

    console = InteractiveConsole(framework)

    try:
        console.run()
    except KeyboardInterrupt:
        output.console.print("\n")
        output.print_info("Interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        output.print_error(f"Fatal error: {e}")
        sys.exit(1)
