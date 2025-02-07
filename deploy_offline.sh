#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Define image names from Docker Hub
BACKEND_IMAGE="purshotamsingh/backend:v2"
FRONTEND_IMAGE="sanki1998/real_estate:v2"

# Pull the Docker images
echo "📂 Pulling Docker images..."
docker pull $BACKEND_IMAGE
docker pull $FRONTEND_IMAGE

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
    command: uvicorn app:app --host 0.0.0.0 --port 8050
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - MODEL_NAME=${MODEL_NAME}
      - DATABASE_PATH=${DATABASE_PATH}
      - CSV_FILE_PATH=${CSV_FILE_PATH}
      - EXCEL_FILE_PATH=${EXCEL_FILE_PATH}

  frontend:
    image: $FRONTEND_IMAGE
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: always
EOF

echo "✅ Docker images pulled successfully."
echo "📤 Please send docker-compose.yml to the client."

# Run docker-compose
docker-compose --env-file .env up -d
echo "🚀 Starting containers..."

echo "✅ Application is now running! Access frontend at http://localhost:3000"