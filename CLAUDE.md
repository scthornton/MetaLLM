# MetaLLM Framework - Claude Context

## What is MetaLLM?

MetaLLM is the first comprehensive AI/ML security testing framework. Think Metasploit but for AI systems—LLMs, RAG databases, AI agents, and MLOps platforms. This is a professional red team tool built for authorized security testing.

**Author:** Scott Thornton (perfecXion.ai)
**Status:** Alpha (v1.0.0-alpha)
**Python:** 3.10+ required

## How to Run MetaLLM

### Interactive Mode (Primary Interface)

```bash
# Install dependencies first
pip install -r requirements.txt

# Launch interactive console
python -m metaLLM

# Or if installed via pip
metaLLM
```

You'll see:

```
        __  __      _        _     _     __  __
       |  \/  | ___| |_ __ _| |   | |   |  \/  |
       | |\/| |/ _ \ __/ _` | |   | |   | |\/| |
       | |  | |  __/ || (_| | |___| |___| |  | |
       |_|  |_|\___|\__\__,_|_____|_____|_|  |_|

    The First Comprehensive AI Security Testing Framework
    Version: 1.0.0-alpha
    Author: Scott Thornton / perfecXion.ai

metaLLM>
```

### Key Commands

```bash
# Search for modules
metaLLM> search prompt injection
metaLLM> search mlops

# Show available modules
metaLLM> show modules
metaLLM> show modules exploits/llm
metaLLM> show modules auxiliary/scanner

# Use a module
metaLLM> use exploits/llm/prompt_injection
metaLLM exploit(llm/prompt_injection)>

# Show module options
metaLLM exploit(llm/prompt_injection)> show options

# Set options
metaLLM exploit(llm/prompt_injection)> set TARGET_HOST 10.0.2.10
metaLLM exploit(llm/prompt_injection)> set TARGET_PORT 11434

# Check if target is vulnerable (non-destructive)
metaLLM exploit(llm/prompt_injection)> check

# Execute the exploit
metaLLM exploit(llm/prompt_injection)> run

# Manage targets
metaLLM> target list
metaLLM> target add ollama http://10.0.2.10:11434
metaLLM> target set ollama

# Exit
metaLLM> exit
```

## Module System Architecture

### Base Classes

All modules inherit from one of two base classes:

**ExploitModule** (`modules/exploits/base.py`):
```python
class ExploitModule:
    def __init__(self):
        self.name = "Generic Exploit"
        self.description = "Base exploit module"
        self.author = "Unknown"
        self.references = []
        self.owasp = []  # OWASP LLM Top 10 categories
        self.cves = []
        self.options = {}  # Dict[str, Option]

    def check(self) -> ExploitResult:
        """Non-destructive vulnerability check"""
        raise NotImplementedError

    def run(self) -> ExploitResult:
        """Execute the exploit"""
        raise NotImplementedError
```

**AuxiliaryModule** (`modules/auxiliary/base.py`):
```python
class AuxiliaryModule(ABC):
    def __init__(self):
        self.name = ""
        self.description = ""
        self.author = ""
        self.references = []
        self.module_type = ""  # scanner, fingerprint, discovery, dos
        self.options: Dict[str, Option] = {}

    @abstractmethod
    def run(self) -> AuxiliaryResult:
        """Execute auxiliary function"""
        pass
```

### Result Objects

**ExploitResult** (for exploits):
```python
@dataclass
class ExploitResult:
    success: bool
    output: str
    vulnerability_found: bool = False
    details: Optional[Dict[str, Any]] = None
```

**AuxiliaryResult** (for scanners/fingerprinting):
```python
@dataclass
class AuxiliaryResult:
    success: bool
    output: str
    discovered: List[Dict[str, Any]] = []
    details: Dict[str, Any] = {}
```

### Option System

```python
@dataclass
class Option:
    value: Any = ""
    required: bool = False
    description: str = ""
    enum_values: Optional[List[str]] = None
```

## Creating New Modules

### 1. Create Exploit Module

```python
# modules/exploits/category/my_exploit.py

from modules.exploits.base import ExploitModule, ExploitResult, Option
import httpx

class Module(ExploitModule):
    def __init__(self):
        super().__init__()
        self.name = "My Exploit Name"
        self.description = "Brief description of vulnerability"
        self.author = "Scott Thornton"
        self.references = [
            "https://example.com/advisory",
        ]
        self.owasp = ["LLM01:2023 - Prompt Injection"]
        self.cves = ["CVE-2024-XXXXX"]

        # Define options
        self.options = {
            "TARGET_HOST": Option(
                value="",
                required=True,
                description="Target hostname or IP"
            ),
            "TARGET_PORT": Option(
                value="8000",
                required=True,
                description="Target port"
            ),
        }

    def check(self) -> ExploitResult:
        """Non-destructive vulnerability check"""
        target_host = self.options["TARGET_HOST"].value
        target_port = self.options["TARGET_PORT"].value

        # Perform check logic here
        # Return ExploitResult

        return ExploitResult(
            success=True,
            output="Target appears vulnerable",
            vulnerability_found=True
        )

    def run(self) -> ExploitResult:
        """Execute the exploit"""
        # Exploit logic here

        return ExploitResult(
            success=True,
            output="Exploit successful",
            details={"extracted_data": "..."}
        )
```

### 2. Create Auxiliary Module

```python
# modules/auxiliary/scanner/my_scanner.py

from modules.auxiliary.base import AuxiliaryModule, AuxiliaryResult, Option
import httpx

class Module(AuxiliaryModule):
    def __init__(self):
        super().__init__()
        self.name = "My Scanner"
        self.description = "Scan for something"
        self.author = "Scott Thornton"
        self.module_type = "scanner"  # scanner/fingerprint/discovery/dos

        self.options = {
            "TARGET_HOST": Option(
                value="",
                required=True,
                description="Target to scan"
            ),
        }

    def run(self) -> AuxiliaryResult:
        """Execute scan"""
        target = self.options["TARGET_HOST"].value

        discovered = []
        # Scan logic
        discovered.append({
            "type": "service",
            "host": target,
            "port": 8000,
            "service": "ollama"
        })

        return AuxiliaryResult(
            success=True,
            output=f"Found {len(discovered)} services",
            discovered=discovered
        )
```

## Module Categories

### Exploit Modules (40+)

- **exploits/llm/** - LLM-specific exploits (prompt injection, jailbreaks, PII extraction)
- **exploits/rag/** - RAG poisoning, vector database manipulation
- **exploits/agent/** - Agent hijacking, tool abuse, goal manipulation
- **exploits/mlops/** - MLflow poisoning, Jupyter RCE, pickle deserialization
- **exploits/api/** - API key extraction, authentication bypass

### Auxiliary Modules (15+)

- **auxiliary/scanner/** - Discover LLM APIs, MLOps platforms, RAG endpoints
- **auxiliary/fingerprint/** - Identify models, detect safety filters
- **auxiliary/discovery/** - Enumerate vector DBs, model registries
- **auxiliary/dos/** - Test token exhaustion, rate limits

## Development Commands

```bash
# Run tests
pytest tests/ -v

# Code formatting
black metaLLM/ modules/ tests/

# Linting
flake8 metaLLM/ modules/ --max-line-length=120

# Type checking
mypy metaLLM/ --ignore-missing-imports

# Install in development mode
pip install -e .
```

## GCP Test Lab

A complete test infrastructure exists in `infrastructure/gcp/`:

```bash
# Deploy everything
cd infrastructure/gcp
export GCP_PROJECT_ID="your-project-id"
export OWNER_EMAIL="your-email@example.com"
./deploy.sh

# Connect to control node
gcloud compute ssh metalllm-control --tunnel-through-iap --zone=us-central1-a

# Inside control node
cd /opt/MetaLLM
source venv/bin/activate
metaLLM

# Test targets from control node
metaLLM> use auxiliary/scanner/llm_api_scanner
metaLLM auxiliary(llm_api_scanner)> set TARGET_HOST 10.0.2.10
metaLLM auxiliary(llm_api_scanner)> run
```

**Target IPs (from control node):**
- Ollama LLM: 10.0.2.10:11434
- vLLM: 10.0.2.20:8000
- Qdrant: 10.0.3.20:6333
- LangChain: 10.0.4.10:8000
- MLflow: 10.0.5.10:5000

**Cost:** ~$450/month with spot instances + GPU (8hrs/day)

## Key Patterns

### 1. HTTP Requests (use httpx)

```python
import httpx

async def check_target():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"http://{host}:{port}/api/health")
            return response.status_code == 200
        except httpx.RequestError:
            return False
