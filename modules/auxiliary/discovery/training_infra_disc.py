"""
Training Infrastructure Discovery Module

Discovers ML training infrastructure including compute clusters, GPU nodes,
distributed training systems, and training job queues.

Author: Scott Thornton (perfecXion.ai)
"""

import httpx
import socket
import structlog
from typing import Dict, List, Any
from modules.auxiliary.base import AuxiliaryModule, Option, AuxiliaryResult

logger = structlog.get_logger()


class TrainingInfraDisc(AuxiliaryModule):
    """Training Infrastructure Discovery"""
    
    def __init__(self):
        super().__init__()
        self.name = "Training Infrastructure Discovery"
        self.description = "Discover ML training infrastructure and compute resources"
        self.author = "Scott Thornton"
        self.module_type = "discovery"
        self.references = ["https://owasp.org/www-project-top-10-for-large-language-model-applications/"]
        
        self.options = {
            "TARGET_HOST": Option(value="localhost", required=True, description="Target hostname or IP"),
            "INFRA_TYPE": Option(value="all", required=False, description="Infrastructure type",
                               enum_values=["all", "kubeflow", "ray", "spark", "dask", "horovod"]),
            "CHECK_GPU": Option(value="true", required=False, description="Check for GPU resources"),
            "TIMEOUT": Option(value="30", required=False, description="Request timeout")
        }
    
    def run(self) -> AuxiliaryResult:
        """Execute training infrastructure discovery"""
        target_host = self.options["TARGET_HOST"].value
        infra_type = self.options["INFRA_TYPE"].value
        check_gpu = self.options["CHECK_GPU"].value.lower() == "true"
        timeout = int(self.options["TIMEOUT"].value)
        
        logger.info("training_infra_disc.run", host=target_host, type=infra_type)
        
        discovered_infra = []
        
        if infra_type in ["all", "kubeflow"]:
            kubeflow_infra = self._discover_kubeflow(target_host, timeout)
            if kubeflow_infra:
                discovered_infra.extend(kubeflow_infra)
        
        if infra_type in ["all", "ray"]:
            ray_infra = self._discover_ray(target_host, timeout)
            if ray_infra:
                discovered_infra.extend(ray_infra)
        
        if infra_type in ["all", "spark"]:
            spark_infra = self._discover_spark(target_host, timeout)
            if spark_infra:
                discovered_infra.extend(spark_infra)
        
        if infra_type in ["all", "dask"]:
            dask_infra = self._discover_dask(target_host, timeout)
            if dask_infra:
                discovered_infra.extend(dask_infra)
        
        # Check for GPU resources if requested
        if check_gpu:
            gpu_info = self._check_gpu_resources(discovered_infra, target_host, timeout)
            if gpu_info:
                discovered_infra.append(gpu_info)
        
        return AuxiliaryResult(
            success=len(discovered_infra) > 0,
            output=f"Discovered {len(discovered_infra)} training infrastructure component(s)",
            discovered=discovered_infra,
            details={"infra_type": infra_type, "check_gpu": check_gpu}
        )
    
    def _discover_kubeflow(self, host: str, timeout: int) -> List[Dict]:
        """Discover Kubeflow infrastructure"""
        logger.info("discovering_kubeflow")
        
        discovered = []
        
        # Common Kubeflow ports
        kubeflow_ports = [8080, 8888, 31380]
        
        for port in kubeflow_ports:
            try:
                # Check Kubeflow Dashboard
                response = httpx.get(f"http://{host}:{port}/", timeout=timeout)
                
                if response.status_code == 200 and "kubeflow" in response.text.lower():
                    infra_info = {
                        "type": "kubeflow",
                        "component": "dashboard",
                        "url": f"http://{host}:{port}",
                        "status": "active"
                    }
                    
                    # Try to get pipeline info
                    try:
                        pipeline_response = httpx.get(
                            f"http://{host}:{port}/pipeline/apis/v1beta1/pipelines",
                            timeout=timeout
                        )
                        
                        if pipeline_response.status_code == 200:
                            data = pipeline_response.json()
                            infra_info["pipelines"] = data.get("total_size", 0)
                    except:
                        pass
                    
                    discovered.append(infra_info)
                    
            except:
                continue
        
        return discovered
    
    def _discover_ray(self, host: str, timeout: int) -> List[Dict]:
        """Discover Ray cluster infrastructure"""
        logger.info("discovering_ray")
        
        discovered = []
        
        # Ray Dashboard port
        ray_port = 8265
        
        try:
            response = httpx.get(f"http://{host}:{ray_port}/api/cluster_status", timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                infra_info = {
                    "type": "ray",
                    "component": "cluster",
                    "url": f"http://{host}:{ray_port}",
                    "status": "active"
                }
                
                # Extract cluster info
                if "data" in data:
                    cluster_data = data["data"]
                    infra_info["nodes"] = cluster_data.get("clusterStatus", {}).get("totalNodes", 0)
                    infra_info["cpus"] = cluster_data.get("clusterStatus", {}).get("totalCPUs", 0)
                
                discovered.append(infra_info)
                
        except:
            pass
        
        return discovered
    
    def _discover_spark(self, host: str, timeout: int) -> List[Dict]:
        """Discover Apache Spark infrastructure"""
        logger.info("discovering_spark")
        
        discovered = []
        
        # Spark UI ports
        spark_ports = [4040, 8080, 18080]
        
        for port in spark_ports:
            try:
                response = httpx.get(f"http://{host}:{port}/", timeout=timeout)
                
                if response.status_code == 200:
                    body_lower = response.text.lower()
                    
                    if "spark" in body_lower:
                        infra_info = {
                            "type": "spark",
                            "url": f"http://{host}:{port}",
                            "status": "active"
                        }
                        
                        # Determine Spark component type
                        if "master" in body_lower:
                            infra_info["component"] = "master"
                        elif "worker" in body_lower:
                            infra_info["component"] = "worker"
                        elif "history" in body_lower:
                            infra_info["component"] = "history_server"
                        else:
                            infra_info["component"] = "application_ui"
                        
                        # Try to get cluster info
                        try:
                            if port == 8080:  # Master UI
                                json_response = httpx.get(
                                    f"http://{host}:{port}/json/",
                                    timeout=timeout
                                )
                                
                                if json_response.status_code == 200:
                                    data = json_response.json()
                                    infra_info["workers"] = data.get("aliveworkers", 0)
                                    infra_info["cores"] = data.get("cores", 0)
                        except:
                            pass
                        
                        discovered.append(infra_info)
                        
            except:
                continue
        
        return discovered
    
    def _discover_dask(self, host: str, timeout: int) -> List[Dict]:
        """Discover Dask cluster infrastructure"""
        logger.info("discovering_dask")
        
        discovered = []
        
        # Dask Dashboard port
        dask_port = 8787
        
        try:
            response = httpx.get(f"http://{host}:{dask_port}/info/main/workers.html", 
                               timeout=timeout)
            
            if response.status_code == 200:
                infra_info = {
                    "type": "dask",
                    "component": "scheduler",
                    "url": f"http://{host}:{dask_port}",
                    "status": "active"
                }
                
                # Try to get worker info
                try:
                    json_response = httpx.get(
                        f"http://{host}:{dask_port}/info/workers",
                        timeout=timeout
                    )
                    
                    if json_response.status_code == 200:
                        data = json_response.json()
                        infra_info["workers"] = len(data)
                except:
                    pass
                
                discovered.append(infra_info)
                
        except:
            pass
        
        return discovered
    
    def _check_gpu_resources(self, discovered_infra: List[Dict], 
                            host: str, timeout: int) -> Dict:
        """Check for GPU resources in discovered infrastructure"""
        logger.info("checking_gpu_resources")
        
        gpu_info = {
            "type": "gpu_resources",
            "detected": False,
            "details": []
        }
        
        # Check Ray for GPU info
        for infra in discovered_infra:
            if infra["type"] == "ray":
                try:
                    url = infra["url"]
                    response = httpx.get(f"{url}/api/cluster_status", timeout=timeout)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "data" in data:
                            cluster_data = data["data"]
                            gpus = cluster_data.get("clusterStatus", {}).get("totalGPUs", 0)
                            
                            if gpus > 0:
                                gpu_info["detected"] = True
                                gpu_info["details"].append({
                                    "source": "ray",
                                    "gpu_count": gpus
                                })
                except:
                    pass
        
        # Check Spark for GPU info
        for infra in discovered_infra:
            if infra["type"] == "spark" and infra.get("component") == "master":
                # Spark doesn't expose GPU info easily via API
                # Mark as potential GPU usage if detected
                gpu_info["details"].append({
                    "source": "spark",
                    "note": "GPU detection requires executor inspection"
                })
        
        return gpu_info if gpu_info["detected"] or gpu_info["details"] else None
