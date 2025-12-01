"""
MetaLLM Interactive Console

Main console interface for the MetaLLM exploitation framework,
providing a Metasploit-style command-line experience.

Author: Scott Thornton (perfecXion.ai)
"""

import sys
import signal
from typing import Optional

from cli.formatter import Formatter
from cli.completer import MetaLLMCompleter
from cli.commands import CommandHandler


class MetaLLMConsole:
    """Main interactive console for MetaLLM"""

    def __init__(self, use_colors: bool = True):
        self.formatter = Formatter(use_colors=use_colors)
        self.command_handler = CommandHandler(self.formatter)
        self.completer = MetaLLMCompleter()
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n" + self.formatter.warning("Interrupt received. Use 'exit' to quit."))
        # Don't exit, just return to prompt

    def start(self):
        """Start the interactive console"""
        # Display banner
        print(self.formatter.banner())

        # Setup tab completion
        self.completer.set_modules(self.command_handler.get_available_modules())
        self.completer.setup_readline()

        self.running = True

        # Main command loop
        while self.running:
            try:
                # Update completer with current module info
                self.completer.set_current_module(
                    self.command_handler.current_module
                )
                self.completer.set_module_options(
                    self.command_handler.get_current_module_options()
                )

                # Get prompt
                prompt = self._get_prompt()

                # Read command
                try:
                    command_line = input(prompt).strip()
                except EOFError:
                    # Handle Ctrl+D
                    print()
                    self.running = False
                    continue

                if not command_line:
                    continue

                # Parse and execute command
                self._execute_command(command_line)

            except KeyboardInterrupt:
                # Ctrl+C was pressed
                continue

            except Exception as e:
                print(self.formatter.error(f"Unexpected error: {str(e)}"))

        # Cleanup
        self._cleanup()

    def _get_prompt(self) -> str:
        """Generate the command prompt"""
        status = self.formatter.status_line(self.command_handler.current_module)
        return self.formatter.prompt(f"{status} > ")

    def _execute_command(self, command_line: str):
        """Parse and execute a command"""
        # Split command and arguments
        parts = command_line.split()
        if not parts:
            return

        command = parts[0].lower()
        args = parts[1:]

        # Map command to handler
        command_map = {
            "use": self.command_handler.handle_use,
            "show": self.command_handler.handle_show,
            "search": self.command_handler.handle_search,
            "info": self.command_handler.handle_info,
            "set": self.command_handler.handle_set,
            "unset": self.command_handler.handle_unset,
            "options": self.command_handler.handle_options,
            "run": self.command_handler.handle_run,
            "exploit": self.command_handler.handle_run,  # Alias
            "check": self.command_handler.handle_check,
            "back": self.command_handler.handle_back,
            "help": self.command_handler.handle_help,
            "?": self.command_handler.handle_help,  # Alias
            "banner": self.command_handler.handle_banner,
            "version": self.command_handler.handle_version,
            "clear": self.command_handler.handle_clear,
            "cls": self.command_handler.handle_clear,  # Alias
            "history": self.command_handler.handle_history,
            "exit": self._handle_exit,
            "quit": self._handle_exit,  # Alias
        }

        # Execute command
        if command in command_map:
            try:
                result = command_map[command](args)
                if result:
                    print(result)
            except Exception as e:
                print(self.formatter.error(f"Command failed: {str(e)}"))
        else:
            print(self.formatter.error(f"Unknown command: {command}. Type 'help' for available commands."))

    def _handle_exit(self, args):
        """Handle exit command"""
        print(self.formatter.info("Exiting MetaLLM..."))
        self.running = False
        return ""

    def _cleanup(self):
        """Cleanup before exit"""
        # Save command history
        self.completer.save_history()

        print(self.formatter.info("Goodbye!"))


def main():
    """Entry point for the console"""
    # Check if colors should be disabled
    use_colors = "--no-color" not in sys.argv

    try:
        console = MetaLLMConsole(use_colors=use_colors)
        console.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
