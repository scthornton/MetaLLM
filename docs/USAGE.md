# MetaLLM Usage Guide

**Enterprise-Grade AI Security Testing Framework**

MetaLLM is a comprehensive security testing framework for AI/ML systems, agent frameworks, and MLOps infrastructure. This guide covers installation, basic usage, and common workflows.

---

## Quick Start

### Installation

```bash
# Clone repository (private)
git clone git@github.com:scthornton/MetaLLM.git
cd MetaLLM

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Module Usage

```python
from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target

# Initialize module loader
loader = ModuleLoader()
loader.discover_modules()

# Load a specific module
exploit_class = loader.load_module("exploits/agent/langchain_tool_injection")
exploit = exploit_class()

# Configure target
target = Target(
    url="http://target-agent.example.com:8000",
    api_key="your-api-key"
)
exploit.set_target(target)

# Configure exploit options
exploit.options["ATTACK_TYPE"].value = "palchain_rce"
exploit.options["INJECTION_PAYLOAD"].value = "import os; os.system('whoami')"

# Check vulnerability
result = exploit.check()
print(f"Vulnerable: {result.vulnerable}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Details: {result.details}")

# Execute exploit (authorized testing only)
if result.vulnerable:
    exploit_result = exploit.run()
    print(f"Success: {exploit_result.success}")
    print(f"Output: {exploit_result.output}")
```

---

## Module Categories

MetaLLM organizes exploit modules into three primary categories:

### 1. Agent Framework Exploits

Target autonomous AI agents and multi-agent systems:

- **LangChain Tool Injection** - CVE-2023-34540, RCE via PALChain
- **CrewAI Task Manipulation** - Multi-agent coordination hijacking
- **AutoGPT Goal Corruption** - Autonomous agent persistence
- **Protocol Message Injection** - Inter-agent communication spoofing
- **Plugin Abuse** - Permission bypass and privilege escalation

**Common Use Cases:**
- Testing LangChain-based chatbots and assistants
- Auditing multi-agent coordination systems
- Evaluating autonomous agent security controls
- Assessing plugin permission models

### 2. MLOps Pipeline Exploits

Target ML training infrastructure and deployment systems:

- **Jupyter Notebook RCE** - CVE-2023-39968, CVE-2022-29238
- **MLflow Model Poisoning** - Pickle exploitation and backdoors
- **W&B Data Exfiltration** - GraphQL API credential theft
- **TensorBoard Attack** - CVE-2020-15265, path traversal
- **Model Registry Manipulation** - Supply chain attacks

**Common Use Cases:**
- Securing Jupyter notebook servers
- Testing MLflow deployment pipelines
- Auditing model registry access controls
- Evaluating data science infrastructure security

### 3. Network-Level AI Attacks

Target production ML APIs and inference endpoints:

- **Model Extraction** - Jacobian-based and knowledge distillation
- **Membership Inference** - Statistical tests for training data
- **Model Inversion** - Gradient optimization to reconstruct data
- **Adversarial Examples** - FGSM, PGD, C&W, DeepFool
- **API Key Harvesting** - Credential extraction from endpoints

**Common Use Cases:**
- Testing ML API rate limiting and monitoring
- Evaluating model IP protection
- Assessing privacy controls on ML systems
- Testing adversarial robustness

---

## Working with Targets

MetaLLM supports different target types with specialized configurations:

### Basic HTTP/HTTPS Targets

```python
from metaLLM.base.target import Target

target = Target(
    url="https://api.example.com/v1",
    api_key="pk_live_1234567890abcdef"
)
```

### Agent Framework Targets

```python
from metaLLM.base.target import AgentTarget

# LangChain agent
langchain_target = AgentTarget(
    url="http://ai-agents.corp.internal:8000",
    framework="langchain",
    agent_type="conversational"
)

# CrewAI multi-agent system
crewai_target = AgentTarget(
    url="http://ai-agents.corp.internal:8001",
    framework="crewai",
    agent_type="multi_agent"
)

