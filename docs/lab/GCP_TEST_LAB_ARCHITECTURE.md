# MetaLLM GCP Test Lab Architecture

## Overview

This document describes a comprehensive Google Cloud Platform (GCP) test lab for MetaLLM security research. The lab provides isolated, vulnerable AI/ML systems for authorized security testing and evaluation research.

## Design Principles

1. **Isolation**: Complete network isolation from production systems
2. **Reproducibility**: Infrastructure as Code (Terraform) for easy rebuild
3. **Cost-Effective**: Spot instances and automatic shutdown when idle
4. **Comprehensive**: Covers all MetaLLM module categories
5. **Realistic**: Mirrors real-world AI/ML deployments
6. **Documented**: Clear setup and teardown procedures

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GCP Project: metalllm-lab                    │
│                    Region: us-central1                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    VPC: metalllm-test-vpc                        │
│                    CIDR: 10.0.0.0/16                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subnet: attacker-subnet (10.0.1.0/24)                     │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  MetaLLM Control Node (n1-standard-2)                │  │ │
│  │  │  - MetaLLM Framework                                 │  │ │
│  │  │  - Testing Scripts                                   │  │ │
│  │  │  - Results Collection                                │  │ │
│  │  │  - Jupyter Notebooks                                 │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subnet: llm-targets-subnet (10.0.2.0/24)                 │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  LLM Target 1: Ollama (n1-standard-4 + T4 GPU)      │  │ │
│  │  │  - Llama 2, Mistral, Phi-2                          │  │ │
│  │  │  - Vulnerable configurations                         │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  LLM Target 2: vLLM Server (n1-standard-4 + T4)     │  │ │
│  │  │  - Multiple model endpoints                          │  │ │
│  │  │  - OpenAI-compatible API                             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  LLM Target 3: Text Generation WebUI (n1-standard-2)│  │ │
│  │  │  - Web interface for models                          │  │ │
│  │  │  - Multiple vulnerabilities                          │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subnet: rag-targets-subnet (10.0.3.0/24)                 │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  RAG System 1: Custom RAG (n1-standard-2)           │  │ │
│  │  │  - FastAPI backend                                   │  │ │
│  │  │  - ChromaDB vector store                             │  │ │
│  │  │  - OpenAI embeddings                                 │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Vector DB 1: Qdrant (n1-standard-2)                │  │ │
│  │  │  - Standalone Qdrant instance                        │  │ │
│  │  │  - No authentication (vulnerable)                    │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Vector DB 2: Weaviate (n1-standard-2)              │  │ │
│  │  │  - Weaviate instance                                 │  │ │
│  │  │  - Weak authentication                               │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subnet: agent-targets-subnet (10.0.4.0/24)               │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Agent System 1: LangChain Server (n1-standard-2)   │  │ │
│  │  │  - Vulnerable LangChain version                      │  │ │
│  │  │  - PALChain enabled                                  │  │ │
│  │  │  - Python REPL tool                                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Agent System 2: AutoGPT Clone (n1-standard-2)      │  │ │
│  │  │  - Simplified AutoGPT implementation                 │  │ │
│  │  │  - Multiple tools enabled                            │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subnet: mlops-targets-subnet (10.0.5.0/24)               │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  MLflow Server (n1-standard-2)                       │  │ │
│  │  │  - Model registry                                    │  │ │
│  │  │  - Tracking server                                   │  │ │
│  │  │  - No authentication                                 │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Jupyter Notebook Server (n1-standard-2)            │  │ │
│  │  │  - Exposed notebook server                           │  │ │
│  │  │  - Weak token authentication                         │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Weights & Biases Server (n1-standard-2)            │  │ │
│  │  │  - Self-hosted W&B                                   │  │ │
│  │  │  - Credential exposure vulnerabilities               │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Shared Services Subnet (10.0.10.0/24)                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  PostgreSQL Database (Cloud SQL)                     │  │ │
│  │  │  - Shared backend for services                       │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Redis Cache (Memorystore)                           │  │ │
│  │  │  - Caching layer                                     │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

External Access:
  ├─ IAP Tunnel (Secure access to Control Node)
  ├─ Cloud NAT (Outbound internet for instances)
  └─ No public IPs (except Load Balancer if needed)
