#!/bin/bash
# Ollama Target Setup Script

set -e

echo "=== Ollama Target Setup ==="

# Update and install dependencies
apt-get update
apt-get upgrade -y
apt-get install -y curl

# Install CUDA drivers (if not already installed by metadata)
if ! command -v nvidia-smi &> /dev/null; then
    echo "Installing NVIDIA drivers..."
    apt-get install -y ubuntu-drivers-common
    ubuntu-drivers autoinstall
fi

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to be ready
sleep 10

# Pull models
ollama pull llama2:7b
ollama pull mistral:7b
ollama pull phi:2.7b

# Configure Ollama to listen on all interfaces
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf << 'OVERRIDE'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
OVERRIDE

systemctl daemon-reload
systemctl restart ollama

echo "=== Ollama Setup Complete ==="
echo "API available at: http://$(hostname -I | awk '{print $1}'):11434"
