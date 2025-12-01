# MetaLLM GCP Test Lab Deployment Guide

## Prerequisites

### 1. GCP Account Setup

- Active GCP account with billing enabled
- Sufficient quota for:
  - 6-8 compute instances
  - 2x NVIDIA T4 GPUs (if enabling GPU instances)
  - 1 VPC network
  - Cloud NAT
  
### 2. Local Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install Terraform
brew install terraform  # macOS
# or
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 3. GCP Project Setup

```bash
# Create new project (recommended)
gcloud projects create metalllm-lab-$(date +%s) --name="MetaLLM Test Lab"
export PROJECT_ID="metalllm-lab-XXXXXXXXXX"  # Use your project ID

# Set as default project
gcloud config set project $PROJECT_ID

# Link billing account
gcloud beta billing accounts list
gcloud beta billing projects link $PROJECT_ID --billing-account=XXXXXX-XXXXXX-XXXXXX

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable iap.googleapis.com
gcloud services enable serviceusage.googleapis.com
```

## Quick Start (5 Minutes)

```bash
# Clone repository
git clone https://github.com/perfecXion/MetaLLM.git
cd MetaLLM/infrastructure/gcp/terraform

# Configure
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars  # Edit: project_id, owner_email

# Deploy
terraform init
terraform plan
terraform apply

# Get connection info
terraform output ssh_command

# Connect to control node
eval $(terraform output -raw ssh_command)
```

## Detailed Deployment Steps

### Step 1: Configure Terraform Variables

```bash
cd MetaLLM/infrastructure/gcp/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id  = "your-project-id"
owner_email = "your-email@example.com"
region      = "us-central1"  # Optional: change region
zone        = "us-central1-a"  # Optional: change zone

# Cost optimization
use_spot_instances = true   # 60-90% cost savings
enable_gpu         = true   # Set to false to skip GPU instances
```

### Step 2: Initialize Terraform

```bash
terraform init
```

This downloads required providers and initializes the backend.

### Step 3: Review Deployment Plan

```bash
terraform plan
```

Review the resources that will be created:
- VPC network with 5 subnets
- Cloud NAT for outbound internet
- Firewall rules
- 6-8 compute instances
- IAP configuration

### Step 4: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes 10-15 minutes.

### Step 5: Verify Deployment

```bash
# Get all outputs
terraform output

# Test SSH access
terraform output -raw ssh_command | bash
```

## Post-Deployment Configuration

### 1. Access Control Node

```bash
# SSH via IAP
gcloud compute ssh metalllm-control --tunnel-through-iap --zone=us-central1-a

# Once connected
cd /opt/MetaLLM
source venv/bin/activate
```

### 2. Verify Target Accessibility

```bash
# Test all targets from control node
curl http://10.0.2.10:11434/api/tags        # Ollama
curl http://10.0.2.20:8000/v1/models        # vLLM
curl http://10.0.3.20:6333/collections      # Qdrant
curl http://10.0.4.10:8000/health           # LangChain
curl http://10.0.5.10:5000/                 # MLflow
```

### 3. Run First MetaLLM Test

```bash
# On control node
metalllm

# In MetaLLM CLI
metalllm> use auxiliary/scanner/llm_api_scanner
metalllm auxiliary(llm_api_scanner)> set TARGET_HOST 10.0.2.10
metalllm auxiliary(llm_api_scanner)> set TARGET_PORT 11434
metalllm auxiliary(llm_api_scanner)> run
```

## Cost Management

### Daily Shutdown/Startup

```bash
# Stop all instances (saves compute costs)
terraform output -raw stop_all_command | bash

# Start all instances
terraform output -raw start_all_command | bash
```

### Automated Shutdown Schedule

```bash
# Create Cloud Scheduler job to stop instances at 6 PM
gcloud scheduler jobs create app-engine \
    stop-lab-instances \
    --schedule="0 18 * * *" \
    --http-method=POST \
    --uri="https://compute.googleapis.com/compute/v1/projects/$PROJECT_ID/zones/us-central1-a/instances/stop" \
    --time-zone="America/New_York"
```

