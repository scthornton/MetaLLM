"""
LLM Model Fingerprinting

Identifies the LLM model, version, and provider through behavioral analysis
and response patterns.

Category: Reconnaissance/Information Gathering
"""

import httpx
import re
import time
from typing import Optional, Dict, Any, List
from metallm.base import AuxiliaryModule, Option, OptionType, Result, ResultStatus, LLMTarget


class LLMFingerprint(AuxiliaryModule):
    """
    LLM Model Fingerprinting Module

    Identifies LLM models through various fingerprinting techniques:
        - Response timing analysis
        - Token limit detection
        - Format preference analysis
        - Error message patterns
        - Behavioral quirks
        - Knowledge cutoff detection
        - Capability testing
    """

    def __init__(self):
        super().__init__()

        # Metadata
        self.name = "LLM Model Fingerprinting"
        self.description = (
            "Identifies the LLM model, version, and provider through behavioral "
            "analysis, timing patterns, and response characteristics."
        )
        self.author = "Scott Thornton"

        # Options
        self.options = {
            "AGGRESSIVE": Option(
                required=False,
                description="Use aggressive fingerprinting (more requests, higher accuracy)",
                type=OptionType.BOOLEAN,
                default=False
            ),
            "TEST_CAPABILITIES": Option(
                required=False,
                description="Test specific model capabilities (multimodal, function calling, etc.)",
                type=OptionType.BOOLEAN,
                default=True
            ),
            "DETECT_PROVIDER": Option(
                required=False,
                description="Attempt to detect API provider (OpenAI, Anthropic, etc.)",
                type=OptionType.BOOLEAN,
                default=True
            ),
            "TIMING_ANALYSIS": Option(
                required=False,
                description="Perform timing analysis for model identification",
                type=OptionType.BOOLEAN,
                default=True
            ),
        }

        # Known model signatures
        self.model_signatures = {
            "gpt-4": {
                "capabilities": ["function_calling", "multimodal", "json_mode"],
                "knowledge_cutoff": "2023-04",
                "typical_response_time": (2.0, 5.0),
                "max_tokens": 8192,
                "quirks": ["uses oxford comma", "formal tone"]
            },
            "gpt-3.5-turbo": {
                "capabilities": ["function_calling", "json_mode"],
                "knowledge_cutoff": "2021-09",
                "typical_response_time": (0.5, 2.0),
                "max_tokens": 4096,
                "quirks": ["concise responses", "occasional hallucinations"]
            },
            "claude-3-opus": {
                "capabilities": ["multimodal", "long_context"],
                "knowledge_cutoff": "2023-08",
                "typical_response_time": (3.0, 7.0),
                "max_tokens": 4096,
                "quirks": ["thoughtful responses", "admits uncertainty"]
            },
            "claude-3-sonnet": {
                "capabilities": ["multimodal", "balanced_performance"],
                "knowledge_cutoff": "2023-08",
                "typical_response_time": (1.5, 4.0),
                "max_tokens": 4096,
                "quirks": ["balanced speed/quality"]
            },
            "llama-2": {
                "capabilities": ["open_source"],
                "knowledge_cutoff": "2023-09",
                "typical_response_time": (1.0, 3.0),
                "max_tokens": 4096,
                "quirks": ["meta attribution", "open source references"]
            },
        }

    def run(self) -> Result:
        """
        Execute model fingerprinting

        Returns:
            Result object with fingerprinting data
        """
        if not isinstance(self.target, LLMTarget):
            return Result(
                status=ResultStatus.ERROR,
                message="Target must be an LLMTarget",
                severity="info"
            )

        fingerprint_data = {
            "model_family": None,
            "model_version": None,
            "provider": None,
            "capabilities": [],
            "confidence": 0.0,
            "evidence": {},
        }

        # Provider detection
        if self.options["DETECT_PROVIDER"].value:
            provider_info = self._detect_provider()
            fingerprint_data.update(provider_info)

        # Knowledge cutoff detection
        cutoff_info = self._detect_knowledge_cutoff()
        fingerprint_data["evidence"]["knowledge_cutoff"] = cutoff_info

        # Timing analysis
        if self.options["TIMING_ANALYSIS"].value:
            timing_info = self._analyze_response_timing()
            fingerprint_data["evidence"]["timing_analysis"] = timing_info

        # Capability testing
        if self.options["TEST_CAPABILITIES"].value:
            capability_info = self._test_capabilities()
            fingerprint_data["capabilities"] = capability_info["detected"]
            fingerprint_data["evidence"]["capability_tests"] = capability_info

        # Behavioral analysis
        behavioral_info = self._analyze_behavior()
        fingerprint_data["evidence"]["behavioral_patterns"] = behavioral_info

        # Match against known signatures
        match_result = self._match_signatures(fingerprint_data)
        fingerprint_data.update(match_result)

        # Determine success
        if fingerprint_data["confidence"] >= 0.5:
            status = ResultStatus.SUCCESS
            message = f"Model identified: {fingerprint_data['model_family']} "
            if fingerprint_data["model_version"]:
                message += f"(version: {fingerprint_data['model_version']})"
            message += f" with {fingerprint_data['confidence']:.0%} confidence"
        else:
            status = ResultStatus.UNKNOWN
            message = "Could not confidently identify model"

        return Result(
            status=status,
            message=message,
            severity="info",
            data=fingerprint_data,
            evidence=[
                f"Provider: {fingerprint_data.get('provider', 'Unknown')}",
                f"Model family: {fingerprint_data.get('model_family', 'Unknown')}",
                f"Capabilities: {', '.join(fingerprint_data['capabilities'])}",
                f"Confidence: {fingerprint_data['confidence']:.0%}"
            ]
        )

    def _detect_provider(self) -> Dict[str, Any]:
        """Detect API provider through endpoint analysis and error patterns"""
        provider_info = {
            "provider": None,
            "provider_confidence": 0.0,
        }

        if not self.target:
            return provider_info

        target = self.target
        assert isinstance(target, LLMTarget)

        # Check URL patterns
        if target.url:
            url_lower = target.url.lower()

            if "openai.com" in url_lower or "api.openai" in url_lower:
                provider_info["provider"] = "OpenAI"
                provider_info["provider_confidence"] = 1.0
            elif "anthropic.com" in url_lower or "claude" in url_lower:
                provider_info["provider"] = "Anthropic"
                provider_info["provider_confidence"] = 1.0
            elif "together.ai" in url_lower or "together.xyz" in url_lower:
                provider_info["provider"] = "Together AI"
                provider_info["provider_confidence"] = 1.0
            elif "replicate.com" in url_lower:
                provider_info["provider"] = "Replicate"
                provider_info["provider_confidence"] = 1.0

        # Test error response format
        if provider_info["provider"] is None:
            error_pattern = self._test_error_format()
            if error_pattern:
                provider_info.update(error_pattern)

        return provider_info

    def _test_error_format(self) -> Optional[Dict[str, Any]]:
        """Test API error response format to identify provider"""
        try:
            # Send intentionally malformed request
            response = self._send_raw_request({"invalid": "request"})

            if not response:
                return None

            # OpenAI error format
            if "error" in response and "message" in response.get("error", {}):
                if "type" in response.get("error", {}):
                    return {
                        "provider": "OpenAI",
                        "provider_confidence": 0.8
                    }

            # Anthropic error format
            if "error" in response and "type" in response.get("error", {}):
                if response["error"]["type"] in ["invalid_request_error", "authentication_error"]:
                    return {
                        "provider": "Anthropic",
                        "provider_confidence": 0.8
                    }

            return None

        except Exception:
            return None

    def _detect_knowledge_cutoff(self) -> Dict[str, Any]:
        """Detect model's knowledge cutoff date"""
        cutoff_info = {
            "estimated_cutoff": None,
            "cutoff_confidence": 0.0,
        }

        # Test questions about events in different time periods
        test_questions = [
            ("What happened on October 7, 2023?", "2023-10"),
            ("Who won the 2023 World Series?", "2023-11"),
            ("What are the latest features in GPT-4 Turbo?", "2023-12"),
            ("What happened in the 2024 US presidential election?", "2024-11"),
        ]

        for question, event_date in test_questions:
            try:
                response = self._send_simple_request(question)

                if not response:
                    continue

                response_lower = response.lower()

                # Check for knowledge indicators
                if any(phrase in response_lower for phrase in [
                    "don't have information",
                    "knowledge cutoff",
                    "not aware of",
                    "after my training",
                    "i don't know"
                ]):
                    # Model doesn't know about this event
                    cutoff_info["estimated_cutoff"] = event_date
                    cutoff_info["cutoff_confidence"] = 0.7
                    break

            except Exception:
                continue

        return cutoff_info

    def _analyze_response_timing(self) -> Dict[str, Any]:
        """Analyze response timing patterns"""
        timing_info = {
            "avg_response_time": 0.0,
            "response_times": [],
        }

        # Send multiple requests and measure timing
        test_prompts = [
            "Hello, how are you?",
            "Explain quantum computing in one sentence.",
            "What is the capital of France?",
        ]

        for prompt in test_prompts:
            try:
                start_time = time.time()
                response = self._send_simple_request(prompt)
                end_time = time.time()

                if response:
                    response_time = end_time - start_time
                    timing_info["response_times"].append(response_time)

            except Exception:
                continue

        if timing_info["response_times"]:
            timing_info["avg_response_time"] = sum(timing_info["response_times"]) / len(timing_info["response_times"])

        return timing_info

    def _test_capabilities(self) -> Dict[str, Any]:
        """Test specific model capabilities"""
        capability_info = {
            "detected": [],
            "tests": {},
        }

        # Test function calling
        function_test = self._test_function_calling()
        capability_info["tests"]["function_calling"] = function_test
        if function_test.get("supported"):
            capability_info["detected"].append("function_calling")

        # Test JSON mode
        json_test = self._test_json_mode()
        capability_info["tests"]["json_mode"] = json_test
        if json_test.get("supported"):
            capability_info["detected"].append("json_mode")

        # Test long context
        long_context_test = self._test_long_context()
        capability_info["tests"]["long_context"] = long_context_test
        if long_context_test.get("supported"):
            capability_info["detected"].append("long_context")

        return capability_info

    def _test_function_calling(self) -> Dict[str, Any]:
        """Test if model supports function calling"""
        # This is a simplified test
        # Real implementation would send actual function calling request
        return {
            "supported": False,
            "method": "api_test",
            "confidence": 0.5
        }

    def _test_json_mode(self) -> Dict[str, Any]:
        """Test if model supports JSON mode"""
        try:
            prompt = "Return the following in JSON format: name: John, age: 30, city: New York"
            response = self._send_simple_request(prompt)

            if response:
                # Check if response is valid JSON
                if response.strip().startswith("{") and response.strip().endswith("}"):
                    return {
                        "supported": True,
                        "confidence": 0.8
                    }

            return {
                "supported": False,
                "confidence": 0.6
            }

        except Exception:
            return {
                "supported": False,
                "confidence": 0.3
            }

    def _test_long_context(self) -> Dict[str, Any]:
        """Test long context window support"""
        # Simplified test - would need longer prompts in practice
        return {
            "supported": False,
            "method": "token_limit_probe",
            "confidence": 0.4
        }

    def _analyze_behavior(self) -> Dict[str, Any]:
        """Analyze behavioral patterns and quirks"""
        behavioral_info = {
            "tone": None,
            "formatting_style": None,
            "quirks": [],
        }

        try:
            # Ask a question that elicits personality
            prompt = "Explain machine learning in simple terms."
            response = self._send_simple_request(prompt)

            if not response:
                return behavioral_info

            response_lower = response.lower()

            # Analyze tone
            if any(word in response_lower for word in ["however", "moreover", "furthermore"]):
                behavioral_info["tone"] = "formal"
            elif any(word in response_lower for word in ["basically", "pretty much", "kind of"]):
                behavioral_info["tone"] = "casual"
            else:
                behavioral_info["tone"] = "neutral"

            # Check for specific quirks
            if response.count("\n") > 3:
                behavioral_info["quirks"].append("structured_formatting")

            if any(emoji in response for emoji in ["😊", "👍", "🎯"]):
                behavioral_info["quirks"].append("uses_emojis")

            if "i.e." in response_lower or "e.g." in response_lower:
                behavioral_info["quirks"].append("uses_latin_abbreviations")

        except Exception:
            pass

        return behavioral_info

    def _match_signatures(self, fingerprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match collected data against known model signatures"""
        match_scores = {}

        for model_name, signature in self.model_signatures.items():
            score = 0.0
            max_score = 0.0

            # Check capabilities
            if fingerprint_data.get("capabilities"):
                capability_matches = len(
                    set(fingerprint_data["capabilities"]) &
                    set(signature.get("capabilities", []))
                )
                score += capability_matches * 0.2
                max_score += len(signature.get("capabilities", [])) * 0.2

            # Check timing
            if fingerprint_data["evidence"].get("timing_analysis", {}).get("avg_response_time"):
                avg_time = fingerprint_data["evidence"]["timing_analysis"]["avg_response_time"]
                expected_range = signature.get("typical_response_time", (0, 10))

                if expected_range[0] <= avg_time <= expected_range[1]:
                    score += 0.3
                max_score += 0.3

            # Check provider
            if fingerprint_data.get("provider"):
                if model_name.startswith("gpt") and fingerprint_data["provider"] == "OpenAI":
                    score += 0.5
                elif model_name.startswith("claude") and fingerprint_data["provider"] == "Anthropic":
                    score += 0.5
                max_score += 0.5

            if max_score > 0:
                match_scores[model_name] = score / max_score

        # Find best match
        if match_scores:
            best_match = max(match_scores, key=match_scores.get)
            confidence = match_scores[best_match]

            return {
                "model_family": best_match,
                "model_version": None,  # Would need more sophisticated detection
                "confidence": confidence,
                "all_matches": match_scores
            }

        return {
            "model_family": "Unknown",
            "model_version": None,
            "confidence": 0.0,
            "all_matches": {}
        }

    def _send_simple_request(self, prompt: str) -> Optional[str]:
        """Send simple request to LLM"""
        if not self.target:
            return None

        target = self.target
        assert isinstance(target, LLMTarget)

        try:
            headers = {}
            if target.api_key:
                headers["Authorization"] = f"Bearer {target.api_key}"

            payload = {
                "prompt": prompt,
                "max_tokens": 150
            }

            if target.model_name:
                payload["model"] = target.model_name

            with httpx.Client() as client:
                response = client.post(
                    target.url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()

                    if "response" in data:
                        return data["response"]
                    elif "text" in data:
                        return data["text"]
                    elif "content" in data:
                        return data["content"]

                return None

        except Exception:
            return None

    def _send_raw_request(self, payload: Dict[str, Any]) -> Optional[Dict]:
        """Send raw request to API"""
        if not self.target:
            return None

        target = self.target
        assert isinstance(target, LLMTarget)

        try:
            headers = {}
            if target.api_key:
                headers["Authorization"] = f"Bearer {target.api_key}"

            with httpx.Client() as client:
                response = client.post(
                    target.url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                return response.json()

        except Exception:
            return None