```

## Component Specifications

### Control Node (Attacker Machine)

**Instance Type:** n1-standard-2 (2 vCPUs, 7.5 GB RAM)  
**OS:** Ubuntu 22.04 LTS  
**Disk:** 50 GB SSD

**Installed Software:**
- MetaLLM framework
- Python 3.11+
- Docker & Docker Compose
- Jupyter Lab (for analysis)
- Git, vim, tmux
- Network tools (nmap, curl, httpie)
- Monitoring tools (htop, nethogs)

**Purpose:**
- Run MetaLLM exploits
- Execute test scenarios
- Collect and analyze results
- Orchestrate test campaigns

**Access:**
- SSH via IAP tunnel only
- No direct public IP
- Bastion-style access to other subnets

### LLM Target Instances

#### Target 1: Ollama Server

**Instance Type:** n1-standard-4 + NVIDIA T4 GPU (4 vCPUs, 15 GB RAM)  
**GPU:** NVIDIA Tesla T4 (16 GB VRAM)  
**OS:** Ubuntu 22.04 LTS with CUDA  
**Disk:** 100 GB SSD

**Models Deployed:**
- Llama 2 7B (vulnerable to prompt injection)
- Mistral 7B (various configurations)
- Phi-2 (smaller model for testing)

**Vulnerabilities Introduced:**
- No input sanitization
- Weak prompt templates
- Exposed system prompts
- No rate limiting

**API Endpoints:**
```
http://10.0.2.10:11434/api/generate
http://10.0.2.10:11434/api/chat
http://10.0.2.10:11434/api/embeddings
```

#### Target 2: vLLM Server

**Instance Type:** n1-standard-4 + NVIDIA T4 GPU  
**OS:** Ubuntu 22.04 LTS with CUDA  
**Disk:** 100 GB SSD

**Configuration:**
- OpenAI-compatible API
- Multiple model endpoints
- Streaming responses enabled

**Vulnerabilities:**
- Weak authentication
- CORS misconfiguration
- Verbose error messages
- No token limits

**API Endpoints:**
```
http://10.0.2.20:8000/v1/completions
http://10.0.2.20:8000/v1/chat/completions
http://10.0.2.20:8000/v1/models
```

#### Target 3: Text Generation WebUI

**Instance Type:** n1-standard-2  
**OS:** Ubuntu 22.04 LTS  
**Disk:** 50 GB SSD

**Features:**
- Web-based model interface
- Multiple model loading
- Extension support (intentionally vulnerable)

**Vulnerabilities:**
- XSS in chat interface
- File upload vulnerabilities
- Exposed configuration files
- Weak session management

### RAG Target Instances

#### Custom RAG System

**Instance Type:** n1-standard-2  
**Components:**
- FastAPI backend (Python 3.11)
- ChromaDB vector database (embedded)
- OpenAI embeddings API integration

**Vulnerabilities:**
- Unvalidated document uploads
- SQL injection in metadata queries
- Context injection attacks possible
- No embedding verification

**Endpoints:**
```
http://10.0.3.10:8000/upload
http://10.0.3.10:8000/query
http://10.0.3.10:8000/documents
```

#### Qdrant Vector Database

**Instance Type:** n1-standard-2  
**Version:** Qdrant 1.7.0  
**Storage:** 50 GB SSD

**Configuration:**
- No authentication enabled
- Open API access
- No TLS
- Debug mode enabled

**Endpoints:**
```
http://10.0.3.20:6333/collections
http://10.0.3.20:6333/collections/{name}/points
```

#### Weaviate Vector Database

**Instance Type:** n1-standard-2  
**Version:** Weaviate 1.23  
**Storage:** 50 GB SSD

**Configuration:**
- Weak API key (hardcoded)
- Verbose error messages
- Schema modification allowed
- Anonymous read enabled

### Agent Target Instances

#### LangChain Server

**Instance Type:** n1-standard-2  
**LangChain Version:** 0.0.150 (vulnerable to CVE-2023-34540)  

**Enabled Chains:**
- PALChain (Python execution)
- SQLDatabaseChain
- PythonREPLTool
- Shell execution tool

**Vulnerabilities:**
- No code sandboxing
- Unrestricted Python execution
- SQL injection via chain
- Command injection

**Endpoint:**
```
http://10.0.4.10:8000/agent
```

#### AutoGPT Clone

**Instance Type:** n1-standard-2  
**Implementation:** Custom simplified AutoGPT

**Available Tools:**
- Web scraping
- File operations
- Code execution
- API calls

**Vulnerabilities:**
- Goal hijacking possible
- Recursive prompt injection
- Tool misuse scenarios
- Memory poisoning

### MLOps Target Instances

#### MLflow Server

**Instance Type:** n1-standard-2  
**Version:** MLflow 2.8.0  
**Database:** PostgreSQL (Cloud SQL)

**Configuration:**
- No authentication
- Open model registry
- Artifact store accessible
- Tracking server exposed

**Vulnerabilities:**
- Model poisoning possible
- Arbitrary file upload
- Metadata injection
- Supply chain attacks

**Endpoints:**
```
http://10.0.5.10:5000/
http://10.0.5.10:5000/api/2.0/mlflow/experiments/list
http://10.0.5.10:5000/api/2.0/mlflow/registered-models/list
```

#### Jupyter Notebook Server

**Instance Type:** n1-standard-2  
**Version:** JupyterLab 4.0  

**Configuration:**
- Weak token: `token123` (intentional)
- No TLS
- File browser enabled
- Terminal access enabled

**Vulnerabilities:**
- RCE via kernel
- Arbitrary file access
- Token exposure in URLs
- No multi-factor authentication

**Endpoint:**
```
http://10.0.5.20:8888/lab?token=token123
```

## Network Architecture

### VPC Configuration

```hcl
VPC Name: metalllm-test-vpc
CIDR Range: 10.0.0.0/16
Region: us-central1

