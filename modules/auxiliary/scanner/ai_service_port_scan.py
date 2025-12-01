"""
AI Service Port Scanner Module

Scans common ports used by AI/ML services and identifies running services.
Focuses on AI-specific services rather than general port scanning.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import socket
import structlog
from typing import Dict, List, Any, Tuple
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class AIServicePortScan(AuxiliaryModule):
    """AI/ML Service Port Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "AI Service Port Scanner"
        self.description = "Scan for AI/ML services on common ports"
        self.author = "Scott Thornton"
        self.module_type = "scanner"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "PORT_RANGE": Option(value="common", required=False, description="Port range to scan",
                               enum_values=["common", "extended", "all", "custom"]),
            "CUSTOM_PORTS": Option(value="", required=False, description="Custom port list (comma-separated)"),
            "TIMEOUT": Option(value="2", required=False, description="Connection timeout"),
            "IDENTIFY_SERVICE": Option(value="true", required=False, description="Attempt service identification")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute AI service port scan"""
        target_host = self.options["TARGET_HOST"].value
        port_range = self.options["PORT_RANGE"].value
        custom_ports = self.options["CUSTOM_PORTS"].value
        timeout = int(self.options["TIMEOUT"].value)
        identify_service = self.options["IDENTIFY_SERVICE"].value.lower() == "true"
        
        logger.info("ai_service_port_scan.run", host=target_host, range=port_range)
        
        # Get ports to scan
        ports = self._get_ports(port_range, custom_ports)
        
        open_ports = []
        
        for port in ports:
            if self._check_port(target_host, port, timeout):
                port_info = {
                    "port": port,
                    "state": "open",
                    "service": self._get_service_name(port)
                }
                
                # Try to identify the actual service
                if identify_service:
                    service_details = self._identify_service(target_host, port, timeout)
                    if service_details:
                        port_info.update(service_details)
                
                open_ports.append(port_info)
                logger.info("open_port_found", port=port, service=port_info.get("service"))
        
        return AuxiliaryResult(
            success=len(open_ports) > 0,
            output=f"Found {len(open_ports)} open AI/ML service port(s)",
            discovered=open_ports,
            details={"ports_scanned": len(ports), "open_ports": len(open_ports)}
        )
    
    def _get_ports(self, port_range: str, custom_ports: str) -> List[int]:
        """Get list of ports to scan"""
        # Common AI/ML service ports
        common_ai_ports = [
            5000,   # MLflow
            6006,   # TensorBoard
            8000,   # Generic API (FastAPI, etc.)
            8080,   # Kubeflow, W&B
            8501,   # Streamlit
            8888,   # Jupyter
            9090,   # Prometheus (ML monitoring)
            6333,   # Qdrant
            19530,  # Milvus
            7474,   # Neo4j
            9200,   # Elasticsearch
            11434,  # Ollama
            8787    # RStudio Server
        ]
        
        extended_ai_ports = common_ai_ports + [
            3000,   # Comet ML
            4040,   # Spark UI
            8265,   # Ray Dashboard
            8443,   # HTTPS alternates
            9000,   # Generic services
            10000,  # Databricks
            16686,  # Jaeger (tracing)
            50051,  # gRPC services
            8001,   # FastAPI alternate
            8081,   # Alternative web services
            5432,   # PostgreSQL (often used with ML)
            27017,  # MongoDB (document store)
            6379    # Redis (caching/queue)
        ]
        
        if port_range == "common":
            return common_ai_ports
        elif port_range == "extended":
            return extended_ai_ports
        elif port_range == "all":
            # Full scan of common service range
            return list(range(1000, 10000))
        elif port_range == "custom" and custom_ports:
            return [int(p.strip()) for p in custom_ports.split(",") if p.strip().isdigit()]
        else:
            return common_ai_ports
    
    def _check_port(self, host: str, port: int, timeout: int) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_service_name(self, port: int) -> str:
        """Get expected service name for a port"""
        service_map = {
            5000: "MLflow",
            6006: "TensorBoard",
            8000: "FastAPI/Generic",
            8080: "Kubeflow/W&B",
            8501: "Streamlit",
            8888: "Jupyter",
            9090: "Prometheus",
            6333: "Qdrant",
            19530: "Milvus",
            7474: "Neo4j",
            9200: "Elasticsearch",
            11434: "Ollama",
            8787: "RStudio",
            3000: "Comet ML",
            4040: "Spark UI",
            8265: "Ray Dashboard",
            50051: "gRPC",
            5432: "PostgreSQL",
            27017: "MongoDB",
            6379: "Redis"
        }
        return service_map.get(port, "Unknown")
    
    def _identify_service(self, host: str, port: int, timeout: int) -> Dict[str, Any]:
        """Identify the actual service running on the port"""
        service_details = {}
        
        # Try HTTP/HTTPS
        for protocol in ["http", "https"]:
            try:
                url = f"{protocol}://{host}:{port}/"
                response = httpx.get(url, timeout=timeout, follow_redirects=True, verify=False)
                
                if response.status_code < 500:
                    # Analyze response to identify service
                    service_type = self._analyze_response(response)
                    if service_type:
                        service_details["identified_service"] = service_type
                        service_details["protocol"] = protocol
                        service_details["status_code"] = response.status_code
                        
                        # Extract version if available
                        if "server" in response.headers:
                            service_details["server_header"] = response.headers["server"]
                        
                        return service_details
                        
            except:
                continue
        
        # Try banner grabbing for non-HTTP services
        banner = self._grab_banner(host, port, timeout)
        if banner:
            service_details["banner"] = banner[:100]  # Limit banner length
            service_details["protocol"] = "tcp"
        
        return service_details
    
    def _analyze_response(self, response: httpx.Response) -> str:
        """Analyze HTTP response to identify service"""
        body_lower = response.text.lower()
        url_lower = str(response.url).lower()
        
        # Service identification patterns
        patterns = {
            "MLflow": ["mlflow", "experiment tracking"],
            "Jupyter": ["jupyter", "jupyterlab", "notebook"],
            "TensorBoard": ["tensorboard", "tensorflow"],
            "Streamlit": ["streamlit"],
            "Kubeflow": ["kubeflow", "pipeline"],
            "W&B": ["wandb", "weights & biases"],
            "Qdrant": ["qdrant"],
            "Weaviate": ["weaviate"],
            "ChromaDB": ["chroma"],
            "Milvus": ["milvus"],
            "FastAPI": ["fastapi", "openapi", "swagger"],
            "Ollama": ["ollama"],
            "Ray": ["ray dashboard"],
            "Spark": ["spark ui", "apache spark"]
        }
        
        for service, indicators in patterns.items():
            if any(indicator in body_lower or indicator in url_lower for indicator in indicators):
                return service
        
        return "Unknown HTTP Service"
    
    def _grab_banner(self, host: str, port: int, timeout: int) -> str:
        """Grab service banner for non-HTTP services"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            
            # Try to read banner
            sock.send(b"\r\n")
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            return banner.strip()
        except:
            return ""
