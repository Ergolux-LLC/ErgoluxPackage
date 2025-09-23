FROM node:20-alpine

WORKDIR /app

# Create logs directory for centralized logging
RUN mkdir -p /app/logs

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose the port
EXPOSE 5173

# Start Vite with host binding for Docker and log output
CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0 2>&1 | tee /app/logs/frontend.log"]