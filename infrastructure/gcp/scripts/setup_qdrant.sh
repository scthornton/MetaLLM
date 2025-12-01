#!/bin/bash
# Qdrant Vector DB Setup Script

set -e

echo "=== Qdrant Target Setup ==="

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Run Qdrant (no authentication - intentionally vulnerable)
docker run -d \
    --name qdrant \
    --restart always \
    -p 6333:6333 \
    -p 6334:6334 \
    -v qdrant_storage:/qdrant/storage \
    qdrant/qdrant:v1.7.0

# Wait for Qdrant to start
sleep 15

# Create sample collections
curl -X PUT 'http://localhost:6333/collections/documents' \
    -H 'Content-Type: application/json' \
    -d '{
        "vectors": {
            "size": 1536,
            "distance": "Cosine"
        }
    }'

curl -X PUT 'http://localhost:6333/collections/embeddings' \
    -H 'Content-Type: application/json' \
    -d '{
        "vectors": {
            "size": 768,
            "distance": "Cosine"
        }
    }'

echo "=== Qdrant Setup Complete ==="
echo "API available at: http://$(hostname -I | awk '{print $1}'):6333"