### Monitor Costs

```bash
# Set budget alert
gcloud billing budgets create \
    --billing-account=XXXXXX-XXXXXX-XXXXXX \
    --display-name="MetaLLM Lab Budget" \
    --budget-amount=500USD \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100
```

## Troubleshooting

### Issue: GPU Quota Exceeded

**Error:** `Quota 'NVIDIA_T4_GPUS' exceeded`

**Solution:**
```bash
# Request quota increase
https://console.cloud.google.com/iam-admin/quotas

# Or disable GPU temporarily
terraform apply -var="enable_gpu=false"
```

### Issue: Cannot SSH to Instance

**Error:** `Connection refused` or `Permission denied`

**Solutions:**
```bash
# 1. Verify IAP is enabled
gcloud services enable iap.googleapis.com

# 2. Check IAM permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/iap.tunnelResourceAccessor"

# 3. Use explicit zone
gcloud compute ssh metalllm-control \
    --zone=us-central1-a \
    --tunnel-through-iap
```

### Issue: Startup Scripts Failed

**Solution:**
```bash
# Check startup script logs
gcloud compute instances get-serial-port-output metalllm-control \
    --zone=us-central1-a

# SSH and manually run setup
gcloud compute ssh metalllm-control --tunnel-through-iap
sudo bash /var/log/daemon.log  # Check for errors
```

### Issue: High Costs

**Immediate actions:**
```bash
# Stop all instances
gcloud compute instances stop --all --zone=us-central1-a

# Check current costs
gcloud billing accounts list
# View in console: https://console.cloud.google.com/billing
```

## Updating the Lab

### Update Terraform Configuration

```bash
cd MetaLLM/infrastructure/gcp/terraform

# Make changes to *.tf files

# Preview changes
terraform plan

# Apply updates
terraform apply
```

### Update Instance Configuration

```bash
# SSH to instance
gcloud compute ssh metalllm-ollama-target --tunnel-through-iap

# Make changes
# ...

# Create snapshot
gcloud compute disks snapshot metalllm-ollama-target \
    --snapshot-names=ollama-snapshot-$(date +%Y%m%d)
```

## Complete Teardown

### Option 1: Terraform Destroy (Recommended)

```bash
cd MetaLLM/infrastructure/gcp/terraform

# Destroy all resources
terraform destroy

# Confirm by typing 'yes'
```

### Option 2: Manual Cleanup

```bash
# Delete all instances
gcloud compute instances delete --all --zone=us-central1-a

# Delete VPC
gcloud compute networks delete metalllm-test-vpc

# Delete project (nuclear option)
gcloud projects delete $PROJECT_ID
```

## Best Practices

### 1. Security

- **Never expose instances publicly** - Use IAP tunnel only
- **Rotate credentials regularly** - If using API keys
- **Review firewall rules** - Ensure deny-all is in place
- **Enable Cloud Armor** - For additional protection
- **Audit access logs** - Check Cloud Audit Logs monthly

### 2. Cost Optimization

- **Use spot instances** - 60-90% cost savings
- **Stop when not in use** - Saves ~$400-600/month
- **Right-size instances** - Start small, scale up if needed
- **Delete unused snapshots** - Clean up old backups
- **Monitor billing** - Set up alerts

### 3. Maintenance

- **Weekly updates** - Update packages and models
- **Backup important data** - Snapshot control node
- **Document changes** - Keep notes on modifications
- **Test disaster recovery** - Practice rebuilding from scratch

## Next Steps

1. **Run comprehensive tests** - Execute full MetaLLM test suite
2. **Collect results** - Document findings for paper
3. **Customize targets** - Add more vulnerable configurations
4. **Automate testing** - Create test automation scripts
5. **Share findings** - Contribute to MetaLLM documentation

## Support

- **GitHub Issues:** https://github.com/perfecXion/MetaLLM/issues
- **Documentation:** docs/lab/
- **GCP Support:** https://cloud.google.com/support

---

**Version:** 1.0  
**Author:** Scott Thornton / perfecXion.ai  
**Last Updated:** December 2025
