#!/bin/bash

# Define image names
BACKEND_IMAGE="backend-offline:latest"
FRONTEND_IMAGE="frontend-offline:latest"

# Build the Backend Docker images
echo "🚀 Building Docker images..."
docker build -t $BACKEND_IMAGE -f backend/Dockerfile .

echo "📦 Saving Docker images..."
docker save -o backend.tar $BACKEND_IMAGE

echo "🚀 Building Frontend Docker images..."
docker build -t $FRONTEND_IMAGE -f frontend/Dockerfile .

# Save the images as tar files
echo "📦 Saving Docker images..."
docker save -o frontend.tar $FRONTEND_IMAGE


