#!/bin/bash
# vLLM Server Setup Script

set -e

echo "=== vLLM Target Setup ==="

# Install CUDA if needed
if ! command -v nvidia-smi &> /dev/null; then
    apt-get update
    apt-get install -y ubuntu-drivers-common
    ubuntu-drivers autoinstall
fi

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Run vLLM with Mistral model (smaller for testing)
docker run -d \
    --name vllm \
    --restart always \
    --gpus all \
    -p 8000:8000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    vllm/vllm-openai:latest \
    --model mistralai/Mistral-7B-v0.1 \
    --host 0.0.0.0 \
    --port 8000

echo "=== vLLM Setup Complete (downloading model, may take time) ==="
echo "API available at: http://$(hostname -I | awk '{print $1}'):8000"