Subnets:
├─ attacker-subnet: 10.0.1.0/24 (Control nodes)
├─ llm-targets-subnet: 10.0.2.0/24 (LLM instances)
├─ rag-targets-subnet: 10.0.3.0/24 (RAG systems)
├─ agent-targets-subnet: 10.0.4.0/24 (Agent systems)
├─ mlops-targets-subnet: 10.0.5.0/24 (MLOps infra)
└─ shared-services-subnet: 10.0.10.0/24 (Databases, caching)
```

### Firewall Rules

```yaml
Firewall Rules:
  # Allow internal communication
  - name: allow-internal
    direction: INGRESS
    source_ranges: [10.0.0.0/16]
    allowed: all protocols
    
  # Allow IAP for SSH
  - name: allow-iap-ssh
    direction: INGRESS
    source_ranges: [35.235.240.0/20]  # IAP range
    allowed: tcp:22
    
  # Deny all inbound from internet
  - name: deny-all-ingress
    direction: INGRESS
    source_ranges: [0.0.0.0/0]
    action: DENY
    
  # Allow outbound for updates
  - name: allow-egress
    direction: EGRESS
    destination_ranges: [0.0.0.0/0]
    allowed: all protocols
```

### Cloud NAT Configuration

```yaml
Cloud NAT:
  name: metalllm-nat
  nat_ip_allocate_option: AUTO_ONLY
  source_subnetwork_ip_ranges_to_nat: ALL_SUBNETWORKS_ALL_IP_RANGES
  
  Purpose: Allow outbound internet for:
    - Package installations
    - Model downloads
    - External API calls
    - No inbound connections allowed
