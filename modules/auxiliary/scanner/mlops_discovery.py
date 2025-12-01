"""
MLOps Infrastructure Discovery Module

Discovers MLOps platforms including MLflow, Kubeflow, Weights & Biases,
Neptune, Comet, and custom ML infrastructure components.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import json
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class MLOpsDiscovery(AuxiliaryModule):
    """MLOps Infrastructure Discovery Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "MLOps Discovery"
        self.description = "Discover MLOps platforms and infrastructure"
        self.author = "Scott Thornton"
        self.module_type = "scanner"
        self.references = [
            "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
            "https://mlsecops.com/"
        ]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "TARGET_PORT": Option(value="5000", required=False, description="Target port (or range)"),
            "SCAN_PLATFORMS": Option(value="all", required=False, description="Platforms to scan", 
                                    enum_values=["all", "mlflow", "kubeflow", "wandb", "neptune", "comet"]),
            "TIMEOUT": Option(value="10", required=False, description="Request timeout"),
            "CHECK_VERSIONS": Option(value="true", required=False, description="Attempt to identify versions")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute MLOps discovery"""
        target_host = self.options["TARGET_HOST"].value
        target_port = self.options["TARGET_PORT"].value
        scan_platforms = self.options["SCAN_PLATFORMS"].value
        timeout = int(self.options["TIMEOUT"].value)
        check_versions = self.options["CHECK_VERSIONS"].value.lower() == "true"
        
        logger.info("mlops_discovery.run", host=target_host, platforms=scan_platforms)
        
        discovered_services = []
        
        # Parse ports
        if "-" in target_port:
            start_port, end_port = map(int, target_port.split("-"))
            ports = range(start_port, end_port + 1)
        else:
            ports = [int(target_port)]
        
        # Get platform detection rules
        platforms = self._get_platform_rules(scan_platforms)
        
        for port in ports:
            for platform_name, rules in platforms.items():
                result = self._scan_platform(
                    target_host, port, platform_name, rules, timeout, check_versions
                )
                if result:
                    discovered_services.append(result)
                    logger.info("mlops_platform_found", platform=platform_name, port=port)
        
        return AuxiliaryResult(
            success=len(discovered_services) > 0,
            output=f"Discovered {len(discovered_services)} MLOps service(s)",
            discovered=discovered_services,
            details={"ports_scanned": len(ports), "platforms_checked": len(platforms)}
        )
    
    def _get_platform_rules(self, scan_platforms: str) -> Dict[str, Dict]:
        """Get platform detection rules"""
        all_platforms = {
            "MLflow": {
                "paths": ["/", "/api/2.0/mlflow/experiments/list", "/#/"],
                "indicators": ["mlflow", "experiment", "model registry"],
                "default_port": 5000
            },
            "Kubeflow": {
                "paths": ["/", "/_/dashboard", "/pipeline"],
                "indicators": ["kubeflow", "pipeline", "notebook"],
                "default_port": 8080
            },
            "Weights & Biases": {
                "paths": ["/", "/api/v1/users/me", "/healthz"],
                "indicators": ["wandb", "weights & biases", "w&b"],
                "default_port": 8080
            },
            "Neptune": {
                "paths": ["/", "/api/leaderboard/v1/health"],
                "indicators": ["neptune", "experiment tracking"],
                "default_port": 8000
            },
            "Comet": {
                "paths": ["/", "/api/rest/v2/health"],
                "indicators": ["comet", "experiment"],
                "default_port": 3000
            },
            "Jupyter": {
                "paths": ["/", "/api", "/tree"],
                "indicators": ["jupyter", "notebook", "jupyterlab"],
                "default_port": 8888
            },
            "TensorBoard": {
                "paths": ["/", "/data/logdir"],
                "indicators": ["tensorboard", "tensorflow"],
                "default_port": 6006
            }
        }
        
        if scan_platforms == "all":
            return all_platforms
        else:
            # Filter to specific platform
            platform_map = {
                "mlflow": "MLflow",
                "kubeflow": "Kubeflow",
                "wandb": "Weights & Biases",
                "neptune": "Neptune",
                "comet": "Comet"
            }
            platform_key = platform_map.get(scan_platforms.lower())
            if platform_key and platform_key in all_platforms:
                return {platform_key: all_platforms[platform_key]}
            return all_platforms
    
    def _scan_platform(self, host: str, port: int, platform_name: str, 
                      rules: Dict, timeout: int, check_versions: bool) -> Dict[str, Any]:
        """Scan for a specific platform"""
        for path in rules["paths"]:
            url = f"http://{host}:{port}{path}"
            
            try:
                response = httpx.get(url, timeout=timeout, follow_redirects=True)
                
                if response.status_code in [200, 302]:
                    body_lower = response.text.lower()
                    
                    # Check for platform indicators
                    matches = sum(1 for indicator in rules["indicators"] 
                                if indicator.lower() in body_lower)
                    
                    if matches > 0:
                        service_info = {
                            "platform": platform_name,
                            "url": url,
                            "status_code": response.status_code,
                            "confidence": "high" if matches >= 2 else "medium",
                            "indicators_matched": matches
                        }
                        
                        # Try to extract version
                        if check_versions:
                            version = self._extract_version(response, platform_name)
                            if version:
                                service_info["version"] = version
                        
                        # Check for common security issues
                        security_issues = self._check_security(response, platform_name)
                        if security_issues:
                            service_info["security_issues"] = security_issues
                        
                        return service_info
                        
            except:
                continue
        
        return None
    
    def _extract_version(self, response: httpx.Response, platform: str) -> str:
        """Extract version information"""
        import re
        
        # Common version patterns
        patterns = [
            rf"{platform.lower()}[\/\s]+v?(\d+\.\d+\.\d+)",
            r"version[\":\s]+(\d+\.\d+\.\d+)",
            r"v(\d+\.\d+\.\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _check_security(self, response: httpx.Response, platform: str) -> List[str]:
        """Check for common security issues"""
        issues = []
        
        # Check for authentication
        if response.status_code == 200 and "login" not in response.text.lower():
            if "api" in response.url:
                issues.append("No authentication required for API")
            else:
                issues.append("No authentication required")
        
        # Check for debug mode
        if any(indicator in response.text.lower() for indicator in ["debug", "traceback", "stack trace"]):
            issues.append("Debug mode enabled")
        
        # Check security headers
        security_headers = ["x-frame-options", "content-security-policy", "strict-transport-security"]
        missing_headers = [h for h in security_headers if h not in response.headers]
        if missing_headers:
            issues.append(f"Missing security headers: {', '.join(missing_headers)}")
        
        return issues
