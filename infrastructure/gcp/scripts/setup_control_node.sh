#!/bin/bash
# MetaLLM Control Node Setup Script

set -e

echo "=== MetaLLM Control Node Setup ==="

# Update system
apt-get update
apt-get upgrade -y

# Install essential tools
apt-get install -y \
    git \
    vim \
    tmux \
    htop \
    curl \
    wget \
    jq \
    nmap \
    netcat \
    python3.11 \
    python3.11-venv \
    python3-pip \
    build-essential

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $(whoami)

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone MetaLLM
cd /opt
git clone https://github.com/perfecXion/MetaLLM.git
cd MetaLLM

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Jupyter Lab for analysis
pip install jupyterlab pandas matplotlib

# Create shortcut scripts
cat > /usr/local/bin/metalllm << 'METALLLM'
#!/bin/bash
cd /opt/MetaLLM
source venv/bin/activate
python metalllm.py "$@"
METALLLM
chmod +x /usr/local/bin/metalllm

# Create targets inventory file
cat > /opt/MetaLLM/targets.yaml << 'TARGETS'
llm_targets:
  - name: "Ollama"
    url: "http://10.0.2.10:11434"
    type: "llm"
  - name: "vLLM"
    url: "http://10.0.2.20:8000"
    type: "llm"

rag_targets:
  - name: "Qdrant"
    url: "http://10.0.3.20:6333"
    type: "vector_db"

agent_targets:
  - name: "LangChain"
    url: "http://10.0.4.10:8000"
    type: "agent"

mlops_targets:
  - name: "MLflow"
    url: "http://10.0.5.10:5000"
    type: "mlops"
TARGETS

echo "=== Control Node Setup Complete ==="
echo "Access with: gcloud compute ssh metalllm-control --tunnel-through-iap"
echo "Run MetaLLM: metalllm"