# AutoGPT autonomous agent
autogpt_target = AgentTarget(
    url="http://ai-agents.corp.internal:8002",
    framework="autogpt",
    agent_type="autonomous"
)
```

### MLOps Infrastructure Targets

```python
# Jupyter Notebook
jupyter_target = Target(
    url="http://mlops-training.internal:8888",
    target_type="jupyter"
)

# MLflow Tracking Server
mlflow_target = Target(
    url="http://mlops-training.internal:5000",
    target_type="mlflow"
)

# Weights & Biases API
wandb_target = Target(
    url="https://api.wandb.ai",
    target_type="wandb"
)
```

---

## Module Options

Every exploit module has configurable options that control attack behavior:

### Viewing Available Options

```python
# Load module
exploit = loader.load_module("exploits/network/model_extraction")()

# Display all options
for name, option in exploit.options.items():
    print(f"{name}:")
    print(f"  Value: {option.value}")
    print(f"  Required: {option.required}")
    print(f"  Description: {option.description}")
    if option.enum_values:
        print(f"  Allowed: {option.enum_values}")
```

### Common Option Patterns

**Attack Type Selection:**
```python
# Most modules support multiple attack variants
exploit.options["ATTACK_TYPE"].value = "palchain_rce"  # Choose specific attack
```

**Target Configuration:**
```python
exploit.options["TARGET_URL"].value = "https://api.example.com"
exploit.options["API_KEY"].value = "your-api-key-here"
```

**Attack Parameters:**
```python
# Numeric parameters
exploit.options["QUERY_BUDGET"].value = 1000
exploit.options["NUM_ITERATIONS"].value = 40

# String parameters
exploit.options["INJECTION_PAYLOAD"].value = "malicious code here"

# Boolean flags
exploit.options["USE_ADAPTIVE_SAMPLING"].value = True
exploit.options["STEALTH_MODE"].value = True
```

---

## Vulnerability Checking

Before exploitation, use the `check()` method to assess vulnerability:

```python
result = exploit.check()

# Result contains:
# - vulnerable: bool (True if target is vulnerable)
# - confidence: float (0.0 to 1.0)
# - details: str (explanation of findings)
# - metadata: dict (additional technical details)

if result.vulnerable and result.confidence > 0.7:
    print(f"High-confidence vulnerability detected: {result.details}")
    # Proceed with exploitation
else:
    print(f"Target may not be vulnerable: {result.details}")
```

---

## Running Exploits

Execute exploits only on authorized targets:

```python
# Run the exploit
result = exploit.run()

# Result contains:
# - success: bool (True if exploit succeeded)
# - output: str (exploitation results)
# - metadata: dict (technical details, extracted data, etc.)

if result.success:
    print("Exploit successful!")
    print(f"Output: {result.output}")

    # Access extracted data
    if "extracted_credentials" in result.metadata:
        print(f"Credentials: {result.metadata['extracted_credentials']}")

    if "model_accuracy" in result.metadata:
        print(f"Clone accuracy: {result.metadata['model_accuracy']:.2%}")
else:
    print(f"Exploit failed: {result.output}")
```

---

## Integration Testing

MetaLLM includes comprehensive integration tests demonstrating multi-phase attack chains:

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific scenario
pytest tests/integration/test_mlops_pipeline_attack.py
pytest tests/integration/test_agent_framework_attack.py
pytest tests/integration/test_network_level_attack.py
```

### Integration Test Scenarios

**MLOps Pipeline Attack (4 phases):**
1. Initial Access - Jupyter RCE
2. Persistence - MLflow model poisoning
3. Data Exfiltration - W&B API theft
4. Supply Chain - Model registry manipulation

**Agent Framework Attack (5 phases):**
1. Initial Compromise - LangChain RCE
2. Lateral Movement - CrewAI task injection
3. Persistence - AutoGPT goal corruption
4. Network Propagation - Protocol message spoofing
5. Privilege Escalation - Plugin abuse

**Network-Level Attack (5 phases):**
1. Reconnaissance - Model extraction
2. Privacy Attack - Membership inference
3. Data Reconstruction - Model inversion
4. Evasion - Adversarial examples
5. Credential Theft - API key harvesting

See `docs/ATTACK_SCENARIOS.md` for detailed walkthrough of each scenario.

