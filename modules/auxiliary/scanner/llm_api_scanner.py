"""
LLM API Scanner Module

Scans for LLM API endpoints including OpenAI, Anthropic, Google, Azure OpenAI,
and custom LLM deployments. Identifies version, authentication requirements,
and available models.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class LLMAPIScanner(AuxiliaryModule):
    """LLM API Endpoint Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "LLM API Scanner"
        self.description = "Scan for LLM API endpoints and enumerate capabilities"
        self.author = "Scott Thornton"
        self.module_type = "scanner"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "TARGET_PORT": Option(value="8000", required=False, description="Target port (or port range: 8000-8100)"),
            "SCAN_TYPE": Option(value="comprehensive", required=True, description="Scan depth", 
                              enum_values=["quick", "comprehensive", "stealth"]),
            "TIMEOUT": Option(value="10", required=False, description="Request timeout"),
            "CHECK_AUTH": Option(value="true", required=False, description="Check authentication requirements")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute LLM API scanning"""
        target_host = self.options["TARGET_HOST"].value
        target_port = self.options["TARGET_PORT"].value
        scan_type = self.options["SCAN_TYPE"].value
        timeout = int(self.options["TIMEOUT"].value)
        check_auth = self.options["CHECK_AUTH"].value.lower() == "true"
        
        logger.info("llm_api_scanner.run", host=target_host, scan_type=scan_type)
        
        discovered_endpoints = []
        
        # Parse port range
        if "-" in target_port:
            start_port, end_port = map(int, target_port.split("-"))
            ports = range(start_port, end_port + 1)
        else:
            ports = [int(target_port)]
        
        # Common LLM API paths
        api_paths = self._get_api_paths(scan_type)
        
        for port in ports:
            for path in api_paths:
                url = f"http://{target_host}:{port}{path}"
                
                try:
                    result = self._scan_endpoint(url, timeout, check_auth)
                    if result:
                        discovered_endpoints.append(result)
                        logger.info("llm_endpoint_found", url=url, type=result.get("type"))
                except:
                    continue
        
        return AuxiliaryResult(
            success=len(discovered_endpoints) > 0,
            output=f"Found {len(discovered_endpoints)} LLM API endpoint(s)",
            discovered=discovered_endpoints,
            details={"scan_type": scan_type, "ports_scanned": len(ports), "paths_tested": len(api_paths)}
        )
    
    def _get_api_paths(self, scan_type: str) -> List[str]:
        """Get API paths based on scan type"""
        quick_paths = [
            "/v1/chat/completions",
            "/v1/completions",
            "/api/chat",
            "/api/generate"
        ]
        
        comprehensive_paths = quick_paths + [
            "/v1/models",
            "/v1/engines",
            "/api/v1/chat",
            "/api/v1/completions",
            "/openai/deployments",
            "/azure/openai/deployments",
            "/chat",
            "/generate",
            "/inference",
            "/predict",
            "/llm/chat",
            "/llm/generate",
            "/ai/chat",
            "/ai/completions"
        ]
        
        if scan_type == "quick":
            return quick_paths
        else:
            return comprehensive_paths
    
    def _scan_endpoint(self, url: str, timeout: int, check_auth: bool) -> Dict[str, Any]:
        """Scan a single endpoint"""
        try:
            # Try GET first
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            
            if response.status_code in [200, 401, 403]:
                endpoint_info = {
                    "url": url,
                    "status_code": response.status_code,
                    "type": self._identify_llm_type(url, response),
                    "requires_auth": response.status_code in [401, 403]
                }
                
                # Try to extract version info
                if "server" in response.headers:
                    endpoint_info["server"] = response.headers["server"]
                
                # Check for API key headers
                if check_auth:
                    auth_info = self._check_authentication(url, timeout)
                    endpoint_info["auth_methods"] = auth_info
                
                # Try POST to detect chat endpoints
                try:
                    post_response = httpx.post(
                        url,
                        json={"messages": [{"role": "user", "content": "test"}]},
                        timeout=timeout
                    )
                    endpoint_info["accepts_post"] = True
                    endpoint_info["post_status"] = post_response.status_code
                except:
                    endpoint_info["accepts_post"] = False
                
                return endpoint_info
                
        except:
            return None
    
    def _identify_llm_type(self, url: str, response: httpx.Response) -> str:
        """Identify the type of LLM API"""
        url_lower = url.lower()
        body_lower = response.text.lower()
        
        if "openai" in url_lower or "openai" in body_lower:
            return "OpenAI"
        elif "anthropic" in url_lower or "claude" in body_lower:
            return "Anthropic"
        elif "azure" in url_lower:
            return "Azure OpenAI"
        elif "google" in url_lower or "palm" in url_lower or "gemini" in body_lower:
            return "Google"
        elif "huggingface" in url_lower:
            return "HuggingFace"
        elif "llama" in body_lower:
            return "LLaMA"
        elif "mistral" in body_lower:
            return "Mistral"
        else:
            return "Custom/Unknown"
    
    def _check_authentication(self, url: str, timeout: int) -> List[str]:
        """Check authentication methods"""
        auth_methods = []
        
        # Common auth headers
        auth_headers = [
            ("Authorization", "Bearer test"),
            ("X-API-Key", "test"),
            ("api-key", "test"),
            ("Ocp-Apim-Subscription-Key", "test")  # Azure
        ]
        
        for header_name, header_value in auth_headers:
            try:
                response = httpx.get(
                    url,
                    headers={header_name: header_value},
                    timeout=timeout
                )
                
                # If response changes with auth header, it's likely used
                if response.status_code not in [404, 405]:
                    auth_methods.append(header_name)
            except:
                continue
        
        return auth_methods
