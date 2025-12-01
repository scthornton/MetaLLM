#!/bin/bash
# MetaLLM GCP Lab Quick Deploy Script

set -e

echo "========================================"
echo "   MetaLLM GCP Test Lab Deployment"
echo "========================================"
echo ""

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "Error: gcloud CLI not installed"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform not installed"; exit 1; }

# Get project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Enter your GCP Project ID:"
    read -r PROJECT_ID
    export GCP_PROJECT_ID=$PROJECT_ID
else
    PROJECT_ID=$GCP_PROJECT_ID
fi

# Get owner email
if [ -z "$OWNER_EMAIL" ]; then
    echo "Enter your email address:"
    read -r EMAIL
    export OWNER_EMAIL=$EMAIL
else
    EMAIL=$OWNER_EMAIL
fi

# Configuration
echo ""
echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Owner Email: $EMAIL"
echo "  Region: us-central1"
echo "  Use Spot Instances: true"
echo "  Enable GPU: true"
echo ""

read -p "Proceed with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Set gcloud project
echo ""
echo "Setting gcloud project..."
gcloud config set project $PROJECT_ID

# Enable APIs
echo ""
echo "Enabling required GCP APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable iap.googleapis.com

# Navigate to terraform directory
cd terraform

# Create terraform.tfvars
echo ""
echo "Creating terraform.tfvars..."
cat > terraform.tfvars << TFVARS
project_id         = "$PROJECT_ID"
owner_email        = "$EMAIL"
region             = "us-central1"
zone               = "us-central1-a"
use_spot_instances = true
enable_gpu         = true
TFVARS

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
terraform init

# Plan deployment
echo ""
echo "Creating deployment plan..."
terraform plan -out=tfplan

# Apply
echo ""
echo "Deploying infrastructure..."
terraform apply tfplan

# Output connection info
echo ""
echo "========================================"
echo "   Deployment Complete!"
echo "========================================"
echo ""
terraform output

echo ""
echo "Next steps:"
echo "1. Connect to control node:"
echo "   $(terraform output -raw ssh_command)"
echo ""
echo "2. Run MetaLLM tests:"
echo "   cd /opt/MetaLLM"
echo "   source venv/bin/activate"
echo "   python metalllm.py"
echo ""
echo "3. Stop instances when done:"
echo "   $(terraform output -raw stop_all_command)"
echo ""
