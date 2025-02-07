#!/bin/bash

# Define image names
BACKEND_IMAGE="backend-offline:latest"
FRONTEND_IMAGE="frontend-offline:latest"

# Load the Docker images
echo "📂 Loading Docker images..."
docker load -i backend.tar
docker load -i frontend.tar

# Create docker-compose.yml for the client
echo "📝 Generating docker-compose.yml..."
cat <<EOF > docker-compose.yml
version: "3.8"
services:

  backend:
    image: $BACKEND_IMAGE
    ports:
      - "8050:8050"
    restart: always

  frontend:
    ports:
    image: $FRONTEND_IMAGE
      - "3000:80"
    depends_on:
      - backend
    restart: always
EOF

echo "✅ Docker images saved: backend.tar, frontend.tar"
echo "📤 Please send backend.tar, frontend.tar, and docker-compose.yml to the client."

# Run docker-compose
echo "🚀 Starting containers..."
docker-compose up -d

echo "✅ Application is now running! Access frontend at http://localhost:3000"