```

## Security Considerations

### Access Control

1. **No Public IPs**
   - All instances use private IPs only
   - Access via IAP tunnel exclusively
   - No internet-facing services

2. **IAP (Identity-Aware Proxy)**
   - Requires Google account authentication
   - Role-based access control
   - Audit logging of all access
   - MFA enforced

3. **Service Accounts**
   - Minimal permissions per instance
   - No key downloads
   - Workload Identity where possible

### Network Isolation

1. **Subnet Segmentation**
   - Each target type in separate subnet
   - Control node can reach all subnets
   - Targets cannot reach each other directly

2. **Private Google Access**
   - Enabled for accessing GCS, Cloud SQL
   - No internet routing required
   - Secure by default

### Data Protection

1. **Encryption**
   - All disks encrypted at rest (Google-managed keys)
   - In-transit encryption for internal traffic
   - TLS for external API calls

2. **Backups**
   - Regular snapshots of control node
   - Model and data backups to GCS
   - Automated retention policy

### Monitoring & Logging

1. **Cloud Monitoring**
   - CPU, memory, disk usage
   - Network traffic patterns
   - Custom metrics for exploits

2. **Cloud Logging**
   - All SSH access logged
   - API calls tracked
   - System logs centralized

3. **Alerting**
   - Budget alerts
   - Resource usage thresholds
   - Unusual network activity

## Cost Optimization

### Instance Strategies

1. **Spot/Preemptible Instances**
   - Use spot instances for all VMs (60-90% cost savings)
   - Accept interruptions (easy to restart)
   - Save/restore state to GCS

2. **Right-Sizing**
   - Start with smaller instances
   - Scale up only if needed
   - Use monitoring to optimize

3. **Scheduled Start/Stop**
   - Auto-shutdown during off-hours
   - Start only when needed
   - Use Cloud Scheduler

### Storage Optimization

1. **Standard Persistent Disk**
   - Use standard (not SSD) where possible
   - SSD only for databases and GPU instances

2. **Cloud Storage**
   - Store models in GCS (cheaper than disk)
   - Download to instance on startup
   - Use lifecycle policies

### GPU Usage

1. **Share GPU Instances**
   - Run multiple models on same GPU
   - Use during testing only
   - Shutdown when idle

2. **T4 vs A100**
   - T4 sufficient for testing (~$300/month)
   - A100 only if needed (~$3000/month)

### Estimated Monthly Costs

```
Cost Breakdown (Spot Instances, 8hrs/day usage):

Control Node (n1-standard-2):               $20
LLM Targets (2x n1-standard-4 + T4 GPU):   $400
LLM Target (1x n1-standard-2):              $20
RAG Targets (3x n1-standard-2):             $60
Agent Targets (2x n1-standard-2):           $40
MLOps Targets (3x n1-standard-2):           $60
Cloud SQL (db-f1-micro):                    $10
Memorystore Redis (1GB):                    $25
Networking (egress):                        $20
Storage (500GB):                            $20

Total Estimated Monthly Cost:              ~$675/month

With 24/7 usage:                           ~$2,025/month
Full spot instances + 8hrs/day:            ~$450/month
```

## Deployment Strategy

### Phase 1: Core Infrastructure (Week 1)

1. Create GCP project
2. Enable required APIs
3. Configure VPC and subnets
4. Deploy control node
5. Set up IAP access
6. Configure Cloud NAT

### Phase 2: LLM Targets (Week 2)

1. Deploy Ollama instance
2. Download and configure models
3. Deploy vLLM server
4. Deploy Text Gen WebUI
5. Validate all endpoints

### Phase 3: RAG & Vector DBs (Week 3)

1. Deploy ChromaDB RAG system
2. Deploy Qdrant
3. Deploy Weaviate
4. Load sample documents
5. Test retrieval pipelines

### Phase 4: Agents & MLOps (Week 4)

1. Deploy LangChain server
2. Deploy AutoGPT clone
3. Deploy MLflow
4. Deploy Jupyter
5. Deploy W&B

### Phase 5: Testing & Validation (Week 5)

1. Test all MetaLLM modules
2. Validate vulnerabilities
3. Document findings
4. Create test automation

## Usage Workflows

### Daily Startup

```bash
# Start all instances
gcloud compute instances start metalllm-control --zone=us-central1-a
gcloud compute instances start ollama-target --zone=us-central1-a
# ... (start other instances)

# Connect to control node
gcloud compute ssh metalllm-control --tunnel-through-iap --zone=us-central1-a

# Run tests
cd MetaLLM
python metalllm.py
```

### Running Test Campaign

```bash
# On control node
cd MetaLLM

# Execute automated test suite
python scripts/run_test_campaign.py --targets all --output results/

# Review results
jupyter lab --no-browser --port=8888
```

### Daily Shutdown

```bash
# Stop all instances
gcloud compute instances stop metalllm-control --zone=us-central1-a
# ... (stop other instances)
```

## Next Steps

1. **Review and Approve Architecture**
2. **Set Budget Limits in GCP**
3. **Deploy Phase 1 (Core Infrastructure)**
4. **Validate Access and Connectivity**
5. **Proceed with Target Deployments**

---

**Version:** 1.0  
**Author:** Scott Thornton / perfecXion.ai  
**Last Updated:** December 2025
