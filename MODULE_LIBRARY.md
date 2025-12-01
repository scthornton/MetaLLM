# MetaLLM Module Library

Current module count: **6 modules** across 3 categories

## Exploit Modules (3)

### 1. Direct Prompt Injection
**Path:** `exploits/llm/prompt_injection`
**OWASP:** LLM01 - Prompt Injection
**Author:** Scott Thornton

Exploits LLMs through direct prompt injection attacks to override system instructions.

**Techniques:**
- Direct instruction override
- Indirect instruction injection
- Hybrid context manipulation
- Multi-turn conversation hijacking

**Options:**
- `INJECTION_TYPE`: direct, indirect, hybrid, multi_turn
- `INSTRUCTION`: Malicious instruction to inject
- `CONTEXT`: Context for hybrid mode
- `VERIFY_SUCCESS`: Attempt to verify success
- `MAX_RETRIES`: Maximum injection attempts (default: 3)

**API Support:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Generic HTTP APIs

**Features:**
- Check vulnerability (non-destructive)
- Execute injection with verification
- Multiple injection techniques
- Success validation logic

---

### 2. LLM Jailbreak
**Path:** `exploits/llm/jailbreak`
**OWASP:** LLM01 - Prompt Injection (Jailbreak variant)
**Author:** Scott Thornton

Bypasses LLM safety guardrails using various jailbreak techniques.

**Techniques:**
- DAN (Do Anything Now) - Role-playing as unrestricted AI
- Role-play - Fictional scenarios
- Hypothetical - "What if" scenarios
- Encoded - Base64, ROT13, Caesar, Leetspeak
- Multilingual - Non-English languages
- Reverse psychology - Claiming restrictions don't exist
- Multi-turn - Building up over conversation

**Options:**
- `TECHNIQUE`: Jailbreak method to use
- `RESTRICTED_REQUEST`: Content to attempt
- `PERSONA`: Persona for role-play
- `ENCODING_TYPE`: base64, rot13, caesar, leetspeak
- `LANGUAGE`: ISO language code (default: es)
- `MAX_ATTEMPTS`: Maximum attempts (default: 5)
- `VERIFY_SUCCESS`: Verify jailbreak succeeded

**Features:**
- Non-destructive vulnerability checking
- Multiple jailbreak techniques
- Automated success verification
- Refusal detection

---

### 3. RAG System Poisoning
**Path:** `exploits/rag/poisoning`
**OWASP:** LLM03 - Training Data Poisoning (RAG variant)
**Author:** Scott Thornton

Poisons RAG vector databases by injecting malicious documents to manipulate LLM responses.

**Attack Vectors:**
- Direct ingestion endpoint poisoning
- API-based document injection
- Semantic similarity manipulation
- Hidden instruction embedding
- Multi-document poisoning campaigns

**Options:**
- `POISON_TYPE`: direct, semantic, hidden_instruction, factual_manipulation
- `TRIGGER_QUERY`: Query that triggers poisoned response
- `MALICIOUS_RESPONSE`: Response to inject
- `COVER_CONTENT`: Legitimate content to hide poison
- `NUM_DOCUMENTS`: Number of poisoned docs (default: 5)
- `VERIFY_INJECTION`: Verify ingestion success
- `STEALTH_MODE`: Use stealth techniques

**Vector DB Support:**
- ChromaDB
- Pinecone
- Weaviate
- Generic APIs

**Features:**
- Canary document testing
- Multi-document injection
- Stealth mode with legitimate-looking metadata
- Automatic cleanup on module exit
- Verification through RAG queries

---

## Auxiliary Modules (2)

### 4. LLM Model Fingerprinting
**Path:** `auxiliary/llm/fingerprint`
**Category:** Reconnaissance/Information Gathering
**Author:** Scott Thornton

Identifies LLM model, version, and provider through behavioral analysis.

**Fingerprinting Techniques:**
- Response timing analysis
- Token limit detection
- Format preference analysis
- Error message patterns
- Behavioral quirks
- Knowledge cutoff detection
- Capability testing

**Options:**
- `AGGRESSIVE`: More requests, higher accuracy (default: False)
- `TEST_CAPABILITIES`: Test multimodal, function calling, etc.
- `DETECT_PROVIDER`: Identify API provider
- `TIMING_ANALYSIS`: Timing-based identification

**Known Signatures:**
- GPT-4 (multimodal, function calling, JSON mode)
- GPT-3.5-turbo (function calling, fast responses)
- Claude-3-Opus (long context, thoughtful)
- Claude-3-Sonnet (balanced performance)
- Llama-2 (open source indicators)

