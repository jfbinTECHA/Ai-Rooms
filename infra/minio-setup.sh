#!/bin/bash

# MinIO setup script for AI Rooms

# Wait for MinIO to be ready
sleep 10

# Configure MinIO client
mc alias set local http://minio:9000 minioadmin minioadmin

# Create buckets
mc mb local/ai-rooms-uploads
mc mb local/ai-rooms-models
mc mb local/ai-rooms-logs

# Set bucket policies (optional)
mc policy set public local/ai-rooms-uploads

echo "MinIO setup completed"