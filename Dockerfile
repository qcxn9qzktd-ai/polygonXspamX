FROM debian:bookworm-slim

# Install system dependencies in a single layer and clean up cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3-pip \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install -U pip

# Set working directory and copy application code
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip3 install -U -r requirements.txt

# Run the application
CMD ["python3", "-m", "SpamX"]
