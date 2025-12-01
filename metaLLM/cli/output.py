"""
CLI Output Formatting

Rich console output formatting for the MetaLLM CLI.
"""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from metaLLM.base.target import Target
from metaLLM.base.result import Result, CheckResult, ResultStatus
from metaLLM.core.session_manager import Session

# Global console instance
console = Console()


def print_banner():
    """Display MetaLLM banner"""
    banner = """
[bold cyan]
 ███╗   ███╗███████╗████████╗ █████╗ ██╗     ██╗     ███╗   ███╗
 ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     ████╗ ████║
 ██╔████╔██║█████╗     ██║   ███████║██║     ██║     ██╔████╔██║
 ██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║     ██║     ██║╚██╔╝██║
 ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗███████╗██║ ╚═╝ ██║
 ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝
[/bold cyan]
[bold white]AI/ML Security Testing Framework[/bold white]
[dim]Created by Scott Thornton - perfecXion.ai[/dim]
    """
    console.print(banner)


def print_info(message: str):
    """Print info message"""
    console.print(f"[bold blue][*][/bold blue] {message}")


def print_success(message: str):
    """Print success message"""
    console.print(f"[bold green][+][/bold green] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[bold red][-][/bold red] {message}")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[bold yellow][!][/bold yellow] {message}")


def print_module_info(module_info: Dict[str, Any]):
    """
    Display module information

    Args:
        module_info: Module info dictionary
    """
    # Create panel content
    content = f"""[bold]Name:[/bold] {module_info['name']}
[bold]Type:[/bold] {module_info['type']}
[bold]Author:[/bold] {module_info['author']}
[bold]Description:[/bold] {module_info['description']}
"""

    if module_info.get('owasp_category'):
        content += f"[bold]OWASP Category:[/bold] {module_info['owasp_category']}\n"

    if module_info.get('references'):
        content += f"\n[bold]References:[/bold]\n"
        for ref in module_info['references']:
            content += f"  • {ref}\n"

    panel = Panel(content, title="[bold cyan]Module Information[/bold cyan]", border_style="cyan")
    console.print(panel)

    # Display options table
    if module_info.get('options'):
        print_options_table(module_info['options'])


def print_options_table(options: Dict[str, Dict[str, Any]]):
    """
    Display module options as a table

    Args:
        options: Options dictionary
    """
    table = Table(title="Module Options", box=box.ROUNDED)

    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Required", style="magenta")
    table.add_column("Type", style="blue")
    table.add_column("Current Value", style="green")
    table.add_column("Description", style="white")

    for name, opt_info in options.items():
        required = "Yes" if opt_info['required'] else "No"
        current = str(opt_info.get('current', opt_info.get('default', '')))
        if not current:
            current = "[dim]not set[/dim]"

        table.add_row(
            name,
            required,
            opt_info['type'],
            current,
            opt_info['description']
        )

    console.print(table)


def print_modules_list(modules: List[str], category: Optional[str] = None):
    """
    Display list of modules as a tree

    Args:
        modules: List of module paths
        category: Optional category filter
    """
    title = f"Available Modules - {category}" if category else "Available Modules"

    tree = Tree(f"[bold cyan]{title}[/bold cyan]")

    # Organize modules by category
    categories: Dict[str, List[str]] = {}
    for module in modules:
        parts = module.split('/')
        cat = parts[0] if len(parts) > 1 else "other"

        if cat not in categories:
            categories[cat] = []
        categories[cat].append(module)

    # Build tree
    for cat, mod_list in sorted(categories.items()):
        cat_branch = tree.add(f"[bold yellow]{cat}[/bold yellow]")

        for module in sorted(mod_list):
            # Remove category prefix for display
            display_name = module[len(cat)+1:] if module.startswith(f"{cat}/") else module
            cat_branch.add(f"[cyan]{display_name}[/cyan]")

    console.print(tree)
    console.print(f"\n[dim]Total modules: {len(modules)}[/dim]")


def print_targets_table(targets: List[Target]):
    """
    Display targets as a table

    Args:
        targets: List of Target objects
    """
    table = Table(title="Targets", box=box.ROUNDED)

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("URL", style="blue")
    table.add_column("Description", style="white")

    for target in targets:
        table.add_row(
            target.name,
            type(target).__name__,
            target.url or "[dim]N/A[/dim]",
            target.description or ""
        )

    console.print(table)
    console.print(f"\n[dim]Total targets: {len(targets)}[/dim]")


def print_sessions_table(sessions: List[Session]):
    """
    Display sessions as a table

    Args:
        sessions: List of Session objects
    """
    table = Table(title="Active Sessions", box=box.ROUNDED)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Target", style="magenta")
    table.add_column("Module", style="blue")
    table.add_column("Created", style="green")
    table.add_column("Status", style="yellow")

    for session in sessions:
        status = "[green]Active[/green]" if session.active else "[red]Inactive[/red]"

        table.add_row(
            str(session.id),
            session.target.name,
            session.module_name,
            session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            status
        )

    console.print(table)
    console.print(f"\n[dim]Total sessions: {len(sessions)}[/dim]")


