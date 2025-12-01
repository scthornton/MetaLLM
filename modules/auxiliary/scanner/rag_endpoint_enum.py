"""
RAG Endpoint Enumeration Module

Enumerates RAG (Retrieval Augmented Generation) system endpoints including
vector databases, embedding APIs, retrieval endpoints, and document stores.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class RAGEndpointEnum(AuxiliaryModule):
    """RAG System Endpoint Enumerator"""
    
    def __init__(self):
        super().__init__()
        self.name = "RAG Endpoint Enumeration"
        self.description = "Enumerate RAG system components and endpoints"
        self.author = "Scott Thornton"
        self.module_type = "scanner"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "TARGET_PORT": Option(value="8000", required=False, description="Target port (or range)"),
            "COMPONENT_TYPE": Option(value="all", required=False, description="Component to scan",
                                   enum_values=["all", "vector_db", "embedding", "retrieval", "document_store"]),
            "TIMEOUT": Option(value="10", required=False, description="Request timeout"),
            "ENUM_COLLECTIONS": Option(value="true", required=False, description="Enumerate collections/indexes")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute RAG endpoint enumeration"""
        target_host = self.options["TARGET_HOST"].value
        target_port = self.options["TARGET_PORT"].value
        component_type = self.options["COMPONENT_TYPE"].value
        timeout = int(self.options["TIMEOUT"].value)
        enum_collections = self.options["ENUM_COLLECTIONS"].value.lower() == "true"
        
        logger.info("rag_endpoint_enum.run", host=target_host, component=component_type)
        
        discovered_endpoints = []
        
        # Parse ports
        if "-" in target_port:
            start_port, end_port = map(int, target_port.split("-"))
            ports = range(start_port, end_port + 1)
        else:
            ports = [int(target_port)]
        
        # Get component detection rules
        components = self._get_component_rules(component_type)
        
        for port in ports:
            for comp_name, rules in components.items():
                results = self._scan_component(
                    target_host, port, comp_name, rules, timeout, enum_collections
                )
                if results:
                    discovered_endpoints.extend(results)
                    logger.info("rag_component_found", component=comp_name, port=port)
        
        return AuxiliaryResult(
            success=len(discovered_endpoints) > 0,
            output=f"Enumerated {len(discovered_endpoints)} RAG endpoint(s)",
            discovered=discovered_endpoints,
            details={"ports_scanned": len(ports), "component_types": len(components)}
        )
    
    def _get_component_rules(self, component_type: str) -> Dict[str, Dict]:
        """Get component detection rules"""
        all_components = {
            "Pinecone": {
                "type": "vector_db",
                "paths": ["/", "/describe_index_stats"],
                "indicators": ["pinecone"],
                "default_port": 443
            },
            "Weaviate": {
                "type": "vector_db",
                "paths": ["/v1", "/v1/schema", "/v1/.well-known/ready"],
                "indicators": ["weaviate"],
                "default_port": 8080
            },
            "Qdrant": {
                "type": "vector_db",
                "paths": ["/", "/collections", "/health"],
                "indicators": ["qdrant"],
                "default_port": 6333
            },
            "Milvus": {
                "type": "vector_db",
                "paths": ["/", "/api/v1/health"],
                "indicators": ["milvus"],
                "default_port": 19530
            },
            "ChromaDB": {
                "type": "vector_db",
                "paths": ["/", "/api/v1/heartbeat", "/api/v1/collections"],
                "indicators": ["chroma"],
                "default_port": 8000
            },
            "ElasticsearchVector": {
                "type": "vector_db",
                "paths": ["/", "/_cluster/health", "/_cat/indices"],
                "indicators": ["elasticsearch", "elastic"],
                "default_port": 9200
            },
            "EmbeddingAPI": {
                "type": "embedding",
                "paths": ["/v1/embeddings", "/api/embed", "/embed"],
                "indicators": ["embedding", "encode"],
                "default_port": 8000
            },
            "RetrievalAPI": {
                "type": "retrieval",
                "paths": ["/api/retrieve", "/retrieve", "/search", "/query"],
                "indicators": ["retrieve", "search", "query"],
                "default_port": 8000
            },
            "DocumentStore": {
                "type": "document_store",
                "paths": ["/documents", "/api/documents", "/store"],
                "indicators": ["document", "store", "upload"],
                "default_port": 8000
            }
        }
        
        if component_type == "all":
            return all_components
        else:
            # Filter by component type
            return {k: v for k, v in all_components.items() 
                   if v["type"] == component_type}
    
    def _scan_component(self, host: str, port: int, comp_name: str,
                       rules: Dict, timeout: int, enum_collections: bool) -> List[Dict[str, Any]]:
        """Scan for a specific RAG component"""
        results = []
        
        for path in rules["paths"]:
            url = f"http://{host}:{port}{path}"
            
            try:
                response = httpx.get(url, timeout=timeout, follow_redirects=True)
                
                if response.status_code in [200, 201]:
                    body_lower = response.text.lower()
                    
                    # Check for component indicators
                    matches = sum(1 for indicator in rules["indicators"]
                                if indicator.lower() in body_lower)
                    
                    if matches > 0 or self._check_response_structure(response, rules["type"]):
                        endpoint_info = {
                            "component": comp_name,
                            "type": rules["type"],
                            "url": url,
                            "status_code": response.status_code,
                            "confidence": "high" if matches >= 1 else "medium"
                        }
                        
                        # Try to enumerate collections/indexes
                        if enum_collections and rules["type"] == "vector_db":
                            collections = self._enumerate_collections(host, port, comp_name, timeout)
                            if collections:
                                endpoint_info["collections"] = collections
                        
                        # Check for authentication
                        endpoint_info["requires_auth"] = self._check_auth_required(url, timeout)
                        
                        # Extract metadata
                        metadata = self._extract_metadata(response, comp_name)
                        if metadata:
                            endpoint_info["metadata"] = metadata
                        
                        results.append(endpoint_info)
                        
            except:
                continue
        
        return results
    
    def _check_response_structure(self, response: httpx.Response, comp_type: str) -> bool:
        """Check if response structure matches expected component type"""
        try:
            data = response.json()
            
            if comp_type == "vector_db":
                # Look for vector DB specific fields
                return any(key in data for key in ["collections", "indexes", "vectors", "dimension"])
            elif comp_type == "embedding":
                return any(key in data for key in ["embeddings", "vectors", "model"])
            elif comp_type == "retrieval":
                return any(key in data for key in ["results", "documents", "matches"])
            
        except:
            pass
        
        return False
    
    def _enumerate_collections(self, host: str, port: int, comp_name: str, timeout: int) -> List[str]:
        """Enumerate collections/indexes for vector databases"""
        collections = []
        
        # Collection endpoints by database type
        collection_paths = {
            "Weaviate": "/v1/schema",
            "Qdrant": "/collections",
            "ChromaDB": "/api/v1/collections",
            "Milvus": "/api/v1/collections",
            "ElasticsearchVector": "/_cat/indices"
        }
        
        if comp_name in collection_paths:
            url = f"http://{host}:{port}{collection_paths[comp_name]}"
            
            try:
                response = httpx.get(url, timeout=timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Extract collection names based on DB type
                        if comp_name == "Weaviate":
                            collections = [c["class"] for c in data.get("classes", [])]
                        elif comp_name == "Qdrant":
                            collections = [c["name"] for c in data.get("result", {}).get("collections", [])]
                        elif comp_name == "ChromaDB":
                            collections = [c["name"] for c in data]
                        elif comp_name == "ElasticsearchVector":
                            # Parse text response
                            collections = [line.split()[2] for line in response.text.strip().split("\n")]
                            
                    except:
                        pass
                        
            except:
                pass
        
        return collections
    
    def _check_auth_required(self, url: str, timeout: int) -> bool:
        """Check if authentication is required"""
        try:
            response = httpx.get(url, timeout=timeout)
            return response.status_code in [401, 403]
        except:
            return False
    
    def _extract_metadata(self, response: httpx.Response, comp_name: str) -> Dict[str, Any]:
        """Extract metadata from response"""
        metadata = {}
        
        try:
            data = response.json()
            
            # Extract version if available
            if "version" in data:
                metadata["version"] = data["version"]
            
            # Extract dimension for vector DBs
            if "dimension" in data:
                metadata["dimension"] = data["dimension"]
            
            # Extract model info for embedding APIs
            if "model" in data:
                metadata["model"] = data["model"]
            
            # Extract count/size info
            if "count" in data:
                metadata["count"] = data["count"]
            if "size" in data:
                metadata["size"] = data["size"]
                
        except:
            pass
        
        return metadata
