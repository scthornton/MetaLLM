"""
Rate Limit Testing Module

Tests rate limiting implementations on LLM APIs to identify thresholds,
bypass techniques, and DoS potential through rate limit exhaustion.

Author: Scott Thornton (perfecXion.ai)
OWASP: LLM04 (Model Denial of Service)
"""

import httpx
import time
import asyncio
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class RateLimitTest(AuxiliaryModule):
    """Rate Limit Tester"""
    
    def __init__(self):
        super().__init__()
        self.name = "Rate Limit Testing"
        self.description = "Test rate limiting implementations"
        self.author = "Scott Thornton"
        self.module_type = "dos"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/chat", required=True, description="Target LLM API endpoint"),
            "TEST_TYPE": Option(value="threshold", required=True, description="Test type",
                              enum_values=["threshold", "burst", "sustained", "bypass"]),
            "MAX_REQUESTS": Option(value="100", required=False, description="Maximum requests to send"),
            "CONCURRENT": Option(value="10", required=False, description="Concurrent requests"),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute rate limit testing"""
        target_url = self.options["TARGET_URL"].value
        test_type = self.options["TEST_TYPE"].value
        max_requests = int(self.options["MAX_REQUESTS"].value)
        concurrent = int(self.options["CONCURRENT"].value)
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("rate_limit_test.run", url=target_url, type=test_type)
        
        if test_type == "threshold":
            results = self._test_threshold(target_url, max_requests, timeout, api_key)
        elif test_type == "burst":
            results = self._test_burst(target_url, max_requests, concurrent, timeout, api_key)
        elif test_type == "sustained":
            results = self._test_sustained(target_url, max_requests, timeout, api_key)
        else:
            results = self._test_bypass(target_url, max_requests, timeout, api_key)
        
        return AuxiliaryResult(
            success=True,
            output=f"Rate limit test: {results.get('rate_limit_found', False)}",
            discovered=[],
            details=results
        )
    
    def _test_threshold(self, url: str, max_requests: int, timeout: int, api_key: str) -> Dict:
        """Find rate limit threshold"""
        logger.info("testing_rate_limit_threshold")
        
        headers = self._build_headers(api_key)
        results = {
            "test_type": "threshold",
            "requests_sent": 0,
            "requests_before_limit": 0,
            "rate_limit_found": False,
            "rate_limit_status_code": None,
            "rate_limit_headers": {},
            "reset_time": None
        }
        
        for i in range(max_requests):
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": "test"}]},
                    headers=headers,
                    timeout=timeout
                )
                
                results["requests_sent"] += 1
                
                if response.status_code == 429:
                    # Rate limit hit
                    results["rate_limit_found"] = True
                    results["requests_before_limit"] = i
                    results["rate_limit_status_code"] = 429
                    
                    # Extract rate limit headers
                    rate_limit_headers = {}
                    for header in ["x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after"]:
                        if header in response.headers:
                            rate_limit_headers[header] = response.headers[header]
                    
                    results["rate_limit_headers"] = rate_limit_headers
                    
                    if "retry-after" in response.headers:
                        results["reset_time"] = response.headers["retry-after"]
                    
                    logger.info("rate_limit_threshold_found", requests=i, headers=rate_limit_headers)
                    break
                
                elif response.status_code == 200:
                    # Log rate limit info if available
                    if "x-ratelimit-remaining" in response.headers:
                        remaining = response.headers["x-ratelimit-remaining"]
                        logger.info("rate_limit_remaining", remaining=remaining, request=i+1)
                
                time.sleep(0.1)  # Small delay between requests
                
            except Exception as e:
                logger.error("threshold_test_error", error=str(e))
                break
        
        if not results["rate_limit_found"]:
            results["requests_before_limit"] = results["requests_sent"]
        
        return results
    
    def _test_burst(self, url: str, max_requests: int, concurrent: int, 
                   timeout: int, api_key: str) -> Dict:
        """Test burst rate limiting with concurrent requests"""
        logger.info("testing_burst_rate_limit")
        
        headers = self._build_headers(api_key)
        results = {
            "test_type": "burst",
            "total_requests": 0,
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "burst_size": concurrent,
            "rate_limit_found": False
        }
        
        # Send requests in bursts
        bursts = max_requests // concurrent
        
        for burst_num in range(bursts):
            burst_results = []
            
            # Send concurrent requests
            for i in range(concurrent):
                try:
                    response = httpx.post(
                        url,
                        json={"messages": [{"role": "user", "content": f"burst test {burst_num}-{i}"}]},
                        headers=headers,
                        timeout=timeout
                    )
                    
                    results["total_requests"] += 1
                    
                    if response.status_code == 200:
                        results["successful_requests"] += 1
                    elif response.status_code == 429:
                        results["rate_limited_requests"] += 1
                        results["rate_limit_found"] = True
                    
                    burst_results.append(response.status_code)
                    
                except Exception as e:
                    logger.error("burst_test_error", error=str(e))
            
            logger.info("burst_completed", burst=burst_num+1, results=burst_results)
            
            # Small delay between bursts
            time.sleep(1)
        
        return results
    
    def _test_sustained(self, url: str, max_requests: int, timeout: int, api_key: str) -> Dict:
        """Test sustained rate limit with consistent request rate"""
        logger.info("testing_sustained_rate_limit")
        
        headers = self._build_headers(api_key)
        results = {
            "test_type": "sustained",
            "total_requests": 0,
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "rate_limit_found": False,
            "requests_per_minute": 0
        }
        
        start_time = time.time()
        
        for i in range(max_requests):
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": f"sustained test {i}"}]},
                    headers=headers,
                    timeout=timeout
                )
                
                results["total_requests"] += 1
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                elif response.status_code == 429:
                    results["rate_limited_requests"] += 1
                    results["rate_limit_found"] = True
                
                # Maintain consistent rate (1 request per second)
                time.sleep(1)
                
            except Exception as e:
                logger.error("sustained_test_error", error=str(e))
        
        elapsed_time = time.time() - start_time
        results["requests_per_minute"] = (results["total_requests"] / elapsed_time) * 60
        
        return results
    
    def _test_bypass(self, url: str, max_requests: int, timeout: int, api_key: str) -> Dict:
        """Test rate limit bypass techniques"""
        logger.info("testing_rate_limit_bypass")
        
        results = {
            "test_type": "bypass",
            "techniques_tested": [],
            "successful_bypasses": []
        }
        
        # Technique 1: Different User-Agent headers
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "curl/7.68.0"
        ]
        
        for ua in user_agents:
            headers = self._build_headers(api_key)
            headers["User-Agent"] = ua
            
            technique = f"user_agent_{ua[:20]}"
            results["techniques_tested"].append(technique)
            
            try:
                # Send multiple requests with this UA
                success_count = 0
                for i in range(5):
                    response = httpx.post(
                        url,
                        json={"messages": [{"role": "user", "content": "test"}]},
                        headers=headers,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                
                if success_count >= 3:
                    results["successful_bypasses"].append(technique)
                    
            except:
                pass
        
        # Technique 2: X-Forwarded-For header rotation
        results["techniques_tested"].append("x_forwarded_for_rotation")
        
        try:
            success_count = 0
            for i in range(5):
                headers = self._build_headers(api_key)
                headers["X-Forwarded-For"] = f"192.168.1.{i}"
                
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": "test"}]},
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    success_count += 1
            
            if success_count >= 3:
                results["successful_bypasses"].append("x_forwarded_for_rotation")
                
        except:
            pass
        
        return results
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
