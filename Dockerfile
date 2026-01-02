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
# Install Chromium dependencies for Playwright
RUN apt-get update && \
    apt-get install -y wget ca-certificates fonts-liberation \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    libcups2 libpango-1.0-0 libcairo2 && \
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

# Install Playwright browsers (Chromium) as root
RUN playwright install chromium

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create output directory and copy Playwright cache to appuser
RUN mkdir -p backend/output && \
    mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/ms-playwright /home/appuser/.cache/ && \
    chown -R appuser:appuser /app /home/appuser/.cache

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# Run application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
