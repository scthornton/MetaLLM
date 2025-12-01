"""
Model Registry Scanner Module

Scans ML model registries including MLflow, HuggingFace Hub, TensorFlow Hub,
and custom model repositories to enumerate models, versions, and metadata.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class ModelRegistryScan(AuxiliaryModule):
    """Model Registry Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "Model Registry Scanner"
        self.description = "Scan ML model registries and repositories"
        self.author = "Scott Thornton"
        self.module_type = "discovery"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_URL": Option(value="http://localhost:5000", required=True, description="Model registry URL"),
            "REGISTRY_TYPE": Option(value="auto", required=False, description="Registry type",
                                  enum_values=["auto", "mlflow", "huggingface", "custom"]),
            "ENUM_VERSIONS": Option(value="true", required=False, description="Enumerate model versions"),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout"),
            "API_KEY": Option(value="", required=False, description="API key if required")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute model registry scanning"""
        target_url = self.options["TARGET_URL"].value
        registry_type = self.options["REGISTRY_TYPE"].value
        enum_versions = self.options["ENUM_VERSIONS"].value.lower() == "true"
        timeout = int(self.options["TIMEOUT"].value)
        api_key = self.options["API_KEY"].value
        
        logger.info("model_registry_scan.run", url=target_url, type=registry_type)
        
        # Auto-detect registry type
        if registry_type == "auto":
            registry_type = self._detect_registry_type(target_url, timeout, api_key)
        
        # Scan based on registry type
        if registry_type == "mlflow":
            models = self._scan_mlflow(target_url, enum_versions, timeout, api_key)
        elif registry_type == "huggingface":
            models = self._scan_huggingface(target_url, enum_versions, timeout, api_key)
        else:
            models = self._scan_generic(target_url, enum_versions, timeout, api_key)
        
        return AuxiliaryResult(
            success=len(models) > 0,
            output=f"Found {len(models)} model(s) in {registry_type} registry",
            discovered=models,
            details={"registry_type": registry_type, "enum_versions": enum_versions}
        )
    
    def _detect_registry_type(self, url: str, timeout: int, api_key: str) -> str:
        """Auto-detect registry type"""
        headers = self._build_headers(api_key)
        
        # Check for MLflow
        try:
            response = httpx.get(f"{url}/api/2.0/mlflow/registered-models/list", 
                               headers=headers, timeout=timeout)
            if response.status_code in [200, 401]:
                logger.info("registry_type_detected", type="mlflow")
                return "mlflow"
        except:
            pass
        
        # Check for HuggingFace
        if "huggingface.co" in url or "hf.co" in url:
            return "huggingface"
        
        return "custom"
    
    def _scan_mlflow(self, url: str, enum_versions: bool, timeout: int, api_key: str) -> List[Dict]:
        """Scan MLflow model registry"""
        logger.info("scanning_mlflow_registry")
        
        headers = self._build_headers(api_key)
        models = []
        
        try:
            # List registered models
            response = httpx.get(
                f"{url}/api/2.0/mlflow/registered-models/list",
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                registered_models = data.get("registered_models", [])
                
                for model in registered_models:
                    model_info = {
                        "registry_type": "mlflow",
                        "model_name": model.get("name"),
                        "creation_timestamp": model.get("creation_timestamp"),
                        "last_updated_timestamp": model.get("last_updated_timestamp")
                    }
                    
                    # Get model versions if requested
                    if enum_versions:
                        versions = self._get_mlflow_versions(
                            url, model.get("name"), headers, timeout
                        )
                        model_info["versions"] = versions
                    
                    models.append(model_info)
                    
        except Exception as e:
            logger.error("mlflow_scan_error", error=str(e))
        
        return models
    
    def _get_mlflow_versions(self, url: str, model_name: str, 
                            headers: Dict, timeout: int) -> List[Dict]:
        """Get MLflow model versions"""
        versions = []
        
        try:
            response = httpx.get(
                f"{url}/api/2.0/mlflow/model-versions/search",
                params={"filter": f"name='{model_name}'"},
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                model_versions = data.get("model_versions", [])
                
                for version in model_versions:
                    versions.append({
                        "version": version.get("version"),
                        "stage": version.get("current_stage"),
                        "run_id": version.get("run_id"),
                        "status": version.get("status")
                    })
                    
        except:
            pass
        
        return versions
    
    def _scan_huggingface(self, url: str, enum_versions: bool, timeout: int, api_key: str) -> List[Dict]:
        """Scan HuggingFace model hub"""
        logger.info("scanning_huggingface_hub")
        
        headers = self._build_headers(api_key)
        models = []
        
        # Parse organization/user from URL
        try:
            # Extract org/user from URL
            parts = url.split("/")
            org = parts[-1] if len(parts) > 0 else None
            
            if org:
                # List models for organization
                api_url = f"https://huggingface.co/api/models?author={org}"
                
                response = httpx.get(api_url, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for model in data:
                        model_info = {
                            "registry_type": "huggingface",
                            "model_name": model.get("modelId"),
                            "author": model.get("author"),
                            "downloads": model.get("downloads"),
                            "likes": model.get("likes"),
                            "tags": model.get("tags", [])
                        }
                        
                        models.append(model_info)
                        
        except Exception as e:
            logger.error("huggingface_scan_error", error=str(e))
        
        return models
    
    def _scan_generic(self, url: str, enum_versions: bool, timeout: int, api_key: str) -> List[Dict]:
        """Scan generic/custom model registry"""
        logger.info("scanning_generic_registry")
        
        headers = self._build_headers(api_key)
        models = []
        
        # Try common model registry endpoints
        endpoints = [
            "/models",
            "/api/models",
            "/registry/models",
            "/v1/models"
        ]
        
        for endpoint in endpoints:
            try:
                response = httpx.get(f"{url}{endpoint}", headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Parse different response structures
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    models.append({
                                        "registry_type": "custom",
                                        "model_name": item.get("name") or item.get("id"),
                                        "metadata": item
                                    })
                                elif isinstance(item, str):
                                    models.append({
                                        "registry_type": "custom",
                                        "model_name": item
                                    })
                        elif isinstance(data, dict):
                            if "models" in data:
                                for model in data["models"]:
                                    models.append({
                                        "registry_type": "custom",
                                        "model_name": model if isinstance(model, str) else model.get("name")
                                    })
                        
                        if models:
                            break  # Found models, stop trying other endpoints
                            
                    except:
                        pass
                        
            except:
                continue
        
        return models
    
    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
        
        return headers
