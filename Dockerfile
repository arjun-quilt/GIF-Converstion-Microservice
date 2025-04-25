FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Rust
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    wget \
    gnupg \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . $HOME/.cargo/env \
    && rm -rf /var/lib/apt/lists/*

# Set Rust environment variables
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python dependencies and Playwright in a single layer
COPY requirements.txt .
RUN . $HOME/.cargo/env && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium && \
    playwright install-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 