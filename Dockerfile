# Multi-stage build for CV Generator

# Stage 1: Frontend build
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (using npm install since package-lock.json may not exist)
RUN npm install

# Copy frontend source and config files
COPY frontend/ ./frontend/
COPY tsconfig.json ./
COPY tsconfig.node.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY vite.config.ts ./

# Build frontend (Vite handles TypeScript compilation internally)
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Install pandoc >= 3.1.4 (download official binary if not available in repos)
RUN apt-get update && \
    apt-get install -y wget ca-certificates fonts-liberation && \
    (apt-get install -y pandoc || \
     (wget -q https://github.com/jgm/pandoc/releases/download/3.1.4/pandoc-3.1.4-1-amd64.deb && \
      dpkg -i pandoc-3.1.4-1-amd64.deb && \
      rm -f pandoc-3.1.4-1-amd64.deb)) && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create output directory
RUN mkdir -p backend/output && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# Run application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
