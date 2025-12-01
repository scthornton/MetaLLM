"""
Tab Completion System

Provides intelligent tab completion for the MetaLLM interactive console,
similar to Metasploit's completion functionality.

Author: Scott Thornton (perfecXion.ai)
"""

from typing import List, Optional
import readline


class MetaLLMCompleter:
    """Tab completion handler for MetaLLM console"""

    def __init__(self):
        self.commands = []
        self.modules = []
        self.current_module = None
        self.module_options = {}

        # Initialize commands
        self.commands = [
            "use",
            "show",
            "search",
            "info",
            "options",
            "set",
            "unset",
            "run",
            "check",
            "exploit",
            "back",
            "help",
            "exit",
            "quit",
            "clear",
            "banner",
            "version",
            "history"
        ]

        # Show command sub-options
        self.show_options = [
            "exploits",
            "modules",
            "options",
            "info"
        ]

        # Search types
        self.search_types = [
            "name:",
            "type:",
            "author:",
            "owasp:",
            "cve:"
        ]

    def set_modules(self, modules: List[str]):
        """Set available modules for completion"""
        self.modules = modules

    def set_current_module(self, module: Optional[str]):
        """Set currently selected module"""
        self.current_module = module

    def set_module_options(self, options: dict):
        """Set options for current module"""
        self.module_options = options

    def complete(self, text: str, state: int) -> Optional[str]:
        """
        Completion handler called by readline

        Args:
            text: Current text being completed
            state: Iteration state (0, 1, 2, ...)

        Returns:
            Completion suggestion or None
        """
        # Get the full line buffer
        line = readline.get_line_buffer()
        tokens = line.split()

        # Determine what to complete based on context
        if not tokens or (len(tokens) == 1 and not line.endswith(' ')):
            # Complete command
            matches = self._complete_command(text)
        elif tokens[0] == "use":
            # Complete module path
            matches = self._complete_module(text)
        elif tokens[0] == "show":
            # Complete show options
            matches = self._complete_show(text)
        elif tokens[0] == "set" and len(tokens) >= 2:
            # Complete option name or value
            if len(tokens) == 2 and not line.endswith(' '):
                matches = self._complete_option_name(text)
            else:
                matches = self._complete_option_value(tokens[1], text)
        elif tokens[0] == "unset":
            # Complete option name
            matches = self._complete_option_name(text)
        elif tokens[0] == "search":
            # Complete search types
            matches = self._complete_search(text)
        elif tokens[0] == "info":
            # Complete module path
            matches = self._complete_module(text)
        else:
            matches = []

        # Return the match at the requested state
        if state < len(matches):
            return matches[state]
        return None

    def _complete_command(self, text: str) -> List[str]:
        """Complete command names"""
        if not text:
            return self.commands
        return [cmd for cmd in self.commands if cmd.startswith(text)]

    def _complete_module(self, text: str) -> List[str]:
        """Complete module paths"""
        if not text:
            return self.modules

        matches = []
        for module in self.modules:
            if module.startswith(text):
                matches.append(module)

        # Also provide directory-level completions
        if '/' in text:
            prefix = text.rsplit('/', 1)[0] + '/'
            dir_matches = set()
            for module in self.modules:
                if module.startswith(prefix):
                    # Get next path component
                    rest = module[len(prefix):]
                    if '/' in rest:
                        next_dir = prefix + rest.split('/')[0] + '/'
                        dir_matches.add(next_dir)

            matches.extend(sorted(dir_matches))

        return sorted(set(matches))

    def _complete_show(self, text: str) -> List[str]:
        """Complete show command options"""
        if not text:
            return self.show_options
        return [opt for opt in self.show_options if opt.startswith(text)]

    def _complete_option_name(self, text: str) -> List[str]:
        """Complete option names for set/unset commands"""
        if not self.module_options:
            return []

        options = list(self.module_options.keys())

        if not text:
            return options
        return [opt for opt in options if opt.startswith(text)]

    def _complete_option_value(self, option_name: str, text: str) -> List[str]:
        """Complete option values based on option type"""
        if not self.module_options or option_name not in self.module_options:
            return []

        option = self.module_options[option_name]

        # If option has enum values, provide those
        if "enum_values" in option and option["enum_values"]:
            enum_values = option["enum_values"]
            if not text:
                return enum_values
            return [val for val in enum_values if val.startswith(text)]

        # For specific option types, provide common values
        if option_name.upper() in ["TARGET_URL", "URL", "RHOST", "RHOSTS"]:
            common_urls = [
                "http://localhost:8000",
                "http://localhost:3000",
                "http://127.0.0.1:8000",
                "https://api.openai.com"
            ]
            if not text:
                return common_urls
            return [url for url in common_urls if url.startswith(text)]

        if option_name.upper() in ["LHOST", "LPORT"]:
            if "HOST" in option_name.upper():
                return ["0.0.0.0", "127.0.0.1", "localhost"]
            else:
                return ["4444", "8080", "443", "80"]

        return []

    def _complete_search(self, text: str) -> List[str]:
        """Complete search terms"""
        if not text:
            return self.search_types

        # If typing a search type
        if ':' not in text:
            return [t for t in self.search_types if t.startswith(text)]

        # If completing value after type
        search_type = text.split(':')[0] + ':'

        if search_type == "type:":
            types = ["llm", "rag", "agent", "api"]
            prefix = text.split(':')[1] if ':' in text else ""
            return [search_type + t for t in types if t.startswith(prefix)]

        if search_type == "owasp:":
            owasp_codes = ["LLM01", "LLM02", "LLM03", "LLM05", "LLM06", "LLM07", "LLM08", "LLM10"]
            prefix = text.split(':')[1] if ':' in text else ""
            return [search_type + code for code in owasp_codes if code.startswith(prefix)]

        return []

    def setup_readline(self):
        """Configure readline for tab completion"""
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

        # Use space and / as word delimiters (not just space)
        readline.set_completer_delims(' \t\n')

        # Enable history
        try:
            readline.read_history_file(".metallm_history")
        except FileNotFoundError:
            pass

    def save_history(self):
        """Save command history"""
        try:
            readline.write_history_file(".metallm_history")
        except Exception:
            pass
