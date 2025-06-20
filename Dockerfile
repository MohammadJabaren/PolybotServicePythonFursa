FROM python:3.10-alpine


WORKDIR /app

# Install only necessary system libraries
RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Use layer caching for dependencies
COPY ./polybot/requirements.txt ./requirements.txt

# Upgrade pip and setuptools to fixed versions
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy the full app
COPY . .

CMD ["python3", "-m", "polybot.app"]
