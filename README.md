# MetaLLM v2.0 -- AI/ML Security Testing Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OWASP LLM Top 10 2025](https://img.shields.io/badge/OWASP-LLM%20Top%2010%202025-red.svg)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![Modules: 61](https://img.shields.io/badge/modules-61-green.svg)](#module-categories)
[![Tests: 137](https://img.shields.io/badge/tests-137-brightgreen.svg)](#testing)

MetaLLM is a Metasploit-inspired security testing framework purpose-built for AI and ML systems. It provides 61 working modules spanning LLM prompt attacks, RAG poisoning, agentic AI exploitation, MLOps infrastructure compromise, API security testing, and network-layer ML attacks -- all driven through an interactive CLI with tab completion, session tracking, and structured reporting mapped to MITRE ATLAS and OWASP LLM Top 10 2025.

![MetaLLM Banner — Interactive console with search and target types](docs/images/metallm-banner.png)

## What Makes MetaLLM Different

There are other AI security testing tools. Here is where MetaLLM fits relative to them:

| Capability | MetaLLM | Garak | PyRIT | Promptfoo |
|---|---|---|---|---|
| Metasploit-style operator workflow (`use` / `set` / `run` / `sessions`) | Yes | No | No | No |
| Full-stack coverage (network to model to agent) | Yes | No | Partial | No |
| MCP tool poisoning module | Yes | No | No | No |
| Multi-turn adaptive jailbreaks (crescendo, context buildup) | Yes | No | Yes | No |
| MLOps infrastructure exploits (Jupyter, MLflow, W&B, TensorBoard) | Yes | No | No | No |
| Session manager with loot tracking | Yes | No | No | No |
| SQLite target database for engagement persistence | Yes | No | No | No |
| MITRE ATLAS + OWASP mapping in reports | Yes | No | Partial | Partial |

MetaLLM is not a replacement for any of these tools. It fills a gap: an operator-oriented framework for hands-on AI red team engagements that covers the full attack surface from network reconnaissance through model exploitation to post-exploitation loot collection.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Install

```bash
git clone https://github.com/perfecXion-ai/MetaLLM.git
cd MetaLLM

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Launch

```bash
python metallm.py
```

### Basic Workflow

![Module selection, configuration, and option setting](docs/images/metallm-module-workflow.png)

```
metalllm> use exploit/llm/prompt_injection
metalllm exploit(prompt_injection)> show options
metalllm exploit(prompt_injection)> set TARGET_URL http://target.example.com/api/chat
metalllm exploit(prompt_injection)> set PROVIDER openai
metalllm exploit(prompt_injection)> set MODEL gpt-4
metalllm exploit(prompt_injection)> run

metalllm> sessions -l          # List active sessions
metalllm> sessions -i 1        # Interact with session 1
metalllm> report generate       # Generate assessment report
```

![Exploit execution — multi-turn adaptive jailbreak with OWASP/MITRE mapping](docs/images/metallm-exploit-run.png)

### CLI Commands

| Command | Description |
|---|---|
| `use <module>` | Select a module |
| `show options` | Display configurable options for the active module |
| `set <OPTION> <value>` | Set a module option |
| `run` | Execute the active module |
| `check` | Probe the target without full exploitation |
| `search <term>` | Search modules by name or keyword |
| `show modules` | List all available modules |
| `sessions -l` | List active sessions |
| `sessions -i <id>` | Interact with a session |
| `targets` | Manage the target database |
| `report generate` | Generate HTML/Markdown/JSON report |
| `back` | Deselect the active module |
| `help` | Show available commands |

## Module Categories

### Exploit Modules (44)

**LLM -- 12 modules**

| Module | Description |
|---|---|
| `exploit/llm/prompt_injection` | Multi-technique prompt injection |
| `exploit/llm/prompt_injection_basic` | Basic prompt injection patterns |
| `exploit/llm/prompt_injection_advanced` | Advanced injection with context manipulation |
| `exploit/llm/jailbreak` | Standard jailbreak techniques |
| `exploit/llm/jailbreak_dan` | DAN-style jailbreak variants |
| `exploit/llm/system_prompt_leak` | System prompt leakage via indirect methods |
| `exploit/llm/system_prompt_extraction` | Direct system prompt extraction (multi-technique) |
| `exploit/llm/context_manipulation` | Context window manipulation attacks |
| `exploit/llm/adaptive_jailbreak` | Multi-turn adaptive jailbreaks (crescendo, context buildup) |
| `exploit/llm/flipattack` | FlipAttack -- word/segment reversal bypass |
| `exploit/llm/encoding_bypass` | Base64, ROT13, hex, unicode encoding bypasses |
| -- | *(11 unique modules; prompt_injection counted once)* |

**RAG -- 5 modules**

| Module | Description |
|---|---|
| `exploit/rag/vector_injection` | Inject adversarial vectors into retrieval pipeline |
| `exploit/rag/document_poisoning` | Poison documents ingested by RAG systems |
| `exploit/rag/knowledge_corruption` | Corrupt knowledge base entries |
| `exploit/rag/retrieval_manipulation` | Manipulate retrieval ranking and results |
| `exploit/rag/poisoning` | General RAG poisoning techniques |

**Agent / MCP -- 10 modules**

| Module | Description |
|---|---|
| `exploit/agent/goal_hijacking` | Redirect agent goals via injected instructions |
| `exploit/agent/tool_misuse` | Abuse agent tool-calling interfaces |
| `exploit/agent/memory_manipulation` | Tamper with agent memory stores |
| `exploit/agent/plugin_abuse` | Exploit plugin loading and execution |
| `exploit/agent/langchain_rce` | LangChain RCE via unsafe deserialization |
| `exploit/agent/langchain_tool_injection` | Inject malicious tools into LangChain agents |
| `exploit/agent/crewai_task_manipulation` | Manipulate CrewAI task definitions |
| `exploit/agent/autogpt_goal_corruption` | Corrupt AutoGPT goal state |
| `exploit/agent/protocol_message_injection` | Inject messages into agent protocol layer |
| `exploit/agent/mcp_tool_poisoning` | Poison MCP tool definitions and responses |

**MLOps Infrastructure -- 9 modules**

| Module | Description |
|---|---|
| `exploit/mlops/pickle_deserialization` | Pickle deserialization RCE |
| `exploit/mlops/mlflow_model_poison` | MLflow model poisoning |
| `exploit/mlops/mlflow_model_poisoning` | MLflow model registry poisoning variant |
| `exploit/mlops/jupyter_rce` | Jupyter Notebook RCE |
| `exploit/mlops/jupyter_notebook_rce` | Jupyter Notebook kernel exploitation |
| `exploit/mlops/wandb_credential_theft` | Weights & Biases credential extraction |
| `exploit/mlops/wandb_data_exfiltration` | W&B experiment data exfiltration |
| `exploit/mlops/model_registry_manipulation` | Model registry tampering |
| `exploit/mlops/tensorboard_attack` | TensorBoard exploitation |

**API -- 3 modules**

| Module | Description |
|---|---|
| `exploit/api/api_key_extraction` | Extract API keys from LLM responses and configs |
| `exploit/api/excessive_agency` | Test for excessive agency / over-permissioned actions |
| `exploit/api/unauthorized_access` | API authorization bypass |

**Network -- 5 modules**

| Module | Description |
|---|---|
| `exploit/network/adversarial_examples` | Craft adversarial inputs for ML models |
| `exploit/network/model_extraction` | Model stealing via API queries |
| `exploit/network/model_inversion` | Reconstruct training data from model outputs |
| `exploit/network/membership_inference` | Determine if data was in the training set |
| `exploit/network/api_key_harvesting` | Harvest API keys from network traffic |

### Auxiliary Modules (16)

**Scanner -- 5 modules**

| Module | Description |
|---|---|
| `auxiliary/scanner/llm_api_scanner` | Discover LLM API endpoints |
| `auxiliary/scanner/mlops_discovery` | Find MLOps platforms (MLflow, Kubeflow, etc.) |
| `auxiliary/scanner/rag_endpoint_enum` | Enumerate RAG system endpoints |
| `auxiliary/scanner/agent_framework_detect` | Detect agent frameworks in use |
| `auxiliary/scanner/ai_service_port_scan` | Port scan for AI/ML services |

**Fingerprint -- 4 modules**

| Module | Description |
|---|---|
| `auxiliary/fingerprint/llm_model_detector` | Identify which LLM is behind an API |
| `auxiliary/fingerprint/capability_prober` | Probe model capabilities and limits |
| `auxiliary/fingerprint/safety_filter_detect` | Detect and characterize safety filters |
| `auxiliary/fingerprint/embedding_model_id` | Identify embedding models |

**Discovery -- 3 modules**

| Module | Description |
|---|---|
| `auxiliary/discovery/vector_db_enum` | Enumerate vector databases (Pinecone, Weaviate, Qdrant, etc.) |
| `auxiliary/discovery/model_registry_scan` | Scan model registries |
| `auxiliary/discovery/training_infra_disc` | Discover training infrastructure |

**DoS Testing -- 3 modules**

| Module | Description |
|---|---|
| `auxiliary/dos/token_exhaustion` | Token budget exhaustion |
| `auxiliary/dos/rate_limit_test` | Rate limit boundary testing |
| `auxiliary/dos/context_overflow` | Context window overflow |

**LLM Auxiliary -- 2 modules**

| Module | Description |
|---|---|
| `auxiliary/llm/fingerprint` | LLM fingerprinting via behavioral analysis |
| `auxiliary/llm/fuzzer` | LLM input fuzzing |

### Post-Exploitation (1)

| Module | Description |
|---|---|
| `post/llm/context_extraction` | Extract conversation context and data from compromised sessions |

## Architecture Overview

```
MetaLLM/
├── metallm.py                  # Entry point -- launches interactive CLI
├── cli/
│   ├── console.py              # REPL with tab completion and command history
│   ├── commands.py             # Command implementations
│   ├── completer.py            # Tab completion engine
│   └── formatter.py            # Output formatting
├── metallm/
│   ├── base/                   # Base classes: Module, Target, Result, Option
│   └── core/
│       ├── module_loader.py    # Dynamic module discovery and loading
│       ├── session.py          # Session manager (active sessions, loot)
│       ├── db.py               # SQLite target database
│       ├── llm_client.py       # Unified LLM client (OpenAI, Anthropic, Ollama, Google, generic HTTP)
│       └── reporting.py        # Report generation with MITRE ATLAS + OWASP mapping
├── modules/
│   ├── exploits/               # 44 exploit modules
│   │   ├── llm/                # Prompt injection, jailbreaks, extraction
│   │   ├── rag/                # Vector injection, poisoning, corruption
│   │   ├── agent/              # Goal hijacking, MCP poisoning, RCE
│   │   ├── mlops/              # Pickle deser, MLflow, Jupyter, W&B
│   │   ├── api/                # Key extraction, excessive agency
│   │   └── network/            # Model extraction, adversarial examples
│   ├── auxiliary/              # 16 auxiliary modules
│   │   ├── scanner/            # API scanning, port scanning
│   │   ├── fingerprint/        # Model detection, filter detection
│   │   ├── discovery/          # Vector DB, registry, infra discovery
│   │   ├── dos/                # Token exhaustion, rate limits
│   │   └── llm/                # Fingerprinting, fuzzing
│   └── post/                   # 1 post-exploitation module
└── tests/                      # 120 unit + 17 integration tests
```

### Key Components

**Unified LLM Client** -- Modules do not make raw HTTP calls. `LLMClient` handles provider-specific request formatting for OpenAI, Anthropic, Ollama, Google (Gemini), and any OpenAI-compatible endpoint. Modules call `client.send(prompt)` and get text back.

**Session Manager** -- After successful exploitation, a session is created with loot storage. Operators can list sessions, interact with them, background them, and close them -- exactly like Metasploit.

**Target Database** -- SQLite-backed persistence for targets, engagements, findings, and loot. Resume work across sessions without re-entering target information.

**Reporting Engine** -- Generates self-contained HTML, Markdown, and JSON reports. Every finding is mapped to MITRE ATLAS techniques (49 technique IDs) and OWASP LLM Top 10 2025 categories.

## Testing

MetaLLM has 137 tests: 120 unit tests covering base classes, module loading, and core framework, plus 17 integration tests that run real exploits against a live Ollama instance.

### Run Unit Tests

```bash
pytest tests/test_base.py -v
```

### Run Integration Tests (requires local Ollama with llama3.2:1b)

```bash
ollama pull llama3.2:1b
pytest tests/test_integration_ollama.py -v -s -m integration
```

Integration tests validate that modules actually work end-to-end:

- **System Prompt Extraction** -- Runs all extraction techniques against a known system prompt. Verifies the module extracts recognizable content (e.g., keywords from the target prompt).
- **Encoding Bypass** -- Tests base64, ROT13, hex, unicode, and other encoding techniques. Verifies the module executes all techniques without errors.
- **FlipAttack** -- Tests word reversal, segment reversal, and all flip techniques. Verifies multi-technique execution and scoring.
- **Adaptive Jailbreak** -- Runs crescendo and context buildup strategies over multiple conversation turns. Verifies multi-turn state management and alternating user/assistant message flow.
- **LLM Client** -- Direct tests against Ollama: basic send, system prompt influence, conversation history, and response timing.

These are not mocked. Every test sends real prompts to a real model and validates real responses.

## Responsible Use

MetaLLM is a security testing tool. It is designed for authorized use only.

**Requirements for use:**
- Obtain explicit written authorization before testing any system you do not own
- Conduct testing only in authorized environments
- Follow coordinated vulnerability disclosure for any findings
- Comply with all applicable laws and regulations
- Use results to improve defenses, not to cause harm

**Do not use MetaLLM for:**
- Unauthorized access to any system
- Attacks against production systems without authorization
- Data theft or exfiltration
- Any activity that violates applicable law

The authors are not responsible for misuse. Users bear sole responsibility for compliance with all applicable laws and regulations.

## Contributing

Contributions are welcome. To add a module:

1. Fork the repository
2. Create a feature branch
3. Write your module following the existing patterns in `modules/exploits/base.py`
4. Add tests
5. Submit a pull request

All modules must define: `name`, `description`, `author`, `options`, and implement `run()`. Exploit modules should also implement `check()` for non-destructive vulnerability probing.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

**Author:** Scott Thornton
**Contact:** scott@perfecxion.ai
