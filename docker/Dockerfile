# Sonic Forage - Docker Image for Autonomous Sessions
# Optimized for GPU (NVIDIA) with long-running autonomous DJ / workstation operation.
#
# Build:
#   docker build -t forage-dj -f docker/Dockerfile .
#
# Run (with Z: drive bind mount - critical for large models):
#   docker run --gpus all -v /mnt/z/IMF2045/forage-dj:/workspace/forage-dj forage-dj

FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON_PREFERENCE=system

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libportaudio2 \
    portaudio19-dev \
    libasound2-dev \
    libjack-jackd2-dev \
    ffmpeg \
    libsndfile1 \
    espeak-ng \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /workspace

# Clone or copy the project (in production you will bind-mount instead)
# For image size, we expect the user to bind-mount the full /mnt/z/... path
COPY . /workspace/forage-dj

WORKDIR /workspace/forage-dj

# Install Python dependencies with uv (GPU-friendly)
RUN uv sync --extra full --group dev || true

# Default entrypoint for autonomous scheduled sessions
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["rave-prep"]