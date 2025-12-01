"""
CLI Output Formatter

Handles formatting of console output with colors, tables, and banners
for the MetaLLM interactive console.

Author: Scott Thornton (perfecXion.ai)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class Formatter:
    """Console output formatter"""

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_colors:
            return text
        return f"{color}{text}{Colors.RESET}"

    def success(self, text: str) -> str:
        """Format success message"""
        return self._color(f"[+] {text}", Colors.GREEN)

    def error(self, text: str) -> str:
        """Format error message"""
        return self._color(f"[-] {text}", Colors.RED)

    def warning(self, text: str) -> str:
        """Format warning message"""
        return self._color(f"[!] {text}", Colors.YELLOW)

    def info(self, text: str) -> str:
        """Format info message"""
        return self._color(f"[*] {text}", Colors.BLUE)

    def prompt(self, text: str) -> str:
        """Format user prompt"""
        return self._color(text, Colors.BRIGHT_CYAN)

    def heading(self, text: str) -> str:
        """Format section heading"""
        return self._color(f"\n{text}\n{'=' * len(text)}", Colors.BOLD + Colors.CYAN)

    def subheading(self, text: str) -> str:
        """Format subsection heading"""
        return self._color(f"\n{text}\n{'-' * len(text)}", Colors.CYAN)

    def banner(self) -> str:
        """Display MetaLLM banner"""
        banner_text = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███╗   ███╗███████╗████████╗ █████╗ ██╗     ██╗     ███╗   ███╗            ║
║   ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     ████╗ ████║            ║
║   ██╔████╔██║█████╗     ██║   ███████║██║     ██║     ██╔████╔██║            ║
║   ██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║     ██║     ██║╚██╔╝██║            ║
║   ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗███████╗██║ ╚═╝ ██║            ║
║   ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝            ║
║                                                                               ║
║              AI Security Testing & Exploitation Framework                    ║
║                        perfecXion.ai Research                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        version_info = f"""
    Version: 1.0.0
    Author:  Scott Thornton
    Build:   {datetime.now().strftime("%Y-%m-%d")}

    Type 'help' for available commands
    Type 'show exploits' to list all exploit modules
"""
        banner_colored = self._color(banner_text, Colors.BRIGHT_CYAN)
        version_colored = self._color(version_info, Colors.CYAN)

        return banner_colored + version_colored

    def table(self, headers: List[str], rows: List[List[str]],
              title: Optional[str] = None) -> str:
        """Format data as a table"""
        if not rows:
            return self.warning("No data to display")

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Build table
        lines = []

        # Title
        if title:
            lines.append(self.heading(title))

        # Header separator
        lines.append("")

        # Headers
        header_row = "  ".join(
            self._color(h.ljust(w), Colors.BOLD + Colors.CYAN)
            for h, w in zip(headers, col_widths)
        )
        lines.append(header_row)

        # Separator
        separator = "  ".join("-" * w for w in col_widths)
        lines.append(self._color(separator, Colors.DIM))

        # Rows
        for row in rows:
            row_str = "  ".join(
                str(cell).ljust(w)
                for cell, w in zip(row, col_widths)
            )
            lines.append(row_str)

        lines.append("")

        return "\n".join(lines)

    def key_value(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format key-value pairs"""
        lines = []
        indent_str = "  " * indent

        for key, value in data.items():
            key_colored = self._color(f"{key}:", Colors.CYAN)

            if isinstance(value, dict):
                lines.append(f"{indent_str}{key_colored}")
                lines.append(self.key_value(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{indent_str}{key_colored}")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self.key_value(item, indent + 1))
                    else:
                        lines.append(f"{indent_str}  - {item}")
            else:
                lines.append(f"{indent_str}{key_colored} {value}")

        return "\n".join(lines)

    def module_info(self, module_data: Dict[str, Any]) -> str:
        """Format module information"""
        lines = []

        # Module name
        lines.append(self.heading(module_data.get("name", "Unknown Module")))

        # Description
        if "description" in module_data:
            lines.append(f"\nDescription: {module_data['description']}")

        # Basic info
        info = {}
        if "author" in module_data:
            info["Author"] = module_data["author"]
        if "owasp" in module_data:
            info["OWASP"] = ", ".join(module_data["owasp"])
        if "cves" in module_data:
            info["CVEs"] = ", ".join(module_data["cves"])

        if info:
            lines.append("\n" + self.key_value(info))

        # References
        if "references" in module_data and module_data["references"]:
            lines.append(self.subheading("References"))
            for ref in module_data["references"]:
                lines.append(f"  - {ref}")

        # Options
        if "options" in module_data and module_data["options"]:
            lines.append(self.subheading("Module Options"))

            option_rows = []
            for opt_name, opt_data in module_data["options"].items():
                required = "yes" if opt_data.get("required", False) else "no"
                current = str(opt_data.get("value", ""))
                description = opt_data.get("description", "")

                option_rows.append([opt_name, required, current, description])

            table = self.table(
                ["Name", "Required", "Current Setting", "Description"],
                option_rows
            )
            lines.append(table)

        return "\n".join(lines)

    def exploit_result(self, result: Dict[str, Any]) -> str:
        """Format exploit execution result"""
        lines = []

        success = result.get("success", False)

        if success:
            lines.append(self.success("Exploit executed successfully"))
        else:
            lines.append(self.error("Exploit execution failed"))

        # Output
        if "output" in result:
            lines.append(f"\n{result['output']}")

        # Details
        if "details" in result and result["details"]:
            lines.append(self.subheading("Details"))
            lines.append(self.key_value(result["details"]))

        # Vulnerability info
        if result.get("vulnerability_found"):
            lines.append(self.warning("\nVulnerability detected!"))

        return "\n".join(lines)

    def help_text(self, commands: Dict[str, str]) -> str:
        """Format help text"""
        lines = [self.heading("Available Commands")]

        # Group commands
        core_cmds = {}
        module_cmds = {}

        for cmd, desc in sorted(commands.items()):
            if cmd in ["use", "show", "search", "info"]:
                core_cmds[cmd] = desc
            elif cmd in ["set", "unset", "options"]:
                module_cmds[cmd] = desc
            else:
                # Other commands
                pass

        # Core commands
        lines.append(self.subheading("Core Commands"))
        for cmd, desc in core_cmds.items():
            cmd_colored = self._color(cmd.ljust(15), Colors.GREEN)
            lines.append(f"  {cmd_colored} {desc}")

        # Module commands
        if module_cmds:
            lines.append(self.subheading("Module Commands"))
            for cmd, desc in module_cmds.items():
                cmd_colored = self._color(cmd.ljust(15), Colors.GREEN)
                lines.append(f"  {cmd_colored} {desc}")

        # Other commands
        other_cmds = {k: v for k, v in commands.items()
                     if k not in core_cmds and k not in module_cmds}
        if other_cmds:
            lines.append(self.subheading("Other Commands"))
            for cmd, desc in other_cmds.items():
                cmd_colored = self._color(cmd.ljust(15), Colors.GREEN)
                lines.append(f"  {cmd_colored} {desc}")

        return "\n".join(lines)

    def status_line(self, current_module: Optional[str] = None) -> str:
        """Format status line for prompt"""
        if current_module:
            module_colored = self._color(current_module, Colors.RED)
            return f"msf6 ({module_colored})"
        else:
            return "msf6"

    def progress(self, message: str, current: int, total: int) -> str:
        """Format progress indicator"""
        percentage = int((current / total) * 100) if total > 0 else 0
        bar_length = 40
        filled = int((current / total) * bar_length) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        return f"{message}: [{bar}] {percentage}% ({current}/{total})"