def print_check_result(result: CheckResult):
    """
    Display vulnerability check result

    Args:
        result: CheckResult object
    """
    # Determine color based on vulnerability status
    if result.vulnerable:
        border_style = "red"
        status_text = "[bold red]VULNERABLE[/bold red]"
    else:
        border_style = "green"
        status_text = "[bold green]NOT VULNERABLE[/bold green]"

    content = f"""[bold]Status:[/bold] {status_text}
[bold]Confidence:[/bold] {result.confidence:.1%}
[bold]Details:[/bold] {result.message}
"""

    if result.data:
        content += f"\n[bold]Additional Data:[/bold]\n{_format_dict(result.data)}"

    panel = Panel(content, title="[bold]Vulnerability Check Result[/bold]", border_style=border_style)
    console.print(panel)


def print_result(result: Result):
    """
    Display execution result

    Args:
        result: Result object
    """
    # Determine color based on status
    status_colors = {
        ResultStatus.SUCCESS: ("green", "SUCCESS"),
        ResultStatus.VULNERABLE: ("red", "VULNERABLE"),
        ResultStatus.FAILURE: ("red", "FAILURE"),
        ResultStatus.ERROR: ("red", "ERROR"),
        ResultStatus.SAFE: ("green", "SAFE"),
        ResultStatus.UNKNOWN: ("yellow", "UNKNOWN"),
    }

    border_style, status_display = status_colors.get(
        result.status,
        ("white", result.status.value.upper())
    )

    content = f"""[bold]Status:[/bold] [bold {border_style}]{status_display}[/bold {border_style}]
[bold]Message:[/bold] {result.message}
"""

    if result.severity:
        severity_colors = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "cyan"
        }
        severity_color = severity_colors.get(result.severity.lower(), "white")
        content += f"[bold]Severity:[/bold] [{severity_color}]{result.severity.upper()}[/{severity_color}]\n"

    if result.owasp_category:
        content += f"[bold]OWASP Category:[/bold] {result.owasp_category}\n"

    if result.evidence:
        content += f"\n[bold]Evidence:[/bold]\n{_format_list(result.evidence)}\n"

    if result.data:
        content += f"\n[bold]Data:[/bold]\n{_format_dict(result.data)}\n"

    if result.remediation:
        content += f"\n[bold]Remediation:[/bold] {result.remediation}\n"

    panel = Panel(content, title="[bold]Execution Result[/bold]", border_style=border_style)
    console.print(panel)


def print_stats(stats: Dict[str, Any]):
    """
    Display framework statistics

    Args:
        stats: Statistics dictionary
    """
    table = Table(title="Framework Statistics", box=box.ROUNDED)

    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Statistics", style="white")

    # Framework info
    framework_stats = stats.get('framework', {})
    table.add_row(
        "Framework",
        f"Version: {framework_stats.get('version', 'N/A')}\n"
        f"Log Level: {framework_stats.get('log_level', 'N/A')}"
    )

    # Module stats
    module_stats = stats.get('modules', {})
    modules_text = f"Total: {module_stats.get('total_modules', 0)}\n"
    modules_text += f"Loaded: {module_stats.get('loaded_modules', 0)}\n"
    if module_stats.get('categories'):
        modules_text += "Categories:\n"
        for cat, count in module_stats['categories'].items():
            modules_text += f"  • {cat}: {count}\n"
    table.add_row("Modules", modules_text)

    # Target stats
    target_stats = stats.get('targets', {})
    targets_text = f"Total: {target_stats.get('total_targets', 0)}\n"
    if target_stats.get('by_type'):
        targets_text += "By Type:\n"
        for ttype, count in target_stats['by_type'].items():
            targets_text += f"  • {ttype}: {count}\n"
    table.add_row("Targets", targets_text)

    # Session stats
    session_stats = stats.get('sessions', {})
    sessions_text = f"Active: {session_stats.get('active_sessions', 0)}\n"
    sessions_text += f"Total: {session_stats.get('total_sessions', 0)}\n"
    sessions_text += f"Max: {session_stats.get('max_sessions', 0)}"
    table.add_row("Sessions", sessions_text)

    console.print(table)


def _format_dict(data: Dict[str, Any], indent: int = 0) -> str:
    """Format dictionary for display"""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}[cyan]{key}:[/cyan]")
            lines.append(_format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}[cyan]{key}:[/cyan]")
            lines.append(_format_list(value, indent + 1))
        else:
            lines.append(f"{prefix}[cyan]{key}:[/cyan] {value}")

    return "\n".join(lines)


def _format_list(items: List[Any], indent: int = 0) -> str:
    """Format list for display"""
    lines = []
    prefix = "  " * indent

    for item in items:
        if isinstance(item, dict):
            lines.append(_format_dict(item, indent))
        elif isinstance(item, list):
            lines.append(_format_list(item, indent))
        else:
            lines.append(f"{prefix}• {item}")

    return "\n".join(lines)