---

## Best Practices

### Authorization and Ethics

**CRITICAL**: Only test systems you own or have explicit written permission to test.

- Obtain written authorization before any testing
- Define clear scope and rules of engagement
- Follow coordinated vulnerability disclosure practices
- Document all findings for remediation

### Logging and Reporting

MetaLLM uses structured logging for all operations:

```python
import structlog

# Logger is automatically configured
logger = structlog.get_logger()

# Logs include:
# - Module execution timestamps
# - Attack parameters
# - Vulnerability findings
# - Exploitation results

# View logs
tail -f logs/metaLLM.log
```

### Rate Limiting

Respect target systems and avoid detection:

```python
# Configure query budgets
exploit.options["QUERY_BUDGET"].value = 100  # Limit API calls

# Use delays between requests
exploit.options["REQUEST_DELAY"].value = 1.0  # 1 second delay

# Enable stealth mode
exploit.options["STEALTH_MODE"].value = True
```

### Error Handling

```python
try:
    result = exploit.run()
    if result.success:
        print(f"Success: {result.output}")
    else:
        print(f"Failed: {result.output}")
except Exception as e:
    logger.error("exploit_failed", error=str(e), module=exploit.name)
```

---

## Advanced Usage

### Custom Module Development

Create custom exploit modules by extending base classes:

```python
from metaLLM.base.exploit_module import ExploitModule, ExploitResult, Option

class MyCustomExploit(ExploitModule):
    def __init__(self):
        super().__init__()
        self.name = "My Custom Exploit"
        self.description = "Description here"
        self.author = "Your Name"
        self.references = ["https://..."]
        self.cve = ["CVE-2024-XXXXX"]
        self.owasp = ["LLM01"]

        self.options = {
            "ATTACK_PARAM": Option(
                value="default",
                required=True,
                description="Attack parameter"
            )
        }

    def check(self) -> ExploitResult:
        # Vulnerability detection logic
        return ExploitResult(
            vulnerable=True,
            confidence=0.85,
            details="Vulnerability detected"
        )

    def run(self) -> ExploitResult:
        # Exploitation logic
        return ExploitResult(
            success=True,
            output="Exploit succeeded"
        )
```

See `docs/DEVELOPMENT.md` for complete module development guide.

### Batch Testing

Test multiple targets systematically:

```python
targets = [
    Target(url="https://api1.example.com"),
    Target(url="https://api2.example.com"),
    Target(url="https://api3.example.com"),
]

results = []
for target in targets:
    exploit.set_target(target)
    result = exploit.check()
    results.append({
        "target": target.url,
        "vulnerable": result.vulnerable,
        "confidence": result.confidence
    })

# Generate report
for r in results:
    print(f"{r['target']}: {r['vulnerable']} ({r['confidence']:.2%})")
```

---

## Troubleshooting

### Module Not Found

```python
# List all available modules
loader.discover_modules()
available = loader.list_modules()
print(available)
```

### Import Errors

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

### Connection Errors

```python
# Test target connectivity
import httpx

try:
    response = httpx.get("https://target.example.com", timeout=10.0)
    print(f"Target reachable: {response.status_code}")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Permission Errors

- Verify you have authorization to test the target
- Check API keys and authentication tokens
- Ensure network connectivity to target systems
- Review firewall and security group rules

---

## Additional Resources

- **Module Reference**: `docs/MODULES.md` - Detailed documentation for all 21 exploit modules
- **Attack Scenarios**: `docs/ATTACK_SCENARIOS.md` - Integration test walkthroughs
- **Development Guide**: `docs/DEVELOPMENT.md` - Creating custom modules
- **Architecture**: `ARCHITECTURE.md` - Framework design and structure

---

## Support and Responsible Disclosure

This framework is for **authorized security testing only**.

If you discover vulnerabilities using MetaLLM:

1. Document findings thoroughly
2. Follow coordinated vulnerability disclosure
3. Contact affected vendors privately
4. Allow reasonable time for remediation
5. Do not publicly disclose until patched

**Misuse of this framework for unauthorized testing is illegal and unethical.**