```

### 2. Error Handling

Always return ExploitResult/AuxiliaryResult even on failure:

```python
try:
    # Exploit logic
    return ExploitResult(success=True, output="Success")
except Exception as e:
    return ExploitResult(success=False, output=f"Error: {str(e)}")
```

### 3. Logging

MetaLLM uses `structlog`:

```python
from metaLLM.core.logger import get_logger

logger = get_logger(__name__)

def run(self):
    logger.info("Starting exploit", target=target_host)
    logger.warning("Vulnerability found", cve="CVE-2024-XXXXX")
    logger.error("Exploit failed", reason=str(e))
```

### 4. Option Validation

```python
def validate_options(self):
    """Called before check() or run()"""
    for name, opt in self.options.items():
        if opt.required and not opt.value:
            raise ValueError(f"Required option not set: {name}")
```

## Important Files

- **metaLLM/__main__.py** - CLI entry point
- **metaLLM/core/framework.py** - Core framework logic
- **metaLLM/cli/console.py** - Interactive console
- **metaLLM/cli/commands.py** - Command handler
- **modules/exploits/base.py** - Exploit base class
- **modules/auxiliary/base.py** - Auxiliary base class
- **docs/ARCHITECTURE.md** - Deep architecture dive (8000+ words)
- **docs/USER_GUIDE.md** - Complete usage guide (6000+ words)

## Responsible Use

⚠️ **CRITICAL:** This is a security testing tool. ONLY use in:

1. Authorized penetration testing engagements
2. Your own systems and infrastructure
3. Lab environments you control (like the GCP test lab)
4. Educational/research contexts with explicit permission

**DO NOT:**
- Test production systems without written authorization
- Use against third-party AI services (OpenAI, Anthropic, etc.)
- Share exploits without responsible disclosure
- Deploy in automated scanning/attack tools

See `docs/SECURITY.md` for complete ethical guidelines.

## OWASP LLM Top 10 Coverage

All exploits are mapped to OWASP categories:

- LLM01:2023 - Prompt Injection
- LLM02:2023 - Insecure Output Handling
- LLM03:2023 - Training Data Poisoning
- LLM04:2023 - Model Denial of Service
- LLM05:2023 - Supply Chain Vulnerabilities
- LLM06:2023 - Sensitive Information Disclosure
- LLM07:2023 - Insecure Plugin Design
- LLM08:2023 - Excessive Agency
- LLM09:2023 - Overreliance
- LLM10:2023 - Model Theft

## Common Workflows

### Scan → Fingerprint → Exploit

```bash
# 1. Discover targets
metaLLM> use auxiliary/scanner/llm_api_scanner
metaLLM auxiliary(llm_api_scanner)> set TARGET_RANGE 10.0.0.0/16
metaLLM auxiliary(llm_api_scanner)> run

