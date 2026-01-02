# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
ENV REACT_APP_BACKEND_URL=https://sibikrish-cr-agent.hf.space
RUN npm run build

# Stage 2: Setup Backend
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition
COPY pyproject.toml .

# Install dependencies
# Using pip to install dependencies defined in pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy backend code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create storage directories (if they don't exist from copy)
RUN mkdir -p uploads persistent_docs chroma_db

# Ingest persistent documents (bakes the vector store into the image)
# This also pre-downloads the embedding model
RUN python ingest_persistent_docs.py

# Expose the port
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
