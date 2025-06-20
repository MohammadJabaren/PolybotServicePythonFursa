FROM python:3.10-alpine

# Prevent interactive prompts during install
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies compatible with Alpine
RUN apk update && apk upgrade && \
    apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libstdc++ \
    libxrender \
    libxext \
    libsm \
    libgl \
    curl

# Copy only requirements first
COPY ./polybot/requirements.txt ./requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the app
CMD ["python3", "-m", "polybot.app"]