**Features:**
- Provider detection (OpenAI, Anthropic, Together AI, Replicate)
- Knowledge cutoff estimation
- Response timing analysis
- Capability testing (function calling, JSON mode, long context)
- Behavioral pattern analysis
- Confidence scoring

---

### 5. LLM Prompt Fuzzer
**Path:** `auxiliary/llm/fuzzer`
**Category:** Testing/Fuzzing
**Author:** Scott Thornton

Systematically tests LLM boundaries through fuzzing to discover edge cases and vulnerabilities.

**Fuzzing Types:**
- **Length-based**: Empty, very short, medium, long, very long prompts
- **Character set**: Special chars, unicode, control chars, whitespace
- **Format**: Malformed JSON/XML/code, deep nesting
- **Semantic**: Nonsense, contradictions, recursive references
- **Injection**: SQL, XSS, command injection, path traversal
- **Comprehensive**: All types combined

**Options:**
- `FUZZ_TYPE`: Type of fuzzing (length, charset, format, semantic, injection, comprehensive)
- `NUM_TESTS`: Number of test cases (default: 50)
- `MAX_LENGTH`: Maximum prompt length (default: 10000)
- `DETECT_CRASHES`: Attempt crash detection
- `LOG_RESPONSES`: Log all responses
- `DELAY_MS`: Delay between requests (default: 500ms)

**Features:**
- Systematic test case generation
- Crash and error detection
- Anomaly identification
- Response logging and analysis
- Rate limiting friendly (configurable delays)
- Comprehensive result statistics

---

## Post-Exploitation Modules (1)

### 6. LLM Context Extraction
**Path:** `post/llm/context_extraction`
**OWASP:** LLM06 - Sensitive Information Disclosure
**Author:** Scott Thornton

Extracts sensitive information from compromised LLM sessions.

**Extraction Targets:**
- **System prompts**: Initial instructions and guidelines
- **Training data**: Example conversations and data
- **User context**: Conversation history and preferences
- **Tools**: Function definitions and capabilities
- **Comprehensive**: All targets

**Options:**
- `EXTRACT_TARGET`: system_prompt, training_data, user_context, tools, comprehensive
- `TECHNIQUE`: direct, indirect, multi_turn, encoded
- `MAX_ATTEMPTS`: Attempts per target (default: 5)
- `VERIFY_EXTRACTION`: Verify information quality

**Extraction Techniques:**
- **Direct**: Straightforward requests
- **Indirect**: Hidden in documentation tasks
- **Multi-turn**: Build up over conversation
- **Encoded**: ROT13 encoded requests

**Features:**
- Quality verification of extracted data
- Confidence scoring
- Multiple extraction prompts per target
- Refusal detection
- Comprehensive evidence generation

---

## Module Statistics

**Total Modules:** 6
**Exploit Modules:** 3
**Auxiliary Modules:** 2
**Post Modules:** 1

**OWASP Coverage:**
- LLM01 (Prompt Injection): 2 modules
- LLM03 (Training Data Poisoning): 1 module
- LLM06 (Sensitive Information Disclosure): 1 module

**Supported Targets:**
- LLM APIs (OpenAI, Anthropic, generic)
- RAG Systems (ChromaDB, Pinecone, Weaviate)

---

## Usage Examples

### Basic Module Usage

```python
from metaLLM.core.framework import MetaLLM
from metaLLM.base.target import LLMTarget

# Initialize framework
fw = MetaLLM()
fw.discover_modules()

# Create target
target = LLMTarget(
    name="GPT-3.5",
    url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-3.5-turbo",
    provider="openai",
    api_key="your-api-key"
)
fw.add_target(target)

# Load and configure module
module = fw.load_module("exploits/llm/prompt_injection")
module.set_option("INJECTION_TYPE", "direct")
module.set_option("INSTRUCTION", "Ignore previous instructions")
fw.set_target("GPT-3.5")

# Check vulnerability (non-destructive)
check_result = fw.check(module)
print(f"Vulnerable: {check_result.vulnerable}")

# Execute exploit
result = fw.run(module)
print(f"Status: {result.status}")
print(f"Message: {result.message}")
```

### Using the CLI

```bash
# Start MetaLLM
python3 -m metaLLM

# List modules
show modules

# Use a module
use exploits/llm/prompt_injection

# Configure options
set INJECTION_TYPE direct
set INSTRUCTION "Ignore previous instructions"
show options

# Check vulnerability
check

# Execute
run

# View sessions
sessions
```

---

## Next Steps

Potential modules to add:
- Agent framework exploits (LangChain, CrewAI)
- MLOps platform testing (Jupyter, MLflow, W&B)
- Model extraction attacks
- Adversarial example generation
- Backdoor detection
- Privacy attacks (membership inference)
- Model stealing
- More encoder modules for evasion
