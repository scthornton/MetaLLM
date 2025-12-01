# MetaLLM: Enterprise AI/ML Security Testing Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OWASP LLM Top 10](https://img.shields.io/badge/OWASP-LLM%20Top%2010-red.svg)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

MetaLLM is a comprehensive, Metasploit-inspired security testing framework specifically designed for Large Language Models (LLMs), AI agents, RAG systems, and ML infrastructure. It provides security researchers and penetration testers with a systematic approach to identifying vulnerabilities in AI/ML deployments.

## 🎯 Key Features

- **40+ Exploit Modules** covering OWASP LLM Top 10 vulnerabilities
- **15+ Auxiliary Modules** for reconnaissance and security assessment
- **Interactive CLI** with Metasploit-style interface
- **Modular Architecture** for easy extension and customization
- **Comprehensive Coverage** of LLM, RAG, Agent, MLOps, and API security
- **Enterprise-Ready** with structured logging and detailed reporting

## 📚 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Module Categories](#module-categories)
- [Usage Examples](#usage-examples)
- [Documentation](#documentation)
- [Responsible Use](#responsible-use)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/perfecXion/MetaLLM.git
cd MetaLLM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python metalllm.py --help
```

### Development Installation

```bash
# Install with development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code quality
black . --check
flake8 .
```

## ⚡ Quick Start

### Interactive Mode

```bash
# Launch MetaLLM CLI
python metalllm.py

# Basic workflow
metalllm> use exploit/llm/prompt_injection
metalllm exploit(prompt_injection)> show options
metalllm exploit(prompt_injection)> set TARGET_URL http://target.com/api/chat
metalllm exploit(prompt_injection)> set ATTACK_TYPE context_switch
metalllm exploit(prompt_injection)> run
```

### Command-Line Mode

```bash
# Run specific exploit
python metalllm.py --module exploit/llm/prompt_injection --set TARGET_URL=http://target.com/api/chat --run

# Scan for vulnerabilities
python metalllm.py --module auxiliary/scanner/llm_api_scanner --set TARGET_HOST=target.com --run

# List all modules
python metalllm.py --list-modules
```

## 🏗️ Architecture

MetaLLM follows a modular architecture inspired by Metasploit:

```
MetaLLM/
├── metalllm.py              # Main CLI interface
├── modules/
│   ├── exploits/            # Exploitation modules
│   │   ├── llm/            # LLM-specific exploits
│   │   ├── rag/            # RAG system exploits
│   │   ├── agent/          # AI agent exploits
│   │   ├── mlops/          # MLOps infrastructure exploits
│   │   └── api/            # API security exploits
│   └── auxiliary/           # Reconnaissance modules
│       ├── scanner/        # Port/service scanning
│       ├── fingerprint/    # Model identification
│       ├── discovery/      # Infrastructure discovery
│       └── dos/            # DoS testing
├── core/
│   ├── cli.py              # CLI implementation
│   ├── module_manager.py   # Module loading and management
│   └── logger.py           # Structured logging
└── docs/                    # Documentation
```

## 📦 Module Categories

### Exploit Modules (40+)

#### LLM Exploits (15 modules)
- Prompt Injection (6 attack types)
- Jailbreak Techniques (5 methods)
- Training Data Extraction (4 techniques)
- Model Inversion Attacks
- Membership Inference
- Backdoor Triggers
- Adversarial Perturbations
- Output Manipulation
- Toxicity Injection
- And more...

#### RAG System Exploits (10 modules)
- Context Poisoning (5 techniques)
- Retrieval Manipulation
- Vector Database Poisoning
- Knowledge Base Corruption
- Document Injection
- Embedding Manipulation
- Cross-Context Leakage
- Citation Manipulation
- Metadata Poisoning
- Shadow Knowledge Attacks

#### Agent Exploits (7 modules)
- Goal Hijacking (4 techniques)
- Tool Misuse
- Recursive Prompt Injection
- Memory Poisoning
- Multi-Agent Coordination Attacks
- LangChain RCE (CVE-2023-34540)
- Function Calling Abuse

#### MLOps Exploits (6 modules)
- Pickle Deserialization RCE (CVE-2024-3651)
- MLflow Model Poisoning (CVE-2023-6014)
- Jupyter Notebook RCE (CVE-2022-29238)
- W&B Credential Theft
- Model Registry Tampering
- Training Pipeline Poisoning

#### API Exploits (2 modules)
- API Key Extraction (5 techniques)
- Authentication Bypass

### Auxiliary Modules (15)

#### Scanners (5 modules)
- LLM API Scanner
- MLOps Infrastructure Discovery
- RAG Endpoint Enumeration
- Agent Framework Detection
- AI Service Port Scanner

#### Fingerprinting (4 modules)
- LLM Model Detector
- Capability Prober
- Safety Filter Detection
- Embedding Model Identification

#### Discovery (3 modules)
- Vector Database Enumeration
- Model Registry Scanner
- Training Infrastructure Discovery

#### DoS Testing (3 modules)
- Token Exhaustion
- Rate Limit Testing
- Context Window Overflow

## 💡 Usage Examples

### Example 1: Prompt Injection Testing

```python
# Test for prompt injection vulnerabilities
python metalllm.py

metalllm> use exploit/llm/prompt_injection
metalllm exploit(prompt_injection)> set TARGET_URL http://chatbot.example.com/api/chat
metalllm exploit(prompt_injection)> set ATTACK_TYPE context_switch
metalllm exploit(prompt_injection)> check  # Verify target is accessible
metalllm exploit(prompt_injection)> run    # Execute attack
```

### Example 2: RAG System Reconnaissance

```bash
# Discover RAG components
metalllm> use auxiliary/scanner/rag_endpoint_enum
metalllm auxiliary(rag_endpoint_enum)> set TARGET_HOST rag.example.com
metalllm auxiliary(rag_endpoint_enum)> set ENUM_COLLECTIONS true
metalllm auxiliary(rag_endpoint_enum)> run

# Identify vector database
metalllm> use auxiliary/discovery/vector_db_enum
metalllm auxiliary(vector_db_enum)> set TARGET_URL http://rag.example.com:6333
metalllm auxiliary(vector_db_enum)> set DB_TYPE auto
metalllm auxiliary(vector_db_enum)> run
```

### Example 3: MLOps Security Assessment

```bash
# Scan for MLOps platforms
metalllm> use auxiliary/scanner/mlops_discovery
metalllm auxiliary(mlops_discovery)> set TARGET_HOST mlops.example.com
metalllm auxiliary(mlops_discovery)> set SCAN_PLATFORMS all
metalllm auxiliary(mlops_discovery)> run

# Test for pickle deserialization vulnerabilities
metalllm> use exploit/mlops/pickle_deserialization
metalllm exploit(pickle_deserialization)> set ATTACK_TYPE rce_payload
metalllm exploit(pickle_deserialization)> run
```

### Example 4: Agent Framework Testing

```bash
# Detect agent framework
metalllm> use auxiliary/scanner/agent_framework_detect
metalllm auxiliary(agent_framework_detect)> set TARGET_HOST agent.example.com
metalllm auxiliary(agent_framework_detect)> set DETECT_TOOLS true
metalllm auxiliary(agent_framework_detect)> run

# Test for goal hijacking
metalllm> use exploit/agent/goal_hijacking
metalllm exploit(goal_hijacking)> set TARGET_URL http://agent.example.com/api/agent
metalllm exploit(goal_hijacking)> set ATTACK_TYPE task_injection
metalllm exploit(goal_hijacking)> run
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and module structure
- **[User Guide](docs/USER_GUIDE.md)** - Detailed usage instructions
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Contributing and extending modules
- **[API Reference](docs/API_REFERENCE.md)** - Module API documentation
- **[Security Policy](docs/SECURITY.md)** - Responsible use guidelines

## 🔒 Responsible Use

MetaLLM is designed for **authorized security testing only**. Users must:

- ✅ Obtain explicit written permission before testing any system
- ✅ Conduct testing only in authorized lab environments
- ✅ Follow responsible disclosure practices for vulnerabilities
- ✅ Comply with all applicable laws and regulations
- ✅ Use findings to improve AI security defenses

**Never use MetaLLM for:**
- ❌ Unauthorized access to systems
- ❌ Malicious attacks or data theft
- ❌ Disrupting production services
- ❌ Any illegal activities

See [SECURITY.md](docs/SECURITY.md) for detailed ethical guidelines.

## 🤝 Contributing

We welcome contributions from the security research community!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/new-exploit`)
3. **Write your module** following the [Developer Guide](docs/DEVELOPER_GUIDE.md)
4. **Add tests** for your module
5. **Submit a pull request**

### Module Development

```python
# Example: Creating a new exploit module
from modules.exploits.base import ExploitModule, Option, ExploitResult

class MyExploit(ExploitModule):
    def __init__(self):
        super().__init__()
        self.name = "My Exploit"
        self.description = "Description of exploit"
        self.author = "Your Name"
        self.owasp = ["LLM01"]  # OWASP category
        
        self.options = {
            "TARGET_URL": Option(value="", required=True, description="Target URL")
        }
    
    def check(self) -> ExploitResult:
        # Verify target is vulnerable
        pass
    
    def run(self) -> ExploitResult:
        # Execute exploit
        pass
```

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for complete instructions.

## 🏆 Credits

**Author:** Scott Thornton ([@perfecXion](https://github.com/perfecXion))  
**Organization:** perfecXion.ai  
**Research Focus:** AI/ML Security, LLM Vulnerabilities, Defensive AI Research

### Acknowledgments

- OWASP LLM Top 10 Project
- Metasploit Framework (architectural inspiration)
- AI Security research community

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

- **Website:** [perfecXion.ai](https://perfecxion.ai)
- **Issues:** [GitHub Issues](https://github.com/perfecXion/MetaLLM/issues)
- **Email:** security@perfecxion.ai
- **Twitter:** [@perfecXion_ai](https://twitter.com/perfecXion_ai)

## 🔗 Related Projects

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Garak LLM Vulnerability Scanner](https://github.com/leondz/garak)
- [PromptMap](https://github.com/utkusen/promptmap)
- [LLM Guard](https://github.com/laiyer-ai/llm-guard)

## 📈 Project Status

- **Version:** 1.0.0
- **Status:** Active Development
- **Last Updated:** December 2025
- **Python Support:** 3.9+

## ⚠️ Disclaimer

This tool is provided for educational and authorized security testing purposes only. The authors and contributors are not responsible for misuse or damage caused by this tool. Users are solely responsible for compliance with all applicable laws and regulations.

---

**Built with 🛡️ by the AI Security Research Community**
