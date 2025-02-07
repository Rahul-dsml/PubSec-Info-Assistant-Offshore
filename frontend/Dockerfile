# Use Node.js for building the frontend
FROM node:22 AS builder

# Set the wodrking directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./package.json ./package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the Vite application
RUN npm run build

# Use Nginx to serve the built frontend
FROM nginx:alpine

# Copy the built files to the Nginx HTML directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 3000
EXPOSE 3000

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]