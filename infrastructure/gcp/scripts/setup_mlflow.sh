#!/bin/bash
# MLflow Server Setup Script

set -e

echo "=== MLflow Target Setup ==="

# Install dependencies
apt-get update
apt-get install -y python3.11 python3.11-venv python3-pip

# Create MLflow directory
mkdir -p /opt/mlflow
cd /opt/mlflow

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mlflow psycopg2-binary boto3

# Create MLflow configuration (no authentication - vulnerable)
cat > mlflow.conf << 'CONF'
backend_store_uri = sqlite:///mlflow.db
default_artifact_root = ./mlartifacts
host = 0.0.0.0
port = 5000
CONF

# Create systemd service
cat > /etc/systemd/system/mlflow.service << 'SERVICE'
[Unit]
Description=MLflow Tracking Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mlflow
ExecStart=/opt/mlflow/venv/bin/mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable mlflow
systemctl start mlflow

echo "=== MLflow Setup Complete ==="
echo "UI available at: http://$(hostname -I | awk '{print $1}'):5000"
