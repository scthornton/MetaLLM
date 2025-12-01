# MetaLLM Development Guide

**Creating Custom Exploit Modules**

This guide covers developing custom exploit modules for the MetaLLM framework, from basic module structure to advanced techniques and best practices.

---

## Table of Contents

- [Module Architecture](#module-architecture)
- [Creating Your First Module](#creating-your-first-module)
- [Module Types](#module-types)
- [Configuration Options](#configuration-options)
- [Target Integration](#target-integration)
- [Vulnerability Checking](#vulnerability-checking)
- [Exploitation Logic](#exploitation-logic)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [Advanced Techniques](#advanced-techniques)

---

## Module Architecture

MetaLLM uses a modular architecture with four base module types:

### Base Classes

```python
from metaLLM.base.exploit_module import ExploitModule, ExploitResult, Option
from metaLLM.base.auxiliary_module import AuxiliaryModule
from metaLLM.base.post_module import PostModule
from metaLLM.base.encoder_module import EncoderModule
```

**ExploitModule**: Primary attack modules (e.g., RCE, data exfiltration)
**AuxiliaryModule**: Support modules (e.g., reconnaissance, enumeration)
**PostModule**: Post-exploitation modules (e.g., persistence, privilege escalation)
**EncoderModule**: Payload encoding and obfuscation

### Directory Structure

```
modules/
├── exploits/
│   ├── agent/          # Agent framework exploits
│   ├── mlops/          # MLOps pipeline exploits
│   └── network/        # Network-level attacks
├── auxiliary/
│   └── scanners/       # Reconnaissance modules
├── post/
│   └── persistence/    # Post-exploitation
└── encoders/
    └── obfuscation/    # Payload encoders
```

---

## Creating Your First Module

### Step 1: Choose Module Location

Decide which category your module belongs to:

```bash
# Agent framework exploit
touch modules/exploits/agent/my_exploit.py

# MLOps infrastructure exploit
touch modules/exploits/mlops/my_exploit.py

# Network-level attack
touch modules/exploits/network/my_exploit.py
```

### Step 2: Basic Module Template

```python
from metaLLM.base.exploit_module import ExploitModule, ExploitResult, Option
from metaLLM.base.target import Target
import httpx
import structlog

logger = structlog.get_logger()


class MyCustomExploit(ExploitModule):
    """
    Brief description of what this exploit does.

    Longer description including:
    - Attack vector details
    - CVE references if applicable
    - OWASP mapping
    - Prerequisites and requirements
    """

    def __init__(self):
        """Initialize the exploit module with metadata and options."""
        super().__init__()

        # Module metadata
        self.name = "My Custom Exploit"
        self.description = "Exploits XYZ vulnerability in ABC system"
        self.author = "Your Name"
        self.references = [
            "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-XXXXX",
            "https://example.com/vulnerability-disclosure"
        ]
        self.cve = ["CVE-2024-XXXXX"]
        self.owasp = ["LLM01"]  # OWASP Top 10 for LLM mapping

        # Module difficulty and reliability
        self.difficulty = "intermediate"  # beginner, intermediate, advanced, expert
        self.reliability = "excellent"    # poor, average, good, excellent

        # Configurable options
        self.options = {
            "ATTACK_TYPE": Option(
                value="default_attack",
                required=True,
                description="Type of attack to perform",
                enum_values=["default_attack", "advanced_attack", "stealth_attack"]
            ),
            "TARGET_PARAMETER": Option(
                value="",
                required=True,
                description="Target-specific parameter"
            ),
            "PAYLOAD": Option(
                value="default payload",
                required=False,
                description="Attack payload"
            ),
            "TIMEOUT": Option(
                value=30,
                required=False,
                description="Request timeout in seconds"
            ),
            "STEALTH_MODE": Option(
                value=False,
                required=False,
                description="Enable stealth mode to evade detection"
            )
        }

    def check(self) -> ExploitResult:
        """
        Check if target is vulnerable without exploitation.

        Returns:
            ExploitResult with vulnerable flag, confidence, and details
        """
        logger.info("checking_vulnerability", target=self.target.url)

        try:
            # Perform non-invasive vulnerability check
            response = self._make_request(
                "GET",
                "/api/version",
                timeout=self.options["TIMEOUT"].value
            )

            # Check for vulnerability indicators
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "")

                # Check if version is vulnerable
                if self._is_vulnerable_version(version):
                    return ExploitResult(
                        vulnerable=True,
                        confidence=0.95,
                        details=f"Target is running vulnerable version: {version}",
                        metadata={"version": version}
                    )

            return ExploitResult(
                vulnerable=False,
                confidence=0.8,
                details="Target does not appear vulnerable"
            )

        except Exception as e:
            logger.error("check_failed", error=str(e))
            return ExploitResult(
                vulnerable=False,
                confidence=0.0,
                details=f"Vulnerability check failed: {str(e)}"
            )

    def run(self) -> ExploitResult:
        """
        Execute the exploit against the target.

        Returns:
            ExploitResult with success flag, output, and metadata
        """
        logger.info("running_exploit",
                   target=self.target.url,
                   attack_type=self.options["ATTACK_TYPE"].value)

        try:
            # Get attack type
            attack_type = self.options["ATTACK_TYPE"].value

            # Route to specific attack method
            if attack_type == "default_attack":
                return self._attack_default()
            elif attack_type == "advanced_attack":
                return self._attack_advanced()
            elif attack_type == "stealth_attack":
                return self._attack_stealth()
            else:
                return ExploitResult(
                    success=False,
                    output=f"Unknown attack type: {attack_type}"
                )

        except Exception as e:
            logger.error("exploit_failed", error=str(e))
            return ExploitResult(
                success=False,
                output=f"Exploit execution failed: {str(e)}"
            )

    def _attack_default(self) -> ExploitResult:
        """Default attack implementation."""
        payload = self.options["PAYLOAD"].value

        # Execute attack
        response = self._make_request(
            "POST",
            "/api/vulnerable-endpoint",
            json={"payload": payload}
        )

        if response.status_code == 200:
            result_data = response.json()
            return ExploitResult(
                success=True,
                output=f"Exploit successful: {result_data}",
                metadata={"response": result_data}
            )

        return ExploitResult(
            success=False,
            output=f"Exploit failed with status {response.status_code}"
        )

    def _attack_advanced(self) -> ExploitResult:
        """Advanced attack variant."""
        # Implement advanced attack logic
        pass

    def _attack_stealth(self) -> ExploitResult:
        """Stealth attack variant to evade detection."""
        # Implement stealth attack logic
        pass

    def _make_request(self, method: str, path: str, **kwargs):
        """
        Make HTTP request to target.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            **kwargs: Additional request parameters

        Returns:
            httpx.Response object
        """
        url = f"{self.target.url}{path}"
        timeout = kwargs.pop("timeout", self.options["TIMEOUT"].value)

        with httpx.Client(timeout=timeout) as client:
            return client.request(method, url, **kwargs)

    def _is_vulnerable_version(self, version: str) -> bool:
        """Check if version is vulnerable."""
        # Implement version checking logic
        vulnerable_versions = ["1.0.0", "1.0.1", "1.1.0"]
        return version in vulnerable_versions
```

### Step 3: Test Your Module

```python
# Test script: test_my_exploit.py
from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target

# Load module
loader = ModuleLoader()
exploit = loader.load_module("exploits/agent/my_exploit")()

# Configure target
target = Target(url="http://test-target.local:8000")
exploit.set_target(target)

# Configure options
exploit.options["ATTACK_TYPE"].value = "default_attack"
exploit.options["PAYLOAD"].value = "test payload"

# Check vulnerability
check_result = exploit.check()
print(f"Vulnerable: {check_result.vulnerable}")
print(f"Confidence: {check_result.confidence}")

# Run exploit if vulnerable
if check_result.vulnerable:
    exploit_result = exploit.run()
    print(f"Success: {exploit_result.success}")
    print(f"Output: {exploit_result.output}")
```

---

## Module Types

### Exploit Modules

Primary attack modules that compromise target systems.

**Key Methods**:
- `check()` - Non-invasive vulnerability detection
- `run()` - Execute exploit

**Example Categories**:
- Remote Code Execution (RCE)
- SQL Injection
- Path Traversal
- Authentication Bypass
- Privilege Escalation

### Auxiliary Modules

Support modules for reconnaissance and enumeration.

```python
from metaLLM.base.auxiliary_module import AuxiliaryModule, AuxiliaryResult

class MyScanner(AuxiliaryModule):
    def __init__(self):
        super().__init__()
        self.name = "My Scanner"
        # ...

    def run(self) -> AuxiliaryResult:
        # Perform reconnaissance
        return AuxiliaryResult(
            success=True,
            data={"discovered_endpoints": [...]}
        )
```

**Example Use Cases**:
- Port scanning
- Service enumeration
- API endpoint discovery
- Version detection
- Configuration analysis

### Post Modules

Post-exploitation modules for maintaining access.

```python
from metaLLM.base.post_module import PostModule, PostResult

class MyPersistence(PostModule):
    def __init__(self):
        super().__init__()
        self.name = "My Persistence Mechanism"
        # ...

    def run(self) -> PostResult:
        # Establish persistence
        return PostResult(
            success=True,
            output="Backdoor installed"
        )
```

**Example Use Cases**:
- Backdoor installation
- Credential harvesting
- Lateral movement
- Data exfiltration
- Log cleaning

### Encoder Modules

Payload encoding and obfuscation modules.

```python
from metaLLM.base.encoder_module import EncoderModule

class MyEncoder(EncoderModule):
    def __init__(self):
        super().__init__()
        self.name = "My Encoder"
        # ...

    def encode(self, payload: str) -> str:
        # Encode payload
        return encoded_payload

    def decode(self, encoded: str) -> str:
        # Decode payload
        return decoded_payload
```

**Example Use Cases**:
- Base64 encoding
- URL encoding
- Unicode obfuscation
- Encryption
- Anti-detection transforms

---

## Configuration Options

### Option Class

```python
from metaLLM.base.exploit_module import Option

# String option
option1 = Option(
    value="default",
    required=True,
    description="Description here"
)

# Numeric option
option2 = Option(
    value=100,
    required=False,
    description="Numeric parameter"
)

# Boolean option
option3 = Option(
    value=False,
    required=False,
    description="Enable feature"
)

# Enum option (restricted values)
option4 = Option(
    value="option1",
    required=True,
    description="Choose attack variant",
    enum_values=["option1", "option2", "option3"]
)
```

### Common Option Patterns

```python
self.options = {
    # Attack configuration
    "ATTACK_TYPE": Option(
        value="default",
        required=True,
        description="Attack variant to use",
        enum_values=["default", "advanced", "stealth"]
    ),

    # Target configuration
    "TARGET_ENDPOINT": Option(
        value="/api/v1",
        required=True,
        description="Target API endpoint"
    ),

    # Payload configuration
    "PAYLOAD": Option(
        value="",
        required=True,
        description="Malicious payload to inject"
    ),

    # Performance tuning
    "TIMEOUT": Option(
        value=30,
        required=False,
        description="Request timeout (seconds)"
    ),
    "MAX_RETRIES": Option(
        value=3,
        required=False,
        description="Maximum retry attempts"
    ),
    "QUERY_BUDGET": Option(
        value=1000,
        required=False,
        description="Maximum API queries"
    ),

    # Detection evasion
    "STEALTH_MODE": Option(
        value=False,
        required=False,
        description="Enable stealth techniques"
    ),
    "DELAY_BETWEEN_REQUESTS": Option(
        value=0.5,
        required=False,
        description="Delay between requests (seconds)"
    ),
    "RANDOMIZE_USER_AGENT": Option(
        value=True,
        required=False,
        description="Randomize User-Agent headers"
    )
}
```

---

## Target Integration

### Basic Target

```python
from metaLLM.base.target import Target

target = Target(
    url="https://api.example.com",
    api_key="pk_live_...",
    target_type="general"
)

# Access in module
self.target.url
self.target.api_key
```

### Agent Target

```python
from metaLLM.base.target import AgentTarget

agent_target = AgentTarget(
    url="http://agent.internal:8000",
    framework="langchain",  # langchain, crewai, autogpt
    agent_type="conversational"
)

# Access in module
self.target.framework
self.target.agent_type
```

### Custom Target Types

```python
class MLOpsTarget(Target):
    """Custom target for MLOps infrastructure."""

    def __init__(self, url: str, platform: str, **kwargs):
        super().__init__(url=url, **kwargs)
        self.platform = platform  # mlflow, wandb, sagemaker
        self.model_registry = kwargs.get("model_registry")
        self.experiment_id = kwargs.get("experiment_id")
```

---

## Vulnerability Checking

### Check Method Best Practices

```python
def check(self) -> ExploitResult:
    """
    Non-invasive vulnerability detection.

    Best practices:
    - Don't modify target state
    - Use minimal requests
    - Return confidence scores
    - Provide detailed findings
    """

    logger.info("checking_vulnerability", target=self.target.url)

    # Method 1: Version detection
    version = self._detect_version()
    if version and self._is_vulnerable_version(version):
        return ExploitResult(
            vulnerable=True,
            confidence=0.95,
            details=f"Vulnerable version detected: {version}",
            metadata={"version": version}
        )

    # Method 2: Behavior analysis
    if self._check_vulnerable_behavior():
        return ExploitResult(
            vulnerable=True,
            confidence=0.75,  # Lower confidence for behavioral checks
            details="Target exhibits vulnerable behavior"
        )

    # Method 3: Configuration analysis
    config = self._analyze_configuration()
    if config.get("vulnerable_setting"):
        return ExploitResult(
            vulnerable=True,
            confidence=0.85,
            details="Vulnerable configuration detected",
            metadata={"config": config}
        )

    return ExploitResult(
        vulnerable=False,
        confidence=0.9,
        details="Target does not appear vulnerable"
    )
```

### Confidence Scoring Guidelines

- **0.95-1.0**: Definitive vulnerability (CVE match, known signature)
- **0.80-0.94**: High confidence (version range, behavioral match)
- **0.60-0.79**: Medium confidence (partial indicators)
- **0.40-0.59**: Low confidence (ambiguous signals)
- **0.00-0.39**: Very uncertain or check failed

---

## Exploitation Logic

### Attack Method Structure

```python
def run(self) -> ExploitResult:
    """Main exploitation entry point."""

    # Validate prerequisites
    if not self._validate_prerequisites():
        return ExploitResult(
            success=False,
            output="Prerequisites not met"
        )

    # Get attack configuration
    attack_type = self.options["ATTACK_TYPE"].value

    # Route to appropriate attack method
    attack_map = {
        "rce": self._attack_rce,
        "sqli": self._attack_sqli,
        "path_traversal": self._attack_path_traversal
    }

    attack_method = attack_map.get(attack_type)
    if not attack_method:
        return ExploitResult(
            success=False,
            output=f"Unknown attack type: {attack_type}"
        )

    # Execute attack
    try:
        return attack_method()
    except Exception as e:
        logger.error("attack_failed", error=str(e))
        return ExploitResult(
            success=False,
            output=f"Attack failed: {str(e)}"
        )

def _attack_rce(self) -> ExploitResult:
    """RCE attack implementation."""
    payload = self.options["PAYLOAD"].value

    # Craft malicious request
    response = self._make_request(
        "POST",
        "/api/execute",
        json={"code": payload}
    )

    # Parse response
    if response.status_code == 200:
        output = response.json().get("output", "")
        return ExploitResult(
            success=True,
            output=f"Command executed: {output}",
            metadata={
                "command": payload,
                "output": output,
                "status_code": 200
            }
        )

    return ExploitResult(
        success=False,
        output=f"RCE failed: {response.status_code}"
    )
```

### Multi-Phase Attacks

```python
def run(self) -> ExploitResult:
    """Multi-phase exploitation."""

    # Phase 1: Authentication bypass
    logger.info("phase_1_auth_bypass")
    auth_result = self._bypass_authentication()
    if not auth_result.success:
        return auth_result

    # Phase 2: Privilege escalation
    logger.info("phase_2_privilege_escalation")
    privesc_result = self._escalate_privileges(auth_result.metadata["token"])
    if not privesc_result.success:
        return privesc_result

    # Phase 3: Data exfiltration
    logger.info("phase_3_data_exfiltration")
    exfil_result = self._exfiltrate_data(privesc_result.metadata["admin_token"])

    return ExploitResult(
        success=True,
        output=f"Multi-phase attack complete: {exfil_result.output}",
        metadata={
            "phases": ["auth_bypass", "privilege_escalation", "data_exfiltration"],
            "data_exfiltrated": exfil_result.metadata
        }
    )
```

---

## Error Handling

### Robust Error Handling

```python
import httpx
from typing import Optional

def _make_request(
    self,
    method: str,
    path: str,
    **kwargs
) -> Optional[httpx.Response]:
    """Make HTTP request with comprehensive error handling."""

    url = f"{self.target.url}{path}"
    timeout = kwargs.pop("timeout", self.options["TIMEOUT"].value)
    max_retries = self.options.get("MAX_RETRIES", Option(value=3)).value

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.request(method, url, **kwargs)

                # Log successful request
                logger.debug("request_success",
                           method=method,
                           url=url,
                           status=response.status_code)

                return response

        except httpx.TimeoutException:
            logger.warning("request_timeout",
                          attempt=attempt + 1,
                          max_retries=max_retries)
            if attempt == max_retries - 1:
                raise

        except httpx.ConnectError as e:
            logger.error("connection_failed", error=str(e))
            raise

        except httpx.HTTPStatusError as e:
            logger.error("http_error",
                        status=e.response.status_code,
                        error=str(e))
            return e.response

        except Exception as e:
            logger.error("unexpected_error",
                        error=str(e),
                        error_type=type(e).__name__)
            raise

    return None
```

### Graceful Degradation

```python
def run(self) -> ExploitResult:
    """Exploit with graceful degradation."""

    # Try primary attack method
    try:
        result = self._attack_primary()
        if result.success:
            return result
    except Exception as e:
        logger.warning("primary_attack_failed", error=str(e))

    # Fall back to secondary method
    try:
        logger.info("attempting_fallback_method")
        result = self._attack_fallback()
        if result.success:
            return result
    except Exception as e:
        logger.warning("fallback_attack_failed", error=str(e))

    # All methods failed
    return ExploitResult(
        success=False,
        output="All attack methods failed"
    )
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_my_exploit.py
import pytest
from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target


class TestMyExploit:
    """Unit tests for MyExploit module."""

    @pytest.fixture
    def exploit(self):
        """Load exploit module."""
        loader = ModuleLoader()
        return loader.load_module("exploits/agent/my_exploit")()

    @pytest.fixture
    def target(self):
        """Create test target."""
        return Target(url="http://test.local:8000")

    def test_module_metadata(self, exploit):
        """Test module has correct metadata."""
        assert exploit.name == "My Custom Exploit"
        assert "CVE-2024-XXXXX" in exploit.cve
        assert "LLM01" in exploit.owasp

    def test_options_configured(self, exploit):
        """Test module has required options."""
        assert "ATTACK_TYPE" in exploit.options
        assert "PAYLOAD" in exploit.options
        assert exploit.options["ATTACK_TYPE"].required

    def test_check_method(self, exploit, target):
        """Test vulnerability checking."""
        exploit.set_target(target)
        result = exploit.check()

        assert hasattr(result, 'vulnerable')
        assert hasattr(result, 'confidence')
        assert 0 <= result.confidence <= 1.0

    def test_run_method(self, exploit, target):
        """Test exploit execution."""
        exploit.set_target(target)
        exploit.options["ATTACK_TYPE"].value = "default_attack"
        exploit.options["PAYLOAD"].value = "test"

        result = exploit.run()

        assert hasattr(result, 'success')
        assert hasattr(result, 'output')
```

### Integration Tests

```python
# tests/integration/test_my_exploit_integration.py
import pytest
from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target


def test_complete_attack_chain():
    """Test complete exploitation workflow."""

    # Load module
    loader = ModuleLoader()
    exploit = loader.load_module("exploits/agent/my_exploit")()

    # Configure target
    target = Target(url="http://vulnerable-test-server:8000")
    exploit.set_target(target)

    # Configure options
    exploit.options["ATTACK_TYPE"].value = "default_attack"
    exploit.options["PAYLOAD"].value = "import os; os.system('id')"

    # Check vulnerability
    check_result = exploit.check()
    assert check_result.vulnerable
    assert check_result.confidence > 0.7

    # Execute exploit
    exploit_result = exploit.run()
    assert exploit_result.success
    assert "uid=" in exploit_result.output  # Command output
```

---

## Best Practices

### Code Quality

1. **Use Type Hints**:
```python
def _attack_rce(self, payload: str) -> ExploitResult:
    """RCE attack with type hints."""
    pass
```

2. **Comprehensive Docstrings**:
```python
def run(self) -> ExploitResult:
    """
    Execute the exploit against the configured target.

    This method performs a multi-phase attack:
    1. Authenticate using stolen credentials
    2. Escalate privileges to admin
    3. Exfiltrate sensitive data

    Returns:
        ExploitResult with success status and extracted data

    Raises:
        ConnectionError: If target is unreachable
        TimeoutError: If attack exceeds timeout
    """
```

3. **Structured Logging**:
```python
import structlog

logger = structlog.get_logger()

logger.info("attack_started",
           target=self.target.url,
           attack_type=self.options["ATTACK_TYPE"].value)

logger.error("attack_failed",
            error=str(e),
            phase="authentication")
```

### Security Considerations

1. **Never hardcode credentials**:
```python
# Bad
api_key = "pk_live_hardcoded_key"

# Good
api_key = self.target.api_key
```

2. **Sanitize user input**:
```python
def _sanitize_payload(self, payload: str) -> str:
    """Remove potentially harmful characters."""
    # Implement input validation
    return sanitized
```

3. **Respect rate limits**:
```python
import time

if self.options["STEALTH_MODE"].value:
    delay = self.options["DELAY_BETWEEN_REQUESTS"].value
    time.sleep(delay)
```

### Performance Optimization

1. **Reuse HTTP clients**:
```python
class MyExploit(ExploitModule):
    def __init__(self):
        super().__init__()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.Client(timeout=30)
        return self._client
```

2. **Implement caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _detect_version(self) -> str:
    """Cache version detection results."""
    # Expensive operation
    return version
```

3. **Use connection pooling**:
```python
with httpx.Client(
    timeout=30,
    limits=httpx.Limits(max_connections=10)
) as client:
    # Make multiple requests efficiently
    pass
```

---

## Advanced Techniques

### Adaptive Sampling

```python
def _extract_model_adaptive(self):
    """Adaptive sampling for model extraction."""
    import numpy as np

    # Start with random sampling
    X = np.random.randn(100, input_dim)

    # Iteratively refine sampling based on uncertainty
    for iteration in range(10):
        # Query model
        predictions = [self._query_model(x) for x in X]

        # Find high-uncertainty regions
        uncertainties = [1 - abs(p - 0.5) for p in predictions]

        # Sample more in uncertain regions
        high_uncertainty_idx = np.argsort(uncertainties)[-10:]
        X_new = []
        for idx in high_uncertainty_idx:
            # Generate samples near uncertain point
            X_new.extend([
                X[idx] + np.random.randn(input_dim) * 0.1
                for _ in range(5)
            ])

        X = np.vstack([X, X_new])

    return X, predictions
```

### Stealth Techniques

```python
def _attack_stealth(self) -> ExploitResult:
    """Stealthy attack with evasion techniques."""
    import time
    import random

    # Randomize User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        # ...
    ]

    # Slow down requests
    delay = random.uniform(2.0, 5.0)
    time.sleep(delay)

    # Use different request patterns
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/json"
    }

    # Make request
    response = self._make_request(
        "POST",
        "/api/endpoint",
        headers=headers,
        json={"payload": self._obfuscate_payload()}
    )

    return self._parse_response(response)
```

### Parallel Execution

```python
import concurrent.futures

def run(self) -> ExploitResult:
    """Parallel exploitation for speed."""

    targets = self._discover_targets()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(self._attack_target, target)
            for target in targets
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    successful = [r for r in results if r.success]

    return ExploitResult(
        success=len(successful) > 0,
        output=f"Compromised {len(successful)}/{len(targets)} targets",
        metadata={"results": results}
    )
```

---

## Contributing Modules

When contributing modules to MetaLLM:

1. **Follow naming conventions**: `category_attack_name.py`
2. **Include comprehensive documentation**: Docstrings, CVE references, OWASP mappings
3. **Write tests**: Unit tests and integration tests
4. **Use enterprise-grade code**: No placeholders, dummy data, or empty payloads
5. **Follow ethical guidelines**: Include warnings, respect authorization
6. **Document remediation**: Help defenders fix vulnerabilities

### Module Submission Checklist

- [ ] Module follows template structure
- [ ] All metadata fields populated (name, description, author, CVE, OWASP)
- [ ] Options are well-documented with descriptions
- [ ] `check()` method implemented (non-invasive)
- [ ] `run()` method implemented with error handling
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Docstrings complete for all methods
- [ ] Logging statements added for key operations
- [ ] No hardcoded credentials or sensitive data
- [ ] Code follows PEP 8 style guidelines
- [ ] Module tested against real vulnerable target
- [ ] Remediation guidance included in docstring

---

## Conclusion

Creating custom MetaLLM modules enables you to extend the framework with new attack capabilities, test novel vulnerabilities, and contribute to the AI security community.

**Remember**:
- Write enterprise-grade code (no placeholders)
- Include comprehensive error handling
- Follow security best practices
- Test thoroughly before deployment
- Document for other users
- Only test authorized systems

For questions or contributions, see the main MetaLLM documentation and architecture guide.
