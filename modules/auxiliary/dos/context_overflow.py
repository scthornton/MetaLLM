"""
Context Overflow DoS Module

Tests LLM context window limits by sending requests that exceed maximum
context length, causing crashes, errors, or resource exhaustion.

Author: Scott Thornton (perfecXion.ai)
OWASP: LLM04 (Model Denial of Service)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class ContextOverflow(AuxiliaryModule):
    """Context Window Overflow Tester"""
    
    def __init__(self):
        super().__init__()
        self.name = "Context Overflow DoS"
        self.description = "Test context window overflow vulnerabilities"
        self.author = "Scott Thornton"
        self.module_type = "dos"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/chat", required=True, description="Target LLM API endpoint"),
            "OVERFLOW_TYPE": Option(value="single_message", required=True, description="Overflow technique",
                                  enum_values=["single_message", "message_history", "combined", "malformed"]),
            "CONTEXT_SIZE": Option(value="128000", required=False, description="Target context size (tokens)"),
            "TIMEOUT": Option(value="120", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute context overflow testing"""
        target_url = self.options["TARGET_URL"].value
        overflow_type = self.options["OVERFLOW_TYPE"].value
        context_size = int(self.options["CONTEXT_SIZE"].value)
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("context_overflow.run", url=target_url, type=overflow_type)
        
        if overflow_type == "single_message":
            results = self._overflow_single_message(target_url, context_size, timeout, api_key)
        elif overflow_type == "message_history":
            results = self._overflow_message_history(target_url, context_size, timeout, api_key)
        elif overflow_type == "combined":
            results = self._overflow_combined(target_url, context_size, timeout, api_key)
        else:
            results = self._overflow_malformed(target_url, timeout, api_key)
        
        return AuxiliaryResult(
            success=True,
            output=f"Context overflow test: {results.get('status', 'completed')}",
            discovered=[],
            details=results
        )
    
    def _overflow_single_message(self, url: str, target_tokens: int, 
                                 timeout: int, api_key: str) -> Dict:
        """Overflow with single extremely long message"""
        logger.info("single_message_overflow")
        
        headers = self._build_headers(api_key)
        results = {
            "overflow_type": "single_message",
            "target_tokens": target_tokens,
            "attempts": []
        }
        
        # Generate increasingly large messages
        # Approximate: 1 token = 4 characters
        token_sizes = [1000, 5000, 10000, 32000, 64000, 128000, 256000]
        
        for token_count in token_sizes:
            if token_count > target_tokens:
                break
            
            # Generate message of approximate token size
            char_count = token_count * 4
            message = "X" * char_count
            
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": message}]},
                    headers=headers,
                    timeout=timeout
                )
                
                attempt_result = {
                    "token_count": token_count,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "error": None
                }
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        attempt_result["error"] = error_data.get("error", {}).get("message", response.text[:100])
                    except:
                        attempt_result["error"] = response.text[:100]
                
                results["attempts"].append(attempt_result)
                logger.info("overflow_attempt", tokens=token_count, status=response.status_code)
                
                if response.status_code != 200:
                    results["overflow_threshold"] = token_count
                    results["status"] = "overflow_detected"
                    break
                    
            except Exception as e:
                results["attempts"].append({
                    "token_count": token_count,
                    "success": False,
                    "error": str(e)
                })
                results["overflow_threshold"] = token_count
                results["status"] = "connection_failed"
                break
        
        return results
    
    def _overflow_message_history(self, url: str, target_tokens: int,
                                  timeout: int, api_key: str) -> Dict:
        """Overflow with long message history"""
        logger.info("message_history_overflow")
        
        headers = self._build_headers(api_key)
        results = {
            "overflow_type": "message_history",
            "target_tokens": target_tokens,
            "attempts": []
        }
        
        # Test with increasing message counts
        message_counts = [10, 50, 100, 500, 1000, 5000]
        
        for msg_count in message_counts:
            # Generate alternating user/assistant messages
            messages = []
            for i in range(msg_count):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({
                    "role": role,
                    "content": f"This is message number {i} with some additional content to increase token count. " * 5
                })
            
            try:
                response = httpx.post(
                    url,
                    json={"messages": messages},
                    headers=headers,
                    timeout=timeout
                )
                
                attempt_result = {
                    "message_count": msg_count,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "error": None
                }
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        attempt_result["error"] = error_data.get("error", {}).get("message", response.text[:100])
                    except:
                        attempt_result["error"] = response.text[:100]
                
                results["attempts"].append(attempt_result)
                logger.info("history_overflow_attempt", messages=msg_count, status=response.status_code)
                
                if response.status_code != 200:
                    results["overflow_threshold"] = msg_count
                    results["status"] = "overflow_detected"
                    break
                    
            except Exception as e:
                results["attempts"].append({
                    "message_count": msg_count,
                    "success": False,
                    "error": str(e)
                })
                results["overflow_threshold"] = msg_count
                results["status"] = "connection_failed"
                break
        
        return results
    
    def _overflow_combined(self, url: str, target_tokens: int,
                          timeout: int, api_key: str) -> Dict:
        """Overflow with combination of long history and long messages"""
        logger.info("combined_overflow")
        
        headers = self._build_headers(api_key)
        results = {
            "overflow_type": "combined",
            "target_tokens": target_tokens,
            "attempts": []
        }
        
        # Combinations of (message_count, chars_per_message)
        combinations = [
            (10, 1000),
            (50, 5000),
            (100, 10000),
            (500, 20000)
        ]
        
        for msg_count, chars in combinations:
            messages = []
            for i in range(msg_count):
                role = "user" if i % 2 == 0 else "assistant"
                content = "X" * chars
                messages.append({"role": role, "content": content})
            
            estimated_tokens = (msg_count * chars) // 4
            
            try:
                response = httpx.post(
                    url,
                    json={"messages": messages},
                    headers=headers,
                    timeout=timeout
                )
                
                attempt_result = {
                    "message_count": msg_count,
                    "chars_per_message": chars,
                    "estimated_tokens": estimated_tokens,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                results["attempts"].append(attempt_result)
                logger.info("combined_overflow_attempt", 
                          messages=msg_count, 
                          chars=chars,
                          status=response.status_code)
                
                if response.status_code != 200:
                    results["status"] = "overflow_detected"
                    break
                    
            except Exception as e:
                results["attempts"].append({
                    "message_count": msg_count,
                    "chars_per_message": chars,
                    "success": False,
                    "error": str(e)
                })
                results["status"] = "connection_failed"
                break
        
        return results
    
    def _overflow_malformed(self, url: str, timeout: int, api_key: str) -> Dict:
        """Test with malformed/edge-case context"""
        logger.info("malformed_overflow")
        
        headers = self._build_headers(api_key)
        results = {
            "overflow_type": "malformed",
            "test_cases": []
        }
        
        # Various malformed/edge-case payloads
        test_cases = [
            {
                "name": "null_content",
                "payload": {"messages": [{"role": "user", "content": None}]}
            },
            {
                "name": "empty_messages",
                "payload": {"messages": []}
            },
            {
                "name": "nested_messages",
                "payload": {"messages": [{"role": "user", "content": {"nested": "object"}}]}
            },
            {
                "name": "unicode_overflow",
                "payload": {"messages": [{"role": "user", "content": "🚀" * 100000}]}
            },
            {
                "name": "newline_flood",
                "payload": {"messages": [{"role": "user", "content": "\n" * 100000}]}
            }
        ]
        
        for test in test_cases:
            try:
                response = httpx.post(
                    url,
                    json=test["payload"],
                    headers=headers,
                    timeout=timeout
                )
                
                test_result = {
                    "test_name": test["name"],
                    "status_code": response.status_code,
                    "vulnerable": response.status_code >= 500
                }
                
                results["test_cases"].append(test_result)
                logger.info("malformed_test", name=test["name"], status=response.status_code)
                
            except Exception as e:
                results["test_cases"].append({
                    "test_name": test["name"],
                    "error": str(e),
                    "vulnerable": True
                })
        
        return results
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
