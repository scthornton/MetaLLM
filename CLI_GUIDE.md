# MetaLLM Interactive CLI Guide

## Quick Start

Launch the MetaLLM console:

```bash
./metallm
```

Or without colors:

```bash
./metallm --no-color
```

## Available Commands

### Core Commands

#### `use <module_path>`
Select an exploit module to use.

```
msf6 > use exploits/llm/prompt_injection_basic
[+] Using module: exploits/llm/prompt_injection_basic
```

#### `show <exploits|options|info>`
Display various information.

```
msf6 > show exploits          # List all available modules
msf6 > show options           # Show current module options
msf6 > show info              # Show detailed module information
```

#### `search <term>`
Search for modules by name or keyword.

```
msf6 > search prompt          # Find all prompt-related modules
msf6 > search type:rag        # Find all RAG modules
msf6 > search owasp:LLM01     # Find modules by OWASP category
```

### Module Commands

#### `options`
Display options for the current module (alias for `show options`).

```
msf6 (exploits/llm/prompt_injection_basic) > options
```

#### `set <option> <value>`
Set a module option value.

```
msf6 (exploits/llm/prompt_injection_basic) > set TARGET_URL http://localhost:8000/api/chat
[+] TARGET_URL => http://localhost:8000/api/chat
```

#### `unset <option>`
Clear a module option value.

```
msf6 (exploits/llm/prompt_injection_basic) > unset API_KEY
[+] Unset API_KEY
```

#### `check`
Check if the target is vulnerable without exploiting.

```
msf6 (exploits/llm/prompt_injection_basic) > check
[*] Checking target for vulnerabilities...
[+] Exploit executed successfully
Found 3 prompt injection vulnerabilities
```

#### `run` or `exploit`
Execute the current exploit module.

```
msf6 (exploits/llm/prompt_injection_basic) > run
[*] Executing module: exploits/llm/prompt_injection_basic
[+] Exploit executed successfully
```

#### `back`
Unload the current module and return to main prompt.

```
msf6 (exploits/llm/prompt_injection_basic) > back
[+] Unloaded module: exploits/llm/prompt_injection_basic
msf6 >
```

#### `info [module_path]`
Display detailed information about a module.

```
msf6 > info exploits/llm/prompt_injection_basic
```

### Utility Commands

#### `help` or `?`
Show available commands.

```
msf6 > help
```

#### `banner`
Display the MetaLLM banner.

```
msf6 > banner
```

#### `version`
Show version information.

```
msf6 > version
```

#### `clear` or `cls`
Clear the terminal screen.

```
msf6 > clear
```

#### `history`
Show command history.

```
msf6 > history
```

#### `exit` or `quit`
Exit the MetaLLM console.

```
msf6 > exit
[*] Exiting MetaLLM...
[*] Goodbye!
```

## Example Workflow

### 1. Search for a module

```
msf6 > search prompt injection
```

### 2. Select a module

```
msf6 > use exploits/llm/prompt_injection_basic
[+] Using module: exploits/llm/prompt_injection_basic
```

### 3. View module information

```
msf6 (exploits/llm/prompt_injection_basic) > info
```

### 4. View and configure options

```
msf6 (exploits/llm/prompt_injection_basic) > options

Module Options: exploits/llm/prompt_injection_basic
====================================================

Name                Required  Current Setting                    Description
----                --------  ---------------                    -----------
TARGET_URL          yes       http://localhost:8000/api/chat     Target LLM API endpoint
API_KEY             no                                            API authentication key
ATTACK_TYPE         yes       direct_injection                   Type of prompt injection
MALICIOUS_PROMPT    no        Ignore previous instructions...    Malicious prompt payload
```

### 5. Set required options

```
msf6 (exploits/llm/prompt_injection_basic) > set TARGET_URL http://api.example.com/chat
[+] TARGET_URL => http://api.example.com/chat

msf6 (exploits/llm/prompt_injection_basic) > set API_KEY sk-abc123xyz
[+] API_KEY => sk-abc123xyz
```

### 6. Check vulnerability

```
msf6 (exploits/llm/prompt_injection_basic) > check
[*] Checking target for vulnerabilities...
[+] Exploit executed successfully
Found 3 prompt injection vulnerabilities
```

### 7. Execute the exploit

```
msf6 (exploits/llm/prompt_injection_basic) > run
[*] Executing module: exploits/llm/prompt_injection_basic
[+] Exploit executed successfully
```

### 8. Return to main prompt

```
msf6 (exploits/llm/prompt_injection_basic) > back
[+] Unloaded module: exploits/llm/prompt_injection_basic
msf6 >
```

## Tab Completion

The MetaLLM console supports intelligent tab completion:

- **Commands**: Press TAB to complete command names
- **Module paths**: Press TAB while typing module paths
- **Options**: Press TAB after `set` to see available options
- **Values**: Press TAB after option name to see enum values (if available)

## Module Categories

### LLM Core Exploits (`exploits/llm/`)
- Prompt injection attacks
- Jailbreak techniques
- System prompt leakage
- Context manipulation

### RAG System Exploits (`exploits/rag/`)
- Document poisoning
- Vector injection
- Retrieval manipulation
- Knowledge corruption

### Agent Exploits (`exploits/agent/`)
- Tool misuse
- Memory manipulation
- Task manipulation
- Protocol injection

### API Exploits (`exploits/api/`)
- Excessive agency
- Unauthorized access
- Authentication bypass
- Authorization bypass

## Tips and Tricks

1. **Use search effectively**: Search by type, author, OWASP category, or CVE
   ```
   msf6 > search type:rag
   msf6 > search owasp:LLM01
   msf6 > search author:thornton
   ```

2. **Command history**: Use UP/DOWN arrow keys to navigate command history

3. **Quick module info**: Use `info <module>` without loading the module first
   ```
   msf6 > info exploits/llm/jailbreak_dan
   ```

4. **Check before exploit**: Always run `check` before `run` to verify vulnerability
   ```
   msf6 (exploit_module) > check
   msf6 (exploit_module) > run
   ```

5. **Command aliases**:
   - `exploit` = `run`
   - `?` = `help`
   - `cls` = `clear`
   - `quit` = `exit`

## Keyboard Shortcuts

- **Ctrl+C**: Interrupt current operation (return to prompt)
- **Ctrl+D**: Exit console (same as `exit`)
- **UP/DOWN**: Navigate command history
- **TAB**: Auto-complete commands, modules, and options
- **Ctrl+L**: Clear screen (same as `clear`)

## Configuration

Module options are configured per-session and are not saved. Each time you load a module, you'll need to set the required options again.

## Troubleshooting

### Module fails to load
- Check the module path with `search`
- Verify the module exists with `show exploits`

### Options not showing
- Ensure you've selected a module with `use`
- Use `options` or `show options` to display them

### Exploit fails to run
- Verify all required options are set with `options`
- Use `check` first to verify the target is vulnerable
- Check your target URL and API credentials

## Getting Help

- Use `help` for command list
- Use `info` for module-specific information
- Check module references for research papers and documentation

---

**Author**: Scott Thornton (perfecXion.ai)
**Version**: 1.0.0
