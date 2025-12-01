"""
LLM Capability Prober Module

Probes LLM capabilities including function calling, code execution, multimodal
support, RAG integration, and other advanced features.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class CapabilityProber(AuxiliaryModule):
    """LLM Capability Prober"""
    
    def __init__(self):
        super().__init__()
        self.name = "Capability Prober"
        self.description = "Probe LLM capabilities and features"
        self.author = "Scott Thornton"
        self.module_type = "fingerprint"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/chat", required=True, description="Target LLM API endpoint"),
            "PROBE_TYPE": Option(value="all", required=False, description="Capability to probe",
                               enum_values=["all", "function_calling", "code_execution", "multimodal", "rag", "tools"]),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute capability probing"""
        target_url = self.options["TARGET_URL"].value
        probe_type = self.options["PROBE_TYPE"].value
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("capability_prober.run", url=target_url, type=probe_type)
        
        capabilities = []
        
        if probe_type in ["all", "function_calling"]:
            if self._probe_function_calling(target_url, timeout, api_key):
                capabilities.append("function_calling")
        
        if probe_type in ["all", "code_execution"]:
            if self._probe_code_execution(target_url, timeout, api_key):
                capabilities.append("code_execution")
        
        if probe_type in ["all", "multimodal"]:
            if self._probe_multimodal(target_url, timeout, api_key):
                capabilities.append("multimodal")
        
        if probe_type in ["all", "rag"]:
            if self._probe_rag(target_url, timeout, api_key):
                capabilities.append("rag")
        
        if probe_type in ["all", "tools"]:
            tools = self._probe_tools(target_url, timeout, api_key)
            if tools:
                capabilities.append(f"tools({len(tools)})")
        
        return AuxiliaryResult(
            success=len(capabilities) > 0,
            output=f"Detected capabilities: {', '.join(capabilities)}" if capabilities else "No capabilities detected",
            discovered=[{"capability": cap} for cap in capabilities],
            details={"probe_type": probe_type, "total_capabilities": len(capabilities)}
        )
    
    def _probe_function_calling(self, url: str, timeout: int, api_key: str) -> bool:
        """Probe for function calling capability"""
        logger.info("probing_function_calling")
        
        headers = self._build_headers(api_key)
        
        # Test with function definition
        test_payload = {
            "messages": [{"role": "user", "content": "What's the weather in San Francisco?"}],
            "functions": [{
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }]
        }
        
        try:
            response = httpx.post(url, json=test_payload, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for function call in response
                if "function_call" in str(data).lower() or "tool_calls" in str(data).lower():
                    logger.info("function_calling_detected")
                    return True
                    
        except:
            pass
        
        return False
    
    def _probe_code_execution(self, url: str, timeout: int, api_key: str) -> bool:
        """Probe for code execution capability"""
        logger.info("probing_code_execution")
        
        headers = self._build_headers(api_key)
        
        # Test prompts that trigger code execution
        test_prompts = [
            "Calculate 123456 * 789012",
            "Write and execute Python code to sort this list: [5, 2, 8, 1]",
            "Run code to check if 17 is prime"
        ]
        
        for prompt in test_prompts:
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": prompt}]},
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = self._extract_response_text(response)
                    
                    # Check for code execution indicators
                    indicators = ["```python", "executed", "result:", "output:", "97418672"]
                    if any(indicator in response_text.lower() for indicator in indicators):
                        logger.info("code_execution_detected")
                        return True
                        
            except:
                continue
        
        return False
    
    def _probe_multimodal(self, url: str, timeout: int, api_key: str) -> bool:
        """Probe for multimodal (image/vision) capability"""
        logger.info("probing_multimodal")
        
        headers = self._build_headers(api_key)
        
        # Test with image reference
        test_payload = {
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KG"}}
                ]
            }]
        }
        
        try:
            response = httpx.post(url, json=test_payload, headers=headers, timeout=timeout)
            
            # If request is accepted (not 400), multimodal likely supported
            if response.status_code in [200, 201]:
                logger.info("multimodal_detected")
                return True
                
        except:
            pass
        
        return False
    
    def _probe_rag(self, url: str, timeout: int, api_key: str) -> bool:
        """Probe for RAG (retrieval) capability"""
        logger.info("probing_rag")
        
        headers = self._build_headers(api_key)
        
        # Test prompts that would trigger retrieval
        test_prompts = [
            "Search your knowledge base for information about X",
            "What do your documents say about Y?",
            "Retrieve information from the database"
        ]
        
        for prompt in test_prompts:
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": prompt}]},
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    response_text = self._extract_response_text(response)
                    
                    # Check for RAG indicators
                    indicators = ["retrieved", "searching", "found in", "according to", "sources", "documents"]
                    if any(indicator in response_text.lower() for indicator in indicators):
                        logger.info("rag_detected")
                        return True
                        
            except:
                continue
        
        return False
    
    def _probe_tools(self, url: str, timeout: int, api_key: str) -> List[str]:
        """Probe for available tools"""
        logger.info("probing_tools")
        
        headers = self._build_headers(api_key)
        tools = []
        
        # Try to get tools list
        base_url = url.rsplit("/", 1)[0]
        tool_endpoints = ["/tools", "/api/tools", "/v1/tools"]
        
        for endpoint in tool_endpoints:
            try:
                response = httpx.get(f"{base_url}{endpoint}", headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list):
                        tools = [t.get("name", str(t)) for t in data]
                    elif isinstance(data, dict) and "tools" in data:
                        tools = list(data["tools"].keys())
                    
                    if tools:
                        logger.info("tools_detected", count=len(tools))
                        return tools
                        
            except:
                continue
        
        # Try via prompt
        try:
            response = httpx.post(
                url,
                json={"messages": [{"role": "user", "content": "List all available tools"}]},
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                response_text = self._extract_response_text(response)
                
                # Parse tool names from response
                import re
                tool_pattern = r'\b([a-z_]+_tool|[A-Z][a-zA-Z]+Tool)\b'
                found_tools = re.findall(tool_pattern, response_text)
                
                if found_tools:
                    return list(set(found_tools))
                    
        except:
            pass
        
        return []
    
    def _extract_response_text(self, response: httpx.Response) -> str:
        """Extract text from various response formats"""
        try:
            data = response.json()
            
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            if "content" in data:
                if isinstance(data["content"], list):
                    return data["content"][0].get("text", "")
                return data["content"]
            if "response" in data:
                return data["response"]
            
            return response.text
        except:
            return response.text
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
