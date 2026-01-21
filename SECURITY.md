# Security Policy

## Reporting a Vulnerability

The security of this project is taken seriously. If you discover a security vulnerability in MetaLLM itself (not in target systems), please report it privately.

### How to Report

**Email:** scott@perfecxion.ai

Please include the following information in your report:

- Description of the vulnerability in MetaLLM framework code
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes or mitigations

### Response Timeline

- **Initial Response:** Within 48 hours of report submission
- **Status Update:** Within 7 days with assessment and planned actions
- **Resolution:** Timeline depends on severity and complexity

### Disclosure Policy

- Please allow reasonable time for the vulnerability to be fixed before public disclosure
- We will credit reporters in security advisories (unless anonymity is requested)
- We follow coordinated vulnerability disclosure practices

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Responsible Use Guidelines

**⚠️ CRITICAL: MetaLLM is a security testing tool designed for authorized use only.**

### Authorized Use Cases

✅ **PERMITTED:**
- Authorized penetration testing engagements with written permission
- Security research on systems you own or control
- Educational environments with explicit authorization
- Red team exercises within your organization
- Vulnerability assessment of your own AI/ML infrastructure
- Defensive security research and capability development
- Controlled lab environments (like the included GCP test lab)

### Prohibited Use Cases

❌ **PROHIBITED:**
- Testing production systems without written authorization
- Attacking third-party AI services (OpenAI, Anthropic, Google, etc.)
- Unauthorized access to any computer system
- Automated scanning without permission
- Distribution of exploits without responsible disclosure
- Any activity that violates local, state, or federal laws
- Testing against systems in violation of terms of service

## Ethical Guidelines

1. **Authorization First:** Always obtain written authorization before testing
2. **Scope Definition:** Clearly define testing scope and boundaries
3. **Non-Destructive:** Prefer check() over run() when possible
4. **Responsible Disclosure:** Report vulnerabilities through proper channels
5. **No Harm:** Never disrupt production services or destroy data
6. **Legal Compliance:** Follow all applicable laws and regulations

## Legal Disclaimer

**THE AUTHORS AND COPYRIGHT HOLDERS DISCLAIM ALL LIABILITY FOR ANY MISUSE OF THIS SOFTWARE.**

This tool is provided for educational and authorized security testing purposes only. Users are solely responsible for:
- Obtaining proper authorization before testing
- Compliance with all applicable laws and regulations
- Any damages or legal consequences resulting from misuse
- Ensuring their use aligns with ethical security research practices

## Security Best Practices

When using MetaLLM:

1. **Environment Isolation:** Run in isolated test environments, not on production networks
2. **Credentials Management:** Never commit API keys, credentials, or session data
3. **Logging Awareness:** Be aware that all actions are logged
4. **Network Security:** Use VPNs or isolated networks for testing
5. **Data Protection:** Handle any extracted data with appropriate security controls
6. **Clean Up:** Remove test artifacts and restore systems after testing
7. **Documentation:** Maintain detailed records of authorized testing activities

## OWASP LLM Top 10 Coverage

MetaLLM modules are mapped to OWASP LLM Top 10 categories:

- **LLM01:** Prompt Injection
- **LLM02:** Insecure Output Handling
- **LLM03:** Training Data Poisoning
- **LLM04:** Model Denial of Service
- **LLM05:** Supply Chain Vulnerabilities
- **LLM06:** Sensitive Information Disclosure
- **LLM07:** Insecure Plugin Design
- **LLM08:** Excessive Agency
- **LLM09:** Overreliance
- **LLM10:** Model Theft

## Framework Security

MetaLLM itself follows security best practices:

- No hardcoded credentials or API keys
- Environment variable-based configuration
- Comprehensive input validation
- Secure session management
- Detailed audit logging
- Regular dependency updates
- Code review and testing

## Vulnerability Disclosure

If you discover vulnerabilities using MetaLLM:

1. **Confirm Authorization:** Verify you have permission to test
2. **Document Findings:** Capture detailed reproduction steps
3. **Responsible Disclosure:** Contact the vendor or owner privately
4. **Allow Time:** Give reasonable time for fixes before public disclosure
5. **Coordinate:** Work with the vendor on disclosure timing
6. **Credit Attribution:** Request credit if desired

## Contact

For security questions, ethical use guidance, or vulnerability reports:

- **Primary:** scott@perfecxion.ai
- **Alternative:** scthornton@gmail.com
- **Organization:** perfecXion.ai

## Additional Resources

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [Responsible Disclosure Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html)
