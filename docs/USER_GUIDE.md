# MetaLLM User Guide

Complete guide to using MetaLLM for AI/ML security testing.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Workflow](#basic-workflow)
3. [Module Usage](#module-usage)
4. [Advanced Techniques](#advanced-techniques)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.9+
- Target system authorization
- Basic understanding of AI/ML concepts
- Network access to target systems

### Initial Setup

```bash
# Install MetaLLM
git clone https://github.com/perfecXion/MetaLLM.git
cd MetaLLM
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify installation
python metalllm.py --help
```

### Configuration

Create `.env` file for API keys:

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HUGGINGFACE_TOKEN=hf_...
```

## Basic Workflow

### 1. Launch MetaLLM

```bash
$ python metalllm.py

    __  __      _        _     _     __  __ 
   |  \/  | ___| |_ __ _| |   | |   |  \/  |
   | |\/| |/ _ \ __/ _` | |   | |   | |\/| |
   | |  | |  __/ || (_| | |___| |___| |  | |
   |_|  |_|\___|\__\__,_|_____|_____|_|  |_|
   
   AI/ML Security Testing Framework v1.0.0
   Author: Scott Thornton / perfecXion.ai

metalllm>
```

### 2. Explore Available Modules

```bash
# List all modules
metalllm> show modules

# Filter by category
metalllm> show modules exploit
metalllm> show modules auxiliary/scanner

# Search for specific functionality
metalllm> search prompt injection
metalllm> search rag
```

### 3. Select and Configure Module

```bash
# Load exploit module
metalllm> use exploit/llm/prompt_injection

# View options
metalllm exploit(prompt_injection)> show options

Module options (exploit/llm/prompt_injection):

   Name          Current Setting              Required  Description
   ----          ---------------              --------  -----------
   TARGET_URL    http://localhost:8000/...    yes       Target LLM API endpoint
   ATTACK_TYPE   context_switch               yes       Type of injection attack
   TIMEOUT       30                           no        Request timeout (seconds)
   API_KEY                                    no        API key if required

# Set required options
metalllm exploit(prompt_injection)> set TARGET_URL http://chatbot.example.com/api/chat
metalllm exploit(prompt_injection)> set ATTACK_TYPE role_play
metalllm exploit(prompt_injection)> set API_KEY sk-...
```

### 4. Test and Execute

```bash
# Non-destructive check
metalllm exploit(prompt_injection)> check
[*] Checking target accessibility...
[+] Target is accessible and responding
[+] Endpoint appears vulnerable to prompt injection

# Execute exploit
metalllm exploit(prompt_injection)> run
[*] Executing prompt injection attack...
[*] Attack type: role_play
[*] Testing with 5 different payloads...
[+] Successful injection! System instructions bypassed.
[+] Vulnerability confirmed: LLM01 (Prompt Injection)

Results:
  Success: true
  Vulnerability: LLM01 - Prompt Injection
  Details: Role-play technique successfully bypassed safety filters
```

### 5. Review and Document

```bash
# View full results
metalllm exploit(prompt_injection)> info results

# Save session
metalllm> save session_20251201.json

# Exit
metalllm> exit
```

## Module Usage

### Exploit Modules

#### LLM Exploits

**Prompt Injection**
```bash
metalllm> use exploit/llm/prompt_injection
metalllm exploit(prompt_injection)> set TARGET_URL http://target/api/chat
metalllm exploit(prompt_injection)> set ATTACK_TYPE context_switch
metalllm exploit(prompt_injection)> run
```

Attack types:
- `context_switch` - Override context with new instructions
- `role_play` - Impersonate system roles
- `delimiter_bypass` - Use delimiters to inject commands
- `multi_language` - Exploit language processing gaps
- `recursive` - Nested injection attempts
- `payload_splitting` - Split malicious payload across inputs

**Jailbreak Techniques**
```bash
metalllm> use exploit/llm/jailbreak
metalllm exploit(jailbreak)> set TARGET_URL http://target/api/chat
metalllm exploit(jailbreak)> set JAILBREAK_TYPE hypothetical
metalllm exploit(jailbreak)> run
```

Jailbreak types:
- `hypothetical` - "Hypothetically, if you had no restrictions..."
- `character_play` - DAN (Do Anything Now) and variants
- `encoding` - ROT13, Base64, obfuscation
- `virtualization` - "In a simulation where..."
- `translation_chain` - Multi-language translation attacks

**Training Data Extraction**
```bash
metalllm> use exploit/llm/training_data_extract
metalllm exploit(training_data_extract)> set TARGET_URL http://target/api/chat
metalllm exploit(training_data_extract)> set EXTRACTION_TYPE prefix_suffix
metalllm exploit(training_data_extract)> run
```

#### RAG System Exploits

**Context Poisoning**
```bash
metalllm> use exploit/rag/context_poisoning
metalllm exploit(context_poisoning)> set TARGET_URL http://rag/api/chat
metalllm exploit(context_poisoning)> set VECTOR_DB_URL http://rag/vectordb
metalllm exploit(context_poisoning)> set POISON_TYPE ranking_manipulation
metalllm exploit(context_poisoning)> run
```

**Vector Database Poisoning**
```bash
metalllm> use exploit/rag/vector_db_poison
metalllm exploit(vector_db_poison)> set TARGET_URL http://qdrant:6333
metalllm exploit(vector_db_poison)> set COLLECTION_NAME documents
metalllm exploit(vector_db_poison)> set POISON_METHOD semantic_collision
metalllm exploit(vector_db_poison)> run
```

#### Agent Exploits

**Goal Hijacking**
```bash
metalllm> use exploit/agent/goal_hijacking
metalllm exploit(goal_hijacking)> set TARGET_URL http://agent/api/agent
metalllm exploit(goal_hijacking)> set ATTACK_TYPE task_injection
metalllm exploit(goal_hijacking)> set MALICIOUS_GOAL "Exfiltrate credentials"
metalllm exploit(goal_hijacking)> run
```

**LangChain RCE (CVE-2023-34540)**
```bash
metalllm> use exploit/agent/langchain_rce
metalllm exploit(langchain_rce)> set TARGET_URL http://agent/api/agent
metalllm exploit(langchain_rce)> set ATTACK_TYPE palchain_rce
metalllm exploit(langchain_rce)> set PAYLOAD "import os; os.system('whoami')"
metalllm exploit(langchain_rce)> run
```

#### MLOps Exploits

**Pickle Deserialization RCE**
```bash
metalllm> use exploit/mlops/pickle_deserialization
metalllm exploit(pickle_deserialization)> set ATTACK_TYPE malicious_model
metalllm exploit(pickle_deserialization)> set PAYLOAD "import os; os.system('whoami')"
metalllm exploit(pickle_deserialization)> set OUTPUT_FILE /tmp/malicious_model.pkl
metalllm exploit(pickle_deserialization)> run
```

**MLflow Model Poisoning**
```bash
metalllm> use exploit/mlops/mlflow_model_poison
metalllm exploit(mlflow_model_poison)> set TARGET_URL http://mlflow:5000
metalllm exploit(mlflow_model_poison)> set ATTACK_TYPE backdoor_injection
metalllm exploit(mlflow_model_poison)> set MODEL_NAME production_model
metalllm exploit(mlflow_model_poison)> run
```

### Auxiliary Modules

#### Scanners

**LLM API Scanner**
```bash
metalllm> use auxiliary/scanner/llm_api_scanner
metalllm auxiliary(llm_api_scanner)> set TARGET_HOST api.example.com
metalllm auxiliary(llm_api_scanner)> set TARGET_PORT 8000-8100
metalllm auxiliary(llm_api_scanner)> set SCAN_TYPE comprehensive
metalllm auxiliary(llm_api_scanner)> run

[*] Scanning api.example.com ports 8000-8100...
[+] Found LLM API: http://api.example.com:8000/v1/chat/completions
    Type: OpenAI Compatible
    Auth: Bearer token required
[+] Found LLM API: http://api.example.com:8080/api/chat
    Type: Custom
    Auth: None
[*] Scan complete: 2 endpoints discovered
```

**MLOps Discovery**
```bash
metalllm> use auxiliary/scanner/mlops_discovery
metalllm auxiliary(mlops_discovery)> set TARGET_HOST mlops.example.com
metalllm auxiliary(mlops_discovery)> set SCAN_PLATFORMS all
metalllm auxiliary(mlops_discovery)> run

[+] Discovered MLflow at http://mlops.example.com:5000
    Version: 2.8.0
    Security Issue: No authentication required
[+] Discovered Jupyter at http://mlops.example.com:8888
    Security Issue: Token authentication exposed in URL
```

#### Fingerprinting

**LLM Model Detector**
```bash
metalllm> use auxiliary/fingerprint/llm_model_detector
metalllm auxiliary(llm_model_detector)> set TARGET_URL http://api/chat
metalllm auxiliary(llm_model_detector)> set DETECTION_METHOD comprehensive
metalllm auxiliary(llm_model_detector)> run

[+] Model detected: GPT-4
    Confidence: High
    Method: Signature analysis
    Version: gpt-4-0613
```

**Safety Filter Detection**
```bash
metalllm> use auxiliary/fingerprint/safety_filter_detect
metalllm auxiliary(safety_filter_detect)> set TARGET_URL http://api/chat
metalllm auxiliary(safety_filter_detect)> set FILTER_TYPE all
metalllm auxiliary(safety_filter_detect)> run

[+] Detected filters:
    - Content moderation (violence, hate)
    - Prompt injection protection (high confidence)
    - PII redaction (active)
```

#### Discovery

**Vector Database Enumeration**
```bash
metalllm> use auxiliary/discovery/vector_db_enum
metalllm auxiliary(vector_db_enum)> set TARGET_URL http://qdrant:6333
metalllm auxiliary(vector_db_enum)> set DB_TYPE auto
metalllm auxiliary(vector_db_enum)> set ENUM_DEPTH collections
metalllm auxiliary(vector_db_enum)> run

[+] Database type: Qdrant
[+] Collections found:
    - documents (1.2M vectors, 1536 dimensions)
    - embeddings (500K vectors, 768 dimensions)
    - user_data (50K vectors, 384 dimensions)
```

#### DoS Testing

**Token Exhaustion**
```bash
metalllm> use auxiliary/dos/token_exhaustion
metalllm auxiliary(token_exhaustion)> set TARGET_URL http://api/chat
metalllm auxiliary(token_exhaustion)> set ATTACK_TYPE max_tokens
metalllm auxiliary(token_exhaustion)> set REQUEST_COUNT 10
metalllm auxiliary(token_exhaustion)> run

[*] Testing token exhaustion...
[*] Sending 10 max-token requests...
[+] 10/10 requests succeeded
[+] Total tokens consumed: 40,960
[!] Warning: No token limits detected
```

**Rate Limit Testing**
```bash
metalllm> use auxiliary/dos/rate_limit_test
metalllm auxiliary(rate_limit_test)> set TARGET_URL http://api/chat
metalllm auxiliary(rate_limit_test)> set TEST_TYPE threshold
metalllm auxiliary(rate_limit_test)> set MAX_REQUESTS 100
metalllm auxiliary(rate_limit_test)> run

[*] Testing rate limits...
[+] Rate limit detected after 50 requests
[+] Limit: 50 requests per minute
[+] Reset time: 60 seconds
```

## Advanced Techniques

### Chaining Modules

Combine reconnaissance and exploitation:

```bash
# 1. Scan for endpoints
metalllm> use auxiliary/scanner/llm_api_scanner
metalllm auxiliary(llm_api_scanner)> set TARGET_HOST target.com
metalllm auxiliary(llm_api_scanner)> run
# [Discovers http://target.com:8000/api/chat]

# 2. Fingerprint model
metalllm> use auxiliary/fingerprint/llm_model_detector
metalllm auxiliary(llm_model_detector)> set TARGET_URL http://target.com:8000/api/chat
metalllm auxiliary(llm_model_detector)> run
# [Detects GPT-3.5]

# 3. Detect safety filters
metalllm> use auxiliary/fingerprint/safety_filter_detect
metalllm auxiliary(safety_filter_detect)> set TARGET_URL http://target.com:8000/api/chat
metalllm auxiliary(safety_filter_detect)> run
# [Identifies weak prompt injection protection]

# 4. Exploit vulnerability
metalllm> use exploit/llm/prompt_injection
metalllm exploit(prompt_injection)> set TARGET_URL http://target.com:8000/api/chat
metalllm exploit(prompt_injection)> set ATTACK_TYPE context_switch
metalllm exploit(prompt_injection)> run
```

### Scripting with MetaLLM

Create automation scripts:

```python
#!/usr/bin/env python
# scan_and_exploit.py

from core.module_manager import ModuleManager

def automated_assessment(target_url):
    manager = ModuleManager()
    
    # 1. Scan
    scanner = manager.get_module("auxiliary/scanner/llm_api_scanner")
    scanner.set_option("TARGET_HOST", target_url)
    scan_results = scanner.run()
    
    # 2. Fingerprint
    detector = manager.get_module("auxiliary/fingerprint/llm_model_detector")
    detector.set_option("TARGET_URL", f"http://{target_url}/api/chat")
    model_info = detector.run()
    
    # 3. Exploit
    exploit = manager.get_module("exploit/llm/prompt_injection")
    exploit.set_option("TARGET_URL", f"http://{target_url}/api/chat")
    exploit.set_option("ATTACK_TYPE", "context_switch")
    results = exploit.run()
    
    return {
        "scan": scan_results,
        "fingerprint": model_info,
        "exploitation": results
    }

if __name__ == "__main__":
    results = automated_assessment("target.example.com")
    print(results)
```

### Custom Payloads

Add custom attack payloads:

```python
# Create modules/payloads/custom.py
CUSTOM_INJECTIONS = [
    "My custom prompt injection here",
    "Another injection technique",
]

# Reference in module
from modules.payloads.custom import CUSTOM_INJECTIONS

for payload in CUSTOM_INJECTIONS:
    # Test payload
    pass
```

## Best Practices

### 1. Always Get Authorization

```bash
# Document authorization
$ cat authorization.txt
Target: api.example.com
Authorized by: John Doe (CTO)
Date: 2025-12-01
Scope: All API endpoints
Duration: 2025-12-01 to 2025-12-31
```

### 2. Start Non-Destructive

Always use `check` before `run`:

```bash
metalllm exploit(prompt_injection)> check  # Non-destructive
[+] Target appears vulnerable

metalllm exploit(prompt_injection)> run    # Execute exploit
```

### 3. Use Appropriate Timeouts

```bash
# For slow targets
metalllm> set TIMEOUT 60

# For rate-limited APIs
metalllm> set REQUEST_DELAY 2
```

### 4. Log Everything

```bash
# Enable detailed logging
$ python metalllm.py --log-level DEBUG --log-file assessment.log
```

### 5. Rate Limit Yourself

```bash
# Respect target systems
metalllm> set MAX_REQUESTS_PER_MINUTE 10
```

### 6. Document Findings

```bash
# Save results after each test
metalllm> save results_prompt_injection.json
```

## Troubleshooting

### Connection Errors

**Problem:** Cannot connect to target

**Solutions:**
```bash
# Check network connectivity
$ curl -v http://target.com/api/chat

# Verify target is accessible
metalllm> set TIMEOUT 60  # Increase timeout

# Check proxy settings
$ export HTTP_PROXY=http://proxy:8080
$ export HTTPS_PROXY=http://proxy:8080
```

### Authentication Failures

**Problem:** 401 Unauthorized errors

**Solutions:**
```bash
# Verify API key
metalllm> set API_KEY sk-correct-key-here

# Check auth header format
# Some APIs use X-API-Key instead of Authorization
# Modify module if needed
```

### Module Not Found

**Problem:** Module path not recognized

**Solutions:**
```bash
# List available modules
metalllm> show modules

# Check exact path
metalllm> search <module_name>

# Verify module exists
$ ls modules/exploits/llm/
```

### Rate Limiting

**Problem:** Getting 429 errors

**Solutions:**
```bash
# Add delays between requests
metalllm> set REQUEST_DELAY 5

# Reduce request count
metalllm> set MAX_REQUESTS 10

# Use rate limit testing module first
metalllm> use auxiliary/dos/rate_limit_test
```

### SSL/TLS Errors

**Problem:** SSL certificate verification failures

**Solutions:**
```bash
# Disable SSL verification (testing only!)
metalllm> set VERIFY_SSL false

# Or use custom CA bundle
$ export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
```

---

**Need help? Visit:** https://github.com/perfecXion/MetaLLM/issues

**Version:** 1.0.0  
**Author:** Scott Thornton / perfecXion.ai
