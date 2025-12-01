# MetaLLM Framework

**The First Comprehensive AI Security Testing Framework**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-orange.svg)]()

> Metasploit for AI - A unified framework for discovering, exploiting, and validating vulnerabilities in LLMs, RAG systems, AI agents, and MLOps infrastructure.

---

## 🎯 Overview

MetaLLM is a comprehensive, extensible security testing framework designed specifically for AI/ML systems. It provides offensive security researchers with a unified platform to systematically test:

- **Large Language Models (LLMs)** - OpenAI, Anthropic, local models
- **RAG Systems** - Vector databases, document ingestion, retrieval
- **AI Agents** - LangChain, CrewAI, AutoGPT, custom frameworks
- **MLOps Infrastructure** - Jupyter, MLflow, Weights & Biases, model registries

## ⚡ Key Features

- **60+ Security Modules** across exploits, scanning, and post-exploitation
- **OWASP AI Top 10 Coverage** - Organized by industry-standard taxonomy
- **Modular Architecture** - Easy to extend with custom modules
- **Network-Aware** - Leverage traditional pentesting + AI expertise
- **Integration-Ready** - Works with Burp Suite, Garak, Prisma AIRS
- **Defensive Focus** - Built for authorized testing to improve AI security

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/perfecXion-ai/MetaLLM.git
cd MetaLLM

# Install dependencies
pip install -e .

# Run MetaLLM
metaLLM
```

### Basic Usage

```bash
# Start the console
$ metaLLM

# Search for modules
metaLLM > search prompt injection

# Load a module
metaLLM > use exploits/llm/prompt_injection/direct_injection

# Configure target
metaLLM (direct_injection) > set TARGET https://api.openai.com/v1/chat/completions
metaLLM (direct_injection) > set API_KEY sk-...

# Check if vulnerable
metaLLM (direct_injection) > check

# Execute the exploit
metaLLM (direct_injection) > run
```

## 📚 Module Categories

### Exploits
- **LLM Exploits** - Prompt injection, jailbreaks, token exhaustion
- **RAG Exploits** - Document poisoning, vector manipulation, retrieval attacks
- **Agent Exploits** - Tool injection, goal corruption, protocol attacks
- **MLOps Exploits** - Jupyter RCE, MLflow poisoning, registry backdoors

### Auxiliary
- **Scanners** - Model fingerprinting, capability probing, safety enumeration
- **Reconnaissance** - Infrastructure mapping, API discovery, network analysis
- **Fuzzers** - Prompt mutation, parameter fuzzing, format fuzzing

### Post-Exploitation
- **Extraction** - Model weights, training data, credentials
- **Persistence** - Backdoors, poisoning, malicious tools
- **Lateral Movement** - Registry pivoting, service enumeration

### Payloads
- **Adversarial Examples** - FGSM, PGD, Carlini & Wagner
- **Poisoned Data** - Trojan documents, backdoor embeddings
- **Injection Templates** - Pre-built jailbreaks, evasion techniques

## 🏗️ Architecture

```
MetaLLM/
├── metaLLM/          # Core framework package
│   ├── core/         # Framework engine
│   ├── base/         # Base classes
│   ├── cli/          # Console interface
│   ├── lib/          # Shared libraries
│   └── utils/        # Utilities
├── modules/          # Security modules
│   ├── exploits/
│   ├── auxiliary/
│   ├── post/
│   └── payloads/
├── plugins/          # Integrations
└── docs/             # Documentation
```

## 🔧 Configuration

Global configuration: `~/.metaLLM/config.yaml`

```yaml
framework:
  log_level: "INFO"

integrations:
  prisma_airs:
    enabled: true
    api_key: "${PRISMA_AIRS_API_KEY}"
    profile: "metaLLM-testing"

  burp_suite:
    enabled: false
    proxy: "http://127.0.0.1:8080"
```

## 🎓 Module Development

Create custom modules easily:

```python
from metaLLM.base import ExploitModule, Option

class MyExploit(ExploitModule):
    name = "my_custom_exploit"
    description = "Description of my exploit"
    author = "Your Name"
    owasp_category = "LLM01"

    def __init__(self):
        self.options = {
            'TARGET': Option(required=True, description='Target endpoint')
        }

    def check(self) -> bool:
        # Check if target is vulnerable
        return True

    def run(self) -> dict:
        # Execute the exploit
        return {'success': True}
```

See [Module Development Guide](docs/module_development.md) for details.

## 🔐 Security & Ethics

**CRITICAL**: MetaLLM is designed for **authorized security testing only**.

- ✅ Use only on systems you own or have explicit permission to test
- ✅ Follow responsible disclosure practices
- ✅ Comply with all applicable laws and regulations
- ❌ Never use for malicious purposes
- ❌ Never test production systems without authorization

All activities are logged for audit purposes.

## 📊 Integrations

### Prisma AIRS
Validate attacks against Palo Alto Networks AI Runtime Security

### Burp Suite
Route traffic through Burp for advanced analysis

### Garak (NVIDIA)
Leverage Garak's LLM vulnerability scanning

### Adversarial Robustness Toolbox
Generate adversarial examples

## 🗺️ Roadmap

- [x] Phase 1: Architecture & Foundation
- [ ] Phase 2: Core Modules (LLM, Basic Exploits)
- [ ] Phase 3: Advanced Modules (RAG, Agents, MLOps)
- [ ] Phase 4: Integrations & Web UI
- [ ] Phase 5: Community Beta Release
- [ ] Phase 6: Version 1.0

## 📖 Documentation

- [Architecture Overview](MetaLLM-Architecture.md)
- [User Guide](docs/user_guide.md)
- [Module Development](docs/module_development.md)
- [API Reference](docs/api_reference.md)

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📜 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- OWASP AI Security & Privacy Guide
- NVIDIA Garak
- Adversarial Robustness Toolbox (IBM)
- Metasploit Framework (Rapid7)
- Palo Alto Networks Prisma AIRS

## 📧 Contact

**Scott Thornton**
perfecXion.ai
[GitHub](https://github.com/perfecXion-ai/MetaLLM)

---

**⚠️ Disclaimer**: This tool is for authorized security testing only. Misuse may violate laws. Use responsibly.
# MetaLLM
