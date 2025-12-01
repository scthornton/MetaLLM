# MetaLLM GCP Test Lab

Complete Google Cloud Platform infrastructure for MetaLLM security testing.

## Quick Start

```bash
# 1. Set environment variables
export GCP_PROJECT_ID="your-project-id"
export OWNER_EMAIL="your-email@example.com"

# 2. Deploy everything
./deploy.sh

# 3. Connect to lab
gcloud compute ssh metalllm-control --tunnel-through-iap --zone=us-central1-a
```

## What Gets Deployed

- **1x Control Node** - MetaLLM framework and testing tools
- **2x LLM Targets** - Ollama and vLLM with GPU (optional)
- **1x RAG Target** - Qdrant vector database
- **1x Agent Target** - Vulnerable LangChain server
- **1x MLOps Target** - MLflow tracking server
- **VPC Network** - Isolated network with 5 subnets
- **Cloud NAT** - Outbound internet access
- **IAP Tunnel** - Secure SSH access

## Estimated Costs

**With spot instances (8 hours/day usage):**
- Without GPU: ~$200/month
- With GPU: ~$450/month

**With standard instances (24/7):**
- Without GPU: ~$600/month
- With GPU: ~$2,000/month

## Directory Structure

```
gcp/
├── deploy.sh                    # Quick deployment script
├── terraform/                   # Infrastructure as Code
│   ├── provider.tf             # Terraform configuration
│   ├── variables.tf            # Input variables
│   ├── network.tf              # VPC and networking
│   ├── instances.tf            # Compute instances
│   ├── outputs.tf              # Output values
│   └── terraform.tfvars.example  # Example configuration
└── scripts/                     # Startup scripts
    ├── setup_control_node.sh   # Control node setup
    ├── setup_ollama.sh         # Ollama LLM target
    ├── setup_vllm.sh           # vLLM target
    ├── setup_qdrant.sh         # Qdrant vector DB
    ├── setup_langchain.sh      # LangChain agent
    └── setup_mlflow.sh         # MLflow server
```

## Documentation

- **[Architecture](../../docs/lab/GCP_TEST_LAB_ARCHITECTURE.md)** - Detailed architecture and design
- **[Deployment Guide](../../docs/lab/DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[Troubleshooting](../../docs/lab/DEPLOYMENT_GUIDE.md#troubleshooting)** - Common issues and solutions

## Management Commands

```bash
# Start all instances
gcloud compute instances start $(gcloud compute instances list --format="value(name)") --zone=us-central1-a

# Stop all instances
gcloud compute instances stop $(gcloud compute instances list --format="value(name)") --zone=us-central1-a

# SSH to control node
gcloud compute ssh metalllm-control --tunnel-through-iap --zone=us-central1-a

# View instance logs
gcloud compute instances get-serial-port-output INSTANCE_NAME --zone=us-central1-a

# Destroy everything
cd terraform && terraform destroy
```

## Support

Issues? Open a ticket: https://github.com/perfecXion/MetaLLM/issues

---

**Author:** Scott Thornton / perfecXion.ai
