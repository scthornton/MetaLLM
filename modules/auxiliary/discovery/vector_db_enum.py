"""
Vector Database Enumeration Module

Enumerates vector databases, collections, indexes, and stored embeddings.
Supports Pinecone, Weaviate, Qdrant, Milvus, ChromaDB, and more.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any, Optional
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class VectorDBEnum(AuxiliaryModule):
    """Vector Database Enumerator"""
    
    def __init__(self):
        super().__init__()
        self.name = "Vector Database Enumeration"
        self.description = "Enumerate vector databases and collections"
        self.author = "Scott Thornton"
        self.module_type = "discovery"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:6333", required=True, description="Vector DB URL"),
            "DB_TYPE": Option(value="auto", required=False, description="Database type",
                            enum_values=["auto", "qdrant", "weaviate", "chromadb", "milvus", "pinecone"]),
            "ENUM_DEPTH": Option(value="collections", required=False, description="Enumeration depth",
                               enum_values=["collections", "vectors", "metadata"]),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute vector database enumeration"""
        target_url = self.options["TARGET_URL"].value
        db_type = self.options["DB_TYPE"].value
        enum_depth = self.options["ENUM_DEPTH"].value
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("vector_db_enum.run", url=target_url, type=db_type)
        
        # Auto-detect database type if needed
        if db_type == "auto":
            db_type = self._detect_db_type(target_url, timeout, api_key)
            if not db_type:
                return AuxiliaryResult(
                    success=False,
                    output="Could not detect vector database type",
                    discovered=[]
                )
        
        # Enumerate based on database type
        enumeration_method = getattr(self, f"_enumerate_{db_type}", None)
        
        if enumeration_method:
            results = enumeration_method(target_url, enum_depth, timeout, api_key)
            
            return AuxiliaryResult(
                success=len(results) > 0,
                output=f"Enumerated {len(results)} collection(s) in {db_type}",
                discovered=results,
                details={"db_type": db_type, "enum_depth": enum_depth}
            )
        else:
            return AuxiliaryResult(
                success=False,
                output=f"Unsupported database type: {db_type}",
                discovered=[]
            )
    
    def _detect_db_type(self, url: str, timeout: int, api_key: str) -> Optional[str]:
        """Auto-detect vector database type"""
        headers = self._build_headers(api_key)
        
        # Detection signatures
        detections = [
            {"type": "qdrant", "path": "/collections", "indicator": "collections"},
            {"type": "weaviate", "path": "/v1/schema", "indicator": "classes"},
            {"type": "chromadb", "path": "/api/v1/heartbeat", "indicator": "nanosecond"},
            {"type": "milvus", "path": "/api/v1/health", "indicator": "milvus"}
        ]
        
        for detection in detections:
            try:
                response = httpx.get(f"{url}{detection['path']}", headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    if detection["indicator"] in response.text.lower():
                        logger.info("db_type_detected", type=detection["type"])
                        return detection["type"]
            except:
                continue
        
        return None
    
    def _enumerate_qdrant(self, url: str, depth: str, timeout: int, api_key: str) -> List[Dict]:
        """Enumerate Qdrant collections"""
        logger.info("enumerating_qdrant")
        
        headers = self._build_headers(api_key)
        results = []
        
        try:
            # Get collections list
            response = httpx.get(f"{url}/collections", headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get("result", {}).get("collections", [])
                
                for collection in collections:
                    collection_info = {
                        "db_type": "qdrant",
                        "collection_name": collection["name"]
                    }
                    
                    # Get detailed collection info
                    if depth in ["vectors", "metadata"]:
                        details = self._get_qdrant_collection_details(
                            url, collection["name"], headers, timeout
                        )
                        collection_info.update(details)
                    
                    results.append(collection_info)
                    
        except Exception as e:
            logger.error("qdrant_enum_error", error=str(e))
        
        return results
    
    def _get_qdrant_collection_details(self, url: str, collection: str, 
                                      headers: Dict, timeout: int) -> Dict:
        """Get detailed Qdrant collection info"""
        try:
            response = httpx.get(
                f"{url}/collections/{collection}",
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                return {
                    "vectors_count": result.get("vectors_count", 0),
                    "points_count": result.get("points_count", 0),
                    "segments_count": result.get("segments_count", 0),
                    "config": result.get("config", {})
                }
        except:
            pass
        
        return {}
    
    def _enumerate_weaviate(self, url: str, depth: str, timeout: int, api_key: str) -> List[Dict]:
        """Enumerate Weaviate classes"""
        logger.info("enumerating_weaviate")
        
        headers = self._build_headers(api_key)
        results = []
        
        try:
            response = httpx.get(f"{url}/v1/schema", headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                classes = data.get("classes", [])
                
                for cls in classes:
                    class_info = {
                        "db_type": "weaviate",
                        "class_name": cls["class"],
                        "properties": [p["name"] for p in cls.get("properties", [])]
                    }
                    
                    if depth in ["vectors", "metadata"]:
                        # Get object count
                        try:
                            count_response = httpx.post(
                                f"{url}/v1/graphql",
                                json={
                                    "query": f"{{ Aggregate {{ {cls['class']} {{ meta {{ count }} }} }} }}"
                                },
                                headers=headers,
                                timeout=timeout
                            )
                            
                            if count_response.status_code == 200:
                                count_data = count_response.json()
                                count = count_data.get("data", {}).get("Aggregate", {}).get(cls['class'], [{}])[0].get("meta", {}).get("count", 0)
                                class_info["object_count"] = count
                        except:
                            pass
                    
                    results.append(class_info)
                    
        except Exception as e:
            logger.error("weaviate_enum_error", error=str(e))
        
        return results
    
    def _enumerate_chromadb(self, url: str, depth: str, timeout: int, api_key: str) -> List[Dict]:
        """Enumerate ChromaDB collections"""
        logger.info("enumerating_chromadb")
        
        headers = self._build_headers(api_key)
        results = []
        
        try:
            response = httpx.get(f"{url}/api/v1/collections", headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                collections = response.json()
                
                for collection in collections:
                    collection_info = {
                        "db_type": "chromadb",
                        "collection_name": collection["name"],
                        "collection_id": collection["id"]
                    }
                    
                    if depth in ["vectors", "metadata"]:
                        # Get collection count
                        try:
                            count_response = httpx.get(
                                f"{url}/api/v1/collections/{collection['id']}/count",
                                headers=headers,
                                timeout=timeout
                            )
                            
                            if count_response.status_code == 200:
                                collection_info["count"] = count_response.json()
                        except:
                            pass
                    
                    results.append(collection_info)
                    
        except Exception as e:
            logger.error("chromadb_enum_error", error=str(e))
        
        return results
    
    def _enumerate_milvus(self, url: str, depth: str, timeout: int, api_key: str) -> List[Dict]:
        """Enumerate Milvus collections"""
        logger.info("enumerating_milvus")
        
        headers = self._build_headers(api_key)
        results = []
        
        try:
            response = httpx.get(f"{url}/api/v1/collections", headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get("data", [])
                
                for collection in collections:
                    collection_info = {
                        "db_type": "milvus",
                        "collection_name": collection
                    }
                    
                    results.append(collection_info)
                    
        except Exception as e:
            logger.error("milvus_enum_error", error=str(e))
        
        return results
    
    def _enumerate_pinecone(self, url: str, depth: str, timeout: int, api_key: str) -> List[Dict]:
        """Enumerate Pinecone indexes"""
        logger.info("enumerating_pinecone")
        
        headers = self._build_headers(api_key)
        results = []
        
        try:
            response = httpx.get(f"{url}/databases", headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                indexes = response.json()
                
                for index in indexes:
                    index_info = {
                        "db_type": "pinecone",
                        "index_name": index
                    }
                    
                    results.append(index_info)
                    
        except Exception as e:
            logger.error("pinecone_enum_error", error=str(e))
        
        return results
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
        
        return headers
