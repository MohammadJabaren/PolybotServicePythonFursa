FROM python:3.10-alpine

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
    mesa-gl \
    libxrender \
    libxext \
    libsm \
    curl

# Copy only requirements file for layer caching
COPY ./polybot/requirements.txt ./requirements.txt

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy rest of the application
COPY . .

CMD ["python3", "-m", "polybot.app"]
