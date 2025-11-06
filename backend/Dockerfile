# Multi-stage build for Python backend
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-slim

# Install runtime dependencies including Nuclei
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Nuclei (using curl with redirect follow)
RUN curl -fsSL -o nuclei.zip https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip \
    && unzip -q nuclei.zip \
    && mv nuclei /usr/local/bin/nuclei \
    && chmod +x /usr/local/bin/nuclei \
    && rm nuclei.zip \
    || echo "Warning: Nuclei installation failed, continuing without it"

# Create non-root user
RUN useradd -m -u 1000 easm && \
    mkdir -p /app /data && \
    chown -R easm:easm /app /data

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/easm/.local

# Copy application code
COPY --chown=easm:easm . .

# Switch to non-root user
USER easm

# Add local bin to PATH
ENV PATH=/home/easm/.local/bin:$PATH

# Update Nuclei templates on build
RUN nuclei -update-templates || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (via startup script that initializes DB first)
CMD ["./start.sh"]
