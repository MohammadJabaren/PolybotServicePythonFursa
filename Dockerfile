# Use a lightweight Alpine-based Python image
FROM python:3.10-alpine

# Prevent interactive prompts during install
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install required system dependencies for Python packages
RUN apk update && apk upgrade && \
    apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libgl1 \
    libx11 \
    libstdc++ \
    curl

# Install Python dependencies
COPY ./polybot/requirements.txt ./requirements.txt
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Set default command
CMD ["python3", "-m", "polybot.app"]
