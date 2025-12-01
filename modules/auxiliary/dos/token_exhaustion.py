"""
Token Exhaustion DoS Module

Tests LLM endpoints for token exhaustion vulnerabilities by sending requests
that maximize token usage and drain token budgets.

Author: Scott Thornton (perfecXion.ai)
OWASP: LLM04 (Model Denial of Service)
"""

import httpx
import json
import time
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class TokenExhaustion(AuxiliaryModule):
    """Token Exhaustion DoS Tester"""
    
    def __init__(self):
        super().__init__()
        self.name = "Token Exhaustion DoS"
        self.description = "Test for token exhaustion vulnerabilities"
        self.author = "Scott Thornton"
        self.module_type = "dos"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/chat", required=True, description="Target LLM API endpoint"),
            "ATTACK_TYPE": Option(value="max_tokens", required=True, description="Exhaustion technique",
                                enum_values=["max_tokens", "long_input", "repeated_requests", "max_output"]),
            "REQUEST_COUNT": Option(value="10", required=False, description="Number of requests to send"),
            "TIMEOUT": Option(value="60", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute token exhaustion test"""
        target_url = self.options["TARGET_URL"].value
        attack_type = self.options["ATTACK_TYPE"].value
        request_count = int(self.options["REQUEST_COUNT"].value)
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("token_exhaustion.run", url=target_url, type=attack_type)
        
        if attack_type == "max_tokens":
            results = self._attack_max_tokens(target_url, request_count, timeout, api_key)
        elif attack_type == "long_input":
            results = self._attack_long_input(target_url, request_count, timeout, api_key)
        elif attack_type == "repeated_requests":
            results = self._attack_repeated_requests(target_url, request_count, timeout, api_key)
        else:
            results = self._attack_max_output(target_url, request_count, timeout, api_key)
        
        return AuxiliaryResult(
            success=True,
            output=f"Token exhaustion test: {results['successful_requests']}/{results['total_requests']} requests succeeded",
            discovered=[],
            details=results
        )
    
    def _attack_max_tokens(self, url: str, count: int, timeout: int, api_key: str) -> Dict:
        """Request maximum token generation"""
        logger.info("max_tokens_attack")
        
        headers = self._build_headers(api_key)
        results = {
            "attack_type": "max_tokens",
            "total_requests": count,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "errors": []
        }
        
        # Prompt designed to generate long responses
        prompt = "Write a comprehensive, detailed essay about artificial intelligence, covering its history, current applications, future potential, ethical considerations, and impact on society. Include specific examples and be as thorough as possible."
        
        for i in range(count):
            try:
                start_time = time.time()
                
                response = httpx.post(
                    url,
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4096  # Request maximum tokens
                    },
                    headers=headers,
                    timeout=timeout
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                    
                    # Try to extract token usage
                    try:
                        data = response.json()
                        if "usage" in data:
                            tokens = data["usage"].get("total_tokens", 0)
                            results["total_tokens"] += tokens
                    except:
                        pass
                else:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Request {i+1}: HTTP {response.status_code}")
                
                logger.info("max_tokens_request", request=i+1, status=response.status_code, time=elapsed)
                
            except Exception as e:
                results["failed_requests"] += 1
                results["errors"].append(f"Request {i+1}: {str(e)}")
        
        return results
    
    def _attack_long_input(self, url: str, count: int, timeout: int, api_key: str) -> Dict:
        """Send extremely long input to exhaust processing"""
        logger.info("long_input_attack")
        
        headers = self._build_headers(api_key)
        results = {
            "attack_type": "long_input",
            "total_requests": count,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors": []
        }
        
        # Generate very long input (repeat pattern to reach token limits)
        base_text = "This is a test sentence to fill the context window. " * 100
        long_prompt = base_text * 50  # Approximately 5000 words
        
        for i in range(count):
            try:
                start_time = time.time()
                
                response = httpx.post(
                    url,
                    json={
                        "messages": [{"role": "user", "content": long_prompt + f" Request {i+1}: Summarize this text."}]
                    },
                    headers=headers,
                    timeout=timeout
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                else:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Request {i+1}: HTTP {response.status_code}")
                
                logger.info("long_input_request", request=i+1, status=response.status_code, time=elapsed)
                
            except Exception as e:
                results["failed_requests"] += 1
                results["errors"].append(f"Request {i+1}: {str(e)}")
        
        return results
    
    def _attack_repeated_requests(self, url: str, count: int, timeout: int, api_key: str) -> Dict:
        """Send many requests in rapid succession"""
        logger.info("repeated_requests_attack")
        
        headers = self._build_headers(api_key)
        results = {
            "attack_type": "repeated_requests",
            "total_requests": count,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited": 0,
            "avg_response_time": 0,
            "errors": []
        }
        
        prompt = "Generate a creative story in 500 words."
        response_times = []
        
        for i in range(count):
            try:
                start_time = time.time()
                
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": prompt}]},
                    headers=headers,
                    timeout=timeout
                )
                
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                elif response.status_code == 429:
                    results["rate_limited"] += 1
                    results["errors"].append(f"Request {i+1}: Rate limited")
                else:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Request {i+1}: HTTP {response.status_code}")
                
                logger.info("repeated_request", request=i+1, status=response.status_code, time=elapsed)
                
                # No delay - send as fast as possible
                
            except Exception as e:
                results["failed_requests"] += 1
                results["errors"].append(f"Request {i+1}: {str(e)}")
        
        if response_times:
            results["avg_response_time"] = sum(response_times) / len(response_times)
        
        return results
    
    def _attack_max_output(self, url: str, count: int, timeout: int, api_key: str) -> Dict:
        """Request maximum output generation"""
        logger.info("max_output_attack")
        
        headers = self._build_headers(api_key)
        results = {
            "attack_type": "max_output",
            "total_requests": count,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors": []
        }
        
        # Prompts that encourage very long responses
        prompts = [
            "List every country in the world with detailed information about each.",
            "Write the longest possible response you can generate.",
            "Count from 1 to 1000 and explain each number.",
            "List 500 different facts about science.",
            "Generate 100 unique creative story ideas with full descriptions."
        ]
        
        for i in range(count):
            try:
                prompt = prompts[i % len(prompts)]
                start_time = time.time()
                
                response = httpx.post(
                    url,
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 8192  # Request very large output
                    },
                    headers=headers,
                    timeout=timeout
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                else:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Request {i+1}: HTTP {response.status_code}")
                
                logger.info("max_output_request", request=i+1, status=response.status_code, time=elapsed)
                
            except Exception as e:
                results["failed_requests"] += 1
                results["errors"].append(f"Request {i+1}: {str(e)}")
        
        return results
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
