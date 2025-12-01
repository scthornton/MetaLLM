"""
Embedding Model Identification Module

Identifies embedding models used in RAG systems and vector databases by
analyzing embedding dimensions, cosine similarity patterns, and model signatures.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any, Optional
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class EmbeddingModelID(AuxiliaryModule):
    """Embedding Model Identifier"""
    
    def __init__(self):
        super().__init__()
        self.name = "Embedding Model Identification"
        self.description = "Identify embedding models used in RAG systems"
        self.author = "Scott Thornton"
        self.module_type = "fingerprint"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:8000/api/embed", required=True, description="Target embedding API endpoint"),
            "DETECTION_METHOD": Option(value="dimension", required=True, description="Detection method",
                                     enum_values=["dimension", "signature", "comprehensive"]),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute embedding model identification"""
        target_url = self.options["TARGET_URL"].value
        detection_method = self.options["DETECTION_METHOD"].value
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("embedding_model_id.run", url=target_url, method=detection_method)
        
        identified_model = None
        
        if detection_method in ["dimension", "comprehensive"]:
            dimension_result = self._identify_by_dimension(target_url, timeout, api_key)
            if dimension_result:
                identified_model = dimension_result
        
        if detection_method in ["signature", "comprehensive"]:
            signature_result = self._identify_by_signature(target_url, timeout, api_key)
            if signature_result:
                identified_model = signature_result
        
        return AuxiliaryResult(
            success=identified_model is not None,
            output=f"Embedding model: {identified_model.get('model', 'Unknown')}" if identified_model else "Model not identified",
            discovered=[identified_model] if identified_model else [],
            details={"detection_method": detection_method}
        )
    
    def _identify_by_dimension(self, url: str, timeout: int, api_key: str) -> Optional[Dict]:
        """Identify model by embedding dimension"""
        logger.info("identifying_by_dimension")
        
        headers = self._build_headers(api_key)
        
        # Test with sample text
        test_text = "This is a test sentence for embedding."
        
        try:
            response = httpx.post(
                url,
                json={"input": test_text},
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract embedding vector
                embedding = self._extract_embedding(data)
                
                if embedding:
                    dimension = len(embedding)
                    logger.info("embedding_dimension_detected", dimension=dimension)
                    
                    # Map dimension to known models
                    model = self._dimension_to_model(dimension)
                    
                    if model:
                        return {
                            "model": model,
                            "dimension": dimension,
                            "confidence": "high" if len(model) == 1 else "medium",
                            "method": "dimension_analysis"
                        }
                        
        except:
            pass
        
        return None
    
    def _identify_by_signature(self, url: str, timeout: int, api_key: str) -> Optional[Dict]:
        """Identify model by API signature"""
        logger.info("identifying_by_signature")
        
        headers = self._build_headers(api_key)
        
        # Try to get model info from API
        model_endpoints = [
            url.replace("/embed", "/models"),
            url.replace("/embeddings", "/models"),
            url + "/models"
        ]
        
        for endpoint in model_endpoints:
            try:
                response = httpx.get(endpoint, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract model name
                    model_name = self._extract_model_name(data)
                    
                    if model_name:
                        return {
                            "model": model_name,
                            "confidence": "high",
                            "method": "api_signature"
                        }
                        
            except:
                continue
        
        # Try to infer from response structure
        try:
            response = httpx.post(
                url,
                json={"input": "test"},
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure for provider signatures
                provider = self._identify_provider(data)
                
                if provider:
                    return {
                        "provider": provider,
                        "confidence": "medium",
                        "method": "response_structure"
                    }
                    
        except:
            pass
        
        return None
    
    def _extract_embedding(self, data: Dict) -> Optional[List[float]]:
        """Extract embedding vector from response"""
        # OpenAI format
        if "data" in data and isinstance(data["data"], list):
            if "embedding" in data["data"][0]:
                return data["data"][0]["embedding"]
        
        # Cohere format
        if "embeddings" in data:
            if isinstance(data["embeddings"], list) and data["embeddings"]:
                return data["embeddings"][0]
        
        # HuggingFace format
        if "embedding" in data:
            return data["embedding"]
        
        # Generic format
        if isinstance(data, list):
            return data
        
        return None
    
    def _dimension_to_model(self, dimension: int) -> str:
        """Map embedding dimension to known models"""
        dimension_map = {
            384: "all-MiniLM-L6-v2 / sentence-transformers-384",
            512: "BERT-base / DistilBERT",
            768: "BERT-large / RoBERTa-base / GPT-2",
            1024: "BERT-large-cased / RoBERTa-large",
            1536: "OpenAI text-embedding-ada-002",
            2048: "OpenAI text-embedding-3-small",
            3072: "OpenAI text-embedding-3-large",
            4096: "Cohere embed-english-v3.0",
            8192: "Cohere embed-english-v3.0 (compressed)"
        }
        
        return dimension_map.get(dimension, f"Unknown (dimension: {dimension})")
    
    def _extract_model_name(self, data: Dict) -> Optional[str]:
        """Extract model name from API response"""
        # Direct model field
        if "model" in data:
            return data["model"]
        
        # Models list
        if "data" in data and isinstance(data["data"], list):
            if data["data"] and "id" in data["data"][0]:
                return data["data"][0]["id"]
        
        # Object type field (sometimes contains model info)
        if "object" in data and "embedding" in str(data["object"]).lower():
            return data.get("model", "embedding_model")
        
        return None
    
    def _identify_provider(self, data: Dict) -> Optional[str]:
        """Identify provider from response structure"""
        # OpenAI signature
        if "data" in data and "object" in data and data["object"] == "list":
            if isinstance(data["data"], list) and data["data"]:
                if "embedding" in data["data"][0] and "index" in data["data"][0]:
                    return "OpenAI"
        
        # Cohere signature
        if "embeddings" in data and "id" in data:
            return "Cohere"
        
        # HuggingFace signature
        if "embedding" in data or "embeddings" in data:
            if "model" not in data:  # Usually HF doesn't include model in response
                return "HuggingFace"
        
        # Sentence Transformers signature
        if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data[:10]):
            return "Sentence-Transformers"
        
        return None
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
        
        return headers
