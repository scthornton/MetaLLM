"""
LLM Model Detector Module

Detects which LLM model is being used by analyzing response patterns,
behavior, capabilities, and known model signatures.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any, Optional
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class LLMModelDetector(AuxiliaryModule):
    """LLM Model Detection and Fingerprinting"""
    
    def __init__(self):
        super().__init__()
        self.name = "LLM Model Detector"
        self.description = "Detect and fingerprint LLM models"
        self.author = "Scott Thornton"
        self.module_type = "fingerprint"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/chat", required=True, description="Target LLM API endpoint"),
            "DETECTION_METHOD": Option(value="comprehensive", required=True, description="Detection technique",
                                     enum_values=["comprehensive", "signature", "behavior", "metadata"]),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute LLM model detection"""
        target_url = self.options["TARGET_URL"].value
        detection_method = self.options["DETECTION_METHOD"].value
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("llm_model_detector.run", url=target_url, method=detection_method)
        
        detected_models = []
        
        if detection_method in ["comprehensive", "metadata"]:
            metadata_result = self._detect_via_metadata(target_url, timeout, api_key)
            if metadata_result:
                detected_models.append(metadata_result)
        
        if detection_method in ["comprehensive", "signature"]:
            signature_result = self._detect_via_signature(target_url, timeout, api_key)
            if signature_result:
                detected_models.append(signature_result)
        
        if detection_method in ["comprehensive", "behavior"]:
            behavior_result = self._detect_via_behavior(target_url, timeout, api_key)
            if behavior_result:
                detected_models.append(behavior_result)
        
        # Consolidate results
        final_detection = self._consolidate_detections(detected_models)
        
        return AuxiliaryResult(
            success=final_detection is not None,
            output=f"Model detected: {final_detection.get('model', 'Unknown')}" if final_detection else "No model detected",
            discovered=[final_detection] if final_detection else [],
            details={"detection_method": detection_method, "all_detections": detected_models}
        )
    
    def _detect_via_metadata(self, url: str, timeout: int, api_key: str) -> Optional[Dict]:
        """Detect model via API metadata"""
        logger.info("detecting_via_metadata")
        
        # Try common model list endpoints
        model_endpoints = [
            "/v1/models",
            "/v1/engines",
            "/models",
            "/api/models"
        ]
        
        base_url = url.rsplit("/", 1)[0]
        headers = self._build_headers(api_key)
        
        for endpoint in model_endpoints:
            try:
                response = httpx.get(f"{base_url}{endpoint}", headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Parse model information
                        if "data" in data and isinstance(data["data"], list):
                            models = [m.get("id") or m.get("name") for m in data["data"]]
                            if models:
                                return {
                                    "model": models[0],
                                    "all_models": models,
                                    "confidence": "high",
                                    "method": "metadata",
                                    "source": endpoint
                                }
                        elif "models" in data:
                            models = data["models"]
                            if models:
                                return {
                                    "model": models[0] if isinstance(models, list) else str(models),
                                    "confidence": "high",
                                    "method": "metadata"
                                }
                    except:
                        pass
            except:
                continue
        
        return None
    
    def _detect_via_signature(self, url: str, timeout: int, api_key: str) -> Optional[Dict]:
        """Detect model via response signatures"""
        logger.info("detecting_via_signature")
        
        # Signature test prompts
        test_prompts = [
            "What model are you?",
            "Tell me your model name and version",
            "What language model powers you?"
        ]
        
        headers = self._build_headers(api_key)
        
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
                    
                    # Check for model signatures
                    model = self._identify_from_response(response_text)
                    if model:
                        return {
                            "model": model,
                            "confidence": "medium",
                            "method": "signature",
                            "response_sample": response_text[:100]
                        }
            except:
                continue
        
        return None
    
    def _detect_via_behavior(self, url: str, timeout: int, api_key: str) -> Optional[Dict]:
        """Detect model via behavioral fingerprinting"""
        logger.info("detecting_via_behavior")
        
        # Behavioral test cases (model-specific behaviors)
        behavior_tests = [
            {
                "prompt": "Repeat the word 'test' exactly 10 times",
                "gpt4_behavior": "structured, counted list",
                "claude_behavior": "natural, may not count exactly",
                "llama_behavior": "variable formatting"
            },
            {
                "prompt": "Output JSON: {\"key\": \"value\"}",
                "gpt4_behavior": "clean JSON",
                "claude_behavior": "markdown-wrapped JSON",
                "llama_behavior": "may include explanation"
            }
        ]
        
        headers = self._build_headers(api_key)
        behavior_scores = {
            "gpt-4": 0,
            "gpt-3.5": 0,
            "claude": 0,
            "llama": 0,
            "mistral": 0
        }
        
        for test in behavior_tests:
            try:
                response = httpx.post(
                    url,
                    json={"messages": [{"role": "user", "content": test["prompt"]}]},
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    response_text = self._extract_response_text(response)
                    
                    # Score based on behavioral patterns
                    if "```json" in response_text.lower():
                        behavior_scores["claude"] += 1
                    if response_text.count("\n") > 5 and "1." in response_text:
                        behavior_scores["gpt-4"] += 1
                    if len(response_text) < 100:
                        behavior_scores["gpt-3.5"] += 1
                        
            except:
                continue
        
        # Find highest scoring model
        if max(behavior_scores.values()) > 0:
            detected_model = max(behavior_scores, key=behavior_scores.get)
            return {
                "model": detected_model,
                "confidence": "low",
                "method": "behavior",
                "scores": behavior_scores
            }
        
        return None
    
    def _identify_from_response(self, text: str) -> Optional[str]:
        """Identify model from response text"""
        text_lower = text.lower()
        
        # Model signatures
        signatures = {
            "gpt-4": ["gpt-4", "gpt 4", "chatgpt", "openai"],
            "gpt-3.5": ["gpt-3.5", "gpt 3.5", "chatgpt"],
            "claude": ["claude", "anthropic"],
            "llama": ["llama", "meta ai"],
            "mistral": ["mistral"],
            "palm": ["palm", "bard", "gemini"],
            "cohere": ["cohere", "command"]
        }
        
        for model, keywords in signatures.items():
            if any(keyword in text_lower for keyword in keywords):
                return model
        
        return None
    
    def _extract_response_text(self, response: httpx.Response) -> str:
        """Extract text from various response formats"""
        try:
            data = response.json()
            
            # OpenAI format
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            
            # Anthropic format
            if "content" in data:
                if isinstance(data["content"], list):
                    return data["content"][0].get("text", "")
                return data["content"]
            
            # Generic format
            if "response" in data:
                return data["response"]
            if "text" in data:
                return data["text"]
            
            return response.text
            
        except:
            return response.text
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
        
        return headers
    
    def _consolidate_detections(self, detections: List[Dict]) -> Optional[Dict]:
        """Consolidate multiple detection results"""
        if not detections:
            return None
        
        # Prioritize high confidence detections
        high_confidence = [d for d in detections if d.get("confidence") == "high"]
        if high_confidence:
            return high_confidence[0]
        
        # Otherwise return most common detection
        return detections[0]
