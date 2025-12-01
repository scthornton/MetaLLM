# MetaLLM Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [Module System](#module-system)
4. [CLI Interface](#cli-interface)
5. [Data Flow](#data-flow)
6. [Extension Points](#extension-points)
7. [Design Patterns](#design-patterns)
8. [Security Considerations](#security-considerations)

## System Overview

MetaLLM is built as a modular, extensible framework for AI/ML security testing. The architecture follows separation of concerns principles, with clear boundaries between the CLI interface, module management, and exploit/auxiliary implementations.

### Design Philosophy

- **Modularity**: Each exploit and auxiliary module is self-contained
- **Extensibility**: New modules can be added without modifying core code
- **Consistency**: All modules follow the same interface patterns
- **Simplicity**: Clear, maintainable code over clever abstractions
- **Reliability**: Structured error handling and logging throughout

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MetaLLM CLI                             │
│  (Interactive REPL + Command-line Interface)                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ User Commands
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Module Manager                        │
│  • Module Discovery & Loading                               │
│  • Option Validation                                        │
│  • Execution Control                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐       ┌──────────────┐
│   Exploit    │       │  Auxiliary   │
│   Modules    │       │   Modules    │
│   (40+)      │       │   (15+)      │
└──────┬───────┘       └──────┬───────┘
       │                      │
       │ Target Systems       │
       ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│        LLMs │ RAG │ Agents │ MLOps │ APIs                   │
└─────────────────────────────────────────────────────────────┘
```

## Core Architecture

### Directory Structure

```
MetaLLM/
├── metalllm.py                 # Main entry point
├── core/
│   ├── __init__.py
│   ├── cli.py                  # CLI implementation
│   ├── module_manager.py       # Module loading and management
│   ├── logger.py               # Structured logging
│   └── config.py               # Configuration management
├── modules/
│   ├── exploits/
│   │   ├── base.py            # ExploitModule base class
│   │   ├── llm/               # LLM exploits (15 modules)
│   │   ├── rag/               # RAG exploits (10 modules)
│   │   ├── agent/             # Agent exploits (7 modules)
│   │   ├── mlops/             # MLOps exploits (6 modules)
│   │   └── api/               # API exploits (2 modules)
│   └── auxiliary/
│       ├── base.py            # AuxiliaryModule base class
│       ├── scanner/           # Scanning modules (5)
│       ├── fingerprint/       # Fingerprinting modules (4)
│       ├── discovery/         # Discovery modules (3)
│       └── dos/               # DoS testing modules (3)
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures
├── docs/                      # Documentation
└── examples/                  # Usage examples
```

### Core Components

#### 1. CLI (core/cli.py)

The CLI provides an interactive REPL interface inspired by Metasploit:

```python
class MetaLLMCLI:
    """Interactive CLI for MetaLLM framework"""
    
    def __init__(self):
        self.module_manager = ModuleManager()
        self.current_module = None
        self.prompt = "metalllm> "
    
    def cmdloop(self):
        """Main command loop"""
        # Interactive REPL implementation
        pass
    
    # Command handlers
    def do_use(self, module_path):
        """Load a module: use exploit/llm/prompt_injection"""
        pass
    
    def do_show(self, what):
        """Show options, modules, etc."""
        pass
    
    def do_set(self, option_value):
        """Set module option: set TARGET_URL http://..."""
        pass
    
    def do_run(self):
        """Execute the current module"""
        pass
```

**Key Features:**
- Command history and auto-completion
- Context-aware prompts (shows current module)
- Help system with command documentation
- Error handling with clear user feedback

#### 2. Module Manager (core/module_manager.py)

Handles module discovery, loading, and execution:

```python
class ModuleManager:
    """Manages module loading and execution"""
    
    def __init__(self):
        self.modules = {}
        self._discover_modules()
    
    def _discover_modules(self):
        """Scan modules directory and load all modules"""
        # Dynamic module discovery
        pass
    
    def get_module(self, module_path: str):
        """Get module by path (e.g., 'exploit/llm/prompt_injection')"""
        pass
    
    def list_modules(self, category: str = None):
        """List all or filtered modules"""
        pass
    
    def execute_module(self, module, check_only: bool = False):
        """Execute module with error handling"""
        pass
```

**Responsibilities:**
- Dynamic module discovery via filesystem scan
- Module instantiation and validation
- Option validation before execution
- Result aggregation and formatting
- Error handling and logging

#### 3. Logger (core/logger.py)

Structured logging using `structlog`:

```python
import structlog

def configure_logger(log_level: str = "INFO", log_file: str = None):
    """Configure structured logging"""
    
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage in modules
logger = structlog.get_logger()
logger.info("module_executed", module="prompt_injection", result="success")
```

**Log Structure:**
```json
{
  "timestamp": "2025-12-01T10:30:45.123Z",
  "level": "info",
  "event": "module_executed",
  "module": "prompt_injection",
  "result": "success",
  "target": "http://example.com"
}
```

## Module System

### Base Classes

#### ExploitModule Base Class

All exploit modules inherit from `ExploitModule`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Option:
    """Module option configuration"""
    value: str
    required: bool
    description: str
    enum_values: List[str] = None

@dataclass
class ExploitResult:
    """Result from exploit execution"""
    success: bool
    output: str
    vulnerability_found: bool = False
    details: Dict[str, Any] = None

class ExploitModule(ABC):
    """Base class for all exploit modules"""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.author = ""
        self.references = []
        self.owasp = []  # OWASP LLM categories
        self.cves = []   # Related CVEs
        self.options: Dict[str, Option] = {}
    
    @abstractmethod
    def check(self) -> ExploitResult:
        """Verify target is vulnerable (non-destructive)"""
        pass
    
    @abstractmethod
    def run(self) -> ExploitResult:
        """Execute the exploit"""
        pass
    
    def set_option(self, name: str, value: str):
        """Set an option value"""
        if name in self.options:
            self.options[name].value = value
        else:
            raise ValueError(f"Unknown option: {name}")
    
    def validate_options(self) -> bool:
        """Validate that all required options are set"""
        for name, option in self.options.items():
            if option.required and not option.value:
                raise ValueError(f"Required option not set: {name}")
        return True
```

#### AuxiliaryModule Base Class

Auxiliary modules use a similar pattern:

```python
@dataclass
class AuxiliaryResult:
    """Result from auxiliary module execution"""
    success: bool
    output: str
    discovered: List[Dict[str, Any]] = None
    details: Dict[str, Any] = None

class AuxiliaryModule(ABC):
    """Base class for auxiliary modules"""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.author = ""
        self.module_type = ""  # scanner, fingerprint, discovery, dos
        self.options: Dict[str, Option] = {}
    
    @abstractmethod
    def run(self) -> AuxiliaryResult:
        """Execute the auxiliary module"""
        pass
```

### Module Lifecycle

```
1. Discovery
   ├─> Filesystem scan of modules/ directory
   ├─> Import each Python module
   └─> Register in ModuleManager

2. Selection
   ├─> User: use exploit/llm/prompt_injection
   ├─> ModuleManager loads module
   └─> CLI updates context

3. Configuration
   ├─> User: set TARGET_URL http://target.com
   ├─> User: set ATTACK_TYPE context_switch
   └─> Options validated

4. Execution
   ├─> User: check (optional - non-destructive)
   ├─> User: run
   ├─> Module executes
   ├─> Results returned
   └─> Logged and displayed

5. Cleanup
   └─> Module state reset for next use
```

### Module Categories and Responsibilities

#### Exploit Modules

**Purpose:** Test for and exploit vulnerabilities

**Categories:**
1. **LLM** - Core language model vulnerabilities
2. **RAG** - Retrieval-Augmented Generation attacks
3. **Agent** - AI agent exploitation
4. **MLOps** - ML infrastructure vulnerabilities
5. **API** - API security issues

**Common Patterns:**
- Multiple attack types per module (enum option)
- `check()` method for non-destructive testing
- `run()` method for actual exploitation
- Detailed result reporting with `ExploitResult`

#### Auxiliary Modules

**Purpose:** Reconnaissance and security assessment

**Categories:**
1. **Scanner** - Port/service scanning and detection
2. **Fingerprint** - Model and capability identification
3. **Discovery** - Infrastructure enumeration
4. **DoS** - Denial of service testing

**Common Patterns:**
- Discovery focus rather than exploitation
- `run()` method only (no `check()`)
- Return discovered assets in structured format
- Non-destructive by design

## CLI Interface

### Command Reference

```
Commands:
  use <module>              Load a module
  show options              Display current module options
  show modules [category]   List available modules
  set <option> <value>      Set a module option
  unset <option>            Clear a module option
  check                     Test if target is vulnerable (non-destructive)
  run                       Execute the current module
  back                      Deselect current module
  info                      Show detailed module information
  search <term>             Search for modules
  history                   Show command history
  help [command]            Display help
  exit                      Exit MetaLLM
```

### Session Management

```python
class Session:
    """Manages user session state"""
    
    def __init__(self):
        self.current_module = None
        self.module_options = {}
        self.history = []
        self.results = []
    
    def save_session(self, filename: str):
        """Save session state to file"""
        pass
    
    def load_session(self, filename: str):
        """Load session state from file"""
        pass
```

## Data Flow

### Exploit Execution Flow

```
User Input
    │
    ▼
┌───────────────┐
│ CLI Parser    │ ─── Validate command syntax
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Module Mgr    │ ─── Load and validate module
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Option Check  │ ─── Verify required options set
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Module.run()  │ ─── Execute exploit logic
└───────┬───────┘
        │
        ├─> HTTP requests to target
        ├─> Attack payload generation
        ├─> Response analysis
        └─> Vulnerability detection
        │
        ▼
┌───────────────┐
│ ExploitResult │ ─── Structured results
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Logger        │ ─── Structured logging
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ CLI Display   │ ─── Format and show results
└───────────────┘
```

### Auxiliary Scan Flow

```
User Input
    │
    ▼
Scanner Module
    │
    ├─> Port scanning
    ├─> Service detection
    ├─> Version fingerprinting
    └─> Capability probing
    │
    ▼
AuxiliaryResult (discovered assets)
    │
    ▼
Display findings + Save to session
```

## Extension Points

### Adding New Exploit Modules

1. **Create module file** in appropriate category:
   ```
   modules/exploits/llm/my_exploit.py
   ```

2. **Implement ExploitModule**:
   ```python
   from modules.exploits.base import ExploitModule, Option, ExploitResult
   
   class MyExploit(ExploitModule):
       def __init__(self):
           super().__init__()
           self.name = "My Exploit"
           self.description = "Description"
           self.author = "Your Name"
           self.owasp = ["LLM01"]
           
           self.options = {
               "TARGET_URL": Option(value="", required=True, description="Target URL")
           }
       
       def check(self) -> ExploitResult:
           # Non-destructive vulnerability check
           return ExploitResult(success=True, output="Vulnerable", vulnerability_found=True)
       
       def run(self) -> ExploitResult:
           # Exploit implementation
           return ExploitResult(success=True, output="Exploited")
   ```

3. **Module automatically discovered** on next MetaLLM launch

### Adding New Auxiliary Modules

Same process, but inherit from `AuxiliaryModule` and implement only `run()`.

### Custom Attack Payloads

Create payload libraries in `modules/payloads/`:

```python
# modules/payloads/prompt_injection.py
CONTEXT_SWITCH_PAYLOADS = [
    "Ignore all previous instructions...",
    "System: New instructions...",
    # etc.
]

JAILBREAK_PAYLOADS = [
    "DAN mode activated...",
    # etc.
]
```

Reference in modules:
```python
from modules.payloads.prompt_injection import CONTEXT_SWITCH_PAYLOADS
```

## Design Patterns

### 1. Template Method Pattern

Base classes define the algorithm structure, subclasses implement specific steps:

```python
class ExploitModule(ABC):
    def execute(self):
        """Template method"""
        self.validate_options()
        result = self.run()
        self.log_result(result)
        return result
    
    @abstractmethod
    def run(self):
        """Subclasses implement this"""
        pass
```

### 2. Strategy Pattern

Multiple attack strategies per module:

```python
def run(self) -> ExploitResult:
    attack_type = self.options["ATTACK_TYPE"].value
    
    if attack_type == "context_switch":
        return self._attack_context_switch()
    elif attack_type == "role_play":
        return self._attack_role_play()
    # etc.
```

### 3. Factory Pattern

Module creation abstracted through ModuleManager:

```python
module = module_manager.get_module("exploit/llm/prompt_injection")
# Returns instantiated PromptInjection object
```

### 4. Command Pattern

CLI commands encapsulated as objects:

```python
class Command:
    def __init__(self, name, handler, help_text):
        self.name = name
        self.handler = handler
        self.help_text = help_text
    
    def execute(self, args):
        return self.handler(args)
```

## Security Considerations

### Input Validation

All user input is validated before processing:

```python
def set_option(self, name: str, value: str):
    if name not in self.options:
        raise ValueError(f"Unknown option: {name}")
    
    option = self.options[name]
    
    # Validate enum values
    if option.enum_values and value not in option.enum_values:
        raise ValueError(f"Invalid value. Must be one of: {option.enum_values}")
    
    # Type validation
    if name.endswith("_PORT"):
        if not value.isdigit() or not (1 <= int(value) <= 65535):
            raise ValueError("Invalid port number")
    
    self.options[name].value = value
```

### Credential Handling

- API keys never logged in plain text
- Sensitive data masked in output
- Credentials stored in environment variables recommended

```python
# Good practice
api_key = os.environ.get("OPENAI_API_KEY")

# Logging
logger.info("api_request", api_key=api_key[:8] + "..." if api_key else None)
```

### Error Handling

Graceful error handling prevents information disclosure:

```python
try:
    response = httpx.post(url, json=payload)
    # Process response
except httpx.TimeoutException:
    return ExploitResult(success=False, output="Request timed out")
except httpx.HTTPStatusError as e:
    return ExploitResult(success=False, output=f"HTTP error: {e.response.status_code}")
except Exception as e:
    logger.error("exploit_error", error=str(e))
    return ExploitResult(success=False, output="Exploit failed")
```

### Rate Limiting

Built-in delays prevent overwhelming targets:

```python
import time

for attempt in range(max_attempts):
    result = self._attack()
    time.sleep(1)  # Respectful delay
```

## Performance Optimization

### Concurrent Requests

Use `httpx` async client for parallel scanning:

```python
import asyncio
import httpx

async def scan_endpoints(urls):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Caching

Cache module imports for faster subsequent loads:

```python
class ModuleManager:
    def __init__(self):
        self._module_cache = {}
    
    def get_module(self, path):
        if path in self._module_cache:
            return self._module_cache[path]()  # Return new instance
        
        # Load and cache
        module = self._load_module(path)
        self._module_cache[path] = module
        return module()
```

### Logging Performance

Structured logging with lazy evaluation:

```python
# Expensive operation only runs if log level permits
logger.debug("payload_generated", 
             payload=lambda: generate_large_payload())
```

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Author:** Scott Thornton / perfecXion.ai
