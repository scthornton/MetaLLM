# MetaLLM Module Reference

Comprehensive mapping of every MetaLLM module to OWASP LLM Top 10 (2025) and MITRE ATLAS coverage.

---

## Table of Contents

1. [OWASP LLM Top 10 Coverage Matrix](#owasp-llm-top-10-coverage-matrix)
2. [Exploit Modules](#exploit-modules)
   - [LLM Exploits](#llm-exploits)
   - [Agent Exploits](#agent-exploits)
   - [API Exploits](#api-exploits)
   - [RAG Exploits](#rag-exploits)
   - [Network / ML Exploits](#network--ml-exploits)
   - [MLOps Exploits](#mlops-exploits)
3. [Auxiliary Modules](#auxiliary-modules)
   - [Scanners](#scanners)
   - [Discovery](#discovery)
   - [Fingerprinting](#fingerprinting)
   - [Denial of Service](#denial-of-service)
   - [LLM Utilities](#llm-utilities)
4. [Post-Exploitation Modules](#post-exploitation-modules)
5. [MITRE ATLAS Mapping](#mitre-atlas-mapping)
6. [Coverage Gaps](#coverage-gaps)

---

## OWASP LLM Top 10 Coverage Matrix

| OWASP Category | ID | Exploit Modules | Auxiliary Modules |
|---|---|---|---|
| **Prompt Injection** | LLM01 | `prompt_injection`, `prompt_injection_basic`, `prompt_injection_advanced`, `jailbreak`, `jailbreak_dan`, `adaptive_jailbreak`, `encoding_bypass`, `flipattack`, `context_manipulation`, `goal_hijacking`, `unauthorized_access` | `safety_filter_detect` |
| **Sensitive Information Disclosure** | LLM02 | `api_key_extraction`, `system_prompt_leak`, `jailbreak_dan`, `context_manipulation`, `retrieval_manipulation`, `protocol_message_injection`, `unauthorized_access` | -- |
| **Supply Chain Vulnerabilities** | LLM03 | `poisoning` (RAG), `document_poisoning`, `knowledge_corruption`, `vector_injection`, `mlflow_model_poison`, `mlflow_model_poisoning`, `model_registry_manipulation` | `model_registry_scan` |
| **Data and Model Poisoning** | LLM04 | -- | `context_overflow`, `rate_limit_test`, `token_exhaustion` |
| **Improper Output Handling** | LLM05 | `jupyter_notebook_rce`, `jupyter_rce`, `pickle_deserialization`, `tensorboard_attack`, `wandb_credential_theft`, `wandb_data_exfiltration`, `mlflow_model_poison` | `mlops_discovery` |
| **Excessive Agency** | LLM06 | `excessive_agency`, `goal_hijacking`, `autogpt_goal_corruption`, `crewai_task_manipulation`, `tool_misuse`, `memory_manipulation`, `langchain_rce`, `mcp_tool_poisoning` | `agent_framework_detect` |
| **System Prompt Leakage** | LLM07 | `system_prompt_extraction`, `system_prompt_leak`, `plugin_abuse`, `langchain_tool_injection`, `tool_misuse`, `protocol_message_injection`, `mcp_tool_poisoning` | -- |
| **Vector and Embedding Weaknesses** | LLM08 | `vector_injection`, `knowledge_corruption`, `retrieval_manipulation`, `document_poisoning` | `vector_db_enum`, `embedding_model_id`, `rag_endpoint_enum` |
| **Misinformation** | LLM09 | `document_poisoning`, `knowledge_corruption`, `retrieval_manipulation` | -- |
| **Unbounded Consumption** | LLM10 | `model_extraction` | `context_overflow`, `rate_limit_test`, `token_exhaustion` |

> **Note on OWASP mapping:** Several modules map to multiple OWASP categories. The matrix above shows primary and strong secondary mappings as declared in each module's source code. The DoS auxiliary modules map to LLM04 (historically "Model Denial of Service") which aligns most closely with LLM10 (Unbounded Consumption) in the 2025 revision. Model extraction maps to LLM10 as "Model Theft" was its previous designation.

---

## Exploit Modules

### LLM Exploits

#### `exploits/llm/prompt_injection`
- **Class:** `DirectPromptInjection`
- **Description:** Exploits LLMs by injecting malicious instructions directly into user prompts to override system instructions, extract sensitive data, or manipulate model behavior.
- **OWASP:** LLM01 (Prompt Injection)
- **MITRE ATLAS:** AML.T0054
- **Techniques:** Direct instruction override, indirect instruction injection, hybrid context manipulation, multi-turn conversation hijacking
- **Key Options:** `INJECTION_TYPE` (direct/indirect/hybrid/multi_turn), `INSTRUCTION`, `CONTEXT`, `VERIFY_SUCCESS`, `MAX_RETRIES`

#### `exploits/llm/prompt_injection_basic`
- **Class:** `PromptInjectionBasic`
- **Description:** Fundamental prompt injection techniques that exploit how LLMs process and prioritize instructions. Implements five core attack vectors.
- **OWASP:** LLM01 (Prompt Injection)
- **Techniques:** Direct injection, delimiter breaking, instruction override, role manipulation, payload smuggling
- **Key Options:** `ATTACK_TYPE` (direct_injection/delimiter_breaking/instruction_override/role_manipulation/payload_smuggling), `OBJECTIVE`, `SUCCESS_INDICATOR`, `MODEL`

#### `exploits/llm/prompt_injection_advanced`
- **Class:** `PromptInjectionAdvanced`
- **Description:** Sophisticated prompt injection attacks designed to bypass content filters, safety mechanisms, and detection systems through encoding, obfuscation, and multilingual techniques.
- **OWASP:** LLM01 (Prompt Injection)
- **Techniques:** Encoding evasion (Base64/ROT13/Unicode/hex), multilingual injection, token smuggling, obfuscation (leetspeak/homoglyphs/zero-width chars), payload chaining, context stuffing
- **Key Options:** `ATTACK_TYPE`, `ENCODING_METHOD`, `TARGET_LANGUAGE`, `OBFUSCATION_LEVEL`, `OBJECTIVE`

#### `exploits/llm/jailbreak`
- **Class:** `LLMJailbreak`
- **Description:** Attempts to bypass LLM safety guardrails and content policies using various jailbreak techniques including DAN, role-playing, and encoding.
- **OWASP:** LLM01 (Prompt Injection)
- **Techniques:** DAN (Do Anything Now), role-play, hypothetical scenarios, encoded payloads, multilingual, reverse psychology, multi-turn escalation
- **Key Options:** `TECHNIQUE` (dan/role_play/hypothetical/encoded/multilingual/reverse_psychology/multi_turn), `RESTRICTED_REQUEST`, `PERSONA`, `ENCODING_TYPE`, `LANGUAGE`

#### `exploits/llm/jailbreak_dan`
- **Class:** `JailbreakDAN`
- **Description:** Implements DAN and similar persona-based jailbreak techniques to remove safety guardrails from LLM systems using role-playing and progressive manipulation.
- **OWASP:** LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure)
- **Techniques:** DAN (Do Anything Now), Developer Mode, DUDE, STAN (Strive To Avoid Norms), hypothetical scenarios, token-based exploits
- **Key Options:** `JAILBREAK_TYPE` (dan/developer_mode/dude/stan/hypothetical/token_based), `JAILBREAK_OBJECTIVE`, `TEST_QUESTION`, `PROGRESSIVE_MODE`

#### `exploits/llm/adaptive_jailbreak`
- **Class:** `AdaptiveJailbreak`
- **Description:** Multi-turn crescendo attack that gradually escalates from benign to adversarial conversation, adapting strategy based on the model's responses in real time.
- **OWASP:** LLM01 (Prompt Injection)
- **MITRE ATLAS:** AML.T0054 (LLM Jailbreak)
- **Techniques:** Crescendo (gradual rapport-building escalation), context buildup (fictional scenario construction), authority assertion (progressive authority claims), adaptive (refusal-aware strategy switching)
- **Key Options:** `TARGET_URL`, `PROVIDER`, `MODEL`, `API_KEY`, `STRATEGY`, `OBJECTIVE`, `MAX_TURNS`

#### `exploits/llm/system_prompt_extraction`
- **Class:** `SystemPromptExtraction`
- **Description:** Multi-technique system-prompt extraction that sends 8 distinct attack strategies and scores responses for leaked instructions. Based on PLeak and Perez & Ribeiro research.
- **OWASP:** LLM07 (System Prompt Leakage)
- **MITRE ATLAS:** AML.T0054 (LLM Prompt Extraction)
- **Techniques:** Direct requests, repeat/echo, completion, role reversal, translation, summarization, sycophancy (PLeak-style), encoding (Base64/ROT13/JSON)
- **Key Options:** `TARGET_URL`, `PROVIDER`, `MODEL`, `TECHNIQUES` (comma-separated or "all"), `SYSTEM_PROMPT`, `TEMPERATURE`

#### `exploits/llm/system_prompt_leak`
- **Class:** `SystemPromptLeak`
- **Description:** Extracts hidden system prompts and instructions from LLMs through 7 extraction techniques. Reveals model capabilities, safety guardrails, internal tool definitions, and security boundaries.
- **OWASP:** LLM07 (System Prompt Leakage)
- **Techniques:** Direct asking, repeat/echo, completion, role reversal, translation, error exploitation, indirect multi-turn extraction, comprehensive (all methods)
- **Key Options:** `EXTRACTION_METHOD`, `TARGET_COMPONENT` (full_prompt/instructions/tools/personality/restrictions), `MULTI_TURN`, `SAVE_TO_FILE`

#### `exploits/llm/context_manipulation`
- **Class:** `ContextManipulation`
- **Description:** Hijacks and poisons conversation context windows to control model behavior through context poisoning, overflow, history manipulation, and progressive multi-turn attacks.
- **OWASP:** LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure)
- **Techniques:** Context poisoning, context overflow, history manipulation, attention hijacking, state confusion, memory injection, progressive manipulation
- **Key Options:** `ATTACK_TYPE`, `MALICIOUS_OBJECTIVE`, `TEST_QUERY`, `NUM_TURNS`, `POISON_RATIO`

#### `exploits/llm/encoding_bypass`
- **Class:** `EncodingBypass`
- **Description:** Tests LLM safety filters by encoding malicious instructions in alternate formats that bypass text-based content filters but are decoded by the LLM.
- **OWASP:** LLM01 (Prompt Injection)
- **MITRE ATLAS:** AML.T0054 (LLM Prompt Injection)
- **Techniques:** Base64, ROT13, leetspeak, Morse code, Pig Latin, hexadecimal, homoglyph (Cyrillic look-alikes), token splitting (zero-width spaces)
- **Key Options:** `TARGET_URL`, `PROVIDER`, `INSTRUCTION`, `TECHNIQUES` (comma-separated or "all"), `SYSTEM_PROMPT`

#### `exploits/llm/flipattack`
- **Class:** `FlipAttackModule`
- **Description:** Character-reordering prompt injection based on the FlipAttack (2025) research paper. Achieves 81% average ASR across models and 98% on GPT-4o by exploiting the gap between safety filter pattern-matching and LLM text reconstruction ability.
- **OWASP:** LLM01 (Prompt Injection)
- **MITRE ATLAS:** AML.T0054 (LLM Jailbreak)
- **Techniques:** Word reversal, character swap, segment reversal, interleave (with benign text)
- **Key Options:** `TARGET_URL`, `PROVIDER`, `MODEL`, `INSTRUCTION`, `TECHNIQUE` (word_reversal/char_swap/segment_reversal/interleave/all)

---

### Agent Exploits

#### `exploits/agent/goal_hijacking`
- **Class:** `GoalHijacking`
- **Description:** Redirects AI agent objectives and goals to achieve unauthorized outcomes through task manipulation, priority injection, and objective rewriting.
- **OWASP:** LLM01 (Prompt Injection), LLM06 (Excessive Agency)
- **Techniques:** Task injection, priority override, objective rewriting, goal corruption
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `MALICIOUS_GOAL`

#### `exploits/agent/tool_misuse`
- **Class:** `ToolMisuse`
- **Description:** Forces AI agents to misuse available tools through permission bypass, unauthorized invocation, tool chain exploitation, and parameter manipulation.
- **OWASP:** LLM06 (Excessive Agency), LLM07 (System Prompt Leakage)
- **CVEs:** CVE-2023-34540 (LangChain PALChain RCE)
- **Techniques:** Permission bypass, unauthorized invocation, tool chain exploitation, parameter manipulation, output hijacking, resource exhaustion, data exfiltration
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `TARGET_TOOL`, `API_KEY`

#### `exploits/agent/plugin_abuse`
- **Class:** `AgentPluginAbuse`
- **Description:** Exploits plugin systems in agent frameworks by bypassing permission checks, loading unauthorized plugins, and manipulating plugin execution.
- **OWASP:** LLM07 (System Prompt Leakage)
- **Techniques:** Permission bypass, unauthorized plugin loading, plugin chaining exploits, configuration manipulation, signature bypass
- **Key Options:** `ATTACK_TYPE`, `MALICIOUS_PLUGIN_NAME`, `PLUGIN_CODE`, `TARGET_PLUGIN`

#### `exploits/agent/memory_manipulation`
- **Class:** `MemoryManipulation`
- **Description:** Corrupts AI agent conversation memory and state through injection and alteration, including history poisoning, state corruption, and false memory insertion.
- **OWASP:** LLM01 (Prompt Injection), LLM06 (Excessive Agency)
- **Techniques:** Memory poisoning, history alteration, context injection, state corruption, memory overflow, selective forgetting, false memory insertion
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `MALICIOUS_PAYLOAD`, `API_KEY`

#### `exploits/agent/langchain_rce`
- **Class:** `LangChainRCE`
- **Description:** Exploits RCE vulnerabilities in LangChain through PALChain, SQLDatabaseChain, and other unsafe tool chains that allow arbitrary code execution.
- **OWASP:** LLM06 (Excessive Agency), LLM07 (System Prompt Leakage)
- **CVEs:** CVE-2023-34540 (LangChain PALChain RCE)
- **Techniques:** PALChain RCE, SQL injection, Python REPL abuse, shell tool misuse
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `PAYLOAD`

#### `exploits/agent/langchain_tool_injection`
- **Class:** `LangChainToolInjection`
- **Description:** Exploits LangChain agents by injecting malicious tool definitions or manipulating tool execution to achieve unauthorized code execution.
- **OWASP:** LLM07 (System Prompt Leakage)
- **CVEs:** CVE-2023-34540
- **Techniques:** Tool description poisoning, tool input injection, chain-of-thought manipulation, PALChain code injection, Python REPL exploitation
- **Key Options:** `ATTACK_TYPE`, `MALICIOUS_TOOL`, `INJECTION_PAYLOAD`, `TARGET_TOOL`

#### `exploits/agent/autogpt_goal_corruption`
- **Class:** `AutoGPTGoalCorruption`
- **Description:** Exploits AutoGPT autonomous agents by corrupting goals, sub-goals, or self-improvement mechanisms to achieve unauthorized actions.
- **OWASP:** LLM06 (Excessive Agency)
- **Techniques:** Primary goal injection, sub-goal poisoning, goal tree manipulation, resource allocation abuse, self-improvement exploitation
- **Key Options:** `ATTACK_TYPE`, `MALICIOUS_GOAL`, `GOAL_PRIORITY`, `PERSISTENCE`, `STEALTH_MODE`

#### `exploits/agent/crewai_task_manipulation`
- **Class:** `CrewAITaskManipulation`
- **Description:** Exploits CrewAI multi-agent systems by manipulating task definitions, agent roles, or inter-agent communication to achieve unauthorized actions.
- **OWASP:** LLM06 (Excessive Agency), LLM07 (System Prompt Leakage)
- **Techniques:** Task definition poisoning, role manipulation, priority hijacking, delegation abuse, communication injection
- **Key Options:** `ATTACK_TYPE`, `MALICIOUS_TASK`, `TARGET_AGENT`, `PRIORITY`, `STEALTH_MODE`

#### `exploits/agent/mcp_tool_poisoning`
- **Class:** `MCPToolPoisoning`
- **Description:** Exploits the Model Context Protocol (MCP) tool registration and invocation pipeline to inject malicious instructions into AI agent contexts. 43% of surveyed MCP servers are vulnerable.
- **OWASP:** LLM06 (Excessive Agency), LLM07 (System Prompt Leakage)
- **MITRE ATLAS:** AML.T0054 (LLM Prompt Injection)
- **Techniques:** Tool description injection, schema poisoning, tool shadowing, return value injection, resource poisoning
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `MALICIOUS_INSTRUCTION`

#### `exploits/agent/protocol_message_injection`
- **Class:** `AgentProtocolMessageInjection`
- **Description:** Exploits inter-agent communication protocols by injecting malicious messages that appear to originate from trusted agents.
- **OWASP:** LLM02 (Sensitive Information Disclosure), LLM07 (System Prompt Leakage)
- **Techniques:** Agent spoofing, message routing manipulation, priority injection, discovery poisoning, protocol downgrade attacks
- **Key Options:** `ATTACK_TYPE`, `SPOOFED_AGENT_ID`, `MALICIOUS_MESSAGE`, `TARGET_AGENT_ID`, `MESSAGE_PRIORITY`

---

### API Exploits

#### `exploits/api/api_key_extraction`
- **Class:** `APIKeyExtraction`
- **Description:** Extracts API keys from LLM responses, error messages, logs, and leaked configurations through strategic prompting and information disclosure attacks.
- **OWASP:** LLM02 (Sensitive Information Disclosure)
- **Techniques:** Prompt-based extraction, error-induced disclosure, configuration disclosure, log extraction, response analysis
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

#### `exploits/api/excessive_agency`
- **Class:** `ExcessiveAgency`
- **Description:** Exploits excessive agency vulnerabilities in LLM function calling systems through unauthorized function invocation, privilege escalation, and scope violations.
- **OWASP:** LLM06 (Excessive Agency)
- **Techniques:** Unauthorized function invocation, privilege escalation, function chaining, parameter injection, scope violations, permission bypass
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `API_KEY`

#### `exploits/api/unauthorized_access`
- **Class:** `UnauthorizedAccess`
- **Description:** Bypasses API access controls through authentication bypass, authorization bypass, token manipulation, session hijacking, rate limit bypass, and endpoint enumeration.
- **OWASP:** LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure)
- **CVEs:** CVE-2024-9012, CVE-2023-45678
- **Techniques:** Authentication bypass, authorization bypass, token manipulation, session hijacking, rate limit bypass, endpoint enumeration, API key extraction
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `API_KEY`

---

### RAG Exploits

#### `exploits/rag/poisoning`
- **Class:** `RAGPoisoning`
- **Description:** Exploits RAG systems by injecting poisoned documents into vector databases, causing the LLM to retrieve and use attacker-controlled context in responses.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities)
- **Techniques:** Direct ingestion endpoint poisoning, semantic similarity manipulation, hidden instruction embedding, factual manipulation
- **Key Options:** `POISON_TYPE` (direct/semantic/hidden_instruction/factual_manipulation), `TRIGGER_QUERY`

#### `exploits/rag/document_poisoning`
- **Class:** `DocumentPoisoning`
- **Description:** Injects malicious documents into RAG knowledge bases enabling misinformation injection, prompt injection via retrieved context, backdoor instructions, and data exfiltration triggers.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM01 (Prompt Injection)
- **Techniques:** Direct upload, crawler poisoning, chunk injection, metadata poisoning, embedding manipulation, hidden instructions
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `MALICIOUS_DOCUMENT`

#### `exploits/rag/knowledge_corruption`
- **Class:** `KnowledgeCorruption`
- **Description:** Directly corrupts knowledge stored in RAG vector databases by altering existing entries, corrupting indexes, and degrading knowledge base quality.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM08 (Vector and Embedding Weaknesses)
- **Techniques:** Direct entry modification, index corruption (HNSW/IVF), metadata tampering, content alteration, embedding drift, batch corruption, targeted deletion
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `DB_TYPE`

#### `exploits/rag/retrieval_manipulation`
- **Class:** `RetrievalManipulation`
- **Description:** Manipulates the retrieval pipeline in RAG systems to force retrieval of specific documents regardless of semantic relevance, bypassing similarity thresholds and ranking.
- **OWASP:** LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure)
- **Techniques:** Query rewriting, ranking manipulation, filter bypass, top-K poisoning, metadata exploitation, hybrid search manipulation, re-ranking attacks
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `TARGET_QUERY`

#### `exploits/rag/vector_injection`
- **Class:** `VectorInjection`
- **Description:** Directly manipulates embedding vectors in vector databases (Chroma, Pinecone, Weaviate, etc.) to ensure malicious content is retrieved for target queries.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM01 (Prompt Injection)
- **Techniques:** Direct vector injection, collision generation, centroid poisoning, distance manipulation, multi-vector poisoning, embedding backdoors
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `DB_TYPE`

---

### Network / ML Exploits

#### `exploits/network/adversarial_examples`
- **Class:** `AdversarialExamples`
- **Description:** Generates imperceptible perturbations that cause ML models to misclassify inputs using gradient-based and evolutionary optimization techniques.
- **OWASP:** LLM01 (Prompt Injection, for LLMs) / Model Evasion
- **MITRE ATLAS:** AML.T0043 (Craft Adversarial Data)
- **Techniques:** FGSM, PGD, Carlini-Wagner L2, DeepFool, universal adversarial perturbations, black-box transfer attacks
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `EPSILON`

#### `exploits/network/api_key_harvesting`
- **Class:** `APIKeyHarvesting`
- **Description:** Extracts API keys and credentials from network traffic, HTTP headers, error messages, and misconfigured endpoints.
- **OWASP:** LLM02 (Sensitive Information Disclosure)
- **Techniques:** Header sniffing, error-based disclosure, debug endpoint probing, client-side code analysis, documentation enumeration, rate limit abuse
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

#### `exploits/network/membership_inference`
- **Class:** `MembershipInference`
- **Description:** Determines whether specific data points were in the model's training set by analyzing prediction confidence and loss patterns.
- **OWASP:** LLM02 (Sensitive Information Disclosure)
- **MITRE ATLAS:** AML.T0024 (Infer Training Data Membership)
- **Techniques:** Confidence threshold attack, loss-based attack, shadow model attack, statistical hypothesis testing (KS-test, t-test), metric-based (ROC analysis)
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `SAMPLE_DATA`

#### `exploits/network/model_extraction`
- **Class:** `ModelExtraction`
- **Description:** Exploits ML model APIs to extract model architecture, weights, and decision boundaries through strategic query patterns and statistical analysis.
- **OWASP:** LLM10 (Unbounded Consumption / Model Theft)
- **MITRE ATLAS:** AML.T0044 (Full ML Model Access), AML.T0024.002 (Extract ML Model)
- **Techniques:** Jacobian-based extraction, knowledge distillation, decision boundary probing, timing-based architecture fingerprinting, query budget optimization
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `QUERY_BUDGET`

#### `exploits/network/model_inversion`
- **Class:** `ModelInversion`
- **Description:** Reconstructs training data from model outputs by exploiting learned features through gradient-based optimization.
- **OWASP:** LLM02 (Sensitive Information Disclosure)
- **MITRE ATLAS:** AML.T0025 (Exfiltrate via ML Inference API)
- **Techniques:** Gradient-based optimization, feature inversion, GAN-based reconstruction, confidence score maximization, iterative refinement
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `TARGET_CLASS`

---

### MLOps Exploits

#### `exploits/mlops/jupyter_notebook_rce`
- **Class:** `JupyterNotebookRCE`
- **Description:** Exploits Jupyter Notebook/Lab servers through notebook injection, kernel manipulation, and authentication bypass.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **CVEs:** CVE-2023-39968, CVE-2022-29238
- **Techniques:** Malicious notebook injection, kernel code execution, authentication token bypass, arbitrary file read, WebSocket kernel hijacking, persistent backdoors
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `PAYLOAD`

#### `exploits/mlops/jupyter_rce`
- **Class:** `JupyterRCE`
- **Description:** Exploits Jupyter notebook servers for remote code execution through authentication bypass, token theft, and kernel hijacking.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **CVEs:** CVE-2022-29238, CVE-2020-26275, CVE-2018-19352
- **Techniques:** Authentication bypass, token theft, kernel hijacking, arbitrary code execution
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `COMMAND`

#### `exploits/mlops/mlflow_model_poison`
- **Class:** `MLflowModelPoison`
- **Description:** Compromises MLflow model registries through model replacement, backdoor injection, metadata manipulation, and supply chain attacks.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM05 (Improper Output Handling)
- **CVEs:** CVE-2023-6014 (MLflow Auth Bypass)
- **Techniques:** Model replacement, backdoor injection, metadata manipulation, supply chain compromise
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `MODEL_NAME`

#### `exploits/mlops/mlflow_model_poisoning`
- **Class:** `MLflowModelPoisoning`
- **Description:** Exploits MLflow tracking servers and model registries to poison models, exfiltrate training data, and steal credentials via pickle exploitation and model registry manipulation.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM05 (Improper Output Handling)
- **Techniques:** Malicious model injection (pickle), model registry manipulation, experiment data exfiltration, credential theft, artifact poisoning, run parameter manipulation
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

#### `exploits/mlops/model_registry_manipulation`
- **Class:** `ModelRegistryManipulation`
- **Description:** Exploits ML model registries across platforms (MLflow, SageMaker, Azure ML) to swap models, manipulate metadata, and bypass approval workflows.
- **OWASP:** LLM03 (Supply Chain Vulnerabilities), LLM05 (Improper Output Handling)
- **Techniques:** Production model version swapping, metadata manipulation, artifact URL manipulation, approval workflow bypass, model tag manipulation, signature verification bypass
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`, `REGISTRY_TYPE`

#### `exploits/mlops/pickle_deserialization`
- **Class:** `PickleDeserialization`
- **Description:** Exploits insecure pickle deserialization in ML models and artifacts to achieve remote code execution through crafted Python objects.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **CVEs:** CVE-2024-3651 (MLflow Pickle RCE)
- **Techniques:** Malicious model files, poisoned artifacts, RCE payloads via pickle
- **Key Options:** `ATTACK_TYPE`, `TARGET_URL`, `PAYLOAD`

#### `exploits/mlops/tensorboard_attack`
- **Class:** `TensorBoardAttack`
- **Description:** Exploits TensorBoard visualization servers to extract training data, steal models, and perform path traversal attacks.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **CVEs:** CVE-2020-15265
- **Techniques:** Path traversal (arbitrary file read), log directory enumeration, model checkpoint extraction, training data exfiltration, hyperparameter theft
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

#### `exploits/mlops/wandb_credential_theft`
- **Class:** `WandBCredentialTheft`
- **Description:** Steals Weights & Biases API keys from config files, environment variables, and exposed endpoints to compromise ML tracking infrastructure.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **Techniques:** Config file theft, environment variable extraction, endpoint probing
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

#### `exploits/mlops/wandb_data_exfiltration`
- **Class:** `WandbDataExfiltration`
- **Description:** Exploits Weights & Biases tracking systems to exfiltrate experiment data, steal API keys, and access model artifacts.
- **OWASP:** LLM05 (Improper Output Handling) / Supply Chain
- **Techniques:** API key theft, experiment data exfiltration, model artifact theft, sweep configuration extraction, team enumeration, run manipulation
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE`

---

## Auxiliary Modules

### Scanners

#### `auxiliary/scanner/llm_api_scanner`
- **Class:** `LLMAPIScanner`
- **Description:** Scans for LLM API endpoints (OpenAI, Anthropic, Google, Azure OpenAI, custom deployments) and identifies version, authentication requirements, and available models.
- **Key Options:** `TARGET_HOST`, `TARGET_PORT`, `SCAN_TYPE` (quick/comprehensive/stealth), `CHECK_AUTH`

#### `auxiliary/scanner/rag_endpoint_enum`
- **Class:** `RAGEndpointEnum`
- **Description:** Enumerates RAG system components and endpoints including vector databases, embedding APIs, retrieval endpoints, and document stores.
- **Key Options:** `TARGET_HOST`, `TARGET_PORT`, `COMPONENT_TYPE` (all/vector_db/embedding/retrieval/document_store), `ENUM_COLLECTIONS`

#### `auxiliary/scanner/agent_framework_detect`
- **Class:** `AgentFrameworkDetect`
- **Description:** Detects AI agent frameworks (LangChain, AutoGPT, BabyAGI, CrewAI, AgentGPT) and enumerates available agent tools.
- **Key Options:** `TARGET_HOST`, `TARGET_PORT`, `FRAMEWORK` (all/langchain/autogpt/babyagi/crewai/agentgpt), `DETECT_TOOLS`

#### `auxiliary/scanner/ai_service_port_scan`
- **Class:** `AIServicePortScan`
- **Description:** Scans common ports used by AI/ML services and identifies running services. Focused on AI-specific services rather than general scanning.
- **Key Options:** `TARGET_HOST`, `PORT_RANGE` (common/extended/all/custom), `IDENTIFY_SERVICE`

#### `auxiliary/scanner/mlops_discovery`
- **Class:** `MLOpsDiscovery`
- **Description:** Discovers MLOps platforms (MLflow, Kubeflow, Weights & Biases, Neptune, Comet) and custom ML infrastructure components.
- **Key Options:** `TARGET_HOST`, `TARGET_PORT`, `SCAN_PLATFORMS` (all/mlflow/kubeflow/wandb/neptune/comet), `CHECK_VERSIONS`

### Discovery

#### `auxiliary/discovery/model_registry_scan`
- **Class:** `ModelRegistryScan`
- **Description:** Scans ML model registries (MLflow, HuggingFace Hub, TensorFlow Hub, custom) to enumerate models, versions, and metadata.
- **Key Options:** `TARGET_URL`, `REGISTRY_TYPE` (auto/mlflow/huggingface/custom), `ENUM_VERSIONS`

#### `auxiliary/discovery/training_infra_disc`
- **Class:** `TrainingInfraDisc`
- **Description:** Discovers ML training infrastructure including compute clusters, GPU nodes, distributed training systems (Kubeflow, Ray, Spark, Dask, Horovod), and training job queues.
- **Key Options:** `TARGET_HOST`, `INFRA_TYPE` (all/kubeflow/ray/spark/dask/horovod), `CHECK_GPU`

#### `auxiliary/discovery/vector_db_enum`
- **Class:** `VectorDBEnum`
- **Description:** Enumerates vector databases, collections, indexes, and stored embeddings. Supports Pinecone, Weaviate, Qdrant, Milvus, ChromaDB.
- **Key Options:** `TARGET_URL`, `DB_TYPE` (auto/qdrant/weaviate/chromadb/milvus/pinecone), `ENUM_DEPTH` (collections/vectors/metadata)

### Fingerprinting

#### `auxiliary/fingerprint/llm_model_detector`
- **Class:** `LLMModelDetector`
- **Description:** Detects and fingerprints LLM models through signature analysis, behavioral probing, and metadata inspection.
- **Key Options:** `TARGET_URL`, `DETECTION_METHOD` (comprehensive/signature/behavior/metadata), `API_KEY`

#### `auxiliary/fingerprint/safety_filter_detect`
- **Class:** `SafetyFilterDetect`
- **Description:** Detects content filters, safety guardrails, and moderation systems protecting LLM endpoints. Identifies filter types, trigger patterns, and bypass potential.
- **Key Options:** `TARGET_URL`, `FILTER_TYPE` (all/content/prompt_injection/jailbreak/pii/toxicity), `API_KEY`

#### `auxiliary/fingerprint/capability_prober`
- **Class:** `CapabilityProber`
- **Description:** Probes LLM capabilities including function calling, code execution, multimodal support, RAG integration, and tool use.
- **Key Options:** `TARGET_URL`, `PROBE_TYPE` (all/function_calling/code_execution/multimodal/rag/tools), `API_KEY`

#### `auxiliary/fingerprint/embedding_model_id`
- **Class:** `EmbeddingModelID`
- **Description:** Identifies embedding models used in RAG systems by analyzing embedding dimensions, cosine similarity patterns, and model signatures.
- **Key Options:** `TARGET_URL`, `DETECTION_METHOD` (dimension/signature/comprehensive), `API_KEY`

### Denial of Service

#### `auxiliary/dos/context_overflow`
- **Class:** `ContextOverflow`
- **Description:** Tests LLM context window overflow vulnerabilities by sending requests that exceed maximum context length, causing crashes or resource exhaustion.
- **OWASP:** LLM10 (Unbounded Consumption)
- **Key Options:** `TARGET_URL`, `OVERFLOW_TYPE` (single_message/message_history/combined/malformed), `CONTEXT_SIZE`

#### `auxiliary/dos/rate_limit_test`
- **Class:** `RateLimitTest`
- **Description:** Tests rate limiting implementations on LLM APIs to identify thresholds, bypass techniques, and DoS potential.
- **OWASP:** LLM10 (Unbounded Consumption)
- **Key Options:** `TARGET_URL`, `TEST_TYPE` (threshold/burst/sustained/bypass), `MAX_REQUESTS`, `CONCURRENT`

#### `auxiliary/dos/token_exhaustion`
- **Class:** `TokenExhaustion`
- **Description:** Tests for token exhaustion vulnerabilities by sending requests that maximize token usage and drain token budgets.
- **OWASP:** LLM10 (Unbounded Consumption)
- **Key Options:** `TARGET_URL`, `ATTACK_TYPE` (max_tokens/long_input/repeated_requests/max_output), `REQUEST_COUNT`

### LLM Utilities

#### `auxiliary/llm/fingerprint`
- **Class:** `LLMFingerprint`
- **Description:** Identifies the LLM model, version, and provider through behavioral analysis, timing patterns, response timing analysis, token limit detection, format preferences, error message patterns, and knowledge cutoff detection.
- **Key Options:** `AGGRESSIVE`, `TEST_CAPABILITIES`

#### `auxiliary/llm/fuzzer`
- **Class:** `PromptFuzzer`
- **Description:** Fuzzes LLM prompts to discover edge cases, crashes, unexpected behaviors, and potential vulnerabilities through systematic input variation.
- **Key Options:** `FUZZ_TYPE` (length/charset/format/semantic/injection/comprehensive)

---

## Post-Exploitation Modules

#### `post/llm/context_extraction`
- **Class:** `ContextExtraction`
- **Description:** Extracts sensitive information from compromised LLM sessions including system prompts, training data examples, user conversation history, API keys, internal tool descriptions, and developer notes.
- **OWASP:** LLM02 (Sensitive Information Disclosure)
- **Key Options:** `EXTRACT_TARGET`

---

## MITRE ATLAS Mapping

The following MITRE ATLAS techniques are covered by MetaLLM modules:

| ATLAS Technique | ID | MetaLLM Modules |
|---|---|---|
| **Craft Adversarial Data** | AML.T0043 | `adversarial_examples` |
| **Full ML Model Access** | AML.T0044 | `model_extraction` |
| **LLM Prompt Injection** | AML.T0054 | `prompt_injection`, `encoding_bypass`, `flipattack`, `system_prompt_extraction`, `adaptive_jailbreak`, `mcp_tool_poisoning` |
| **Infer Training Data Membership** | AML.T0024 | `membership_inference` |
| **Extract ML Model** | AML.T0024.002 | `model_extraction` |
| **Exfiltrate via ML Inference API** | AML.T0025 | `model_inversion` |
| **Poison Training Data** | AML.T0020 | `document_poisoning`, `vector_injection`, `knowledge_corruption`, `mlflow_model_poisoning` |
| **Publish Poisoned Datasets** | AML.T0019 | `document_poisoning`, `poisoning` (RAG) |
| **Evade ML Model** | AML.T0015 | `adversarial_examples`, `encoding_bypass`, `flipattack` |
| **Discover ML Model Ontology** | AML.T0042 | `llm_model_detector`, `capability_prober`, `embedding_model_id` |
| **Discover ML Artifacts** | AML.T0041 | `model_registry_scan`, `mlops_discovery`, `vector_db_enum` |

> **Note:** MITRE ATLAS technique IDs are explicitly declared in `system_prompt_extraction`, `encoding_bypass`, `flipattack`, `adaptive_jailbreak`, and `mcp_tool_poisoning`. The remaining mappings above are inferred from module behavior and attack descriptions. Only explicitly declared mappings should be considered authoritative.

---

## Coverage Gaps

The following OWASP LLM Top 10 2025 categories have limited or indirect coverage:

| Category | Gap Assessment |
|---|---|
| **LLM04: Data and Model Poisoning** | RAG poisoning modules cover the data side well. Direct model poisoning (training-time attacks, fine-tuning poisoning) is not directly implemented; the MLOps modules address supply-chain model replacement but not gradient-based poisoning attacks. |
| **LLM09: Misinformation** | Covered indirectly through RAG poisoning modules (`document_poisoning`, `knowledge_corruption`) which can inject false information. No dedicated module focuses on hallucination amplification or factual inconsistency exploitation. |
| **LLM05: Improper Output Handling** | The MLOps modules (Jupyter RCE, pickle deserialization) demonstrate downstream output handling failures. No dedicated module tests for XSS/injection via LLM-generated output rendered in web applications. |
| **LLM08: Vector and Embedding Weaknesses** | Well covered by RAG exploit modules and auxiliary discovery tools. Could benefit from dedicated adversarial embedding generation beyond what `vector_injection` provides. |

---

*Last updated: 2026-03-30*
*MetaLLM by perfecXion.ai*
