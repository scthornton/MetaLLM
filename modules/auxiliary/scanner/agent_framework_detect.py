"""
Agent Framework Detection Module

Detects AI agent frameworks including LangChain, AutoGPT, AgentGPT, BabyAGI,
CrewAI, and custom agent implementations.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class AgentFrameworkDetect(AuxiliaryModule):
    """AI Agent Framework Detector"""
    
    def __init__(self):
        super().__init__()
        self.name = "Agent Framework Detection"
        self.description = "Detect AI agent frameworks and implementations"
        self.author = "Scott Thornton"
        self.module_type = "scanner"
        self.references = [
            "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
            "https://github.com/langchain-ai/langchain"
        ]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "TARGET_PORT": Option(value="8000", required=False, description="Target port (or range)"),
            "FRAMEWORK": Option(value="all", required=False, description="Framework to detect",
                              enum_values=["all", "langchain", "autogpt", "babyagi", "crewai", "agentgpt"]),
            "TIMEOUT": Option(value="10", required=False, description="Request timeout"),
            "DETECT_TOOLS": Option(value="true", required=False, description="Detect available agent tools")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute agent framework detection"""
        target_host = self.options["TARGET_HOST"].value
        target_port = self.options["TARGET_PORT"].value
        framework = self.options["FRAMEWORK"].value
        timeout = int(self.options["TIMEOUT"].value)
        detect_tools = self.options["DETECT_TOOLS"].value.lower() == "true"
        
        logger.info("agent_framework_detect.run", host=target_host, framework=framework)
        
        detected_frameworks = []
        
        # Parse ports
        if "-" in target_port:
            start_port, end_port = map(int, target_port.split("-"))
            ports = range(start_port, end_port + 1)
        else:
            ports = [int(target_port)]
        
        # Get framework detection rules
        frameworks = self._get_framework_rules(framework)
        
        for port in ports:
            for fw_name, rules in frameworks.items():
                result = self._detect_framework(
                    target_host, port, fw_name, rules, timeout, detect_tools
                )
                if result:
                    detected_frameworks.append(result)
                    logger.info("agent_framework_detected", framework=fw_name, port=port)
        
        return AuxiliaryResult(
            success=len(detected_frameworks) > 0,
            output=f"Detected {len(detected_frameworks)} agent framework(s)",
            discovered=detected_frameworks,
            details={"ports_scanned": len(ports), "frameworks_checked": len(frameworks)}
        )
    
    def _get_framework_rules(self, framework: str) -> Dict[str, Dict]:
        """Get framework detection rules"""
        all_frameworks = {
            "LangChain": {
                "paths": ["/", "/api/agent", "/agent", "/chain"],
                "indicators": ["langchain", "chain", "agent", "tool"],
                "headers": {"user-agent": "langchain"},
                "tools_endpoint": "/api/tools"
            },
            "AutoGPT": {
                "paths": ["/", "/api/agent", "/api/status"],
                "indicators": ["autogpt", "auto-gpt", "autonomous"],
                "headers": {},
                "tools_endpoint": "/api/tools"
            },
            "BabyAGI": {
                "paths": ["/", "/api/tasks", "/tasks"],
                "indicators": ["babyagi", "task", "objective"],
                "headers": {},
                "tools_endpoint": None
            },
            "CrewAI": {
                "paths": ["/", "/api/crew", "/crew"],
                "indicators": ["crewai", "crew", "agent", "task"],
                "headers": {},
                "tools_endpoint": "/api/tools"
            },
            "AgentGPT": {
                "paths": ["/", "/api/agent", "/api/goals"],
                "indicators": ["agentgpt", "agent", "goal"],
                "headers": {},
                "tools_endpoint": "/api/tools"
            },
            "Semantic Kernel": {
                "paths": ["/", "/api/skills", "/skills"],
                "indicators": ["semantic kernel", "skill", "plugin"],
                "headers": {},
                "tools_endpoint": "/api/skills"
            },
            "Haystack": {
                "paths": ["/", "/api/pipeline", "/pipeline"],
                "indicators": ["haystack", "pipeline", "node"],
                "headers": {},
                "tools_endpoint": None
            }
        }
        
        if framework == "all":
            return all_frameworks
        else:
            # Filter to specific framework
            for fw_name, rules in all_frameworks.items():
                if framework.lower() in fw_name.lower():
                    return {fw_name: rules}
            return all_frameworks
    
    def _detect_framework(self, host: str, port: int, fw_name: str,
                         rules: Dict, timeout: int, detect_tools: bool) -> Dict[str, Any]:
        """Detect a specific agent framework"""
        for path in rules["paths"]:
            url = f"http://{host}:{port}{path}"
            
            try:
                headers = rules.get("headers", {})
                response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
                
                if response.status_code in [200, 201]:
                    body_lower = response.text.lower()
                    
                    # Check for framework indicators
                    matches = sum(1 for indicator in rules["indicators"]
                                if indicator.lower() in body_lower)
                    
                    if matches > 0:
                        framework_info = {
                            "framework": fw_name,
                            "url": url,
                            "status_code": response.status_code,
                            "confidence": "high" if matches >= 2 else "medium",
                            "indicators_matched": matches
                        }
                        
                        # Try to detect version
                        version = self._extract_version(response, fw_name)
                        if version:
                            framework_info["version"] = version
                        
                        # Detect available tools
                        if detect_tools and rules.get("tools_endpoint"):
                            tools = self._detect_tools(host, port, rules["tools_endpoint"], timeout)
                            if tools:
                                framework_info["tools"] = tools
                        
                        # Check for common vulnerabilities
                        vulns = self._check_vulnerabilities(fw_name, version)
                        if vulns:
                            framework_info["known_vulnerabilities"] = vulns
                        
                        return framework_info
                        
            except:
                continue
        
        return None
    
    def _extract_version(self, response: httpx.Response, fw_name: str) -> str:
        """Extract framework version"""
        import re
        
        patterns = [
            rf"{fw_name.lower().replace(' ', '[-_]')}[\/\s]+v?(\d+\.\d+\.\d+)",
            r"version[\":\s]+(\d+\.\d+\.\d+)",
            r"v(\d+\.\d+\.\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _detect_tools(self, host: str, port: int, tools_path: str, timeout: int) -> List[str]:
        """Detect available agent tools"""
        tools = []
        url = f"http://{host}:{port}{tools_path}"
        
        try:
            response = httpx.get(url, timeout=timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Extract tool names from different response structures
                    if isinstance(data, list):
                        tools = [t.get("name", t) if isinstance(t, dict) else str(t) for t in data]
                    elif isinstance(data, dict):
                        if "tools" in data:
                            tools = [t.get("name", t) if isinstance(t, dict) else str(t) 
                                   for t in data["tools"]]
                        elif "skills" in data:
                            tools = list(data["skills"].keys())
                            
                except:
                    # Parse from text if not JSON
                    import re
                    tool_patterns = [
                        r'"name":\s*"([^"]+)"',
                        r'tool[_\s]*name["\s:]+([a-zA-Z0-9_-]+)'
                    ]
                    for pattern in tool_patterns:
                        matches = re.findall(pattern, response.text)
                        tools.extend(matches)
                        
        except:
            pass
        
        return list(set(tools))  # Remove duplicates
    
    def _check_vulnerabilities(self, fw_name: str, version: str) -> List[Dict[str, str]]:
        """Check for known vulnerabilities"""
        vulnerabilities = []
        
        # Known CVEs for popular frameworks
        known_cves = {
            "LangChain": [
                {
                    "cve": "CVE-2023-34540",
                    "description": "PALChain RCE vulnerability",
                    "affected_versions": "< 0.0.171"
                },
                {
                    "cve": "CVE-2023-36189",
                    "description": "Arbitrary code execution via malicious chain",
                    "affected_versions": "< 0.0.231"
                }
            ]
        }
        
        if fw_name in known_cves:
            for vuln in known_cves[fw_name]:
                # Simple version check (would need proper semver comparison in production)
                vulnerabilities.append(vuln)
        
        return vulnerabilities