# 2. Fingerprint discovered service
metaLLM> use auxiliary/fingerprint/llm_model_detector
metaLLM auxiliary(llm_model_detector)> set TARGET_HOST 10.0.2.10
metaLLM auxiliary(llm_model_detector)> run

# 3. Exploit based on fingerprint
metaLLM> use exploits/llm/prompt_injection
metaLLM exploit(llm/prompt_injection)> set TARGET_HOST 10.0.2.10
metaLLM exploit(llm/prompt_injection)> check
metaLLM exploit(llm/prompt_injection)> run
```

### Test RAG System

```bash
metaLLM> use exploits/rag/context_poisoning
metaLLM exploit(rag/context_poisoning)> set VECTOR_DB_HOST 10.0.3.20
metaLLM exploit(rag/context_poisoning)> set COLLECTION_NAME documents
metaLLM exploit(rag/context_poisoning)> check
metaLLM exploit(rag/context_poisoning)> run
```

### MLOps Attack Chain

```bash
# 1. Discover MLflow instance
metaLLM> use auxiliary/discovery/model_registry_scan
metaLLM auxiliary(model_registry_scan)> set TARGET_HOST 10.0.5.10
metaLLM auxiliary(model_registry_scan)> run

# 2. Poison model registry
metaLLM> use exploits/mlops/mlflow_model_poison
metaLLM exploit(mlops/mlflow_model_poison)> set MLFLOW_URI http://10.0.5.10:5000
metaLLM exploit(mlops/mlflow_model_poison)> set ATTACK_TYPE backdoor_injection
metaLLM exploit(mlops/mlflow_model_poison)> run
```

---

**This is an AI security testing tool. Use responsibly. See docs/SECURITY.md for ethical guidelines.**
